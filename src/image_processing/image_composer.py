"""
Image composition functionality for Article2Image.

Functions for adding text, logos and frames to generated images.
"""
import logging
import datetime
from babel.dates import format_date
from PIL import Image, ImageDraw, ImageFont

from src.utils.constants import (
    IMG_WIDTH, IMG_HEIGHT, TEXT_SIDE_MARGIN, 
    DATE_FONT_SIZE, MAIN_TEXT_LINE_SPACING, 
    INITIAL_MAIN_FONT_SIZE, MIN_MAIN_FONT_SIZE,
    DEFAULT_TEXT_COLOR, ACCENT_COLOR, CATEGORY_FONT_SIZE
)
from src.utils.text_utils import wrap_text, get_font


def draw_date_text(draw, date_str, font, position, color):
    """
    Draws the date string at the specified position.
    
    Args:
        draw: ImageDraw object
        date_str: The date string to draw
        font: The font to use
        position: Tuple (x, y) position to draw at
        color: Tuple (r, g, b) color to use
    """
    try:
        draw.text(position, date_str, fill=color, font=font)
        logging.info(f"Drew date: {date_str} at {position}")
    except Exception as e:
        logging.error(f"Error in draw_date_text: {e}")


def calculate_date_position(img_size, text_area_top, side_margin):
    """
    Calculate date position independently from main text.
    
    Args:
        img_size: Tuple (width, height) of the image
        text_area_top: Y-coordinate of the top of the text area
        side_margin: Margin from the sides
        
    Returns:
        Tuple (x, y) for date position
    """
    try:
        # Fixed position from the top of the text area
        fixed_top_margin = 50  # Distance from text_area_top
        date_y = text_area_top + fixed_top_margin
        # Horizontal position from left edge with consistent margin
        date_x = side_margin + 180
        return (date_x, date_y)
    except Exception as e:
        logging.error(f"Error calculating date position: {e}")
        # Return a fallback position if calculation fails
        return (side_margin + 180, text_area_top + 35)


def draw_main_text(draw, lines, font, start_y, img_width, color, line_height, line_spacing):
    """
    Draws the wrapped main text, centered horizontally.
    
    Args:
        draw: ImageDraw object
        lines: List of wrapped text lines
        font: The font to use
        start_y: Y coordinate to start drawing from
        img_width: Width of the image for centering
        color: Tuple (r, g, b) color to use
        line_height: Height of each line of text
        line_spacing: Additional spacing between lines
    """
    current_y = start_y
    try:
        for line in lines:
            line_bbox = draw.textbbox((0, 0), line, font=font)
            line_width = line_bbox[2] - line_bbox[0]
            start_x = (img_width - line_width) // 2 # Center horizontally
            draw.text((start_x, current_y), line, fill=color, font=font)
            current_y += line_height + line_spacing
        logging.info(f"Drew {len(lines)} lines of main text starting at y={start_y}")
    except Exception as e:
        logging.error(f"Error in draw_main_text: {e}")


def draw_category_label(draw, text, font_path, font_size, position, text_color, bg_color, padding):
    """
    Draws a category label with a background rectangle.

    Args:
        draw: The ImageDraw object
        text: The text for the label
        font_path: Path to the preferred font file
        font_size: The desired font size
        position: Tuple (x, y) for the top-left corner
        text_color: Tuple for text color
        bg_color: Tuple for background color
        padding: Tuple (horizontal_padding, vertical_padding)
    """
    try:
        # Try loading the preferred font, with fallbacks
        font = get_font(["Poppins-BoldItalic.ttf", font_path, "Montserrat-Bold.ttf", "Montserrat-Italic.ttf", "arialbd.ttf"], font_size)

        # Calculate text size
        text_bbox = draw.textbbox((0, 0), text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]

        # Calculate background rectangle size
        rect_width = text_width + 2 * padding[0] # Horizontal padding
        rect_height = text_height + 2 * padding[1] # Vertical padding

        # Define rectangle coordinates (using top-left from position)
        rect_x0 = position[0]
        rect_y0 = position[1]
        rect_x1 = rect_x0 + rect_width
        rect_y1 = rect_y0 + rect_height

        # Draw the background rectangle (simple rectangle for now)
        draw.rectangle([(rect_x0, rect_y0), (rect_x1, rect_y1)], fill=bg_color)

        # Calculate text position (centered within the rectangle)
        # Adjusting for font metrics can be tricky, this centers the baseline roughly
        text_x = rect_x0 + padding[0]
        text_y = rect_y0 + padding[1] - text_bbox[1] # Offset by the font's top bearing

        # Draw the text
        draw.text((text_x, text_y), text, fill=text_color, font=font)
        logging.info(f"Drew category label '{text}' at {position}")

    except Exception as e:
        logging.error(f"Error in draw_category_label: {e}")


