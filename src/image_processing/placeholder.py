"""
Placeholder image generation functions for Article2Image.
"""
import random
import time
import logging
from PIL import Image, ImageDraw, ImageFont


def create_simple_image(bullet_point="Demo image", size=(1079, 1345)):
    """
    Create a simple image with text for testing
    
    Args:
        bullet_point: Text to display on the image
        size: Tuple of (width, height) for the image
        
    Returns:
        PIL Image object
    """
    img = Image.new('RGB', size, color=(40, 70, 120))
    draw = ImageDraw.Draw(img)
    
    # Draw a gradient background
    for y in range(size[1]):
        r = int(40 + (y / size[1]) * 40)
        g = int(70 + (y / size[1]) * 30)
        b = int(120 - (y / size[1]) * 40)
        draw.line([(0, y), (size[0], y)], fill=(r, g, b))
    
    # Add some shapes
    for i in range(5):
        x = int(size[0] * (0.2 + 0.15 * i))
        y = int(size[1] * 0.3)
        radius = int(size[0] * 0.08)
        draw.ellipse([x-radius, y-radius, x+radius, y+radius], 
                     fill=(255, 255, 255, 100), 
                     outline=(255, 255, 255))
    
    try:
        font = ImageFont.truetype("arial.ttf", 30)
    except:
        font = ImageFont.load_default()
    
    # Add text
    timestamp = time.strftime("%H:%M:%S")
    text = f"TEST IMAGE\n{bullet_point[:30]}...\nCreated at: {timestamp}"
    
    text_bbox = draw.textbbox((0,0), text, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    
    position = ((size[0] - text_width) // 2, (size[1] - text_height) // 2)
    draw.text(position, text, font=font, fill=(255, 255, 255))
    
    return img


def create_enhanced_placeholder(text, size=(1079, 1345)):
    """
    Create a visually interesting placeholder image based on the content
    
    Args:
        text: Text to be represented visually in the image
        size: Tuple of (width, height) for the image
        
    Returns:
        PIL Image object
    """
    # Explicitly use the target size passed to the function
    target_width, target_height = size
    logging.info(f"Creating placeholder with dimensions: {target_width}x{target_height}")
    
    # Create a base image with gradient
    img = Image.new('RGB', (target_width, target_height), color=(30, 50, 70))
    draw = ImageDraw.Draw(img)
    
    # Create a more colorful gradient background
    for y in range(target_height):
        # Create a gradient with more Instagram-friendly colors
        progress = y / target_height
        # Create a more vibrant gradient (purple to coral-orange)
        r = int(100 + (155 * progress))
        g = int(50 + (100 * progress))
        b = int(180 - (100 * progress))
        draw.line([(0, y), (target_width, y)], fill=(r, g, b))
    
    # Extract keywords for visualization
    keywords = []
    for word in text.split():
        if len(word) > 4 and word.lower() not in ['with', 'this', 'that', 'from', 'your', 'have', 'there']:
            keywords.append(word.strip('.,!?;:()[]{}'))
    
    # Use up to 5 keywords
    keywords = keywords[:5]
    
    # Add a visually appealing background pattern
    for i in range(15):  # Add more elements for visual interest
        x = random.randint(0, target_width)
        y = random.randint(0, target_height)
        radius = random.randint(int(min(target_width, target_height)*0.05), int(min(target_width, target_height)*0.1))
        opacity = random.randint(30, 80)
        color = (255, 255, 255, opacity)
        draw.ellipse((x-radius, y-radius, x+radius, y+radius), fill=color)
    
    # Create abstract shapes representing the keywords
    shapes = []
    
    # Generate abstract shapes based on keywords
    for i, keyword in enumerate(keywords):
        # Use the hash of the keyword to generate consistent shapes
        seed = sum(ord(c) for c in keyword)
        random.seed(seed)
        
        # Shape parameters
        shape_type = random.choice(['circle', 'rectangle', 'triangle'])
        x_center = random.randint(int(target_width * 0.2), int(target_width * 0.8))
        y_center = random.randint(int(target_height * 0.2), int(target_height * 0.8))
        
        # Size proportional to word length
        size_factor = len(keyword) / 10 + 0.5
        shape_size = int(min(target_width, target_height) * 0.15 * size_factor)
        
        # Color based on the keyword
        hue = (sum(ord(c) for c in keyword) % 360) / 360.0
        
        # Convert HSV to RGB (simplified)
        if hue < 1/6:
            r, g, b = 255, int(255 * hue * 6), 0
        elif hue < 2/6:
            r, g, b = int(255 * (2/6 - hue) * 6), 255, 0
        elif hue < 3/6:
            r, g, b = 0, 255, int(255 * (hue - 2/6) * 6)
        elif hue < 4/6:
            r, g, b = 0, int(255 * (4/6 - hue) * 6), 255
        elif hue < 5/6:
            r, g, b = int(255 * (hue - 4/6) * 6), 0, 255
        else:
            r, g, b = 255, 0, int(255 * (1 - hue) * 6)
        
        # Add opacity
        opacity = 120 + random.randint(0, 100)
        color = (r, g, b, opacity)
        
        # Draw the shape
        if shape_type == 'circle':
            draw.ellipse(
                [(x_center - shape_size, y_center - shape_size), 
                 (x_center + shape_size, y_center + shape_size)], 
                fill=color
            )
        elif shape_type == 'rectangle':
            rotation = random.randint(0, 45)
            rect_img = Image.new('RGBA', (shape_size*2, shape_size), (r, g, b, opacity))
            rect_img = rect_img.rotate(rotation, expand=True)
            img.paste(rect_img, (x_center - shape_size, y_center - shape_size//2), rect_img)
        elif shape_type == 'triangle':
            points = [
                (x_center, y_center - shape_size),
                (x_center - shape_size, y_center + shape_size),
                (x_center + shape_size, y_center + shape_size)
            ]
            draw.polygon(points, fill=color)
        
        # Add shape to the list for connecting lines
        shapes.append((x_center, y_center))
    
    # Add some connecting lines
    if len(shapes) > 1:
        for i in range(len(shapes) - 1):
            start = shapes[i]
            end = shapes[i + 1]
            draw.line([(start[0], start[1]), (end[0], end[1])], fill=(255, 255, 255, 100), width=2)
        
        # Add a final connecting line to close the shape
        if len(shapes) > 2:
            draw.line([(shapes[-1][0], shapes[-1][1]), (shapes[0][0], shapes[0][1])], 
                      fill=(255, 255, 255, 100), width=2)
    
    # Add a mock Instagram-style interface element at the bottom to make it look more like an IG post
    footer_height = 50
    draw.rectangle([(0, target_height-footer_height), (target_width, target_height)], fill=(20, 20, 20, 200))
    
    # Add some small icons in the footer to simulate Instagram UI
    icon_y = target_height - footer_height//2
    # Like icon (heart shape)
    draw.ellipse([(20, icon_y-10), (40, icon_y+10)], fill=(255, 255, 255, 150))
    # Comment icon
    draw.rectangle([(60, icon_y-10), (80, icon_y+10)], fill=(255, 255, 255, 150))
    # Share icon
    draw.rectangle([(100, icon_y-10), (120, icon_y+10)], fill=(255, 255, 255, 150))
    
    # Add a timestamp-like text in the corner
    try:
        small_font = ImageFont.truetype("arial.ttf", 12)
    except:
        small_font = ImageFont.load_default()
    timestamp = time.strftime("%H:%M")
    draw.text((target_width-50, 20), timestamp, fill=(255, 255, 255, 200), font=small_font)
    
    # Convert to RGB for compatibility
    if img.mode == 'RGBA':
        img = img.convert('RGB')
    
    return img 