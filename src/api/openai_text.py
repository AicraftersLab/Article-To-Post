"""
Integration with OpenAI API for text generation functions.
"""
import logging
import streamlit as st


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
        
        # Determine target language for prompt
        prompt = f"""
        Create 1 concise bullet point in {language} that summarizes the key point from this article.
        The bullet point should be approximately {max_words} words long.
        Make it clear, informative, and capture the most important aspect of the article.
        Do NOT include a bullet marker or any formatting, just plain text.
        
        Article:
        {article_text}
        """
        
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a skilled content summarizer."},
                {"role": "user", "content": prompt}
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
        
        prompt = f"""
        Extract the core message of the following article and present it as an engaging description in {language}, approximately {max_words} words long.
        Write the description directly, as if it's a compelling snippet from the article itself. 
        Do NOT start with phrases like 'This article discusses' or 'The author argues'. 
        Focus on presenting the key information and takeaways in an informative and captivating way for a social media audience.
        
        Article:
        {article_text}
        """
        
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a skilled content creator for social media."},
                {"role": "user", "content": prompt}
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
        
        prompt = f"""
        Generate exactly {num_hashtags} relevant hashtags for a social media post about this article.
        The primary language of the content is {language}. Generate hashtags appropriate for this language context.
        Format them as: #Hashtag1 #Hashtag2 #Hashtag3 etc.
        ONLY return the hashtags themselves with no additional text, explanations, or numbering.
        Make them relevant to the content.
        
        Article:
        {article_text}
        """
        
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a social media hashtag specialist."},
                {"role": "user", "content": prompt}
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
        
        prompt = f"""
        Analyze the following content (which might be in any language):
        Bullet Point: {bullet_point}
        Description: {description}

        Choose the MOST relevant category KEY from this list:
        {', '.join(allowed_categories)}

        Return ONLY the category KEY from the list, with no other text or explanation. For example, if the best category is 'hi-tech', just return 'hi-tech'.
        """
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",  # Using a smaller model for simple categorization
            messages=[
                {"role": "system", "content": "You are a content categorization specialist."},
                {"role": "user", "content": prompt}
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