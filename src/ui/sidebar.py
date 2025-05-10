"""
Sidebar components for the Article2Image app.
"""
import streamlit as st
import os
from PIL import Image

from src.app_config import go_to_step
from src.utils.translations import get_text, TRANSLATIONS


def render_sidebar():
    """Render the sidebar content"""
    st.sidebar.header(get_text('settings', current_language=st.session_state.language))
    
    # Add a new post button in sidebar
    if st.sidebar.button("🔄 Nouvelle Publication", use_container_width=True):
        # Reset content, keep persistent logo file and state
        if 'bullet_point' in st.session_state:
            del st.session_state.bullet_point
        if 'description' in st.session_state:
            del st.session_state.description
        if 'hashtags' in st.session_state:
            del st.session_state.hashtags
        if 'base_image' in st.session_state:
            del st.session_state.base_image
        if 'generated' in st.session_state:
            del st.session_state.generated
        if 'image_generated' in st.session_state:
            del st.session_state.image_generated
        if 'article_hash' in st.session_state:
            del st.session_state.article_hash
        # Delete the current session logo, but persistent state/file remain
        if 'brand_logo' in st.session_state:
            del st.session_state.brand_logo  
        # Return to step 1
        go_to_step(1)
    
    # Language selector
    render_language_selector()
    
    # Improved input method selection
    st.sidebar.markdown(f"### 1️⃣ {get_text('input_method', current_language=st.session_state.language)}")
    input_method = st.sidebar.radio(
        get_text('select_input', current_language=st.session_state.language), 
        [get_text('url', current_language=st.session_state.language), 
         get_text('text', current_language=st.session_state.language)]
    )
    
    # Content parameters
    render_content_settings()
    
    return input_method


def render_language_selector():
    """Render the language selector"""
    st.sidebar.markdown(f"### 🌐 {get_text('language', current_language=st.session_state.language)}")
    
    language_options_display = {
        'en': 'English 🇬🇧', 
        'fr': 'Français 🇫🇷',
        # 'de': 'Deutsch 🇩🇪', 'it': 'Italiano 🇮🇹', 'pt': 'Português 🇵🇹','es': 'Español 🇪🇸',
    }
    
    # Ensure language_name exists for display formatting
    for code, name in language_options_display.items():
        if code not in TRANSLATIONS: 
            TRANSLATIONS[code] = {}
        if 'language_name' not in TRANSLATIONS[code]: 
            TRANSLATIONS[code]['language_name'] = name.split(' ')[0]
        if 'categories' not in TRANSLATIONS[code]: 
            TRANSLATIONS[code]['categories'] = {}
    
    # Calculate index based on the current session state language
    try:
        current_lang_index = list(language_options_display.keys()).index(st.session_state.language)
    except ValueError:
        # Fallback if the state somehow holds an invalid value
        current_lang_index = list(language_options_display.keys()).index('fr')
    
    selected_language_code = st.sidebar.selectbox(
        "Langue du contenu généré:",
        options=list(language_options_display.keys()),
        format_func=lambda code: language_options_display[code], # Show full name
        index=current_lang_index, # Use the calculated index
        key='content_language_selector', # Added key back for potentially better state handling
        help="Choisissez la langue pour le contenu généré."
    )
    
    # Update language and rerun ONLY if changed
    if selected_language_code != st.session_state.language:
        st.session_state.language = selected_language_code
        # Reset generated flag to trigger regeneration
        if 'generated' in st.session_state:
            st.session_state.generated = False
        st.rerun()


def render_content_settings():
    """Render the content generation settings"""
    st.sidebar.markdown(f"### 📊 {get_text('content_settings', current_language=st.session_state.language)}")
    
    bullet_word_count = st.sidebar.slider(
        get_text('bullet_words', current_language=st.session_state.language), 
        5, 15, 10, 
        help="Nombre de mots dans le point principal"
    )
    st.session_state.bullet_word_count = bullet_word_count
    
    description_word_count = st.sidebar.slider(
        get_text('description_words', current_language=st.session_state.language), 
        20, 70, 50, 
        help="Nombre de mots dans la description"
    )
    st.session_state.description_word_count = description_word_count
    
    hashtag_count = st.sidebar.slider(
        get_text('hashtag_count', current_language=st.session_state.language), 
        3, 8, 5, 
        help="Nombre de hashtags à générer"
    )
    st.session_state.hashtag_count = hashtag_count


def load_persistent_logo():
    """Attempt to load persistent logo at startup"""
    persistent_logo_path = "persistent_logo.png"
    if 'persistent_logo' not in st.session_state and os.path.exists(persistent_logo_path):
        try:
            st.session_state.persistent_logo = Image.open(persistent_logo_path).convert("RGBA")
            st.sidebar.success("Logo chargé depuis le fichier.")
        except Exception as e:
            st.sidebar.error(f"Erreur lors du chargement du logo: {e}")