def add_text_to_image(image, bullet_point, category_key, brand_logo=None, language='en'):
    """
    Overlay Frame.png and add text (including date and category) to the generated image
    
    Args:
        image: Base image to add text to
        bullet_point: Main text to add to the image
        category_key: Category key for the label
        brand_logo: Optional logo to add to the image
        language: Language code for date formatting
        
    Returns:
        Final composited image with text and overlays
    """
    # Ensure the base image is in RGBA mode for proper compositing
    base_image = image.convert('RGBA') if image.mode != 'RGBA' else image.copy()
    target_size = (IMG_WIDTH, IMG_HEIGHT) # Should be (1079, 1345)

    # --- Load Frame --- (Error handling remains the same)
    frame_path = "Frame.png"
    frame_image = None
    try:
        frame_image = Image.open(frame_path).convert('RGBA')
        if frame_image.size != target_size:
            logging.warning(f"Resizing frame from {frame_image.size} to {target_size}")
            frame_image = frame_image.resize(target_size, Image.LANCZOS)
    except Exception as e:
        logging.error(f"Error loading/processing frame {frame_path}: {e}")

    # --- Prepare Overlays ---
    text_overlay = Image.new('RGBA', target_size, (0, 0, 0, 0))
    text_draw = ImageDraw.Draw(text_overlay)
    logo_overlay = None

    # --- Define Text Area Parameters & Constants ---
    img_width, img_height = target_size
    # ASSUMING frame structure for text placement:
    black_band_height_assumption = int(img_height * 0.32)
    text_area_top = img_height - black_band_height_assumption + 60
    text_area_height = black_band_height_assumption - 80
    side_margin = TEXT_SIDE_MARGIN
    max_text_width = img_width - (side_margin * 2)
    main_text_line_spacing = MAIN_TEXT_LINE_SPACING
    date_color = ACCENT_COLOR
    line_color = date_color
    line_thickness = 4
    line_date_spacing = 60 # Drastically increased spacing for testing
    main_text_color = DEFAULT_TEXT_COLOR

    # --- Load Fonts ---
    main_font_path = None
    preferred_fonts = ["Poppins-Bold.ttf", "Montserrat-Bold.ttf", "arialbd.ttf", "ariblk.ttf", "arial.ttf"]
    
    main_font = get_font(preferred_fonts, INITIAL_MAIN_FONT_SIZE)
    date_font = get_font(["Poppins-Italic.ttf", "Montserrat-Italic.ttf", "ariali.ttf", "arial.ttf"], DATE_FONT_SIZE)

    # --- Format Date using Babel --- 
    date_str = ""
    date_text_height = 0
    try:
        today = datetime.date.today()
        # Use Babel's format_date for locale-aware formatting
        try:
            # Use the language code directly with Babel
            date_str = format_date(today, format='EEEE, dd/MM/y', locale=language)
            # Capitalize only the first letter for French style if needed
            if language == 'fr': 
                date_str = date_str.capitalize() 
            logging.info(f"Formatted date using Babel for locale '{language}': {date_str}")
        except Exception as babel_err: # Catch potential Babel errors (e.g., unknown locale)
            logging.error(f"Babel date formatting failed for locale '{language}': {babel_err}. Falling back.")
            date_str = today.strftime("%Y-%m-%d") # Basic fallback

        # Calculate text size using the loaded date_font
        if date_font:
             date_text_bbox = text_draw.textbbox((0, 0), date_str, font=date_font)
             date_text_height = date_text_bbox[3] - date_text_bbox[1]
        else:
             logging.error("Date font not available for size calculation.")
             date_text_height = 0 # Set to zero if font failed to load

    except Exception as date_err:
        logging.error(f"Error preparing date: {date_err}", exc_info=True)
        date_str = "" # Clear date string on error
        date_text_height = 0

    # --- Calculate Main Text Size --- (Using loaded main font)
    initial_font_size = INITIAL_MAIN_FONT_SIZE
    min_font_size = MIN_MAIN_FONT_SIZE
    current_font_size = initial_font_size
    final_lines = []
    total_main_text_height = 0
    actual_line_height = 0
    text_fits = False

    # Calculate available height for main text - no longer dependent on date height
    available_height_for_main_text = text_area_height - 60  # Fixed spacing reserved for date area

    while current_font_size >= min_font_size:
        try:
            # Try to create or adjust the font size
            if current_font_size != main_font.size:
                main_font = get_font(preferred_fonts, current_font_size)
                
            wrapped_lines = wrap_text(bullet_point.strip(), main_font, max_text_width)
            line_height_bbox = main_font.getbbox('Mg') # Use letters with ascenders/descenders
            actual_line_height = line_height_bbox[3] - line_height_bbox[1]
            _total_height = len(wrapped_lines) * actual_line_height + max(0, len(wrapped_lines) - 1) * main_text_line_spacing

            if _total_height <= available_height_for_main_text:
                final_lines = wrapped_lines
                total_main_text_height = _total_height
                text_fits = True
                logging.info(f"Main text fits at font size: {current_font_size}")
                break
            else:
                current_font_size -= 5
                # Will get a new font in the next iteration
                
        except Exception as e:
            logging.error(f"Error calculating text size: {e}", exc_info=True)
            current_font_size -= 5
            # Continue to try smaller font sizes

    if not text_fits:
        logging.warning(f"Main text might be cut off. Using min font size {min_font_size}.")
        main_font = get_font(preferred_fonts, min_font_size)
        final_lines = wrap_text(bullet_point.strip(), main_font, max_text_width)
        line_height_bbox = main_font.getbbox('Mg')
        actual_line_height = line_height_bbox[3] - line_height_bbox[1]
        total_main_text_height = len(final_lines) * actual_line_height + max(0, len(final_lines) - 1) * main_text_line_spacing

    # --- Calculate Vertical Positions --- (Independently)
    # Date position calculated first and independently
    date_position = calculate_date_position((img_width, img_height), text_area_top, side_margin)
    
    # Main text positioned independently, centered in the remaining area
    main_text_vertical_margin = 80  # Space from top of text area to main text
    main_text_start_y = text_area_top + main_text_vertical_margin
    
    # Center the main text block in the available space
    content_area_height = text_area_height - main_text_vertical_margin - 20  # 20px bottom margin
    main_text_start_y += (content_area_height - total_main_text_height) // 2

    # --- Draw Date and Line (if date was prepared successfully and font loaded) ---
    if date_str and date_font:
        # Draw date using function with the calculated position
        draw_date_text(text_draw, date_str, date_font, date_position, date_color)
        logging.info(f"Drew date: {date_str} at {date_position}")
    elif not date_font:
        logging.error("Could not draw date because date_font was not loaded.")
    # else: date_str might be empty due to error

    # --- Draw Main Text --- (Using calculated position and dedicated function)
    if main_font:
        draw_main_text(text_draw, final_lines, main_font, main_text_start_y, img_width, 
                      main_text_color, actual_line_height, main_text_line_spacing)
    else:
        logging.error("Could not draw main text because main_font was not loaded.")

    # --- Draw Category Label ---
    try:
        # Use the category_key directly
        display_category_text = category_key.title() # Title case the key name
        logging.info(f"Category text before drawing: '{display_category_text}' (Original key: '{category_key}')")

        category_text_color = (255, 255, 255) # White
        category_bg_color = (0, 0, 0, 0) # Transparent
        category_padding = (20, 10) # Simplified padding (H, V)
        # Try to use a Bold Italic font, fallback for sizing
        category_font_path = "Montserrat-BoldItalic.ttf" # Preferred bold italic font

        # Fixed Position for Category Label (Top-Right Area)
        fixed_category_x = img_width - 490 # Pixels from right edge
        fixed_category_y = 870       # Pixels from top edge

        # Call the drawing function (which also handles font loading)
        draw_category_label(
            draw=text_draw,
            text=display_category_text,
            font_path=category_font_path,
            font_size=CATEGORY_FONT_SIZE,
            position=(fixed_category_x, fixed_category_y),
            text_color=category_text_color,
            bg_color=category_bg_color,
            padding=category_padding
        )
    except Exception as cat_err:
        logging.error(f"Error drawing category label: {cat_err}")

    # --- Prepare Logo Overlay ---
    if brand_logo:
        try:
            logo_size = (150, 70)
            brand_logo = brand_logo.convert('RGBA') if brand_logo.mode != 'RGBA' else brand_logo
            brand_logo_resized = brand_logo.resize(logo_size, Image.LANCZOS)
            logo_overlay = Image.new('RGBA', target_size, (0, 0, 0, 0))
            logo_x = (img_width - logo_size[0]+760) // 2
            logo_y = 30 # Position near top
            logo_overlay.paste(brand_logo_resized, (logo_x, logo_y), brand_logo_resized)
            logging.info("Prepared logo overlay")
        except Exception as e:
            logging.error(f"Error preparing logo overlay: {e}")
            logo_overlay = None

    # --- Compositing Sequence ---
    final_image = base_image # Start with base
    if frame_image: final_image = Image.alpha_composite(final_image, frame_image) # Add frame
    final_image = Image.alpha_composite(final_image, text_overlay) # Add text (date + main)
    if logo_overlay: final_image = Image.alpha_composite(final_image, logo_overlay) # Add logo

    # Convert back to RGB for final output
    return final_image.convert('RGB') 