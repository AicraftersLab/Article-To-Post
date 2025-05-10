"""
Integration with Google's Gemini AI models.
"""
import logging
import google.generativeai as genai
import streamlit as st


def configure_gemini():
    """
    Configure the Gemini API with the API key from Streamlit secrets
    
    Returns:
        bool: True if configuration was successful, False otherwise
    """
    GOOGLE_API_KEY = st.secrets.get("GOOGLE_API_KEY")
    
    if not GOOGLE_API_KEY:
        st.error("Google API Key (GOOGLE_API_KEY) not found in Streamlit secrets. Please set it in your deployment settings or secrets.toml.")
        return False
    
    try:
        genai.configure(api_key=GOOGLE_API_KEY)
        logging.info("Google Generative AI configured successfully")
        return True
    except Exception as e:
        st.error(f"Error configuring Google API: {e}")
        return False


def generate_summary_bullet(article_text, max_words=30, language='en'):
    """
    Generate a single concise bullet point using Gemini in the specified language
    
    Args:
        article_text: The article text to summarize
        max_words: Maximum number of words for the bullet point
        language: Target language for the content
        
    Returns:
        A string containing the generated bullet point
    """
    try:
        model = genai.GenerativeModel('gemini-2.0-flash')
        # Determine target language name
        prompt = f"""
        Create 1 concise bullet point in {language} that summarizes the key point from this article.
        The bullet point should be approximately {max_words} words long.
        Make it clear, informative, and capture the most important aspect of the article.
        Do NOT include a bullet marker or any formatting, just plain text.
        
        Article:
        {article_text}
        """
        response = model.generate_content(prompt)
        logging.info(f"Generated bullet point in {language}")
        return response.text.strip()
    except Exception as e:
        st.error(f"Error generating bullet point: {e}")
        return ""


def generate_article_description(article_text, max_words=70, language='en'):
    """
    Generate a brief description using Gemini in the specified language
    
    Args:
        article_text: The article text to describe
        max_words: Maximum number of words for the description
        language: Target language for the content
        
    Returns:
        A string containing the generated description
    """
    try:
        model = genai.GenerativeModel('gemini-2.0-flash')
        prompt = f"""
        Extract the core message of the following article and present it as an engaging description in {language}, approximately {max_words} words long.
        Write the description directly, as if it's a compelling snippet from the article itself. 
        Do NOT start with phrases like 'This article discusses' or 'The author argues'. 
        Focus on presenting the key information and takeaways in an informative and captivating way for a social media audience.
        
        Article:
        {article_text}
        """
        response = model.generate_content(prompt)
        logging.info(f"Generated description in {language} (direct style)")
        return response.text.strip()
    except Exception as e:
        st.error(f"Error generating description: {e}")
        return ""


def generate_hashtags(article_text, num_hashtags=5, language='en'):
    """
    Generate relevant hashtags using Gemini, considering the selected language
    
    Args:
        article_text: The article text to generate hashtags for
        num_hashtags: Number of hashtags to generate
        language: Target language for the content
        
    Returns:
        A string containing the generated hashtags
    """
    try:
        model = genai.GenerativeModel('gemini-2.0-flash')
        prompt = f"""
        Generate exactly {num_hashtags} relevant hashtags for a social media post about this article.
        The primary language of the content is {language}. Generate hashtags appropriate for this language context.
        Format them as: #Hashtag1 #Hashtag2 #Hashtag3 etc.
        ONLY return the hashtags themselves with no additional text, explanations, or numbering.
        Make them relevant to the content.
        
        Article:
        {article_text}
        """
        response = model.generate_content(prompt)
        hashtags = response.text.strip()
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
        return ""


def generate_category(bullet_point, description, allowed_categories):
    """
    Generate a category KEY based on the bullet point and description using Gemini.
    
    Args:
        bullet_point: The bullet point summary text
        description: The article description
        allowed_categories: List of allowed category keys
        
    Returns:
        A string containing the generated category key
    """
    try:
        model = genai.GenerativeModel('gemini-2.0-flash')
        # The prompt still asks for a KEY from the predefined list
        prompt = f"""
        Analyze the following content (which might be in any language):
        Bullet Point: {bullet_point}
        Description: {description}

        Choose the MOST relevant category KEY from this list:
        {', '.join(allowed_categories)}

        Return ONLY the category KEY from the list, with no other text or explanation. For example, if the best category is 'hi-tech', just return 'hi-tech'.
        """
        response = model.generate_content(prompt)
        category_key = response.text.strip()

        # Validate the response against the keys
        if category_key in allowed_categories:
            logging.info(f"Gemini generated category key: {category_key}")
            return category_key
        else:
            logging.warning(f"Gemini returned an invalid category key '{category_key}'. Defaulting to 'Societe'.")
            return "Societe" # Default category key

    except Exception as e:
        st.error(f"Error generating category: {e}")
        logging.error(f"Error generating category: {e}", exc_info=True)
        return "Societe" # Default category key on error 