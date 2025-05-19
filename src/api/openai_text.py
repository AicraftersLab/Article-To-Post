"""
Integration with OpenAI API for text generation functions.
"""
import logging
import streamlit as st
import re

# Import the prompt templates
from src.api.text_prompt_templates import (
    BULLET_SYSTEM_PROMPT,
    BULLET_USER_PROMPT_TEMPLATE,
    DESCRIPTION_SYSTEM_PROMPT,
    DESCRIPTION_USER_PROMPT_TEMPLATE,
    HASHTAG_SYSTEM_PROMPT,
    HASHTAG_USER_PROMPT_TEMPLATE,
    CATEGORY_SYSTEM_PROMPT,
    CATEGORY_USER_PROMPT_TEMPLATE,
    COMBINED_SYSTEM_PROMPT,
    COMBINED_USER_PROMPT_TEMPLATE
)


def generate_all_content(article_text, max_words=30, num_hashtags=5, language='en'):
    """
    Generate bullet point, description, and hashtags in a single API call
    
    Args:
        article_text: The article text to process
        max_words: Maximum number of words for bullet point and description
        num_hashtags: Number of hashtags to generate
        language: Target language for the content
        
    Returns:
        tuple: (bullet_point, description, hashtags)
    """
    try:
        from openai import OpenAI
        client = OpenAI(api_key=st.secrets.get("OPENAI_API_KEY"))
        
        # Format the user prompt with the article text and parameters
        user_prompt = COMBINED_USER_PROMPT_TEMPLATE.format(
            language=language,
            max_words=max_words,
            num_hashtags=num_hashtags,
            article_text=article_text
        )
        
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": COMBINED_SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7,
            max_tokens=1000
        )
        
        content = response.choices[0].message.content.strip()
        
        # Parse the response into components
        bullet_match = re.search(r'BULLET:\s*(.*?)(?=DESCRIPTION:|$)', content, re.DOTALL)
        desc_match = re.search(r'DESCRIPTION:\s*(.*?)(?=HASHTAGS:|$)', content, re.DOTALL)
        hashtags_match = re.search(r'HASHTAGS:\s*(.*?)$', content, re.DOTALL)
        
        bullet_point = bullet_match.group(1).strip() if bullet_match else ""
        description = desc_match.group(1).strip() if desc_match else ""
        hashtags = hashtags_match.group(1).strip() if hashtags_match else ""
        
        # Clean up hashtags
        if hashtags:
            hashtag_pattern = r'#[A-Za-z0-9_]+'
            found_hashtags = re.findall(hashtag_pattern, hashtags)
            if found_hashtags:
                hashtags = ' '.join(found_hashtags)
        
        logging.info(f"Generated all content in {language}")
        return bullet_point, description, hashtags
        
    except Exception as e:
        st.error(f"Error generating content: {e}")
        logging.error(f"Error in generate_all_content: {e}", exc_info=True)
        return "", "", ""


def generate_summary_bullet(article_text, max_words=30, language='en'):
    """
    Generate a single concise bullet point using OpenAI in the specified language
    
    Args:
        article_text: The article text to summarize
        max_words: Maximum number of words for the bullet point
        language: Target language for the content
        
    Returns:
        A string containing the generated bullet point
    """
    try:
        bullet_point, _, _ = generate_all_content(article_text, max_words, 5, language)
        return bullet_point
    except Exception as e:
        st.error(f"Error generating bullet point: {e}")
        logging.error(f"Error in generate_summary_bullet: {e}", exc_info=True)
        return ""


def generate_article_description(article_text, max_words=70, language='en'):
    """
    Generate a brief description using OpenAI in the specified language
    
    Args:
        article_text: The article text to describe
        max_words: Maximum number of words for the description
        language: Target language for the content
        
    Returns:
        A string containing the generated description
    """
    try:
        _, description, _ = generate_all_content(article_text, max_words, 5, language)
        return description
    except Exception as e:
        st.error(f"Error generating description: {e}")
        logging.error(f"Error in generate_article_description: {e}", exc_info=True)
        return ""


def generate_hashtags(article_text, num_hashtags=5, language='en'):
    """
    Generate relevant hashtags using OpenAI, considering the selected language
    
    Args:
        article_text: The article text to generate hashtags for
        num_hashtags: Number of hashtags to generate
        language: Target language for the content
        
    Returns:
        A string containing the generated hashtags
    """
    try:
        _, _, hashtags = generate_all_content(article_text, 30, num_hashtags, language)
        return hashtags
    except Exception as e:
        st.error(f"Error generating hashtags: {e}")
        logging.error(f"Error in generate_hashtags: {e}", exc_info=True)
        return ""


def generate_category(bullet_point, description, allowed_categories):
    """
    Generate a category KEY based on the bullet point and description using OpenAI.
    
    Args:
        bullet_point: The bullet point summary text
        description: The article description
        allowed_categories: List of allowed category keys
        
    Returns:
        A string containing the generated category key
    """
    try:
        from openai import OpenAI
        client = OpenAI(api_key=st.secrets.get("OPENAI_API_KEY"))
        
        # Format the user prompt with the content and categories
        user_prompt = CATEGORY_USER_PROMPT_TEMPLATE.format(
            bullet_point=bullet_point,
            description=description,
            categories=', '.join(allowed_categories)
        )
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",  # Using a smaller model for simple categorization
            messages=[
                {"role": "system", "content": CATEGORY_SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.3,
            max_tokens=50
        )
        
        category_key = response.choices[0].message.content.strip()

        # Validate the response against the keys
        if category_key in allowed_categories:
            logging.info(f"OpenAI generated category key: {category_key}")
            return category_key
        else:
            logging.warning(f"OpenAI returned an invalid category key '{category_key}'. Defaulting to 'Societe'.")
            return "Societe" # Default category key

    except Exception as e:
        st.error(f"Error generating category: {e}")
        logging.error(f"Error generating category: {e}", exc_info=True)
        return "Societe" # Default category key on error 