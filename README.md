# Article2Image

A Streamlit application that converts articles (from URL or text) into Instagram post images using Google's Gemini 2.0 Flash AI model.

## Features

- Extract article content from URLs or direct text input
- Generate concise bullet point summary with customizable word count
- Create separate article description
- Generate relevant hashtags for social media with customizable count
- Preview generated image before adding text
- Apply text overlay with visual highlights (white text with light green accents)
- Add brand logo/watermark
- Download final Instagram posts (768x957 pixels)

## Setup

1. Clone the repository:
```
git clone https://github.com/yourusername/Article2Image.git
cd Article2Image
```

2. Install the required dependencies:
```
pip install -r requirements.txt
pip install lxml_html_clean  # Required for newspaper3k
```

3. Create a `.env` file in the project root and add your API keys:
```
GOOGLE_API_KEY=your_google_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
```

To get a Google API key for Gemini:
- Visit [Google AI Studio](https://makersuite.google.com/)
- Sign up or log in
- Create an API key
- Enable the Gemini 2.0 Flash model

To get an OpenAI API key for DALL-E:
- Visit [OpenAI Platform](https://platform.openai.com/)
- Sign up or log in
- Go to API keys section
- Create a new secret key
- Note: DALL-E image generation requires a paid OpenAI account with credits

## Usage

1. Run the Streamlit app:
```
python -m streamlit run app.py
```

2. The application will open in your browser

3. Select input method (URL or direct text)

4. Enter the article URL or paste the article text

5. Use the sidebar to adjust content settings (word counts, number of hashtags)

6. Follow the tabbed workflow:
   - Generate Content: Create and edit bullet point, description and hashtags
   - Preview Image: Generate and preview the image without text
   - Final Output: Create the final post with text overlay and download

7. Download the generated image

## Requirements

- Python 3.7+
- Streamlit
- Google Generative AI package
- Pillow (PIL)
- Newspaper3k
- BeautifulSoup4
- Python-dotenv
- lxml_html_clean

## License

MIT 