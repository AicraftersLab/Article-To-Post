"""
Integration with OpenAI API for image generation and potentially other services.
"""
import io
import logging
import requests
import streamlit as st
from PIL import Image
import random
import os

# Import the prompt templates
from src.api.prompt_templates import (
    IMAGE_SYSTEM_PROMPT,
    IMAGE_USER_PROMPT_TEMPLATE,
    IMAGE_PROMPT_SUFFIX,
    FALLBACK_IMAGE_PROMPT
)


def configure_openai():
    """
    Configure the OpenAI API client with the API key from Streamlit secrets
    
    Returns:
        tuple: (openai_client, is_available_flag) or (None, False) if error
    """
    # First check for a temporary key in session state (highest priority)
    OPENAI_API_KEY = None
    if 'temp_openai_key' in st.session_state:
        OPENAI_API_KEY = st.session_state.temp_openai_key
        logging.info("Using temporary OpenAI API key from session state")
    
    # If not found in session state, try Streamlit secrets
    if not OPENAI_API_KEY:
        OPENAI_API_KEY = st.secrets.get("OPENAI_API_KEY")
    
    # If not found in secrets, try environment variables
    if not OPENAI_API_KEY:
        OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
        if OPENAI_API_KEY:
            logging.info("Using OpenAI API key from environment variables")
    
    if not OPENAI_API_KEY:
        logging.warning("OpenAI API Key not found in session state, secrets, or environment variables")
        st.warning("🔑 OpenAI API Key is missing. Please add it to your secrets.toml file or .env file.")
        return None, False
    
    # Check if the API key starts with "sk-" which is required for standard OpenAI keys
    if not OPENAI_API_KEY.startswith("sk-"):
        logging.error("Invalid OpenAI API key format. Must start with 'sk-'")
        st.error("❌ Invalid OpenAI API key format. OpenAI API keys must start with 'sk-'.")
        st.info("If you're using a project key (starting with 'sk-proj-'), please use a standard API key instead.")
        return None, False
        
    try:
        from openai import OpenAI
        client = OpenAI(api_key=OPENAI_API_KEY)
        
        # Test the configuration
        try:
            models = client.models.list()
            logging.info(f"OpenAI API connection successful: {len(models.data)} models available")
            return client, True
        except Exception as test_error:
            error_msg = str(test_error)
            logging.error(f"OpenAI API key validation failed: {error_msg}")
            
            # Provide more helpful error messages based on error type
            if "401" in error_msg:
                if "invalid_api_key" in error_msg:
                    st.error("❌ Invalid API key. Please check that you're using a correct, active OpenAI API key.")
                    st.info("Note: Project keys (starting with 'sk-proj-') are not compatible with this application. Please use a standard API key.")
                else:
                    st.error("❌ Authentication error. Your API key appears to be incorrect or revoked.")
            elif "insufficient_quota" in error_msg or "429" in error_msg:
                st.error("❌ OpenAI API quota exceeded. Your account has reached its usage limit.")
                st.info("Check your OpenAI billing status at https://platform.openai.com/account/billing")
            else:
                st.error(f"❌ OpenAI API connection failed: {error_msg}")
            
            return None, False
            
    except ImportError:
        logging.error("Failed to import OpenAI client. Install with 'pip install openai'")
        st.error("❌ OpenAI library not installed. Please install with 'pip install openai'")
        return None, False


