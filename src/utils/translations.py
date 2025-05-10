"""
Translation utilities for Article2Image application.
"""
import logging

# Define allowed category keys (used internally)
ALLOWED_CATEGORY_KEYS = ["Societe", "hi-tech", "sports", "nation", "economie", "regions", "culture", "monde", "Sante", "LifeStyle"]

# Language translations - Keep French UI, keep category translations for display
TRANSLATIONS = {
    'en': {
        # No UI translations needed
        'categories': {
            'Societe': "Society", 'hi-tech': "Hi-Tech", 'sports': "Sports", 'nation': "Nation", 'economie': "Economy",
            'regions': "Regions", 'culture': "Culture", 'monde': "World", 'Sante': "Health", 'LifeStyle': "Lifestyle"
        },
        'language_name': "English"
    },
    'fr': {
        # Keep all French UI translations
        'title': "Générateur de Publications Instagram",
        'settings': "Paramètres",
        'input_method': "Méthode d'Entrée",
        'select_input': "Sélectionnez comment saisir votre article :",
        'url': "URL",
        'text': "Texte",
        'appearance': "Paramètres d'Apparence",
        'highlight_color': "Couleur de surbrillance pour les mots-clés :",
        'shadow': "Ombre d'arrière-plan du texte :",
        'image_style': "Style d'image :",
        'how_to_use': "Comment utiliser",
        'url_input': "Entrez l'URL de l'article :",
        'url_help': "Collez un lien vers n'importe quel article d'actualité ou blog",
        'text_input': "Entrez le texte de l'article :",
        'text_help': "Copiez et collez le texte de votre article ici",
        'example_btn': "Charger un Exemple",
        'content_settings': "Paramètres de Contenu",
        'bullet_words': "Mots du Point Principal",
        'description_words': "Mots de la Description",
        'hashtag_count': "Nombre de Hashtags",
        'generate_content': "Générer le Contenu",
        'bullet_point': "Point Principal",
        'bullet_info': "Ceci apparaîtra sur votre image",
        'article_description': "Description de l'Article",
        'description_info': "Ceci apparaîtra dans la légende de votre publication (pas sur l'image)",
        'hashtags': "Hashtags",
        'hashtags_info': "Ceux-ci apparaîtront dans la légende de votre publication (pas sur l'image)",
        'content_success': "Contenu généré ! Continuez vers l'onglet Image.",
        'preview': "Aperçu",
        'generate_image': "Générer une Image IA",
        'image_info': "Utilisation de DALL-E pour créer une image personnalisée basée sur votre contenu",
        'generate_btn': "Générer l'Image",
        'upload_image': "Télécharger Votre Propre Image",
        'upload_info': "Téléchargez une image d'arrière-plan personnalisée (sera redimensionnée à 768x957)",
        'upload_btn': "Télécharger une image d'arrière-plan personnalisée",
        'image_ready': "Image prête ! Passez à l'onglet Logo ou sautez à la Publication Finale.",
        'please_content': "Veuillez générer du contenu dans l'onglet Contenu en premier.",
        'add_logo': "Ajouter Votre Logo (Facultatif)",
        'logo_info': "Votre logo apparaîtra au centre en haut de l'image",
        'upload_logo': "Téléchargez votre logo de marque (PNG transparent recommandé)",
        'logo_uploaded': "Logo téléchargé ! Passez à l'onglet Publication Finale.",
        'remove_logo': "Supprimer le Logo",
        'skip_logo': "Téléchargez un logo ou passez à l'onglet Publication Finale si vous ne souhaitez pas ajouter de logo.",
        'please_image': "Veuillez générer une image dans l'onglet Image en premier.",
        'create_post': "Créer la Publication Instagram Finale",
        'create_btn': "Créer la Publication Instagram Finale",
        'download_btn': "Télécharger l'Image",
        'copy_btn': "Copier la Légende",
        'instagram_caption': "Légende Instagram",
        'view_copy': "Cliquez pour afficher/copier la légende de la publication",
        'copy_description': "Copier la description :",
        'copy_hashtags': "Copier les hashtags :",
        'post_ready': "Votre publication Instagram est prête ! Téléchargez l'image et copiez la légende pour la publication.",
        'what_next': "Que souhaitez-vous faire ensuite ?",
        'another_post': "Créer une Autre Publication",
        'different_style': "Essayer un Style Différent",
        'edit_post': "Modifier Cette Publication",
        'language': "Langue de Contenu", # Correctly label for content language
        'edit': "Modifier",
        'select_category_label': "Sélectionner la Catégorie :",
        'categories': {
            'Societe': "Société", 'hi-tech': "Hi-Tech", 'sports': "Sports", 'nation': "Nation", 'economie': "Économie",
            'regions': "Régions", 'culture': "Culture", 'monde': "Monde", 'Sante': "Santé", 'LifeStyle': "Style de Vie"
        },
        'language_name': "Français"
    },
    # Keep other language entries JUST for categories and language_name display
    'es': {
        'categories': {
             'Societe': "Sociedad", 'hi-tech': "Alta Tecnología", 'sports': "Deportes", 'nation': "Nación", 'economie': "Economía",
            'regions': "Regiones", 'culture': "Cultura", 'monde': "Mundo", 'Sante': "Salud", 'LifeStyle': "Estilo de Vida"
        },
        'language_name': "Español"
    },
    'de': {
         'categories': {
            'Societe': "Gesellschaft", 'hi-tech': "Hi-Tech", 'sports': "Sport", 'nation': "Nation", 'economie': "Wirtschaft",
            'regions': "Regionen", 'culture': "Kultur", 'monde': "Welt", 'Sante': "Gesundheit", 'LifeStyle': "Lebensstil"
        },
        'language_name': "Deutsch"
    },
    # ... Add other languages' categories and language_name as needed ...
}

def get_text(key, lang=None, current_language='fr'):
    """
    Get UI text in French, but get category/content-related translations
    in the language specified by 'lang' or current_language.
    
    Args:
        key: The key to look up in the translation dictionary
        lang: Optional override for language
        current_language: The current language setting from session state
        
    Returns:
        The translated text string
    """
    selected_lang = lang if lang is not None else current_language

    # Handle category keys specifically - use the selected language for display
    if key.startswith('category_'):
        category_key = key.split('_', 1)[1]
        # Check selected language first
        if selected_lang in TRANSLATIONS and 'categories' in TRANSLATIONS[selected_lang] and category_key in TRANSLATIONS[selected_lang]['categories']:
            return TRANSLATIONS[selected_lang]['categories'][category_key]
        # Fallback to French category names if translation missing in selected lang
        if 'fr' in TRANSLATIONS and 'categories' in TRANSLATIONS['fr'] and category_key in TRANSLATIONS['fr']['categories']:
             logging.warning(f"Category translation for '{category_key}' not found in language '{selected_lang}'. Falling back to French.")
             return TRANSLATIONS['fr']['categories'][category_key]
        return category_key # Return key if no translation found anywhere

    # For all other keys (UI elements), always return French
    if 'fr' in TRANSLATIONS and key in TRANSLATIONS['fr']:
        return TRANSLATIONS['fr'][key]

    # Fallback for missing French UI keys
    logging.warning(f"UI translation key '{key}' not found in French. Using fallback.")
    return key.replace('_', ' ').title() 