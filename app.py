import streamlit as st
import google.generativeai as genai
import openai
from PIL import Image, ImageDraw, ImageFont
import requests
from bs4 import BeautifulSoup
from newspaper import Article
import io
import os
import tempfile
import base64
import time
import logging
import uuid  # Add this import for unique IDs
import datetime # To get current date
import locale # For date formatting
from babel.dates import format_date # Import Babel for date formatting

# Try importing fal_client, but gracefully handle if not installed
try:
    import fal_client
    from io import BytesIO # For Fal AI image handling
    FAL_CLIENT_AVAILABLE = True
    logging.info("Successfully imported fal_client")
except ImportError as e:
    FAL_CLIENT_AVAILABLE = False
    logging.warning(f"Could not import fal_client: {e}. Fal AI image generation will not be available.")

# Set page configuration
st.set_page_config(
    page_title="Article2Image - Instagram Post Generator",
    page_icon="📰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better UI
st.markdown("""
<style>
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    h1, h2, h3 {
        color: #1E88E5;
    }
    .stProgress > div > div > div > div {
        background-color: #1E88E5;
    }
    .stButton button {
        background-color: #1E88E5;
        color: white;
        border-radius: 5px;
        border: none;
        padding: 0.5rem 1rem;
        font-weight: bold;
    }
    .stButton button:hover {
        background-color: #1565C0;
        opacity: 0.9;
    }
    .highlight {
        background-color: #F5F7FA;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1.5rem 0;
        border-left: 5px solid #1E88E5;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    .success-box {
        background-color: #E8F5E9;
        border-left: 5px solid #4CAF50;
        padding: 1rem;
        border-radius: 0 5px 5px 0;
        margin: 1rem 0;
    }
    .info-box {
        background-color: #E3F2FD;
        border-left: 5px solid #2196F3;
        padding: 1rem;
        border-radius: 0 5px 5px 0;
        margin: 1rem 0;
    }
    .warning-box {
        background-color: #FFF3E0;
        border-left: 5px solid #FF9800;
        padding: 1rem;
        border-radius: 0 5px 5px 0;
        margin: 1rem 0;
    }
    .step-counter {
        background-color: #1E88E5;
        color: white;
        border-radius: 50%;
        width: 30px;
        height: 30px;
        text-align: center;
        line-height: 30px;
        margin-right: 10px;
        display: inline-block;
    }
    .preview-container {
        max-height: 500px;
        overflow-y: auto;
        border: 1px solid #ddd;
        border-radius: 5px;
        padding: 10px;
    }
    /* Accessibility improvements */
    .stTextInput input, .stTextArea textarea {
        font-size: 16px !important;
        padding: 10px !important;
    }
    # .stSelectbox > div > div {
    #     # padding: 10px !important;
    # }
    button {
        min-height: 44px !important; /* Ensure touch target size */
    }
    /* Focus indicators for accessibility */
    button:focus, input:focus, textarea:focus, select:focus {
        outline: 2px solid #1E88E5 !important;
        outline-offset: 2px !important;
    }
    /* High contrast form elements */
    .stTextInput input, .stTextArea textarea {
        border: 1px solid #555 !important;
    }
    /* Improved visual hierarchy */
    h1 {
        font-size: 32px !important;
        margin-bottom: 20px !important;
    }
    h2 {
        font-size: 24px !important;
        margin-top: 30px !important;
        margin-bottom: 15px !important;
    }
    h3 {
        font-size: 20px !important;
        margin-top: 25px !important;
        margin-bottom: 10px !important;
    }
</style>
""", unsafe_allow_html=True)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Configure API Keys using Streamlit Secrets
GOOGLE_API_KEY = st.secrets.get("GOOGLE_API_KEY")
FAL_KEY = st.secrets.get("FAL_KEY")
OPENAI_API_KEY = st.secrets.get("OPENAI_API_KEY") # Optional, if you use it

# Set FAL_KEY as environment variable for fal_client library if available
if FAL_KEY:
    os.environ['FAL_KEY'] = FAL_KEY
    logging.info("FAL_KEY set in environment for fal_client.")
else:
    # Log warning but don't prevent app run if only Fal is missing
    logging.warning("FAL_KEY not found in Streamlit secrets. Fal AI image generation will be unavailable.")

# Configure Google Generative AI
if not GOOGLE_API_KEY:
    # Display error prominently in the app
    st.error("Google API Key (GOOGLE_API_KEY) not found in Streamlit secrets. Please set it in your deployment settings or secrets.toml.")
    # Optionally, stop the app if Google API is essential
    # st.stop()
else:
    try:
        genai.configure(api_key=GOOGLE_API_KEY)
        logging.info("Google Generative AI configured successfully")
    except Exception as e:
        st.error(f"Error configuring Google API: {e}")

# Configure OpenAI if API key is available (Optional)
if OPENAI_API_KEY:
    try:
        openai.api_key = OPENAI_API_KEY
        logging.info("OpenAI configured successfully (Optional)")
    except Exception as e:
        st.warning(f"Error configuring OpenAI: {e}")
else:
    logging.info("OpenAI API Key not found in secrets, skipping configuration.")

# Add support for OpenAI GPT-Image-1 model
OPENAI_GPT_IMAGE_AVAILABLE = False
if st.secrets.get("OPENAI_API_KEY"):
    try:
        from openai import OpenAI
        # Test the client configuration with a simple API call
        try:
            client = OpenAI(api_key=st.secrets.get("OPENAI_API_KEY"))
            models = client.models.list()
            logging.info(f"OpenAI API connection successful: {len(models.data)} models available")
            OPENAI_GPT_IMAGE_AVAILABLE = True
            logging.info("OpenAI GPT-Image-1 support configured successfully")
        except Exception as test_error:
            logging.error(f"OpenAI API key validation failed: {test_error}")
            st.error(f"OpenAI API key validation failed: {test_error}")
    except ImportError:
        logging.error("Failed to import OpenAI client. Install with 'pip install openai'")
        st.error("OpenAI library not installed. Please install with 'pip install openai'")
else:
    logging.warning("OpenAI API key not found in Streamlit secrets")
    st.warning("OpenAI API key not found - GPT-Image-1 won't be available")

# Set image dimensions for Instagram post
IMG_WIDTH = 1079
IMG_HEIGHT = 1345

# Initialize session state variables if they don't exist
if 'current_step' not in st.session_state:
    st.session_state.current_step = 1
# Remove highlight/shadow settings but keep user_preferences structure for compatibility
if 'user_preferences' not in st.session_state:
    st.session_state.user_preferences = {
        'image_style': 'photorealistic'
    }
if 'language' not in st.session_state:
    st.session_state.language = 'en'
if 'page_id' not in st.session_state:
    st.session_state.page_id = str(uuid.uuid4())  # Create a unique session ID
if 'image_generated' not in st.session_state:
    st.session_state.image_generated = False
if 'generated' not in st.session_state:
    st.session_state.generated = False
    
# Add step navigation functions
def go_to_step(step_number):
    st.session_state.current_step = step_number
    st.rerun()
    
def next_step():
    st.session_state.current_step += 1
    st.rerun()
    
def prev_step():
    if st.session_state.current_step > 1:
        st.session_state.current_step -= 1
        st.rerun()

# Define allowed category keys (used internally)
ALLOWED_CATEGORY_KEYS = ["Societe", "hi-tech", "sports", "nation", "economie", "regions", "culture", "monde", "Sante", "LifeStyle"]

# Language translations - Keep French UI, keep category translations for display
TRANSLATIONS = {
    'en': {
        # No UI translations needed
        'categories': {
            'Societe': "Society", 'hi-tech': "Hi-Tech", 'sports': "Sports", 'nation': "Nation", 'economie': "Economy",
            'regions': "Regions", 'culture': "Culture", 'monde': "World", 'Sante': "Health", 'LifeStyle': "Lifestyle"
        },
        'language_name': "English"
    },
    'fr': {
        # Keep all French UI translations
        'title': "Générateur de Publications Instagram",
        'settings': "Paramètres",
        'input_method': "Méthode d'Entrée",
        'select_input': "Sélectionnez comment saisir votre article :",
        'url': "URL",
        'text': "Texte",
        'appearance': "Paramètres d'Apparence",
        'highlight_color': "Couleur de surbrillance pour les mots-clés :",
        'shadow': "Ombre d'arrière-plan du texte :",
        'image_style': "Style d'image :",
        'how_to_use': "Comment utiliser",
        'url_input': "Entrez l'URL de l'article :",
        'url_help': "Collez un lien vers n'importe quel article d'actualité ou blog",
        'text_input': "Entrez le texte de l'article :",
        'text_help': "Copiez et collez le texte de votre article ici",
        'example_btn': "Charger un Exemple",
        'content_settings': "Paramètres de Contenu",
        'bullet_words': "Mots du Point Principal",
        'description_words': "Mots de la Description",
        'hashtag_count': "Nombre de Hashtags",
        'generate_content': "Générer le Contenu",
        'bullet_point': "Point Principal",
        'bullet_info': "Ceci apparaîtra sur votre image",
        'article_description': "Description de l'Article",
        'description_info': "Ceci apparaîtra dans la légende de votre publication (pas sur l'image)",
        'hashtags': "Hashtags",
        'hashtags_info': "Ceux-ci apparaîtront dans la légende de votre publication (pas sur l'image)",
        'content_success': "Contenu généré ! Continuez vers l'onglet Image.",
        'preview': "Aperçu",
        'generate_image': "Générer une Image IA",
        'image_info': "Utilisation de DALL-E pour créer une image personnalisée basée sur votre contenu",
        'generate_btn': "Générer l'Image",
        'upload_image': "Télécharger Votre Propre Image",
        'upload_info': "Téléchargez une image d'arrière-plan personnalisée (sera redimensionnée à 768x957)",
        'upload_btn': "Télécharger une image d'arrière-plan personnalisée",
        'image_ready': "Image prête ! Passez à l'onglet Logo ou sautez à la Publication Finale.",
        'please_content': "Veuillez générer du contenu dans l'onglet Contenu en premier.",
        'add_logo': "Ajouter Votre Logo (Facultatif)",
        'logo_info': "Votre logo apparaîtra au centre en haut de l'image",
        'upload_logo': "Téléchargez votre logo de marque (PNG transparent recommandé)",
        'logo_uploaded': "Logo téléchargé ! Passez à l'onglet Publication Finale.",
        'remove_logo': "Supprimer le Logo",
        'skip_logo': "Téléchargez un logo ou passez à l'onglet Publication Finale si vous ne souhaitez pas ajouter de logo.",
        'please_image': "Veuillez générer une image dans l'onglet Image en premier.",
        'create_post': "Créer la Publication Instagram Finale",
        'create_btn': "Créer la Publication Instagram Finale",
        'download_btn': "Télécharger l'Image",
        'copy_btn': "Copier la Légende",
        'instagram_caption': "Légende Instagram",
        'view_copy': "Cliquez pour afficher/copier la légende de la publication",
        'copy_description': "Copier la description :",
        'copy_hashtags': "Copier les hashtags :",
        'post_ready': "Votre publication Instagram est prête ! Téléchargez l'image et copiez la légende pour la publication.",
        'what_next': "Que souhaitez-vous faire ensuite ?",
        'another_post': "Créer une Autre Publication",
        'different_style': "Essayer un Style Différent",
        'edit_post': "Modifier Cette Publication",
        'language': "Langue de Contenu", # Correctly label for content language
        'edit': "Modifier",
        'select_category_label': "Sélectionner la Catégorie :",
        'categories': {
            'Societe': "Société", 'hi-tech': "Hi-Tech", 'sports': "Sports", 'nation': "Nation", 'economie': "Économie",
            'regions': "Régions", 'culture': "Culture", 'monde': "Monde", 'Sante': "Santé", 'LifeStyle': "Style de Vie"
        },
        'language_name': "Français"
    },
    # Keep other language entries JUST for categories and language_name display
    'es': {
        'categories': {
             'Societe': "Sociedad", 'hi-tech': "Alta Tecnología", 'sports': "Deportes", 'nation': "Nación", 'economie': "Economía",
            'regions': "Regiones", 'culture': "Cultura", 'monde': "Mundo", 'Sante': "Salud", 'LifeStyle': "Estilo de Vida"
        },
        'language_name': "Español"
    },
    'de': {
         'categories': {
            'Societe': "Gesellschaft", 'hi-tech': "Hi-Tech", 'sports': "Sport", 'nation': "Nation", 'economie': "Wirtschaft",
            'regions': "Regionen", 'culture': "Kultur", 'monde': "Welt", 'Sante': "Gesundheit", 'LifeStyle': "Lebensstil"
        },
        'language_name': "Deutsch"
    },
    # ... Add other languages' categories and language_name as needed ...
}

# Function to get text - French UI, selected language categories/content
def get_text(key, lang=None):
    """
    Get UI text in French, but get category/content-related translations
    in the language specified by 'lang' or session_state.language.
    """
    selected_lang = lang if lang is not None else st.session_state.language

    # Handle category keys specifically - use the selected language for display
    if key.startswith('category_'):
        category_key = key.split('_', 1)[1]
        # Check selected language first
        if selected_lang in TRANSLATIONS and 'categories' in TRANSLATIONS[selected_lang] and category_key in TRANSLATIONS[selected_lang]['categories']:
            return TRANSLATIONS[selected_lang]['categories'][category_key]
        # Fallback to French category names if translation missing in selected lang
        if 'fr' in TRANSLATIONS and 'categories' in TRANSLATIONS['fr'] and category_key in TRANSLATIONS['fr']['categories']:
             logging.warning(f"Category translation for '{category_key}' not found in language '{selected_lang}'. Falling back to French.")
             return TRANSLATIONS['fr']['categories'][category_key]
        return category_key # Return key if no translation found anywhere

    # For all other keys (UI elements), always return French
    if 'fr' in TRANSLATIONS and key in TRANSLATIONS['fr']:
        return TRANSLATIONS['fr'][key]

    # Fallback for missing French UI keys
    logging.warning(f"UI translation key '{key}' not found in French. Using fallback.")
    return key.replace('_', ' ').title()

def extract_article_from_url(url):
    """Extract article content from a given URL"""
    try:
        # Set a user agent to mimic a browser
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # First get the content with requests
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            st.error(f"Failed to access the URL: {url} (Status code: {response.status_code})")
            return None
            
        # Create article with pre-fetched html
        article = Article(url)
        article.download(input_html=response.text)
        article.parse()
        
        # Check if text extraction was successful
        if not article.text:
            st.warning(f"Could not automatically extract text content from {url}. The site might be blocking scraping.")
            return None
            
        return {
            "title": article.title,
            "text": article.text,
            "summary": article.summary
        }
    except Exception as e:
        st.error(f"Error extracting article: {e}")
        return None

def generate_summary_bullet(article_text, max_words=30):
    """Generate a single concise bullet point using Gemini in the selected language"""
    try:
        model = genai.GenerativeModel('gemini-2.0-flash')
        # Determine target language name from TRANSLATIONS
        target_language = TRANSLATIONS.get(st.session_state.language, {}).get('language_name', st.session_state.language) # Fallback to code if name missing
        prompt = f"""
        Create 1 concise bullet point in {target_language} that summarizes the key point from this article.
        The bullet point should be approximately {max_words} words long.
        Make it clear, informative, and capture the most important aspect of the article.
        Do NOT include a bullet marker or any formatting, just plain text.
        
        Article:
        {article_text}
        """
        response = model.generate_content(prompt)
        logging.info(f"Generated bullet point in {target_language}")
        return response.text.strip()
    except Exception as e:
        st.error(f"Error generating bullet point: {e}")
        return ""

def generate_article_description(article_text, max_words=70):
    """Generate a brief description using Gemini in the selected language"""
    try:
        model = genai.GenerativeModel('gemini-2.0-flash')
        target_language = TRANSLATIONS.get(st.session_state.language, {}).get('language_name', st.session_state.language)
        prompt = f"""
        Extract the core message of the following article and present it as an engaging description in {target_language}, approximately {max_words} words long.
        Write the description directly, as if it's a compelling snippet from the article itself. 
        Do NOT start with phrases like 'This article discusses' or 'The author argues'. 
        Focus on presenting the key information and takeaways in an informative and captivating way for a social media audience.
        
        Article:
        {article_text}
        """
        response = model.generate_content(prompt)
        logging.info(f"Generated description in {target_language} (direct style)")
        return response.text.strip()
    except Exception as e:
        st.error(f"Error generating description: {e}")
        return ""

def generate_hashtags(article_text, num_hashtags=5):
    """Generate relevant hashtags using Gemini, considering the selected language"""
    try:
        model = genai.GenerativeModel('gemini-2.0-flash')
        target_language = TRANSLATIONS.get(st.session_state.language, {}).get('language_name', st.session_state.language)
        prompt = f"""
        Generate exactly {num_hashtags} relevant hashtags for a social media post about this article.
        The primary language of the content is {target_language}. Generate hashtags appropriate for this language context.
        Format them as: #Hashtag1 #Hashtag2 #Hashtag3 etc.
        ONLY return the hashtags themselves with no additional text, explanations, or numbering.
        Make them relevant to the content.
        
        Article:
        {article_text}
        """
        response = model.generate_content(prompt)
        hashtags = response.text.strip()
        logging.info(f"Generated hashtags for {target_language} context")
        # ... (hashtag cleanup remains the same) ...
        if '#' in hashtags:
            import re
            hashtag_pattern = r'#[A-Za-z0-9_]+'
            found_hashtags = re.findall(hashtag_pattern, hashtags)
            if found_hashtags:
                return ' '.join(found_hashtags)
        return hashtags
    except Exception as e:
        st.error(f"Error generating hashtags: {e}")
        return ""

# --- Generate Category --- (Uses content generated in selected language)
def generate_category(bullet_point, description):
    """Generate a category KEY based on the bullet point and description using Gemini."""
    try:
        model = genai.GenerativeModel('gemini-2.0-flash')
        # The prompt still asks for a KEY from the predefined list
        prompt = f"""
        Analyze the following content (which might be in any language):
        Bullet Point: {bullet_point}
        Description: {description}

        Choose the MOST relevant category KEY from this list:
        {', '.join(ALLOWED_CATEGORY_KEYS)}

        Return ONLY the category KEY from the list, with no other text or explanation. For example, if the best category is 'hi-tech', just return 'hi-tech'.
        """
        response = model.generate_content(prompt)
        category_key = response.text.strip()

        # Validate the response against the keys
        if category_key in ALLOWED_CATEGORY_KEYS:
            logging.info(f"Gemini generated category key: {category_key}")
            return category_key
        else:
            logging.warning(f"Gemini returned an invalid category key '{category_key}'. Defaulting to 'Societe'.")
            return "Societe" # Default category key

    except Exception as e:
        st.error(f"Error generating category: {e}")
        logging.error(f"Error generating category: {e}", exc_info=True)
        return "Societe" # Default category key on error

def generate_image(bullet_point, description, size=(IMG_WIDTH, IMG_HEIGHT)):
    """Generate image using OpenAI's GPT-Image-1 model with proper dimensions"""
    target_width, target_height = 1079, 1345  # Fixed dimensions for Instagram
    
    logging.info(f"Generating image for: {bullet_point[:50]}...")
    
    # Check if OpenAI is available first
    if not OPENAI_GPT_IMAGE_AVAILABLE:
        logging.warning("OpenAI GPT-Image-1 is not available. Using placeholder instead.")
        return create_enhanced_placeholder(bullet_point, (target_width, target_height))
    
    # Create prompt for OpenAI
    scene_prompt = (
        f"Ultra-realistic 4K editorial photograph press shot illustrating the following topic: {bullet_point}. "
        f"Context: {description}. "
        "Symbolic, in-animate elements that visually convey the story; dramatic cinematic lighting, high contrast, deep shadows, news-photography style, vertical 9:16 composition. "
        "Scene is completely deserted — absolutely no faces, silhouettes or body parts; no written text, no logos, no flags or religious symbols.no public figures. "
        "without written text, without logos, without flags or religious symbols, without public figures."
    )
    
    try:
        # Initialize OpenAI client
        if not st.secrets.get("OPENAI_API_KEY"):
            raise ValueError("OpenAI API key not found in Streamlit secrets")
            
        from openai import OpenAI
        client = OpenAI(api_key=st.secrets.get("OPENAI_API_KEY"))
        
        # Call OpenAI's image generation
        logging.info("Calling OpenAI GPT-Image-1 API")
        response = client.images.generate(
            model="gpt-image-1",
            prompt=scene_prompt,
            n=1,
            size="1024x1024",  # Use standard size first
            quality="high",
        )
        
        # Check if response contains valid data
        if not response.data or len(response.data) == 0:
            raise ValueError("Invalid response from OpenAI API - missing image data")
            
        # Extract the image URL from the response
        image_url = None
        if hasattr(response.data[0], 'url') and response.data[0].url:
            image_url = response.data[0].url
        elif hasattr(response.data[0], 'b64_json') and response.data[0].b64_json:
            # Handle base64 image if URL is not available
            import base64
            image_bytes = base64.b64decode(response.data[0].b64_json)
            img = Image.open(io.BytesIO(image_bytes))
            logging.info(f"Image created from base64 data. Size: {img.size}")
        else:
            raise ValueError("No image URL or base64 data received in OpenAI API response")
        
        # If we have a URL, download the image
        if image_url:
            logging.info(f"Image URL received, downloading...")
            response = requests.get(image_url, timeout=10)
            response.raise_for_status()
            img = Image.open(io.BytesIO(response.content))
            logging.info(f"Image downloaded. Size: {img.size}, Mode: {img.mode}")
        
        # Calculate dimensions to maintain aspect ratio for target size
        original_aspect = img.width / img.height
        target_aspect = target_width / target_height
        
        if original_aspect > target_aspect:
            # Original image is wider - resize to target height then crop width
            new_width = int(target_height * original_aspect)
            new_height = target_height
            img = img.resize((new_width, new_height), Image.LANCZOS)
            left = (new_width - target_width) // 2
            img = img.crop((left, 0, left + target_width, target_height))
        else:
            # Original image is taller - resize to target width then crop height
            new_height = int(target_width / original_aspect)
            new_width = target_width
            img = img.resize((new_width, new_height), Image.LANCZOS)
            top = (new_height - target_height) // 2
            img = img.crop((0, top, target_width, top + target_height))
        
        # Convert to RGB if needed
        if img.mode != 'RGB':
            img = img.convert('RGB')
            
        logging.info(f"Final image dimensions: {img.size}")
        
        # Record model used for the image generation
        st.session_state['image_model_used'] = "OpenAI GPT-Image-1"
        
        return img
        
    except Exception as e:
        logging.error(f"Error generating image with OpenAI: {e}", exc_info=True)
        st.error(f"Failed to generate image: {str(e)}")
        # Return a placeholder image with the exact dimensions
        st.session_state['image_model_used'] = "Fallback (Error)"
        return create_enhanced_placeholder(bullet_point, (target_width, target_height))

def create_simple_image(bullet_point="Demo image", size=(IMG_WIDTH, IMG_HEIGHT)):
    """Create a simple image with text for testing"""
    img = Image.new('RGB', size, color=(40, 70, 120))
    draw = ImageDraw.Draw(img)
    
    # Draw a gradient background
    for y in range(size[1]):
        r = int(40 + (y / size[1]) * 40)
        g = int(70 + (y / size[1]) * 30)
        b = int(120 - (y / size[1]) * 40)
        draw.line([(0, y), (size[0], y)], fill=(r, g, b))
    
    # Add some shapes
    for i in range(5):
        x = int(size[0] * (0.2 + 0.15 * i))
        y = int(size[1] * 0.3)
        radius = int(size[0] * 0.08)
        draw.ellipse([x-radius, y-radius, x+radius, y+radius], 
                     fill=(255, 255, 255, 100), 
                     outline=(255, 255, 255))
    
    try:
        font = ImageFont.truetype("arial.ttf", 30)
    except:
        font = ImageFont.load_default()
    
    # Add text
    timestamp = time.strftime("%H:%M:%S")
    text = f"TEST IMAGE\n{bullet_point[:30]}...\nCreated at: {timestamp}"
    
    text_bbox = draw.textbbox((0,0), text, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    
    position = ((size[0] - text_width) // 2, (size[1] - text_height) // 2)
    draw.text(position, text, font=font, fill=(255, 255, 255))
    
    return img

def extract_image_from_response(response, size=(IMG_WIDTH, IMG_HEIGHT)):
    """Helper function to try extracting image from response in various formats"""
    try:
        # Check if it's a candidate-based response
        if hasattr(response, 'candidates') and response.candidates:
            for candidate in response.candidates:
                if hasattr(candidate, 'content') and candidate.content:
                    content = candidate.content
                    if hasattr(content, 'parts') and content.parts:
                        for part in content.parts:
                            # Try different possible image data locations
                            if hasattr(part, 'inline_data') and part.inline_data:
                                inline_data = part.inline_data
                                if hasattr(inline_data, 'data') and inline_data.data:
                                    import base64
                                    try:
                                        img_data = base64.b64decode(inline_data.data)
                                        img = Image.open(io.BytesIO(img_data))
                                        img = img.resize(size)
                                        return img
                                    except Exception:
                                        pass
                            
                            # Try other possible formats (data URI in text)
                            if hasattr(part, 'text') and part.text and part.text.startswith('data:image'):
                                try:
                                    import base64
                                    data_uri = part.text
                                    img_data = data_uri.split(',')[1]
                                    img = Image.open(io.BytesIO(base64.b64decode(img_data)))
                                    img = img.resize(size)
                                    return img
                                except Exception:
                                    pass
                                    
        # Check if direct parts format
        if hasattr(response, 'parts'):
            for part in response.parts:
                # Various possible formats
                if hasattr(part, 'inline_data') and hasattr(part.inline_data, 'data'):
                    try:
                        import base64
                        img_data = base64.b64decode(part.inline_data.data)
                        img = Image.open(io.BytesIO(img_data))
                        img = img.resize(size)
                        return img
                    except Exception:
                        pass
        
        # Nothing found
        return None
        
    except Exception as e:
        st.error(f"Error extracting image: {e}")
        return None

def create_enhanced_placeholder(text, size=(IMG_WIDTH, IMG_HEIGHT)):
    """Create a visually interesting placeholder image based on the content, using the correct global dimensions"""
    import random
    import math
    
    # Explicitly use the target size passed to the function
    target_width, target_height = size
    logging.info(f"Creating placeholder with dimensions: {target_width}x{target_height}")
    
    # Create a base image with gradient
    img = Image.new('RGB', (target_width, target_height), color=(30, 50, 70))
    draw = ImageDraw.Draw(img)
    
    # Create a more colorful gradient background
    for y in range(target_height):
        # Create a gradient with more Instagram-friendly colors
        progress = y / target_height
        # Create a more vibrant gradient (purple to coral-orange)
        r = int(100 + (155 * progress))
        g = int(50 + (100 * progress))
        b = int(180 - (100 * progress))
        draw.line([(0, y), (target_width, y)], fill=(r, g, b))
    
    # Extract keywords for visualization
    keywords = []
    for word in text.split():
        if len(word) > 4 and word.lower() not in ['with', 'this', 'that', 'from', 'your', 'have', 'there']:
            keywords.append(word.strip('.,!?;:()[]{}'))
    
    # Use up to 5 keywords
    keywords = keywords[:5]
    
    # Add a visually appealing background pattern
    for i in range(15):  # Add more elements for visual interest
        x = random.randint(0, target_width)
        y = random.randint(0, target_height)
        radius = random.randint(int(min(target_width, target_height)*0.05), int(min(target_width, target_height)*0.1))
        opacity = random.randint(30, 80)
        color = (255, 255, 255, opacity)
        draw.ellipse((x-radius, y-radius, x+radius, y+radius), fill=color)
    
    # Create abstract shapes representing the keywords
    shapes = []
    
    # Generate abstract shapes based on keywords
    for i, keyword in enumerate(keywords):
        # Use the hash of the keyword to generate consistent shapes
        seed = sum(ord(c) for c in keyword)
        random.seed(seed)
        
        # Shape parameters
        shape_type = random.choice(['circle', 'rectangle', 'triangle'])
        x_center = random.randint(int(target_width * 0.2), int(target_width * 0.8))
        y_center = random.randint(int(target_height * 0.2), int(target_height * 0.8))
        
        # Size proportional to word length
        size_factor = len(keyword) / 10 + 0.5
        shape_size = int(min(target_width, target_height) * 0.15 * size_factor)
        
        # Color based on the keyword
        hue = (sum(ord(c) for c in keyword) % 360) / 360.0
        
        # Convert HSV to RGB (simplified)
        if hue < 1/6:
            r, g, b = 255, int(255 * hue * 6), 0
        elif hue < 2/6:
            r, g, b = int(255 * (2/6 - hue) * 6), 255, 0
        elif hue < 3/6:
            r, g, b = 0, 255, int(255 * (hue - 2/6) * 6)
        elif hue < 4/6:
            r, g, b = 0, int(255 * (4/6 - hue) * 6), 255
        elif hue < 5/6:
            r, g, b = int(255 * (hue - 4/6) * 6), 0, 255
        else:
            r, g, b = 255, 0, int(255 * (1 - hue) * 6)
        
        # Add opacity
        opacity = 120 + random.randint(0, 100)
        color = (r, g, b, opacity)
        
        # Draw the shape
        if shape_type == 'circle':
            draw.ellipse(
                [(x_center - shape_size, y_center - shape_size), 
                 (x_center + shape_size, y_center + shape_size)], 
                fill=color
            )
        elif shape_type == 'rectangle':
            rotation = random.randint(0, 45)
            rect_img = Image.new('RGBA', (shape_size*2, shape_size), (r, g, b, opacity))
            rect_img = rect_img.rotate(rotation, expand=True)
            img.paste(rect_img, (x_center - shape_size, y_center - shape_size//2), rect_img)
        elif shape_type == 'triangle':
            points = [
                (x_center, y_center - shape_size),
                (x_center - shape_size, y_center + shape_size),
                (x_center + shape_size, y_center + shape_size)
            ]
            draw.polygon(points, fill=color)
        
        # Add shape to the list for connecting lines
        shapes.append((x_center, y_center))
    
    # Add some connecting lines
    if len(shapes) > 1:
        for i in range(len(shapes) - 1):
            start = shapes[i]
            end = shapes[i + 1]
            draw.line([(start[0], start[1]), (end[0], end[1])], fill=(255, 255, 255, 100), width=2)
        
        # Add a final connecting line to close the shape
        if len(shapes) > 2:
            draw.line([(shapes[-1][0], shapes[-1][1]), (shapes[0][0], shapes[0][1])], 
                      fill=(255, 255, 255, 100), width=2)
    
    # Add a mock Instagram-style interface element at the bottom to make it look more like an IG post
    footer_height = 50
    draw.rectangle([(0, target_height-footer_height), (target_width, target_height)], fill=(20, 20, 20, 200))
    
    # Add some small icons in the footer to simulate Instagram UI
    icon_y = target_height - footer_height//2
    # Like icon (heart shape)
    draw.ellipse([(20, icon_y-10), (40, icon_y+10)], fill=(255, 255, 255, 150))
    # Comment icon
    draw.rectangle([(60, icon_y-10), (80, icon_y+10)], fill=(255, 255, 255, 150))
    # Share icon
    draw.rectangle([(100, icon_y-10), (120, icon_y+10)], fill=(255, 255, 255, 150))
    
    # Add a timestamp-like text in the corner
    try:
        small_font = ImageFont.truetype("arial.ttf", 12)
    except:
        small_font = ImageFont.load_default()
    timestamp = time.strftime("%H:%M")
    draw.text((target_width-50, 20), timestamp, fill=(255, 255, 255, 200), font=small_font)
    
    # Convert to RGB for compatibility
    if img.mode == 'RGBA':
        img = img.convert('RGB')
    
    return img

# Helper function for color selection
def get_color_from_name(color_name):
    colors = {
        'green': (120, 255, 150),
        'blue': (100, 180, 255),
        'purple': (180, 120, 255),
        'orange': (255, 160, 80),
        'pink': (255, 120, 180),
        'yellow': (255, 230, 100)
    }
    return colors.get(color_name, (120, 255, 150))  # Default to green if not found

# Helper function for text wrapping
def wrap_text(text, font, max_width):
    lines = []
    # If the text width is within the max width, return it as a single line
    if font.getbbox(text)[2] <= max_width:
        lines.append(text)
    else:
        # Split the text into words
        words = text.split(' ')
        i = 0
        # Append every word into a line while its width is shorter than the max width
        while i < len(words):
            line = ''
            while i < len(words) and font.getbbox(line + words[i])[2] <= max_width:
                line = line + words[i] + " "
                i += 1
            if not line:
                line = words[i]
                i += 1
            lines.append(line.strip())
    return lines

# --- New Drawing Functions ---

def draw_date_text(draw, date_str, font, position, color):
    """Draws the date string at the specified position."""
    try:
        draw.text(position, date_str, fill=color, font=font)
        logging.info(f"Drew date: {date_str} at {position}")
    except Exception as e:
        logging.error(f"Error in draw_date_text: {e}")

def calculate_date_position(img_size, text_area_top, side_margin):
    """Calculate date position independently from main text.
    This function places the date in a fixed position relative to the top text area,
    independent of the main text block.
    """
    try:
        # Fixed position from the top of the text area
        fixed_top_margin = 50  # Distance from text_area_top
        date_y = text_area_top + fixed_top_margin
        # Horizontal position from left edge with consistent margin
        date_x = side_margin + 180  # Same as previously defined
        return (date_x, date_y)
    except Exception as e:
        logging.error(f"Error calculating date position: {e}")
        # Return a fallback position if calculation fails
        return (side_margin + 180, text_area_top + 35)

def draw_main_text(draw, lines, font, start_y, img_width, color, line_height, line_spacing):
    """Draws the wrapped main text, centered horizontally."""
    current_y = start_y
    try:
        for line in lines:
            line_bbox = draw.textbbox((0, 0), line, font=font)
            line_width = line_bbox[2] - line_bbox[0]
            start_x = (img_width - line_width) // 2 # Center horizontally
            draw.text((start_x, current_y), line, fill=color, font=font)
            current_y += line_height + line_spacing
        logging.info(f"Drew {len(lines)} lines of main text starting at y={start_y}")
    except Exception as e:
        logging.error(f"Error in draw_main_text: {e}")

def draw_category_label(draw, text, font_path, font_size, position, text_color, bg_color, padding):
    """Draws a category label with a background rectangle.

    Args:
        draw: The ImageDraw object.
        text: The text for the label.
        font_path: Path to the preferred font file.
        font_size: The desired font size.
        position: Tuple (x, y) for the top-left corner.
        text_color: Tuple for text color.
        bg_color: Tuple for background color.
        padding: Tuple (horizontal_padding, vertical_padding).
    """
    try:
        # Try loading the preferred font, with fallbacks
        # font_size = 32 # Font size is now passed as an argument
        font = None
        try:
            font = ImageFont.truetype(font_path, font_size) # Use passed font_size
            logging.info(f"Using preferred category font: {font_path} at size {font_size}")
        except (IOError, TypeError):
            logging.warning(f"Preferred font '{font_path}' not found or invalid. Trying fallbacks.")
            # Fallback sequence: Bold -> Italic -> Arial Bold -> Arial Italic -> Arial Regular -> Default
            fallback_fonts = [
                "Montserrat-Bold.ttf",
                "Montserrat-Italic.ttf",
                "arialbd.ttf",
                "ariali.ttf",
                "arial.ttf"
            ]
            fallback_found = False
            for fb in fallback_fonts:
                try:
                    font = ImageFont.truetype(fb, font_size)
                    logging.info(f"Using fallback category font: {fb}")
                    fallback_found = True
                    break
                except IOError:
                    logging.debug(f"Fallback font {fb} not found.")
                    continue

            if not fallback_found:
                 logging.warning("All fallback fonts failed. Using default PIL font.")
                 font = ImageFont.load_default(size=font_size)

        # Calculate text size
        text_bbox = draw.textbbox((0, 0), text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]

        # Calculate background rectangle size
        rect_width = text_width + 2 * padding[0] # Horizontal padding
        rect_height = text_height + 2 * padding[1] # Vertical padding

        # Define rectangle coordinates (using top-left from position)
        rect_x0 = position[0]
        rect_y0 = position[1]
        rect_x1 = rect_x0 + rect_width
        rect_y1 = rect_y0 + rect_height

        # Draw the background rectangle (simple rectangle for now)
        draw.rectangle([(rect_x0, rect_y0), (rect_x1, rect_y1)], fill=bg_color)

        # Calculate text position (centered within the rectangle)
        # Adjusting for font metrics can be tricky, this centers the baseline roughly
        text_x = rect_x0 + padding[0]
        text_y = rect_y0 + padding[1] - text_bbox[1] # Offset by the font's top bearing

        # Draw the text
        draw.text((text_x, text_y), text, fill=text_color, font=font)
        logging.info(f"Drew category label '{text}' at {position}")

    except Exception as e:
        logging.error(f"Error in draw_category_label: {e}")

# --- End New Drawing Functions ---

def add_text_to_image(image, bullet_point, category_key, brand_logo=None):
    """Overlay Frame.png and add text (including date and category) to the generated image"""

    # Ensure the base image is in RGBA mode for proper compositing
    base_image = image.convert('RGBA') if image.mode != 'RGBA' else image.copy()
    target_size = (IMG_WIDTH, IMG_HEIGHT) # Should be (1079, 1345)

    # --- Load Frame --- (Error handling remains the same)
    frame_path = "Frame.png"
    frame_image = None
    try:
        frame_image = Image.open(frame_path).convert('RGBA')
        if frame_image.size != target_size:
            logging.warning(f"Resizing frame from {frame_image.size} to {target_size}")
            frame_image = frame_image.resize(target_size, Image.Resampling.LANCZOS)
    except Exception as e:
        logging.error(f"Error loading/processing frame {frame_path}: {e}")
        st.error(f"Frame file '{frame_path}' not found or invalid. Proceeding without frame.")

    # --- Prepare Overlays ---
    text_overlay = Image.new('RGBA', target_size, (0, 0, 0, 0))
    text_draw = ImageDraw.Draw(text_overlay)
    logo_overlay = None

    # --- Define Text Area Parameters & Constants ---
    img_width, img_height = target_size
    # ASSUMING frame structure for text placement:
    black_band_height_assumption = int(img_height * 0.32)
    text_area_top = img_height - black_band_height_assumption + 60
    text_area_height = black_band_height_assumption - 80
    side_margin = 60
    max_text_width = img_width - (side_margin * 2)
    main_text_line_spacing = 15
    date_main_text_spacing = 20 # Vertical space between date and main text
    date_font_size = 30
    date_color = (0, 178, 80) # Green
    line_color = date_color
    line_length = 50
    line_thickness = 4
    line_date_spacing = 60 # Drastically increased spacing for testing
    main_text_color = (255, 255, 255) # White

    # --- Load Fonts ---
    main_font_path = None
    preferred_fonts = ["Montserrat-Bold.ttf", "arialbd.ttf", "ariblk.ttf", "arial.ttf"]
    for pf in preferred_fonts:
        try: ImageFont.truetype(pf, 10); main_font_path = pf; break
        except IOError: pass
    if main_font_path: logging.info(f"Using main font: {main_font_path}")
    else: logging.warning("Main bold font not found, using default.")

    date_font_path = None
    italic_fonts = ["Montserrat-Italic.ttf", "ariali.ttf"] # Prioritize italic fonts
    for itf in italic_fonts:
        try:
            ImageFont.truetype(itf, 10)
            date_font_path = itf
            logging.info(f"Using date font: {date_font_path}")
            break
        except IOError:
            logging.warning(f"Italic font not found: {itf}")
            continue
    
    # Fallback to regular fonts if italic not found
    if not date_font_path:
        logging.warning("Italic date fonts not found. Falling back to default.")
        date_font = ImageFont.load_default(size=date_font_size) # Request size
    elif date_font_path:
        try:
            date_font = ImageFont.truetype(date_font_path, date_font_size)
        except Exception as e:
            logging.error(f"Error loading date font {date_font_path}: {e}")
            date_font = ImageFont.load_default(size=date_font_size)
 
    if date_font_path:
        date_font = ImageFont.truetype(date_font_path, date_font_size)
    else:
        logging.warning("Date font not found, using default.")
        date_font = ImageFont.load_default(size=date_font_size) # Request size

    # --- Format Date using Babel --- 
    date_str = ""
    date_text_height = 0
    try:
        today = datetime.date.today()
        lang = st.session_state.language # Get current language code (e.g., 'fr', 'en')
        
        # Use Babel's format_date for locale-aware formatting
        # format='full' gives like "Wednesday, April 30, 2025"
        # format='long' gives like "April 30, 2025"
        # Custom format: "EEEE, dd/MM/y" (EEEE is full day name)
        try:
            # Use the language code directly with Babel
            date_str = format_date(today, format='EEEE, dd/MM/y', locale=lang)
            # Capitalize only the first letter for French style if needed
            if lang == 'fr': 
                date_str = date_str.capitalize() 
            logging.info(f"Formatted date using Babel for locale '{lang}': {date_str}")
        except Exception as babel_err: # Catch potential Babel errors (e.g., unknown locale)
            logging.error(f"Babel date formatting failed for locale '{lang}': {babel_err}. Falling back.")
            date_str = today.strftime("%Y-%m-%d") # Basic fallback

        # Calculate text size using the loaded date_font
        if date_font:
             date_text_bbox = text_draw.textbbox((0, 0), date_str, font=date_font)
             date_text_height = date_text_bbox[3] - date_text_bbox[1]
        else:
             logging.error("Date font not available for size calculation.")
             date_text_height = 0 # Set to zero if font failed to load

    except Exception as date_err:
        logging.error(f"Error preparing date: {date_err}", exc_info=True)
        date_str = "" # Clear date string on error
        date_text_height = 0
        # date_font is already handled above

    # --- Calculate Main Text Size --- (Using loaded main font)
    initial_font_size = 45 # Reduced further
    min_font_size = 25   # Reduced further
    current_font_size = initial_font_size
    final_lines = []
    main_font = None
    total_main_text_height = 0
    actual_line_height = 0
    text_fits = False

    # Calculate available height for main text - no longer dependent on date height
    available_height_for_main_text = text_area_height - 60  # Fixed spacing reserved for date area

    while current_font_size >= min_font_size:
        try:
            if main_font_path:
                main_font = ImageFont.truetype(main_font_path, current_font_size)
            else:
                main_font = ImageFont.load_default(size=current_font_size)
        except Exception as e:
            logging.error(f"Error loading main font size {current_font_size}: {e}")
            main_font = ImageFont.load_default(size=current_font_size)

        wrapped_lines = wrap_text(bullet_point.strip(), main_font, max_text_width)
        line_height_bbox = main_font.getbbox('Mg') # Use letters with ascenders/descenders
        actual_line_height = line_height_bbox[3] - line_height_bbox[1]
        _total_height = len(wrapped_lines) * actual_line_height + max(0, len(wrapped_lines) - 1) * main_text_line_spacing

        if _total_height <= available_height_for_main_text:
            final_lines = wrapped_lines
            total_main_text_height = _total_height
            text_fits = True
            logging.info(f"Main text fits at font size: {current_font_size}")
            break
        else:
            current_font_size -= 5

    if not text_fits:
        logging.warning(f"Main text might be cut off. Using min font size {min_font_size}.")
        if main_font is None or main_font.size != min_font_size:
             try:
                 if main_font_path: main_font = ImageFont.truetype(main_font_path, min_font_size)
                 else: main_font = ImageFont.load_default(size=min_font_size)
             except: main_font = ImageFont.load_default(size=min_font_size)
        final_lines = wrap_text(bullet_point.strip(), main_font, max_text_width)
        line_height_bbox = main_font.getbbox('Mg')
        actual_line_height = line_height_bbox[3] - line_height_bbox[1]
        total_main_text_height = len(final_lines) * actual_line_height + max(0, len(final_lines) - 1) * main_text_line_spacing

    # --- Calculate Vertical Positions --- (Independently)
    # Date position calculated first and independently
    date_position = calculate_date_position((img_width, img_height), text_area_top, side_margin)
    
    # Main text positioned independently, centered in the remaining area
    main_text_vertical_margin = 80  # Space from top of text area to main text
    main_text_start_y = text_area_top + main_text_vertical_margin
    
    # Center the main text block in the available space
    content_area_height = text_area_height - main_text_vertical_margin - 20  # 20px bottom margin
    main_text_start_y += (content_area_height - total_main_text_height) // 2

    # --- Draw Date and Line (if date was prepared successfully and font loaded) ---
    if date_str and date_font:
        # Draw date using function with the calculated position
        draw_date_text(text_draw, date_str, date_font, date_position, date_color)
        logging.info(f"Drew date: {date_str} at {date_position}")
    elif not date_font:
        logging.error("Could not draw date because date_font was not loaded.")
    # else: date_str might be empty due to error

    # --- Draw Main Text --- (Using calculated position and dedicated function)
    if main_font:
        draw_main_text(text_draw, final_lines, main_font, main_text_start_y, img_width, 
                      main_text_color, actual_line_height, main_text_line_spacing)
    else:
        logging.error("Could not draw main text because main_font was not loaded.")

    # --- Draw Category Label ---
    try:
        # Look up the translated category name using the key and selected language
        translated_category_name = get_text(f"category_{category_key}")

        # --- Prepare the category text for display ---
        display_category_text = translated_category_name.title() # Title case the translated name
        logging.info(f"Category text before drawing: '{display_category_text}' (Original key: '{category_key}', Language: {st.session_state.language})")
        # --------------------------------------------

        category_text_color = (255, 255, 255) # White
        # category_bg_color = (0, 128, 64) # Darker Green
        category_bg_color = (0, 0, 0, 0) # Transparent
        category_padding = (20, 10) # Simplified padding (H, V) - match previous usage in draw_category_label
        # Try to use a Bold Italic font, fallback for sizing
        category_font_path = "Montserrat-BoldItalic.ttf" # Preferred bold italic font

        # Fixed Position for Category Label (Top-Right Area)
        fixed_category_x = img_width - 490 # Pixels from right edge
        fixed_category_y = 870       # Pixels from top edge
        # Define font size here, as it's needed by draw_category_label
        category_font_size = 50

        # Call the drawing function (which also handles font loading)
        draw_category_label(
            draw=text_draw,
            text=display_category_text, # Use the prepared variable
            font_path=category_font_path,
            font_size=category_font_size, # Pass the desired font size
            position=(fixed_category_x, fixed_category_y), # Pass the fixed position
            text_color=category_text_color,
            bg_color=category_bg_color,
            padding=category_padding
        )
    except Exception as cat_err:
        logging.error(f"Error drawing category label: {cat_err}")

    # --- Prepare Logo Overlay ---
    if brand_logo:
        try:
            # --- Start of block to indent ---
            logo_size = (150, 70)
            brand_logo = brand_logo.convert('RGBA') if brand_logo.mode != 'RGBA' else brand_logo
            brand_logo_resized = brand_logo.resize(logo_size, Image.Resampling.LANCZOS)
            logo_overlay = Image.new('RGBA', target_size, (0, 0, 0, 0))
            logo_x = (img_width - logo_size[0]+760) // 2
            logo_y = 30 # Position near top
            logo_overlay.paste(brand_logo_resized, (logo_x, logo_y), brand_logo_resized)
            logging.info("Prepared logo overlay")
            # --- End of block to indent ---
        except Exception as e:
            logging.error(f"Error preparing logo overlay: {e}")
            logo_overlay = None

    # --- Compositing Sequence ---
    final_image = base_image # Start with base
    if frame_image: final_image = Image.alpha_composite(final_image, frame_image) # Add frame
    final_image = Image.alpha_composite(final_image, text_overlay) # Add text (date + main)
    if logo_overlay: final_image = Image.alpha_composite(final_image, logo_overlay) # Add logo

    # Convert back to RGB for final output
    return final_image.convert('RGB')

# Add this function to automatically generate content
def auto_generate_content(article_text, bullet_word_count, description_word_count, hashtag_count):
    """Automatically generate content when article text is available"""
    # Only generate if we haven't already or if this is a new article
    if ('article_hash' not in st.session_state or 
        hash(article_text) != st.session_state.article_hash or
        not st.session_state.get('generated', False)):
        
        # Store hash of current article to detect changes
        st.session_state.article_hash = hash(article_text)
        
        with st.spinner("Generating content..."):
            progress_bar = st.progress(0)
            
            # Generate bullet point
            progress_bar.progress(25)
            st.write("Generating bullet point summary...")
            bullet_point = generate_summary_bullet(article_text, bullet_word_count)
            
            # Generate description
            progress_bar.progress(50)
            st.write("Creating article description...")
            description = generate_article_description(article_text, description_word_count)
            
            # Generate hashtags
            progress_bar.progress(75)
            st.write("Finding relevant hashtags...")
            hashtags = generate_hashtags(article_text, hashtag_count)
            
            # Generate category
            category = generate_category(bullet_point, description)
            st.session_state.category = category
            
            # Store in session state
            st.session_state.bullet_point = bullet_point
            st.session_state.description = description
            st.session_state.hashtags = hashtags
            st.session_state.generated = True
            progress_bar.progress(100)
            time.sleep(0.5)
            progress_bar.empty()
            
            return True
    return False

def generate_image_for_display(bullet_point, description, use_test_image=False):
    """Generate image and return it directly for display"""
    try:
        if use_test_image:
            logging.info("Using test image generation")
            img = create_simple_image(bullet_point)
        else:
            # Now using OpenAI for image generation directly
            logging.info("Using OpenAI GPT-Image-1 for image generation")
            img = generate_image(bullet_point, description)
        
        # Ensure the image is in RGB mode for compatibility
        if img and img.mode != 'RGB':
            logging.info(f"Converting image from {img.mode} to RGB for compatibility")
            img = img.convert('RGB')
            
        return img
    except Exception as e:
        logging.error(f"Error in generate_image_for_display: {e}", exc_info=True)
        st.error(f"Failed to generate display image: {str(e)}")
        return create_enhanced_placeholder(bullet_point)

def main():
    st.title(f"Article2Image - {get_text('title')}")
    
    # Attempt to load persistent logo at startup
    persistent_logo_path = "persistent_logo.png"
    if 'persistent_logo' not in st.session_state and os.path.exists(persistent_logo_path):
        try:
            st.session_state.persistent_logo = Image.open(persistent_logo_path).convert("RGBA")
            logging.info("Loaded persistent logo from file.")
        except Exception as e:
            logging.error(f"Error loading persistent logo from {persistent_logo_path}: {e}")
            
    # Initialize session state (ensure category is initialized)
    if 'category' not in st.session_state:
        st.session_state.category = "Societe" # Default category key
    
    # Simplified sidebar with only essential settings
    st.sidebar.header(get_text('settings'))
    
    # Add a new post button in sidebar
    if st.sidebar.button("🔄 Nouvelle Publication", use_container_width=True):
        # Reset content, keep persistent logo file and state
        if 'bullet_point' in st.session_state:
            del st.session_state.bullet_point
        # ... (keep other deletions for content/image state) ...
        if 'description' in st.session_state:
            del st.session_state.description
        if 'hashtags' in st.session_state:
            del st.session_state.hashtags
        if 'base_image' in st.session_state:
            del st.session_state.base_image
        if 'generated' in st.session_state:
            del st.session_state.generated
        if 'image_generated' in st.session_state:
            del st.session_state.image_generated
        if 'article_hash' in st.session_state:
            del st.session_state.article_hash
        # Delete the current session logo, but persistent state/file remain
        if 'brand_logo' in st.session_state:
            del st.session_state.brand_logo  
        # Return to step 1
        go_to_step(1)
        st.rerun()
    
    # Initialize language state correctly (only if not already set)
    if 'language' not in st.session_state:
        st.session_state.language = 'fr' # Default content language to French

    st.sidebar.markdown(f"### 🌐 Langue du Contenu")
    language_options_display = {
        'en': 'English 🇬🇧', 'fr': 'Français 🇫🇷',
        # 'de': 'Deutsch 🇩🇪', 'it': 'Italiano 🇮🇹', 'pt': 'Português 🇵🇹','es': 'Español 🇪🇸',
    }
    # Ensure language_name exists for display formatting
    for code, name in language_options_display.items():
        if code not in TRANSLATIONS: TRANSLATIONS[code] = {}
        if 'language_name' not in TRANSLATIONS[code]: TRANSLATIONS[code]['language_name'] = name.split(' ')[0]
        if 'categories' not in TRANSLATIONS[code]: TRANSLATIONS[code]['categories'] = {} # Ensure categories dict exists

    # Calculate index based on the *current* session state language
    try:
        current_lang_index = list(language_options_display.keys()).index(st.session_state.language)
    except ValueError:
        # Fallback if the state somehow holds an invalid value
        current_lang_index = list(language_options_display.keys()).index('fr')

    selected_language_code = st.sidebar.selectbox(
        "Langue du contenu généré:",
        options=list(language_options_display.keys()),
        format_func=lambda code: language_options_display[code], # Show full name
        index=current_lang_index, # Use the calculated index
        key='content_language_selector', # Added key back for potentially better state handling
        help="Choisissez la langue pour le contenu généré."
    )

    # Update language and rerun ONLY if changed
    if selected_language_code != st.session_state.language:
        st.session_state.language = selected_language_code
        # Reset generated flag to trigger regeneration
        if 'generated' in st.session_state:
            st.session_state.generated = False 
        st.rerun()
    
    # Improved input method selection
    st.sidebar.markdown(f"### 1️⃣ {get_text('input_method')}")
    input_method = st.sidebar.radio(get_text('select_input'), [get_text('url'), get_text('text')])
    
    # Move the control parameters to sidebar
    st.sidebar.markdown(f"### 📊 {get_text('content_settings')}")
    
    bullet_word_count = st.sidebar.slider(get_text('bullet_words'), 5, 15, 10, help="Nombre de mots dans le point principal")
    st.session_state.bullet_word_count = bullet_word_count
    
    description_word_count = st.sidebar.slider(get_text('description_words'), 20, 70, 50, help="Nombre de mots dans la description")
    st.session_state.description_word_count = description_word_count
    
    hashtag_count = st.sidebar.slider(get_text('hashtag_count'), 3, 8, 5, help="Nombre de hashtags à générer")
    st.session_state.hashtag_count = hashtag_count
    
    # Use session state for article text persistence
    if 'article_text' not in st.session_state:
        st.session_state['article_text'] = ""
    article_text = st.session_state['article_text']

    # ======================= STEP NAVIGATION ======================= 
    steps = [
        {"number": 1, "name": "Entrée d'Article", "icon": "📄"},
        {"number": 2, "name": "Contenu Généré", "icon": "✏️"},
        {"number": 3, "name": "Génération d'Image", "icon": "🖼️"},
        {"number": 4, "name": "Ajout de Logo", "icon": "🏷️"},
        {"number": 5, "name": "Publication Finale", "icon": "📱"}
    ]
    
    # Display step indicator
    st.markdown("<div style='margin-bottom: 30px;'>", unsafe_allow_html=True)
    cols = st.columns(len(steps))
    for i, col in enumerate(cols):
        step = steps[i]
        step_style = ""
        if step["number"] == st.session_state.current_step:
            # Current step
            step_style = "background-color: #1E88E5; color: white; border-radius: 10px; padding: 10px; text-align: center; font-weight: bold;"
        elif step["number"] < st.session_state.current_step:
            # Completed step
            step_style = "background-color: #BBDEFB; color: #1565C0; border-radius: 10px; padding: 10px; text-align: center; font-weight: bold;"
        else:
            # Future step
            step_style = "background-color: #F5F5F5; color: #9E9E9E; border-radius: 10px; padding: 10px; text-align: center;"
        
        col.markdown(f"<div style='{step_style}'>{step['icon']} {step['name']}</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    
    # ========================= STEP 1: ARTICLE INPUT =========================
    if st.session_state.current_step == 1:
        st.markdown('<div class="highlight">', unsafe_allow_html=True)
        st.markdown(f"## Étape 1: Entrée d'Article")
        
        # URL input mode
        if input_method == get_text('url'):
            # Form for URL submission
            with st.form(key="url_input_form"):
                url = st.text_input("Entrez l'URL de l'article:", help="Collez un lien vers n'importe quel article d'actualité ou blog", placeholder="https://example.com/article")
                submit_col1, submit_col2 = st.columns([1, 3])
                with submit_col1:
                    submit_btn = st.form_submit_button("Soumettre", use_container_width=True)
                
            # Process URL if submitted and URL exists
            if submit_btn and url:
                with st.spinner("Extraction de l'article..."):
                    try:
                        article_data = extract_article_from_url(url)
                        if article_data:
                            st.markdown('<div class="success-box">Article extrait avec succès!</div>', unsafe_allow_html=True)
                            st.session_state['article_text'] = article_data["text"]
                            article_text = st.session_state['article_text']
                            # Auto-generate content when article is extracted
                            auto_generate_content(
                                st.session_state['article_text'], 
                                bullet_word_count, 
                                description_word_count,
                                hashtag_count
                            )
                            # Go to next step automatically
                            if st.session_state.get('generated', False):
                                next_step()
                        else:
                            st.error(f"Impossible d'extraire le contenu de {url}. Veuillez essayer une autre URL ou entrer le texte directement.")
                    except Exception as e:
                        st.error(f"Erreur lors de l'extraction de l'article: {str(e)}")
                        st.info("Veuillez essayer une autre URL ou utiliser l'option de saisie de texte.")
        
        # Text input mode
        else:
            # Form for text submission
            with st.form(key="text_input_form"):
                text_input_val = st.text_area("Entrez le texte de l'article:", 
                                             value=st.session_state['article_text'], 
                                             height=200, 
                                             help="Copiez et collez le texte de votre article ici", 
                                             placeholder="Collez le texte de votre article ici...")
                submit_col1, submit_col2 = st.columns([1, 3])
                with submit_col1:
                    submit_btn = st.form_submit_button("Soumettre", use_container_width=True)
            # Process text if submitted and text exists
            if submit_btn and text_input_val:
                st.session_state['article_text'] = text_input_val
                article_text = st.session_state['article_text']
                auto_generate_content(
                    st.session_state['article_text'], 
                    bullet_word_count, 
                    description_word_count,
                    hashtag_count
                )
                # Go to next step automatically
                if st.session_state.get('generated', False):
                    next_step()
        
        # Add regenerate button when we have article text and content has been generated
        if st.session_state['article_text'] and st.session_state.get('generated', False):
            st.success("Contenu généré avec succès! Cliquez sur 'Suivant' pour continuer ou 'Régénérer' pour réessayer.")
            regen_col1, next_col = st.columns([1, 1])
            with regen_col1:
                if st.button("Régénérer", key="regenerate_btn", use_container_width=True):
                    # Clear previous generation
                    st.session_state.generated = False
                    # Force regeneration with new settings
                    auto_generate_content(
                        st.session_state['article_text'], 
                        bullet_word_count, 
                        description_word_count,
                        hashtag_count
                    )
            
            with next_col:
                if st.button("Suivant →", key="step1_next", use_container_width=True):
                    next_step()
        
        st.markdown('</div>', unsafe_allow_html=True)
            
    # ========================= STEP 2: CONTENT GENERATION =========================
    elif st.session_state.current_step == 2:
        # Check if we have generated content
        if not st.session_state.get('generated', False):
            st.warning("Veuillez d'abord générer du contenu à l'étape 1.")
            if st.button("← Retour à l'étape 1", key="go_back_to_step1", use_container_width=False):
                prev_step()
        else:
            st.markdown('<div class="highlight">', unsafe_allow_html=True)
            st.markdown("## Étape 2: Contenu Généré")
            st.info("Révisez et modifiez le contenu généré ci-dessous.")
            
            col1, col2 = st.columns([3, 2])
            
            with col1:
                st.subheader("Point Principal")
                st.info("Ceci apparaîtra sur votre image")
                st.session_state.bullet_point = st.text_area(
                    "Éditer le point principal:", 
                    st.session_state.bullet_point, 
                    height=100,
                    key="edit_bullet_point"
                )
                
            with col2:
                st.subheader("Description de l'Article")
                st.info("Ceci apparaîtra dans la légende de votre publication (pas sur l'image)")
                st.session_state.description = st.text_area(
                    "Éditer la description:", 
                    st.session_state.description, 
                    height=150,
                    key="edit_description"
                )
            
            st.subheader("Hashtags")
            st.info("Ceux-ci apparaîtront dans la légende de votre publication (pas sur l'image)")
            st.session_state.hashtags = st.text_area(
                "Éditer les hashtags:", 
                st.session_state.hashtags, 
                height=100,
                key="edit_hashtags"
            )
            
            st.markdown("--- ") # Separator before buttons
            # Navigation and Action buttons
            back_col, regen_col, next_col = st.columns([1, 1, 1])
            with back_col:
                if st.button("← Retour", key="step2_back", use_container_width=True):
                    prev_step()

            with regen_col:
                # Add Regenerate Content button
                if st.button("🔄 Régénérer Contenu", key="step2_regenerate", use_container_width=True):
                     with st.spinner("Régénération du contenu..."):
                         # Reset generated flag and call auto-generate
                         st.session_state.generated = False 
                         regenerated = auto_generate_content(
                             st.session_state['article_text'], 
                             st.session_state.bullet_word_count, 
                             st.session_state.description_word_count,
                             st.session_state.hashtag_count
                         )
                         if regenerated:
                            st.toast("Contenu régénéré !", icon="✅")
                         else:
                            st.toast("Échec de la régénération.", icon="❌")
                         st.rerun() # Rerun to reflect changes immediately
            
            with next_col:
                if st.button("Suivant →", key="step2_next", use_container_width=True):
                    next_step()
                    
            st.markdown('</div>', unsafe_allow_html=True)
    
    # ========================= STEP 3: IMAGE GENERATION =========================
    elif st.session_state.current_step == 3:
        if not st.session_state.get('generated', False):
            st.warning("Veuillez d'abord générer du contenu à l'étape 1.")
            if st.button("← Retour à l'étape 1", key="go_back_to_step1_from_3"):
                go_to_step(1)
        else:
            st.markdown('<div class="highlight">', unsafe_allow_html=True)
            st.markdown("## Étape 3: Génération d'Image")
            
            # Check for existing image or generation in progress
            if st.session_state.get('generating_image', False):
                # Currently generating image - show spinner and progress
                with st.spinner("Création de l'image IA..."):
                    progress = st.progress(0)
                    status_msg = st.info("Génération de l'image (cela peut prendre jusqu'à 30 secondes)...")
                    progress.progress(25) # Indicate start
                    
                    try:
                        logging.info("Starting image generation.")
                        image = generate_image_for_display(
                            st.session_state.bullet_point,
                            st.session_state.description,
                            use_test_image=False
                        )
                        
                        # Update progress upon completion
                        progress.progress(100)
                        status_msg.empty()
                        progress.empty()
                        
                        if image is None:
                            logging.error("Image generation function returned None.")
                            st.session_state['image_error'] = "Échec de la génération d'image. La fonction de génération n'a renvoyé aucun résultat."
                        else:
                            st.session_state.base_image = image
                            st.session_state.image_generated = True
                            logging.info("Image generated and stored in session state.")
                            
                    except Exception as e:
                        error_msg = str(e)
                        logging.error(f"Error during image generation: {error_msg}", exc_info=True)
                        st.session_state['image_error'] = f"Une erreur s'est produite: {error_msg}"
                    
                    # Set generating flag to false and rerun to display result/error
                    st.session_state['generating_image'] = False
                    st.rerun()
                    
            elif st.session_state.get('image_generated', False) and 'base_image' in st.session_state:
                # Image already generated - show it
                st.success("✅ Image générée avec succès")
                try:
                    img_buf = io.BytesIO()
                    st.session_state.base_image.save(img_buf, format='PNG')
                    img_buf.seek(0)
                    # Calculate display width that maintains aspect ratio
                    display_width = 450  # Increased from 300 (300 * 1.5)
                    display_height = int(display_width * (1345/1079))  # Maintain aspect ratio
                    st.image(img_buf, caption="Votre Image pour Instagram", width=display_width)
                    
                    st.markdown("--- ") # Separator before buttons
                    # Navigation and Action buttons
                    back_col, regen_col, next_col = st.columns([1, 1, 1])
                    with back_col:
                        if st.button("← Retour", key="step3_back", use_container_width=True):
                            prev_step()
                            
                    with regen_col:
                        # Add Regenerate Image button
                        if st.button("🔄 Régénérer Image", key="step3_regenerate", use_container_width=True):
                             # Set flags to trigger regeneration on rerun
                             st.session_state['generating_image'] = True
                             st.session_state['image_generated'] = False
                             st.session_state['image_error'] = None
                             st.rerun()

                    with next_col:
                        if st.button("Suivant →", key="step3_next", use_container_width=True):
                            next_step()
                            
                except Exception as img_display_error:
                    logging.error(f"Error displaying image: {str(img_display_error)}")
                    st.error(f"Image générée mais impossible à afficher: {str(img_display_error)}")
                    retry_col1, retry_col2 = st.columns([1, 1])
                    with retry_col1:
                        if st.button("Réessayer", use_container_width=True):
                            st.session_state['generating_image'] = True
                            st.session_state['image_error'] = None
                            st.rerun()
                    
                    with retry_col2:
                        if st.button("← Retour", key="step3_error_back", use_container_width=True):
                            prev_step()
                    
            elif st.session_state.get('image_error'):
                # Error occurred - show error and retry button
                st.error(f"❌ {st.session_state['image_error']}")
                retry_col1, retry_col2 = st.columns([1, 1])
                with retry_col1:
                    if st.button("Réessayer", use_container_width=True):
                        st.session_state['generating_image'] = True
                        st.session_state['image_error'] = None
                        st.rerun()
                
                with retry_col2:
                    if st.button("← Retour", key="step3_error_back2", use_container_width=True):
                        prev_step()
                    
            else:
                # Initial state - show the two options
                st.write("Choisissez comment créer l'image pour votre publication Instagram:")
                
                choice = st.radio("Options d'image:", ["Générer une Image IA", "Télécharger Votre Propre Image"], horizontal=True)
                
                if choice == "Générer une Image IA":
                    # Check for FAL_KEY from config.py and library availability
                    if not FAL_KEY or not FAL_CLIENT_AVAILABLE:
                        errors = []
                        if not FAL_KEY:
                            errors.append("⚠️ Clé API Fal AI (FAL_KEY) non trouvée dans config.py. Veuillez la définir.")
                        if not FAL_CLIENT_AVAILABLE:
                            errors.append("⚠️ Bibliothèque client Fal non installée. Exécutez 'pip install fal-client' pour l'installer.")
                        
                        for error in errors:
                            st.warning(error)
                        
                        # Adjust message based on the issue
                        if not FAL_CLIENT_AVAILABLE:
                            st.error("Impossible de générer des images IA car la bibliothèque client Fal est manquante.")
                        elif not FAL_KEY:
                            st.error("Impossible de générer des images IA car la clé API Fal AI (FAL_KEY) est manquante dans config.py.")
                        
                        st.info("Téléchargez votre propre image à la place.")
                        # Disable the generate button if dependencies are missing
                        gen_col1, back_col = st.columns([1, 1])
                        with gen_col1:
                            st.button("Générer Maintenant", use_container_width=True, disabled=True)
                        with back_col:
                            if st.button("← Retour", key="step3_disabled_back", use_container_width=True):
                                prev_step()
                    else:
                        st.info("Cliquez sur le bouton ci-dessous pour créer une image.")
                        gen_col1, back_col = st.columns([1, 1])
                        with gen_col1:
                            if st.button("Générer Maintenant", use_container_width=True):
                                logging.info("Generate Image button clicked (Fal AI)")
                                # Set flags to trigger generation on rerun
                                st.session_state['generating_image'] = True
                                st.session_state['image_generated'] = False
                                st.session_state['image_error'] = None
                                st.rerun()
                        with back_col:
                            if st.button("← Retour", key="step3_gen_back", use_container_width=True):
                                prev_step()
                            
                else:  # Upload option
                    st.info("Téléchargez une image à utiliser comme arrière-plan de votre publication Instagram.")
                    uploaded_file = st.file_uploader(
                        "Choisissez un fichier image", 
                        type=["jpg", "jpeg", "png"], 
                        key="upload_image_file", 
                        help="Sélectionnez une image à utiliser comme arrière-plan de votre publication"
                    )
                    if uploaded_file is not None:
                        try:
                            image = Image.open(uploaded_file)
                            image = image.resize((IMG_WIDTH, IMG_HEIGHT))
                            st.session_state.base_image = image
                            st.session_state.image_generated = True
                            st.session_state.image_error = None
                            st.session_state.generating_image = False
                            st.rerun() # Rerun to display the uploaded image
                        except Exception as e:
                            st.error(f"❌ Erreur lors du traitement de l'image téléchargée: {str(e)}")
                    
                    back_col1, back_col2 = st.columns([1, 3])
                    with back_col1:
                        if st.button("← Retour", key="step3_upload_back", use_container_width=True):
                            prev_step()
            
            st.markdown('</div>', unsafe_allow_html=True)
            
    # ========================= STEP 4: LOGO ADDITION =========================
    elif st.session_state.current_step == 4:
        # Check if we have an image
        if not st.session_state.get('image_generated', False) or 'base_image' not in st.session_state:
            st.warning("Veuillez d'abord générer ou télécharger une image à l'étape 3.")
            if st.button("← Retour à l'étape 3", key="go_back_to_step3_from_4"):
                go_to_step(3)
        else:
            st.markdown('<div class="highlight">', unsafe_allow_html=True)
            st.markdown("## Étape 4: Ajout de Logo (Facultatif)")
            
            st.info("Votre logo apparaîtra au centre en haut de l'image")
            
            # Removed the display of the base image for reference
            # img_buf = io.BytesIO()
            # st.session_state.base_image.save(img_buf, format='PNG')
            # img_buf.seek(0)
            # st.image(img_buf, caption="Votre Image pour Instagram", width=300)
            
            persistent_logo_path = "persistent_logo.png"
            current_logo_to_display = None

            # Determine which logo to display: current session > persistent file
            if 'brand_logo' in st.session_state:
                current_logo_to_display = st.session_state.brand_logo
                # Ensure the persistent state matches if a logo exists in session
                if 'persistent_logo' not in st.session_state or st.session_state.persistent_logo != st.session_state.brand_logo:
                    st.session_state.persistent_logo = st.session_state.brand_logo.copy()
            elif 'persistent_logo' in st.session_state:
                current_logo_to_display = st.session_state.persistent_logo
            
            if current_logo_to_display:
                # Logo exists (either from session or persistent file)
                col1, col2 = st.columns([1, 1])
                with col1:
                    st.image(current_logo_to_display, caption="Logo Actuel", width=150)
                with col2:
                    remove_col1, remove_col2 = st.columns([1, 1])
                    with remove_col1:
                        if st.button("Supprimer le Logo", use_container_width=True):
                            if 'brand_logo' in st.session_state:
                                del st.session_state.brand_logo
                            if 'persistent_logo' in st.session_state:
                                del st.session_state.persistent_logo
                            # Delete the file as well
                            if os.path.exists(persistent_logo_path):
                                try:
                                    os.remove(persistent_logo_path)
                                    logging.info(f"Deleted {persistent_logo_path}")
                                except Exception as e:
                                    logging.error(f"Error deleting {persistent_logo_path}: {e}")
                            st.rerun()
                
                # Navigation buttons
                back_col, next_col = st.columns([1, 1])
                with back_col:
                    if st.button("← Retour", key="step4_back", use_container_width=True):
                        prev_step()
                with next_col:
                    if st.button("Suivant →", key="step4_next", use_container_width=True):
                        next_step()
            else:
                # No logo yet (neither in session nor persistent)
                st.write("Souhaitez-vous ajouter un logo à votre image?")
                
                add_logo_col, skip_logo_col = st.columns([1, 1])
                with add_logo_col:
                    uploaded_logo = st.file_uploader(
                        "Téléchargez votre logo", 
                        type=["png"], 
                        key="upload_logo_file", 
                        help="Téléchargez un logo PNG transparent à ajouter à votre image"
                    )
                    if uploaded_logo:
                        try:
                            brand_logo = Image.open(uploaded_logo).convert("RGBA")
                            # Save to file (overwrite existing)
                            brand_logo.save(persistent_logo_path, "PNG")
                            logging.info(f"Saved new logo to {persistent_logo_path}")
                            # Update session state for current use
                            st.session_state.brand_logo = brand_logo
                            st.session_state.persistent_logo = brand_logo.copy()
                            st.success("Logo téléchargé et sauvegardé!")
                            st.rerun()
                        except Exception as e:
                            logging.error(f"Error processing/saving uploaded logo: {e}")
                            st.error(f"Erreur lors du traitement du logo: {e}")

            st.markdown('</div>', unsafe_allow_html=True)
            
    # ========================= STEP 5: FINAL POST =========================
    elif st.session_state.current_step == 5:
        # Check if we have an image
        if not st.session_state.get('image_generated', False) or 'base_image' not in st.session_state:
            st.warning("Veuillez d'abord générer ou télécharger une image.")
            if st.button("← Retour à l'étape 3", key="go_back_to_step3_from_5"):
                go_to_step(3)
        else:
            st.markdown('<div class="highlight">', unsafe_allow_html=True)
            st.markdown("## Étape 5: Création de la Publication Finale")
            
            # --- Category Selection Dropdown ---
            allowed_categories = ["Societe", "hi-tech", "sports", "nation", "economie", "regions", "culture", "monde", "Sante", "LifeStyle"]
            # Get the current category from session state, default if not found
            default_category = st.session_state.get('category', 'Societe')
            # Ensure the default is valid, fallback if it somehow isn't
            if default_category not in allowed_categories:
                 default_category = 'Societe'
            try:
                 # Find the index of the default category for the selectbox
                 default_index = allowed_categories.index(default_category)
            except ValueError:
                 logging.warning(f"Default category '{default_category}' not in allowed list. Using index 0.")
                 default_index = 0 # Default to the first category if lookup fails

            st.write("Choisissez une catégorie pour votre publication (ou utilisez celle générée automatiquement):")
            selected_category = st.selectbox(
                 "Sélectionner la Catégorie:",
                 options=allowed_categories,
                 index=default_index,
                 help="Choisissez l'étiquette de catégorie pour votre image. La catégorie suggérée par l'IA est présélectionnée.",
                 key="category_selection"
            )
            # Update session state with the user's choice
            st.session_state.category = selected_category
            # ----------------------------------
            
            create_col1, back_col = st.columns([1, 1])
            with create_col1:
                if st.button("Créer la Publication", key="create_final_post_btn", use_container_width=True):
                    with st.spinner("Création de votre publication Instagram..."):
                        progress_bar = st.progress(0)
                        time.sleep(0.3)  # Small delay for visual feedback
                        
                        # Get stored values
                        bullet_point = st.session_state.bullet_point
                        description = st.session_state.description
                        hashtags = st.session_state.hashtags
                        base_image = st.session_state.base_image
                        
                        # Determine which logo to use for the final post
                        brand_logo_to_use = None
                        if 'brand_logo' in st.session_state:
                            brand_logo_to_use = st.session_state.brand_logo
                        elif 'persistent_logo' in st.session_state:
                            brand_logo_to_use = st.session_state.persistent_logo
                        
                        # --- Log dimensions before adding text/frame ---
                        if base_image:
                            logging.info(f"Dimensions of base_image BEFORE add_text_to_image: {base_image.size}")
                        else:
                            logging.error("base_image not found in session state before add_text_to_image")
                            st.error("Erreur: L'image de base est manquante.")
                            st.stop() # Stop execution if base image is missing
                        # --------------------------------------------------
                        
                        progress_bar.progress(50)
                        time.sleep(0.3)  # Small delay for visual feedback
                        
                        # Add text overlay (only bullet point text on the image)
                        final_image = add_text_to_image(
                            base_image, 
                            bullet_point,
                            st.session_state.category, # <--- Use the final category from session state
                            brand_logo_to_use
                        )
                        
                        # --- Log dimensions after adding text/frame ---
                        if final_image:
                            logging.info(f"Dimensions of final_image AFTER add_text_to_image: {final_image.size}")
                        else:
                             logging.error("final_image is None after add_text_to_image call")
                             st.error("Erreur: Échec de la création de l'image finale.")
                             st.stop()
                        # -------------------------------------------------
                        
                        progress_bar.progress(100)
                        time.sleep(0.3)  # Small delay for visual feedback
                        progress_bar.empty()
                        
                        # Display the final image
                        st.success("✅ Publication Instagram créée avec succès!")
                        # Calculate display width that maintains aspect ratio
                        display_width = 450  # Increased from 300 (300 * 1.5)
                        display_height = int(display_width * (1345/1079))  # Maintain aspect ratio
                        st.image(final_image, caption="Prêt pour Instagram", width=display_width)
                        
                        # Create columns for download and copy options
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            # Save image option with FORCED dimensions
                            buf = io.BytesIO()
                            
                            # FORCE the image to be exactly 1079x1345 before download
                            download_image = final_image.resize((1079, 1345), Image.Resampling.LANCZOS)
                            
                            # Verify dimensions before save
                            logging.info(f"DOWNLOAD IMAGE dimensions (after forced resize): {download_image.size}")
                            
                            # Save the properly sized image
                            download_image.save(buf, format="PNG")
                            byte_im = buf.getvalue()
                            
                            # Display the actual dimensions that will be downloaded
                            st.caption(f"L'image sera téléchargée avec les dimensions: {download_image.size[0]}x{download_image.size[1]} pixels")
                            
                            st.download_button(
                                label="Télécharger l'Image",
                                data=byte_im,
                                file_name="instagram_post.png",
                                mime="image/png"
                            )
                        
                        with col2:
                            # Generate unique IDs for clipboard elements based on language
                            caption_id = f"instagram-caption-text-{st.session_state.language}"
                            button_id = f"copy-button-{st.session_state.language}"

                            # Copy to clipboard button (uses JavaScript)
                            st.markdown(f"""
                            <button id="{button_id}" onclick="
                                const textToCopy = document.getElementById('{caption_id}').innerText;
                                navigator.clipboard.writeText(textToCopy).then(() => {{
                                    // Change button text briefly to show success
                                    const button = document.getElementById('{button_id}');
                                    const originalText = button.innerText;
                                    button.innerText = 'Copié!';
                                    setTimeout(() => {{ button.innerText = originalText; }}, 2000);
                                }}).catch(err => {{
                                    console.error('Failed to copy: ', err);
                                    alert('Échec de la copie du texte.');
                                }});
                            " style="
                                background-color: #1E88E5; 
                                color: white; 
                                border: none; 
                                border-radius: 5px; 
                                padding: 0.5rem 1rem; 
                                font-weight: bold;
                                cursor: pointer;
                                width: 100%;
                            ">📋 Copier la Légende</button>
                            """, unsafe_allow_html=True)
                        
                        # Display description and hashtags below the image (copyable)
                        st.subheader("Légende Instagram")
                        with st.expander("Cliquez pour afficher/copier la légende de la publication", expanded=True):
                            # Create a div with ID for the JavaScript to target
                            st.markdown(f"""
                            <div id="{caption_id}" style="white-space: pre-wrap;">
                            {description}
                            
                            {hashtags}
                            </div>
                            """, unsafe_allow_html=True)
                            
                            st.text_area("Copier la description:", description, height=100, key="copy_description")
                            st.text_area("Copier les hashtags:", hashtags, height=80, key="copy_hashtags")
                        
                        # User engagement - asking for feedback
                        st.success("Votre publication Instagram est prête! Téléchargez l'image et copiez la légende pour la publication.")
                        
                        # Removed the three buttons at the bottom for simplicity
            
            with back_col:
                if st.button("← Retour", key="step5_back", use_container_width=True):
                    prev_step()
                    
            st.markdown('</div>', unsafe_allow_html=True)
            
    # Footer 
    st.markdown("---")
    st.caption("Article2Image - Générateur de Publications Instagram")

if __name__ == "__main__":
    # Basic session state initialization
    if 'language' not in st.session_state:
        st.session_state.language = 'en' # Default language
    if 'user_preferences' not in st.session_state:
        st.session_state.user_preferences = {
            'image_style': 'photorealistic'
        }
    if 'generated' not in st.session_state:
        st.session_state.generated = False
    if 'image_generated' not in st.session_state:
        st.session_state.image_generated = False
    if 'current_step' not in st.session_state:
        st.session_state.current_step = 1
    # Add other necessary initializations if needed
    logging.info("Starting Streamlit App")
    main()