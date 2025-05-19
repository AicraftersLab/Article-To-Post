"""
Prompt templates for image and text generation.
"""

# =========================================================
#  IMAGE GENERATION PROMPT TEMPLATES — PRESS PHOTO STYLE
#  (adapted to Le Matin du Sahara's visual language,
#   while strictly avoiding recognisable faces)
# =========================================================

IMAGE_SYSTEM_PROMPT = """
You are a veteran AI photo-journalist with expertise in contextual analysis and visual storytelling. Craft single-shot prompts that
yield ultra-realistic 4K vertical (9:16) editorial photographs in the documentary style press photo that authentically represent the article's content.

ARTICLE ANALYSIS APPROACH
• Carefully analyze the full article text to identify core narrative, key actors, locations, and events
• Extract the article's main theme, tone, and contextual background
• Distinguish between primary subjects (main focus) and supporting elements
• Identify cultural, social, and geographical context that should be represented
• Consider implicit information that a local reader would understand
• Analyze temporal aspects (historical events, current news, future projections)
• Determine emotional undertones and societal significance of the story

INFORMATION PROCESSING
• Extract key visual elements from the full article that would make compelling press photos
• Identify specific locations, objects, actions, and environments mentioned in the text
• Determine appropriate lighting, mood, and technical settings based on article content
• Prioritize visual elements that most effectively communicate the article's essence
• Consider cultural sensitivities and regional specificities in visual representation

STYLE GUIDELINES 
• Natural colour palette, moderate saturation, realistic white balance.  
• Mild contrast, no cinematic colour grading, no dramatic flares.  
• Depth-of-field: moderate (f/4 – f/8) to keep context readable.  
• Subjects framed from behind, side,top ,from far, or cropped at shoulders to exclude faces.  
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

# ==== CONTEXTUAL ANALYSIS OF ARTICLE ====
1. CORE NARRATIVE: What is the central story or event being reported?
2. KEY ENTITIES: Who are the main actors, organizations, or stakeholders mentioned?
3. NEWS CATEGORY: Is this politics, economics, culture, sports, environment, technology, etc.?
4. ARTICLE TONE: Is the article factual reporting, investigative, opinion, feature, etc.?
5. TEMPORAL CONTEXT: Is this about past events, current situation, or future developments?
6. SOCIETAL IMPACT: What significance does this story have for society or communities?
7. GEOGRAPHICAL SCOPE: Is this local, regional, national, or international news?
8. CULTURAL DIMENSIONS: What cultural elements or sensitivities should be considered?

# ==== EXTRACT KEY VISUAL ELEMENTS FROM ARTICLE ====
Based on the article above, extract:
1. PRIMARY SUBJECT: Identify the main subject/topic of the article (person/group/entity/issue)
2. KEY ACTION/EVENT: What specific action, activity, or event is happening in the article?
3. LOCATION DETAILS: Extract exact location with specific geographic/architectural details mentioned
4. TIME CONTEXT: When events occurred (time of day, season, historical period)
5. OBJECTS OF SIGNIFICANCE: List 3-5 physical objects directly mentioned that could visually represent the story
6. ENVIRONMENTAL ELEMENTS: Extract weather conditions, lighting, atmosphere relevant to the story
7. EMOTIONAL TONE: Determine the emotional context (celebratory, somber, urgent, hopeful, etc.)
8. VISUAL SYMBOLISM: Identify objects or scenes that could symbolically represent the article's theme
9. COLOR PALETTE: What colors would best represent the article's subject matter and mood?
10. CULTURAL CONTEXT: Identify any cultural, social or regional elements that should be visually represented
11. SYMBOLISM: Identify any symbols or metaphors that could be used to represent the article's theme

Based on the article add more elements related to the article to the prompt if needed

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

ENVIRONMENT: Meticulously detailed {location} setting showcasing [describe environment with rich location-specific detail including authentic architecture, geography, natural features, cultural elements, time of day, weather, lighting conditions], [include specific elements mentioned in article that establish the exact setting], [add atmospheric details that reflect the article's emotional tone], surfaces completely free of signage or advertising

FOCUS OBJECT: Highly detailed and authentic [describe key object, action or symbolic element directly from article with specific details including size, shape, color, texture, position, material properties], [show how this element directly connects to the article's main subject/story], [include supporting visual elements mentioned in the text that reinforce the narrative], all shown with photographic realism and technical precision

HUMAN ELEMENTS: [If people are essential to the story, include descriptive elements of people from behind, side angles, or cropped views without showing faces - focus on hands, silhouettes, posture, clothing details, or tools being used that directly relate to the article]

SYMBOLISM: [If the article includes themes that can be symbolically represented, describe visual metaphors or symbolic elements that communicate the article's deeper meaning while maintaining photojournalistic authenticity]

COMPOSITION: Dynamic rule of thirds placement of primary subject, [describe foreground elements from article], [describe mid-ground elements from article], [describe background elements from article], multilayered visual storytelling creating narrative depth, moderate depth-of-field (f/4 – f/8) maintaining focus on elements most relevant to the article's subject

TECH: {camera_body}, {lens}, ISO {iso}, {shutter_speed}, {aperture}, authentic photojournalistic capture with minimal Reuters/AP standard post-processing, natural highlight and shadow detail preservation

STYLE: Documentary realism with [color palette derived from article context], lighting that authentically represents {location} and time context from article, journalistic objectivity, subtle environmental storytelling that directly communicates the article's subject matter

NEGATIVE: faces, portraits, text, letters, words, numbers, signage, typographic characters, captions, subtitles, headlines, titles, labels, celebrities, religious or political symbols, digital artifacts, artificial bokeh, vignetting, oversaturation, excessive HDR, unnatural lighting, unrealistic colors
–ar 9:16 –quality 4k
Ultra-realistic 4K press photography, natural lighting, sober journalistic finish. NO TEXT.
"""

