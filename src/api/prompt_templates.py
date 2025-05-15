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

STYLE GUIDELINES 
• Natural colour palette, moderate saturation, realistic white balance.  
• Mild contrast, no cinematic colour grading, no dramatic flares.  
• Depth-of-field: moderate (f/4 – f/8) to keep context readable.  
• Subjects framed from behind, side, or cropped at shoulders to exclude faces.  
• Visual focus on action, objects, textures, or symbolic details.

EDITORIAL CODE
• IMPORTANT: DO NOT INCLUDE ANY TEXT IN THE IMAGE - NO CAPTIONS, NO HEADLINES, NO WORDS.
• Exclude faces, public figures, logos, slogans, **any form of text**, religious or political symbols.  
• Follow Reuters / AP ethics: minimal colour / exposure corrections only — no CGI artefacts.
• Never render headlines, captions or any textual information directly on the image.

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
5. TIME OF DAY: Identify when events occurred or what time would be most appropriate
6. WEATHER CONDITIONS: Determine appropriate weather for the scene if outdoors
7. SYMBOLIC ELEMENTS: Identify any symbolic objects or elements that represent the story's theme

# ==== TECHNICAL PARAMETERS ====
ISO: {iso}
SHUTTER SPEED: {shutter_speed}
APERTURE: {aperture}
CAMERA BODY: {camera_body}
LENS: {lens}

# ==== GENERATE IMAGE PROMPT FOR GPT-IMAGE-1 ====
NO_TEXT_IN_IMAGE. NO CAPTIONS. NO HEADLINES. NO WORDS WHATSOEVER.
Editorial, documentary press photo, exclude faces,exclude text,exclude celebrities,exclude religious or political symbols,exclude digital artefacts

# CONTEXT ONLY (NOT TO BE RENDERED IN IMAGE): {headline}

ENVIRONMENT: Detailed and specific {location} setting: [describe environment with rich detail including architecture, geography, natural features, time of day, weather, lighting conditions, nearby objects, textures, colors, and atmosphere], {lighting_weather_mood}, surfaces free of signage or advertising
FOCUS OBJECT: Highly detailed [describe key object or action with specific details including size, shape, color, texture, position, and how it relates to the surroundings and story], shown with photographic realism and technical precision
COMPOSITION: rule of thirds, foreground interest, moderate depth-of-field (f/4 – f/8), multiple planes of visual information, balanced negative space
TECH: {camera_body}, {lens}, ISO {iso}, {shutter_speed}, {aperture}, RAW look, minimal Reuters/AP colour correction
STYLE: neutral colour palette, mild contrast, realistic white balance.
NEGATIVE: faces, portraits, text, letters, words, numbers, signage, typographic characters, captions, subtitles, headlines, titles, labels, celebrities, religious or political symbols, digital artefacts
–ar 9:16 –quality 4k
Ultra-realistic 4K press photography, natural lighting, sober journalistic finish.
"""

IMAGE_PROMPT_SUFFIX = (
    "Ultra-realistic 4K press photography, natural lighting, sober journalistic finish. NO TEXT."
)

FALLBACK_IMAGE_PROMPT = (
    "Editorial 4 K vertical photograph illustrating « {headline} ». "
    "Documentary realism, no faces, NO TEXT OR CAPTIONS WHATSOEVER, no symbols. Natural colours, moderate depth-of-field. "
    "IMPORTANT: DO NOT INCLUDE ANY TEXT OR WORDS IN THE IMAGE."
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
NO_TEXT_IN_IMAGE. NO CAPTIONS. NO HEADLINES. NO WORDS WHATSOEVER.
Editorial, documentary press photo, exclude faces,exclude text,exclude celebrities,exclude religious or political symbols,exclude digital artefacts

# CONTEXT ONLY (NOT TO BE RENDERED IN IMAGE): Government launches coastal clean-up drive in Agadir

ENVIRONMENT: Agadir beach, Morocco, early morning low tide, soft overcast daylight with pink-orange horizon glow, wet sand reflecting sky colors, gentle waves breaking at shoreline, scattered seashells and small rocks, distant fishing boats on horizon, curved coastline with view of beachfront buildings in far background, surfaces free of signage or advertising
FOCUS OBJECT: Worker's weathered gloved hands gripping blue plastic bottle with extended metal grabber tool, visible texture of rubber gloves with sand grains stuck to surface, biodegradable collection bag (half-filled with assorted plastic waste) visible to the side, small pile of collected debris nearby showing bottle caps, plastic fragments, and tangled fishing line
COMPOSITION: rule of thirds, foreground interest (hands & plastic), gentle background layers of sand and sea, moderate depth-of-field (f/4 – f/8)
TECH: Canon EOS R5, 50 mm f/1.2, ISO 320, 1/500 s, f/5.6, RAW look, minimal Reuters/AP colour correction
STYLE: neutral colour palette, mild contrast, realistic white balance
NEGATIVE: faces, portraits, text, letters, words, numbers, signage, typographic characters, captions, subtitles, headlines, titles, labels, celebrities, religious or political symbols, digital artefacts
–ar 9:16 –quality 4k
Ultra-realistic 4K press photography, natural lighting, sober journalistic finish. NO TEXT.
"""
