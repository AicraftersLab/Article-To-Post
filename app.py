"""
Article2Image - Instagram Post Generator

Main application file that uses a modular structure to separate concerns.
"""
import streamlit as st
import logging
import os
from PIL import Image
import io
import time

# Import configuration and initialization
from src.app_config import (
    setup_logging, set_page_config, get_custom_css, 
    initialize_session_state, configure_api_keys,
    go_to_step, next_step, prev_step
)

# Import UI components
from src.ui.sidebar import render_sidebar, load_persistent_logo
from src.ui.steps import display_step_navigation, get_steps

# Import API functionality
from src.api.content_generator import auto_generate_content
from src.utils.text_utils import extract_article_from_url

# Import image processing
from src.image_processing.image_generator import generate_image_for_display 
from src.image_processing.image_composer import add_text_to_image


def main():
    """Main application entry point"""
    # Setup logging
    setup_logging()
    
    # Configure page settings
    set_page_config()
    
    # Apply custom CSS
    st.markdown(get_custom_css(), unsafe_allow_html=True)
    
    # Initialize session state
    initialize_session_state()
    
    # Configure API keys
    gemini_configured, openai_client, openai_available = configure_api_keys()
    
    # Load persistent logo
    load_persistent_logo()
    
    # Display title
    st.title(f"Article2Image - Instagram Post Generator")
    
    # Display step navigation
    display_step_navigation(get_steps())
    
    # Render sidebar and get selected input method
    input_method = render_sidebar()
    
    # Handle each step
    if st.session_state.current_step == 1:
        handle_step1_article_input(input_method)
    elif st.session_state.current_step == 2:
        handle_step2_content_generation()
    elif st.session_state.current_step == 3:
        handle_step3_image_generation(openai_client)
    elif st.session_state.current_step == 4:
        handle_step4_logo_addition()
    elif st.session_state.current_step == 5:
        handle_step5_final_post()
    
    # Footer
    st.markdown("---")
    st.caption("Article2Image - Générateur de Publications Instagram")


def handle_step1_article_input(input_method):
    """Handle the article input step"""
    st.markdown('<div class="highlight">', unsafe_allow_html=True)
    st.markdown(f"## Étape 1: Entrée d'Article")
    
    # URL input mode
    if input_method == "URL":
        # Form for URL submission
        with st.form(key="url_input_form"):
            url = st.text_input("Entrez l'URL de l'article:", 
                               help="Collez un lien vers n'importe quel article d'actualité ou blog", 
                               placeholder="https://example.com/article")
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
                        st.session_state.article_text = article_data["text"]
                        
                        # Auto-generate content when article is extracted
                        content = auto_generate_content(
                            st.session_state.article_text, 
                            st.session_state.bullet_word_count, 
                            st.session_state.description_word_count,
                            st.session_state.hashtag_count,
                            st.session_state.language
                        )
                        
                        if content:
                            st.session_state.bullet_point = content['bullet_point']
                            st.session_state.description = content['description']
                            st.session_state.hashtags = content['hashtags']
                            st.session_state.category = content['category']
                            st.session_state.article_hash = content['article_hash']
                            st.session_state.generated = True
                            
                            # Go to next step automatically
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
                                 value=st.session_state.article_text, 
                                 height=200, 
                                 help="Copiez et collez le texte de votre article ici", 
                                 placeholder="Collez le texte de votre article ici...")
            submit_col1, submit_col2 = st.columns([1, 3])
            with submit_col1:
                submit_btn = st.form_submit_button("Soumettre", use_container_width=True)
        
        # Process text if submitted and text exists
        if submit_btn and text_input_val:
            st.session_state.article_text = text_input_val
            
            # Auto-generate content
            content = auto_generate_content(
                st.session_state.article_text, 
                st.session_state.bullet_word_count, 
                st.session_state.description_word_count,
                st.session_state.hashtag_count,
                st.session_state.language
            )
            
            if content:
                st.session_state.bullet_point = content['bullet_point']
                st.session_state.description = content['description']
                st.session_state.hashtags = content['hashtags']
                st.session_state.category = content['category']
                st.session_state.article_hash = content['article_hash']
                st.session_state.generated = True
                
                # Go to next step automatically
                next_step()
    
    # Add regenerate button when we have article text and content has been generated
    if st.session_state.article_text and st.session_state.get('generated', False):
        st.success("Contenu généré avec succès! Cliquez sur 'Suivant' pour continuer ou 'Régénérer' pour réessayer.")
        regen_col1, next_col = st.columns([1, 1])
        with regen_col1:
            if st.button("Régénérer", key="regenerate_btn", use_container_width=True):
                # Clear previous generation
                st.session_state.generated = False
        
                # Force regeneration with new settings
                content = auto_generate_content(
                    st.session_state.article_text, 
                    st.session_state.bullet_word_count, 
                    st.session_state.description_word_count,
                    st.session_state.hashtag_count,
                    st.session_state.language
                )
                
                if content:
                    st.session_state.bullet_point = content['bullet_point']
                    st.session_state.description = content['description']
                    st.session_state.hashtags = content['hashtags']
                    st.session_state.category = content['category']
                    st.session_state.article_hash = content['article_hash']
                    st.session_state.generated = True
                    st.rerun()
        
        with next_col:
            if st.button("Suivant →", key="step1_next", use_container_width=True):
                next_step()
    
    st.markdown('</div>', unsafe_allow_html=True)
            