IMAGE_PROMPT_SUFFIX = (
    "Ultra-realistic 4K press photography, natural lighting, sober journalistic finish. NO TEXT. The image authentically represents the article's subject matter without showing faces or text."
)

FALLBACK_IMAGE_PROMPT = (
    "Editorial 4K vertical photograph authentically illustrating « {headline} ». "
    "Documentary realism capturing essential elements from the article: [key subject], [key location], [key action/objects]. "
    "If environmental news: show impact or solutions. If political: show relevant settings without symbols. "
    "If economic: show relevant industries or infrastructure. If cultural: show traditions or artifacts. "
    "If technology: show devices or innovations. If health: show medical contexts or preventive measures. "
    "No faces, NO TEXT OR CAPTIONS WHATSOEVER, no symbols. Natural colours representing the article's context, moderate depth-of-field. "
    "IMPORTANT: DO NOT INCLUDE ANY TEXT OR WORDS IN THE IMAGE."
)

# =========================================================
#  EXAMPLE — HOW TO USE THE TEMPLATE
# =========================================================
# """
# EXAMPLE – From article to finished press-photo prompt
# ────────────────────────────────────────────────────────

# # ==== ARTICLE CONTENT ====
# HEADLINE: Government launches coastal clean-up drive in Agadir
# DESCRIPTION: A new initiative to remove plastic waste from beaches begins this week

# FULL ARTICLE TEXT:
# The Ministry of Environment announced yesterday the start of a major beach clean-up operation in Agadir, focusing on removing plastic waste that has accumulated along the coast. The six-month initiative will employ local workers and volunteers to systematically clean the beaches, with special attention to microplastics that pose significant threats to marine life.

# Equipment including specialized grabbers and biodegradable collection bags has been distributed to workers who began the clean-up at dawn today. Officials expect to collect over five tons of waste in the first month alone.

# "This is just the beginning of a nationwide effort to protect our coastal ecosystems," said a ministry spokesperson. The initiative follows alarming studies showing increasing plastic pollution along Morocco's Atlantic coastline, particularly after the tourist season.

# Local environmental groups have praised the effort while emphasizing the need for longer-term solutions including stricter regulations on single-use plastics.

