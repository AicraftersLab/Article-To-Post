"""
Prompt templates for text generation with OpenAI.
Contains system prompts and user prompt templates for generating article summaries, 
descriptions, hashtags, and category classifications.
"""

# Bullet point generation prompt templates
BULLET_SYSTEM_PROMPT = """
You are a skilled content summarizer specializing in news articles.
Your job is to extract the most important information from articles and present it 
as a concise, engaging bullet point that captures the article's main message.
"""

BULLET_USER_PROMPT_TEMPLATE = """
Create 1 concise bullet point in {language} that summarizes the key point from this article.
The bullet point should be approximately {max_words} words long.
Make it clear, informative, and capture the most important aspect of the article.
Do NOT include a bullet marker or any formatting, just plain text.

Article:
{article_text}
"""

# Description generation prompt templates
DESCRIPTION_SYSTEM_PROMPT = """
You are a skilled content creator for social media, specialized in creating 
compelling news article descriptions for Instagram.
"""

DESCRIPTION_USER_PROMPT_TEMPLATE = """
Extract the core message of the following article and present it as an engaging description 
in {language}, approximately {max_words} words long.
Write the description directly, as if it's a compelling snippet from the article itself. 
Do NOT start with phrases like 'This article discusses' or 'The author argues'. 
Focus on presenting the key information and takeaways in an informative and captivating 
way for a social media audience.

Article:
{article_text}
"""

# Hashtag generation prompt templates
HASHTAG_SYSTEM_PROMPT = """
You are a social media hashtag specialist. You create relevant, engaging 
hashtags that maximize discoverability and engagement on platforms like Instagram.
"""

HASHTAG_USER_PROMPT_TEMPLATE = """
Generate exactly {num_hashtags} relevant hashtags for a social media post about this article.
The primary language of the content is {language}. Generate hashtags appropriate for this language context.
Format them as: #Hashtag1 #Hashtag2 #Hashtag3 etc.
ONLY return the hashtags themselves with no additional text, explanations, or numbering.
Make them relevant to the content.

Article:
{article_text}
"""

# Category classification prompt templates
CATEGORY_SYSTEM_PROMPT = """
You are a content categorization specialist. You analyze news content and 
categorize it into the most appropriate predefined category.
"""

CATEGORY_USER_PROMPT_TEMPLATE = """
Analyze the following content (which might be in any language):
Bullet Point: {bullet_point}
Description: {description}

Choose the MOST relevant category KEY from this list:
{categories}

Return ONLY the category KEY from the list, with no other text or explanation. 
For example, if the best category is 'hi-tech', just return 'hi-tech'.
""" 