def handle_step2_content_generation():
    """Handle content generation step"""
    # Shortened to brief overview - implement fully in a real app
    st.markdown('<div class="highlight">', unsafe_allow_html=True)
    st.markdown("## Étape 2: Contenu Généré")
    
    # Check if we have generated content
    if not st.session_state.get('generated', False):
        st.warning("Veuillez d'abord générer du contenu à l'étape 1.")
        if st.button("← Retour à l'étape 1", key="go_back_to_step1", use_container_width=False):
            prev_step()
    else:
        st.info("Révisez et modifiez le contenu généré ci-dessous.")
        
        # Add regeneration button
        if st.button("🔄 Régénérer le contenu", key="regenerate_content_btn"):
            with st.spinner("Régénération du contenu..."):
                # Force regeneration with current settings
                content = auto_generate_content(
                    st.session_state.article_text, 
                    st.session_state.bullet_word_count, 
                    st.session_state.description_word_count,
                    st.session_state.hashtag_count,
                    st.session_state.language
                )
                
                if content:
                    st.session_state.bullet_point = content['bullet_point']
                    st.session_state.description = content['description']
                    st.session_state.hashtags = content['hashtags']
                    st.session_state.category = content['category']
                    st.session_state.article_hash = content['article_hash']
                    st.rerun()
        
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
        
    st.markdown("--- ")
    back_col, next_col = st.columns([1, 1])
    with back_col:
        if st.button("← Retour", key="step2_back", use_container_width=True):
            prev_step()
    
    with next_col:
        if st.button("Suivant →", key="step2_next", use_container_width=True):
            next_step()
                    
    st.markdown('</div>', unsafe_allow_html=True)
    

def handle_step3_image_generation(openai_client):
    """Handle image generation step"""
    # Shortened to brief overview - implement fully in a real app
    st.markdown('<div class="highlight">', unsafe_allow_html=True)
    st.markdown("## Étape 3: Génération d'Image")
    
    if not st.session_state.get('generated', False):
        st.warning("Veuillez d'abord générer du contenu à l'étape 1.")
        if st.button("← Retour à l'étape 1", key="go_back_to_step1_from_3"):
            go_to_step(1)
    else:
        # Display image generation options or the generated image
        if st.session_state.get('image_generated', False) and 'base_image' in st.session_state:
            st.success("✅ Image générée avec succès")
            img_buf = io.BytesIO()
            st.session_state.base_image.save(img_buf, format='PNG')
            img_buf.seek(0)
            display_width = 450
            st.image(img_buf, caption="Votre Image pour Instagram", width=display_width)
            
            st.markdown("--- ")
            back_col, next_col = st.columns([1, 1])
            with back_col:
                if st.button("← Retour", key="step3_back", use_container_width=True):
                    prev_step()

            with next_col:
                if st.button("Suivant →", key="step3_next", use_container_width=True):
                    next_step()
        else:
            # Initial state - show the two options
            st.write("Choisissez comment créer l'image pour votre publication Instagram:")
            
            choice = st.radio("Options d'image:", ["Générer une Image IA", "Télécharger Votre Propre Image"], horizontal=True)
            
            if choice == "Générer une Image IA":
                st.info("Cliquez sur le bouton ci-dessous pour créer une image.")
                gen_col, back_col = st.columns([1, 1])
                with gen_col:
                    if st.button("Générer Maintenant", use_container_width=True):
                        with st.spinner("Création de l'image IA..."):
                            progress = st.progress(0)
                            status_msg = st.info("Génération de l'image (cela peut prendre jusqu'à 30 secondes)...")
                            progress.progress(25)
                            
                            # Generate the image
                            image = generate_image_for_display(
                                openai_client,
                                st.session_state.bullet_point,
                                st.session_state.description
                            )
                            
                            progress.progress(100)
                            status_msg.empty()
                            progress.empty()
                            
                            st.session_state.base_image = image
                            st.session_state.image_generated = True
                            st.rerun()
                
                st.markdown('</div>', unsafe_allow_html=True)
            

