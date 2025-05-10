"""
Step navigation and rendering for the Article2Image app.
"""
import streamlit as st


def display_step_navigation(steps):
    """
    Display the step indicator and navigation
    
    Args:
        steps: List of step dictionaries with 'number', 'name', and 'icon' keys
    """
    # Display step indicator
    st.markdown("<div style='margin-bottom: 30px;'>", unsafe_allow_html=True)
    cols = st.columns(len(steps))
    for i, col in enumerate(cols):
        step = steps[i]
        step_style = ""
        if step["number"] == st.session_state.current_step:
            # Current step
            step_style = "background-color: #1E88E5; color: white; border-radius: 10px; padding: 10px; text-align: center; font-weight: bold;"
        elif step["number"] < st.session_state.current_step:
            # Completed step
            step_style = "background-color: #BBDEFB; color: #1565C0; border-radius: 10px; padding: 10px; text-align: center; font-weight: bold;"
        else:
            # Future step
            step_style = "background-color: #F5F5F5; color: #9E9E9E; border-radius: 10px; padding: 10px; text-align: center;"
        
        col.markdown(f"<div style='{step_style}'>{step['icon']} {step['name']}</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)


def get_steps():
    """
    Get the list of steps
    
    Returns:
        List of step dictionaries
    """
    return [
        {"number": 1, "name": "Entrée d'Article", "icon": "📄"},
        {"number": 2, "name": "Contenu Généré", "icon": "✏️"},
        {"number": 3, "name": "Génération d'Image", "icon": "🖼️"},
        {"number": 4, "name": "Ajout de Logo", "icon": "🏷️"},
        {"number": 5, "name": "Publication Finale", "icon": "📱"}
    ]