def generate_image_prompt(client, bullet_point, description, article_text=None):
    """
    Generate an optimized image prompt using OpenAI based on the article content
    
    Args:
        client: The configured OpenAI client
        bullet_point: The bullet point text to base the image on
        description: Additional context for image generation
        article_text: The full article text (optional, if available)
        
    Returns:
        str: An optimized prompt for image generation
    """
    try:
        if not client:
            # Fall back to a default prompt structure if client isn't available
            return FALLBACK_IMAGE_PROMPT.format(headline=bullet_point)
        
        from openai import OpenAI
        
        # Prepare parameters for the template
        # These are selected to ensure a good variety of images based on the content
        camera_options = ["Canon EOS R5", "Nikon Z9", "Sony A1"]
        lens_options = ["35mm f/1.4", "50mm f/1.2", "85mm f/1.8", "24mm f/1.4"]
        iso_options = ["100", "200", "400", "800", "1600"]
        aperture_options = ["f/1.4", "f/1.8", "f/2.8", "f/4.0", "f/5.6", "f/8.0"]
        shutter_options = ["1/125s", "1/250s", "1/500s", "1/1000s"]
        
        # Default to description if full article text isn't available
        if article_text is None or article_text.strip() == "":
            article_text = description
            
        # Extract a potential location from the text for more detailed prompts
        # This is a simple heuristic - the LLM will do more sophisticated extraction
        location = "relevant location"
        if article_text:
            # Try to find location references in the text
            import re
            # Look for city names, countries, or place references that are likely capitalized
            location_pattern = r'\b([A-Z][a-z]+(?:\s[A-Z][a-z]+)*(?:,\s[A-Z][a-z]+)?)\b'
            location_matches = re.findall(location_pattern, article_text)
            
            # Filter common non-location capitalized words
            common_non_locations = ["The", "A", "An", "I", "We", "They", "Monday", "Tuesday", 
                                   "Wednesday", "Thursday", "Friday", "Saturday", "Sunday",
                                   "January", "February", "March", "April", "May", "June", 
                                   "July", "August", "September", "October", "November", "December"]
            
            filtered_locations = [loc for loc in location_matches if loc not in common_non_locations]
            
            if filtered_locations:
                # Use the longest match as it's likely to be more specific
                location = max(filtered_locations, key=len)
            
        # Format the lighting_weather_mood based on the content
        lighting_options = [
            "golden hour sunlight", 
            "high contrast midday light", 
            "soft diffused morning light",
            "dramatic cloudy conditions",
            "blue hour twilight",
            "neutral indoor lighting",
            "overcast daylight"
        ]
        
        # Format the user prompt template with all the parameters
        user_prompt = IMAGE_USER_PROMPT_TEMPLATE.format(
            headline=bullet_point,
            description=description,
            article_text=article_text,
            location=location,
            lighting_weather_mood=random.choice(lighting_options),
            iso=random.choice(iso_options),
            shutter_speed=random.choice(shutter_options),
            aperture=random.choice(aperture_options),
            camera_body=random.choice(camera_options),
            lens=random.choice(lens_options)
        )
        
        logging.info("Generating optimized image prompt from full article text...")
        
        # Make the LLM call to generate the prompt
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": IMAGE_SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7,
            max_tokens=5000,  # Increased token limit for more detailed prompts
            response_format={"type": "text"}  # Ensures plain text response
        )
        
        generated_prompt = response.choices[0].message.content.strip()
        logging.info(f"Generated image prompt: {generated_prompt[:100]}...")
        
        # The template already adds the suffix, so we don't need to add it again
        return generated_prompt
        
    except Exception as e:
        logging.error(f"Error generating image prompt: {e}", exc_info=True)
        # Fallback to a simpler prompt
        return FALLBACK_IMAGE_PROMPT.format(headline=bullet_point)


def generate_image(client, bullet_point, description, width=1079, height=1345, article_text=None):
    """
    Generate image using OpenAI's GPT-Image-1 model with proper dimensions
    
    Args:
        client: The configured OpenAI client
        bullet_point: The bullet point text to base the image on
        description: Additional context for image generation
        width: Target width of the final image
        height: Target height of the final image
        article_text: The full article text for context (optional)
        
    Returns:
        The generated image as a PIL Image object
    """
    target_width, target_height = width, height
    
    logging.info(f"Generating image for: {bullet_point[:50]}...")
    
    # Check if OpenAI client is available
    if not client:
        logging.warning("OpenAI client is not available. Using placeholder instead.")
        from src.image_processing.placeholder import create_enhanced_placeholder
        return create_enhanced_placeholder(bullet_point, (target_width, target_height))
    
    # Generate the optimized prompt using LLM
    scene_prompt = generate_image_prompt(client, bullet_point, description, article_text)
    
    try:
        # Call OpenAI's image generation
        logging.info("Calling OpenAI GPT-Image-1 API with optimized prompt")
        logging.info(f"Using prompt length: {len(scene_prompt)} chars")
        
        # Log a truncated version of the prompt for debugging
        if len(scene_prompt) > 200:
            logging.info(f"Prompt preview: {scene_prompt[:200]}...")
        else:
            logging.info(f"Prompt preview: {scene_prompt}")
        
        response = client.images.generate(
            model="gpt-image-1",
            prompt=scene_prompt,
            n=1,
            size="1024x1024",  # Standard size for compatibility
            quality="high",    # Use high quality setting
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
        
        # Determine the resampling filter based on PIL/Pillow version
        try:
            RESAMPLING_FILTER = Image.Resampling.LANCZOS
        except AttributeError:
            # Fallback for older Pillow versions
            RESAMPLING_FILTER = Image.LANCZOS
        
        if original_aspect > target_aspect:
            # Original image is wider - resize to target height then crop width
            new_width = int(target_height * original_aspect)
            new_height = target_height
            img = img.resize((new_width, new_height), RESAMPLING_FILTER)
            left = (new_width - target_width) // 2
            img = img.crop((left, 0, left + target_width, target_height))
        else:
            # Original image is taller - resize to target width then crop height
            new_height = int(target_width / original_aspect)
            new_width = target_width
            img = img.resize((new_width, new_height), RESAMPLING_FILTER)
            top = (new_height - target_height) // 2
            img = img.crop((0, top, target_width, top + target_height))
        
        # Convert to RGB if needed
        if img.mode != 'RGB':
            img = img.convert('RGB')
            
        logging.info(f"Final image dimensions: {img.size}")
        return img
        
    except Exception as e:
        logging.error(f"Error generating image with OpenAI: {e}", exc_info=True)
        
        # Try to extract more useful information from the error
        error_details = str(e)
        if hasattr(e, 'response') and hasattr(e.response, 'json'):
            try:
                error_json = e.response.json()
                if 'error' in error_json and 'message' in error_json['error']:
                    error_details = error_json['error']['message']
            except:
                pass
                
        st.error(f"Failed to generate image: {error_details}")
        # Return a placeholder image with the exact dimensions
        from src.image_processing.placeholder import create_enhanced_placeholder
        return create_enhanced_placeholder(bullet_point, (target_width, target_height)) 