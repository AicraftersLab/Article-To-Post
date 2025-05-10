"""
Integration with OpenAI API for image generation and potentially other services.
"""
import io
import logging
import requests
import streamlit as st
from PIL import Image


def configure_openai():
    """
    Configure the OpenAI API client with the API key from Streamlit secrets
    
    Returns:
        tuple: (openai_client, is_available_flag) or (None, False) if error
    """
    OPENAI_API_KEY = st.secrets.get("OPENAI_API_KEY")
    
    if not OPENAI_API_KEY:
        logging.warning("OpenAI API Key not found in Streamlit secrets")
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
            logging.error(f"OpenAI API key validation failed: {test_error}")
            st.error(f"OpenAI API key validation failed: {test_error}")
            return None, False
            
    except ImportError:
        logging.error("Failed to import OpenAI client. Install with 'pip install openai'")
        st.error("OpenAI library not installed. Please install with 'pip install openai'")
        return None, False


def generate_image(client, bullet_point, description, width=1079, height=1345):
    """
    Generate image using OpenAI's GPT-Image-1 model with proper dimensions
    
    Args:
        client: The configured OpenAI client
        bullet_point: The bullet point text to base the image on
        description: Additional context for image generation
        width: Target width of the final image
        height: Target height of the final image
        
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
    
    # Create prompt for OpenAI
    scene_prompt = (
        f"Ultra-realistic 4K editorial photograph press shot illustrating the following topic: {bullet_point}. "
        f"Context: {description}. "
        "Symbolic, in-animate elements that visually convey the story; dramatic cinematic lighting, high contrast, deep shadows, news-photography style, vertical 9:16 composition. "
        "Scene is completely deserted — absolutely no faces, silhouettes or body parts; no written text, no logos, no flags or religious symbols.no public figures. "
        "without written text, without logos, without flags or religious symbols, without public figures."
    )
    
    try:
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
        return img
        
    except Exception as e:
        logging.error(f"Error generating image with OpenAI: {e}", exc_info=True)
        st.error(f"Failed to generate image: {str(e)}")
        # Return a placeholder image with the exact dimensions
        from src.image_processing.placeholder import create_enhanced_placeholder
        return create_enhanced_placeholder(bullet_point, (target_width, target_height)) 