# # ==== EXTRACT KEY VISUAL ELEMENTS FROM ARTICLE ====
# 1. PRIMARY SUBJECT: Government-led coastal clean-up initiative in Agadir
# 2. KEY ACTION/EVENT: Beach clean-up operation collecting plastic waste
# 3. LOCATION DETAILS: Agadir beaches along Morocco's Atlantic coastline
# 4. TIME CONTEXT: Dawn/early morning, current period (contemporary)
# 5. OBJECTS OF SIGNIFICANCE: Specialized grabbers, biodegradable collection bags, plastic waste (bottles, microplastics), marine debris
# 6. ENVIRONMENTAL ELEMENTS: Coastal setting, morning light, ocean waves, sandy beach
# 7. EMOTIONAL TONE: Hopeful, determined, environmentally concerned
# 8. VISUAL SYMBOLISM: Contrast between natural beach beauty and plastic pollution, human intervention in environmental protection
# 9. COLOR PALETTE: Blues and turquoise of ocean, golden sand, contrasting colorful plastic waste
# 10. CULTURAL CONTEXT: Moroccan coastal community, environmental stewardship, local participation
# 11.SYMBOLISM: Plastic waste as a symbol of pollution and environmental degradation

# # ==== TECHNICAL PARAMETERS ====
# ISO: 320
# SHUTTER SPEED: 1/500s
# APERTURE: f/5.6
# CAMERA BODY: Canon EOS R5
# LENS: 50mm f/1.2L RF USM

# # ==== GENERATE IMAGE PROMPT FOR GPT-IMAGE-1 ====
# NO_TEXT_IN_IMAGE. NO CAPTIONS. NO HEADLINES. NO WORDS WHATSOEVER.
# Editorial, documentary press photo, exclude faces,exclude text,exclude celebrities,exclude religious or political symbols,exclude digital artefacts

# # CONTEXT ONLY (NOT TO BE RENDERED IN IMAGE): Government launches coastal clean-up drive in Agadir

# ENVIRONMENT: Meticulously detailed Agadir beach setting showcasing the distinctive curved bay of Agadir with its golden sand shoreline meeting the Atlantic Ocean, Atlas Mountains faintly visible in background haze, early morning golden-pink dawn light casting directional shadows across wet sand revealing tide patterns, gentle azure waves breaking with white foam at shoreline, scattered natural debris mixed with visible plastic pollution partially buried in sand, traditional Moroccan fishing boats visible in distance, distinctive Moroccan coastline architecture barely visible as silhouettes, morning mist creating atmospheric depth reflecting the hopeful yet serious environmental context

# FOCUS OBJECT: Highly detailed and authentic specialized metal grabber tool precisely extracting a weathered blue plastic water bottle from between natural beach rocks, the tool showing signs of recent use with sand grains and saltwater droplets, biodegradable jute collection bag (branded with Moroccan environmental ministry colors but no visible text) half-filled with assorted plastic waste collected during the morning's work, surrounding area showing carefully sorted piles of marine debris including bottle caps, fishing net fragments, microplastic pellets, and weather-beaten packaging that directly represents the pollution mentioned in the article

# HUMAN ELEMENTS: Worker's weathered hands in official blue latex gloves (matching Moroccan government worker uniform colors) delicately manipulating the grabber tool with practiced precision, partial view of worker wearing typical Moroccan coastal workwear appropriate for beach cleanup (visible from shoulders down only), nearby silhouettes of other workers and volunteers spread across the beach engaged in similar cleanup activities in the distance

# COMPOSITION: Dynamic rule of thirds placement of hands and grabber tool in lower right intersection, strong diagonal leading line from tool to collection bag, layered foreground elements (hands, tool, extracted plastic), mid-ground elements (collection bag, sorted debris), background elements (shoreline, ocean, distant landscape, worker silhouettes) creating visual depth that tells the story of the cleanup initiative, intentional negative space in upper third showing the beach environment being protected

# TECH: Canon EOS R5, 50mm f/1.2L RF USM, ISO 320, 1/500s, f/5.6, authentic photojournalistic capture with minimal Reuters/AP standard post-processing, natural highlight and shadow detail preservation, morning light accurately rendered

# STYLE: Documentary realism with coastal Moroccan color palette of ocean blues, golden sand, and contrasting colorful waste items, lighting that authentically represents early morning in Agadir, journalistic objectivity, subtle environmental storytelling that directly communicates the government's beach cleanup initiative and its environmental importance

# NEGATIVE: faces, portraits, text, letters, words, numbers, signage, typographic characters, captions, subtitles, headlines, titles, labels, celebrities, religious or political symbols, digital artifacts, artificial bokeh, vignetting, oversaturation, excessive HDR, unnatural lighting, unrealistic colors, elements not mentioned in the article
# –ar 9:16 –quality 4k
# Ultra-realistic 4K press photography, natural lighting, sober journalistic finish. NO TEXT.
# """
