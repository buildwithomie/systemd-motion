#!/usr/bin/env python3

from PIL import Image, ImageDraw
import os

def create_icon():
    # Create a 48x48 icon
    size = 48
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Draw a simple activity monitor icon
    # Background circle
    draw.ellipse([2, 2, size-2, size-2], fill=(52, 101, 164, 255), outline=(255, 255, 255, 255), width=2)
    
    # Activity bars
    bar_width = 3
    bar_spacing = 2
    start_x = 8
    start_y = 20
    
    for i in range(6):
        x = start_x + i * (bar_width + bar_spacing)
        height = 8 + (i % 3) * 4  # Varying heights
        draw.rectangle([x, start_y + (16 - height), x + bar_width, start_y + 16], 
                      fill=(255, 255, 255, 255))
    
    # Save icon
    icon_dir = os.path.dirname(__file__) + "/../data/icons/48x48/apps/"
    os.makedirs(icon_dir, exist_ok=True)
    img.save(icon_dir + "com.motion.activity-monitor.png")
    print(f"Icon created at {icon_dir}com.motion.activity-monitor.png")

if __name__ == "__main__":
    create_icon()
