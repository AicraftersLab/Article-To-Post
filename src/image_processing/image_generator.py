"""
Image generation functionality for Article2Image.
"""
import logging
import streamlit as st
from src.api.openai_integration import generate_image
from src.image_processing.placeholder import create_enhanced_placeholder, create_simple_image
from src.utils.constants import IMG_WIDTH, IMG_HEIGHT


def generate_image_for_display(client, bullet_point, description, use_test_image=False, article_text=None):
    """
    Generate image and return it directly for display
    
    Args:
        client: The configured OpenAI client, or None to use placeholder
        bullet_point: The bullet point to base the image on
        description: Additional context for the image
        use_test_image: Whether to use a simple test image instead
        article_text: The full article text for context (optional)
        
    Returns:
        PIL Image object
    """
    try:
        if use_test_image:
            logging.info("Using test image generation")
            img = create_simple_image(bullet_point)
        else:
            # Use OpenAI for image generation directly
            logging.info("Using OpenAI GPT-Image-1 for image generation with full article context")
            logging.info("IMPORTANT: Ensuring no text, captions, headlines or words in the generated image")
            img = generate_image(client, bullet_point, description, IMG_WIDTH, IMG_HEIGHT, article_text)
        
        # Ensure the image is in RGB mode for compatibility
        if img and img.mode != 'RGB':
            logging.info(f"Converting image from {img.mode} to RGB for compatibility")
            img = img.convert('RGB')
            
        return img
    except Exception as e:
        logging.error(f"Error in generate_image_for_display: {e}", exc_info=True)
        st.error(f"Failed to generate display image: {str(e)}")
        return create_enhanced_placeholder(bullet_point, (IMG_WIDTH, IMG_HEIGHT)) 