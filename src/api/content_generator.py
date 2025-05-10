"""
Content generation functionality for Article2Image.
"""
import streamlit as st
import logging

from src.api.gemini import (
    generate_summary_bullet, 
    generate_article_description, 
    generate_hashtags,
    generate_category
)
from src.utils.translations import ALLOWED_CATEGORY_KEYS


def auto_generate_content(article_text, bullet_word_count, description_word_count, hashtag_count, language='en'):
    """
    Automatically generate content when article text is available
    
    Args:
        article_text: The article text to generate content from
        bullet_word_count: Number of words for the bullet point
        description_word_count: Number of words for the description
        hashtag_count: Number of hashtags to generate
        language: Target language for the content
        
    Returns:
        bool: True if content was generated successfully, False otherwise
    """
    try:
        # Store hash of current article to detect changes
        article_hash = hash(article_text)
        
        with st.spinner("Generating content..."):
            progress_bar = st.progress(0)
            
            # Generate bullet point
            progress_bar.progress(25)
            st.write("Generating bullet point summary...")
            bullet_point = generate_summary_bullet(article_text, bullet_word_count, language)
            
            # Generate description
            progress_bar.progress(50)
            st.write("Creating article description...")
            description = generate_article_description(article_text, description_word_count, language)
            
            # Generate hashtags
            progress_bar.progress(75)
            st.write("Finding relevant hashtags...")
            hashtags = generate_hashtags(article_text, hashtag_count, language)
            
            # Generate category
            category = generate_category(bullet_point, description, ALLOWED_CATEGORY_KEYS)
            
            progress_bar.progress(100)
            
            # Return the generated content
            return {
                'bullet_point': bullet_point,
                'description': description,
                'hashtags': hashtags,
                'category': category,
                'article_hash': article_hash
            }
            
    except Exception as e:
        st.error(f"Error generating content: {e}")
        logging.error(f"Error in auto_generate_content: {e}", exc_info=True)
        return None 