def handle_step4_logo_addition():
    """Handle logo addition step"""
    # Shortened to brief overview - implement fully in a real app
    st.markdown('<div class="highlight">', unsafe_allow_html=True)
    st.markdown("## Étape 4: Ajout de Logo (Facultatif)")
    
    if not st.session_state.get('image_generated', False) or 'base_image' not in st.session_state:
        st.warning("Veuillez d'abord générer ou télécharger une image à l'étape 3.")
        if st.button("← Retour à l'étape 3", key="go_back_to_step3_from_4"):
            go_to_step(3)
    else:
        st.info("Votre logo apparaîtra au centre en haut de l'image")
        
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
            

def handle_step5_final_post():
    """Handle final post generation step"""
    # Shortened to brief overview - implement fully in a real app
    st.markdown('<div class="highlight">', unsafe_allow_html=True)
    st.markdown("## Étape 5: Création de la Publication Finale")
    
    if not st.session_state.get('image_generated', False) or 'base_image' not in st.session_state:
        st.warning("Veuillez d'abord générer ou télécharger une image.")
        if st.button("← Retour à l'étape 3", key="go_back_to_step3_from_5"):
            go_to_step(3)
    else:
        # Use session state category if available, default to "Societe"
        default_category = st.session_state.get('category', 'Societe')
        allowed_categories = ["société", "hi-tech", "sports", "nation", "économie", 
                             "regions", "culture", "monde", "santé", "LifeStyle"]

        st.write("Choisissez une catégorie pour votre publication (ou utilisez celle générée automatiquement):")
        selected_category = st.selectbox(
             "Sélectionner la Catégorie:",
             options=allowed_categories,
             index=allowed_categories.index(default_category) if default_category in allowed_categories else 0,
             help="Choisissez l'étiquette de catégorie pour votre image.",
             key="category_selection"
        )
    
        st.session_state.category = selected_category
        
        create_col, back_col = st.columns([1, 1])
        with create_col:
            if st.button("Créer la Publication", key="create_final_post_btn", use_container_width=True):
                with st.spinner("Création de votre publication Instagram..."):
                    progress_bar = st.progress(0)
                    time.sleep(0.3)
                    
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
                    
                    progress_bar.progress(50)
                    time.sleep(0.3)
                    
                    # Add text overlay
                    final_image = add_text_to_image(
                        base_image, 
                        bullet_point,
                        st.session_state.category,
                        brand_logo_to_use,
                        st.session_state.language
                    )
                    
                    progress_bar.progress(100)
                    time.sleep(0.3)
                    progress_bar.empty()
                    
                    # Display the final image
                    st.success("✅ Publication Instagram créée avec succès!")
                    display_width = 450
                    st.image(final_image, caption="Prêt pour Instagram", width=display_width)
                    
                    # Download button
                    img_buf = io.BytesIO()
                    final_image.save(img_buf, format="PNG")
                    byte_im = img_buf.getvalue()
                    
                    st.download_button(
                        label="Télécharger l'Image",
                        data=byte_im,
                        file_name="instagram_post.png",
                        mime="image/png"
                    )
                    
                    # Display caption
                    st.subheader("Légende Instagram")
                    with st.expander("Cliquez pour afficher la légende", expanded=True):
                        st.text_area("Description:", description, height=100)
                        st.text_area("Hashtags:", hashtags, height=80)
            
        with back_col:
            if st.button("← Retour", key="step5_back", use_container_width=True):
                prev_step()
                
        st.markdown('</div>', unsafe_allow_html=True)
            

if __name__ == "__main__":
    main()