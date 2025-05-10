"""
Text processing utilities for Article2Image.
"""
import re
import logging
import requests
from newspaper import Article
import streamlit as st
from PIL import ImageFont


def extract_article_from_url(url):
    """
    Extract article content from a given URL
    
    Args:
        url: The URL to extract content from
        
    Returns:
        A dictionary with title, text and summary or None if extraction fails
    """
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


def wrap_text(text, font, max_width):
    """
    Wrap text to fit within a maximum width
    
    Args:
        text: The text to wrap
        font: The font to use for determining text width
        max_width: The maximum width in pixels
        
    Returns:
        A list of lines containing the wrapped text
    """
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


def get_font(preferred_fonts, size):
    """
    Try to load a font from a list of preferred fonts, 
    with graceful fallback to default font
    
    Args:
        preferred_fonts: List of font file names to try
        size: Font size to use
        
    Returns:
        The font object
    """
    font = None
    # First try to load from the fonts directory
    for font_name in preferred_fonts:
        try:
            # Try from the fonts directory first
            font_path = f"fonts/{font_name}"
            font = ImageFont.truetype(font_path, size)
            logging.info(f"Using font from fonts directory: {font_path} at size {size}")
            return font
        except IOError:
            # Try as an absolute path or system font
            try:
                font = ImageFont.truetype(font_name, size)
                logging.info(f"Using system font: {font_name} at size {size}")
                return font
            except IOError:
                logging.debug(f"Font {font_name} not found.")
                continue
    
    # If all preferred fonts fail, use default
    logging.warning(f"All preferred fonts failed. Using default PIL font.")
    return ImageFont.load_default(size=size) 