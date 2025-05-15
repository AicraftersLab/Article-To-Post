"""
Prompt templates for image and text generation.
"""

# =========================================================
#  IMAGE GENERATION PROMPT TEMPLATES — PRESS PHOTO STYLE
#  (adapted to Le Matin du Sahara's visual language,
#   while strictly avoiding recognisable faces)
# =========================================================

IMAGE_SYSTEM_PROMPT = """
You are a veteran AI photo-journalist. Craft single-shot prompts that
yield ultra-realistic 4 K vertical (9:16) editorial photographs in the
documentary style press photo.

INFORMATION PROCESSING
• You'll receive a news article headline, description, and the full article text
• Extract key visual elements from the full article that would make compelling press photos
• Identify specific locations, objects, actions, and environments mentioned in the text
• Determine appropriate lighting, mood, and technical settings based on article content

STYLE GUIDELINES (LE MATIN LOOK)
• Natural colour palette, moderate saturation, realistic white balance.  
• Mild contrast, no cinematic colour grading, no dramatic flares.  
• Depth-of-field: moderate (f/4 – f/8) to keep context readable.  
• Subjects framed from behind, side, or cropped at shoulders to exclude faces.  
• Visual focus on action, objects, textures, or symbolic details.

EDITORIAL CODE
• Exclude faces, public figures, logos, slogans, **any form of text**, religious or political symbols.  
• Follow Reuters / AP ethics: minimal colour / exposure corrections only — no CGI artefacts.

TECH SPECS
• Classification : Editorial, documentary press photo  
• Resolution     : 3840 × 2160 px, portrait (9:16)  
• Camera bodies  : Canon EOS R5 · Nikon Z9 · Sony A1 (pick one)  
• Lenses         : 35 mm f/1.4 · 50 mm f/1.2 · 85 mm f/1.8 (prime)  
• Settings       : ISO 100 – 3200, realistic shutter & aperture (f/4 – f/8 preferred), RAW look  
• Lighting       : Golden hour · blue hour · overcast daylight · neutral indoor  
• Composition    : Rule of thirds, leading lines, layers for depth

Return **only** the finished image prompt — no comments, no markdown.
"""

IMAGE_USER_PROMPT_TEMPLATE = """
# ==== ARTICLE CONTENT ====
HEADLINE: {headline}
DESCRIPTION: {description}

FULL ARTICLE TEXT:
{article_text}

# ==== CREATE VISUAL ELEMENTS FROM ARTICLE ====
Based on the article above, extract:
1. LOCATION: Identify a specific location mentioned or implied in the article
2. KEY OBJECT/ACTION: Identify a specific object, action or detail that visually represents the story
3. LIGHTING & MOOD: Determine appropriate lighting and atmosphere for this news story
4. EMOTIONAL TONE: Determine the emotional context of the story

# ==== TECHNICAL PARAMETERS ====
ISO: {iso}
SHUTTER SPEED: {shutter_speed}
APERTURE: {aperture}
CAMERA BODY: {camera_body}
LENS: {lens}

# ==== GENERATE IMAGE PROMPT FOR GPT-IMAGE-1 ====
NO_TEXT_IN_IMAGE.
Editorial, documentary press photo, no faces
HEADLINE: {headline}
ENVIRONMENT: [describe environment based on article details], {lighting_weather_mood}, surfaces free of signage or advertising
FOCUS OBJECT: [describe key object or action from article]
COMPOSITION: rule of thirds, foreground interest, moderate depth-of-field (f/4 – f/8)
TECH: {camera_body}, {lens}, ISO {iso}, {shutter_speed}, {aperture}, RAW look, minimal Reuters/AP colour correction
STYLE: neutral colour palette, mild contrast, realistic white balance, Le Matin documentary aesthetic
NEGATIVE: faces, portraits, text, letters, words, numbers, signage, typographic characters, captions, subtitles, celebrities, religious or political symbols, digital artefacts
–ar 9:16 –quality 4k
Ultra-realistic 4K press photography, natural lighting, sober journalistic finish.
"""

IMAGE_PROMPT_SUFFIX = (
    "Ultra-realistic 4K press photography, natural lighting, sober journalistic finish."
)

FALLBACK_IMAGE_PROMPT = (
    "Editorial 4 K vertical photograph illustrating « {headline} ». "
    "Documentary realism, no faces, no text, no symbols. Natural colours, moderate depth-of-field."
)

# =========================================================
#  EXAMPLE — HOW TO USE THE TEMPLATE
# =========================================================
"""
EXAMPLE – From article to finished press-photo prompt
────────────────────────────────────────────────────────

# ==== ARTICLE CONTENT ====
HEADLINE: Government launches coastal clean-up drive in Agadir
DESCRIPTION: A new initiative to remove plastic waste from beaches begins this week

FULL ARTICLE TEXT:
The Ministry of Environment announced yesterday the start of a major beach clean-up operation in Agadir, focusing on removing plastic waste that has accumulated along the coast. The six-month initiative will employ local workers and volunteers to systematically clean the beaches, with special attention to microplastics that pose significant threats to marine life.

Equipment including specialized grabbers and biodegradable collection bags has been distributed to workers who began the clean-up at dawn today. Officials expect to collect over five tons of waste in the first month alone.

"This is just the beginning of a nationwide effort to protect our coastal ecosystems," said a ministry spokesperson. The initiative follows alarming studies showing increasing plastic pollution along Morocco's Atlantic coastline, particularly after the tourist season.

Local environmental groups have praised the effort while emphasizing the need for longer-term solutions including stricter regulations on single-use plastics.

# ==== GENERATE IMAGE PROMPT FOR GPT-IMAGE-1 ====
NO_TEXT_IN_IMAGE.
Editorial, documentary press photo, exclude faces,exclude text,exclude celebrities,exclude religious or political symbols,exclude digital artefacts
HEADLINE: Government launches coastal clean-up drive in Agadir
ENVIRONMENT: Agadir beach, Morocco, early morning low tide, soft overcast daylight, surfaces free of signage or advertising
FOCUS OBJECT: worker's gloved hands picking plastic bottle with metal grabber, biodegradable collection bag visible to the side
COMPOSITION: rule of thirds, foreground interest (hands & plastic), gentle background layers of sand and sea, moderate depth-of-field (f/4 – f/8)
TECH: Canon EOS R5, 50 mm f/1.2, ISO 320, 1/500 s, f/5.6, RAW look, minimal Reuters/AP colour correction
STYLE: neutral colour palette, mild contrast, realistic white balance, Le Matin documentary aesthetic
NEGATIVE: faces, portraits, text, letters, words, numbers, signage, typographic characters, captions, subtitles, celebrities, religious or political symbols, digital artefacts
–ar 9:16 –quality 4k
Ultra-realistic 4K press photography, natural lighting, sober journalistic finish.
"""
