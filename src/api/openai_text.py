"""
Integration with OpenAI API for text generation functions.
"""
import logging
import streamlit as st

# Import the prompt templates
from src.api.text_prompt_templates import (
    BULLET_SYSTEM_PROMPT,
    BULLET_USER_PROMPT_TEMPLATE,
    DESCRIPTION_SYSTEM_PROMPT,
    DESCRIPTION_USER_PROMPT_TEMPLATE,
    HASHTAG_SYSTEM_PROMPT,
    HASHTAG_USER_PROMPT_TEMPLATE,
    CATEGORY_SYSTEM_PROMPT,
    CATEGORY_USER_PROMPT_TEMPLATE
)


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
        from openai import OpenAI
        client = OpenAI(api_key=st.secrets.get("OPENAI_API_KEY"))
        
        # Format the user prompt with the article text and parameters
        user_prompt = BULLET_USER_PROMPT_TEMPLATE.format(
            language=language,
            max_words=max_words,
            article_text=article_text
        )
        
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": BULLET_SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7,
            max_tokens=150
        )
        
        logging.info(f"Generated bullet point in {language}")
        return response.choices[0].message.content.strip()
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
        from openai import OpenAI
        client = OpenAI(api_key=st.secrets.get("OPENAI_API_KEY"))
        
        # Format the user prompt with the article text and parameters
        user_prompt = DESCRIPTION_USER_PROMPT_TEMPLATE.format(
            language=language,
            max_words=max_words,
            article_text=article_text
        )
        
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": DESCRIPTION_SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7,
            max_tokens=250
        )
        
        logging.info(f"Generated description in {language} (direct style)")
        return response.choices[0].message.content.strip()
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
        from openai import OpenAI
        client = OpenAI(api_key=st.secrets.get("OPENAI_API_KEY"))
        
        # Format the user prompt with the article text and parameters
        user_prompt = HASHTAG_USER_PROMPT_TEMPLATE.format(
            num_hashtags=num_hashtags,
            language=language,
            article_text=article_text
        )
        
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": HASHTAG_SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7,
            max_tokens=100
        )
        
        hashtags = response.choices[0].message.content.strip()
        logging.info(f"Generated hashtags for {language} context")
        
        if '#' in hashtags:
            import re
            hashtag_pattern = r'#[A-Za-z0-9_]+'
            found_hashtags = re.findall(hashtag_pattern, hashtags)
            if found_hashtags:
                return ' '.join(found_hashtags)
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