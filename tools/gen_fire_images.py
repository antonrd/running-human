# from PIL import Image, ImageDraw
# import random

# # Create a larger, randomized fire effect that better fills the 32x32 canvas

# # Initialize a transparent 32x32 canvas
# canvas_size = (32, 32)
# random_fire_canvas = Image.new("RGBA", canvas_size, (0, 0, 0, 0))
# draw = ImageDraw.Draw(random_fire_canvas)

# # Generate random fire patterns using pixel blocks
# for y in range(32):  # Vertical progression (flame height)
#     for x in range(32):  # Horizontal spread (flame width)
#         # Randomize flame intensity and color based on height (y-coordinate)
#         if 20 <= y <= 31:  # Base: orange and yellow
#             if random.random() > 0.6:
#                 color = random.choice([(255, 165, 0, 255), (255, 223, 0, 255)])
#                 draw.point((x, y), fill=color)
#         elif 10 <= y < 20:  # Middle: orange and light red
#             if random.random() > 0.7:
#                 color = random.choice([(255, 140, 0, 255), (255, 69, 0, 255)])
#                 draw.point((x, y), fill=color)
#         elif 0 <= y < 10:  # Top: darker red and sporadic orange
#             if random.random() > 0.85:
#                 color = random.choice([(255, 69, 0, 255), (255, 99, 71, 255)])
#                 draw.point((x, y), fill=color)

# # Save the randomized fire pattern
# randomized_file_path = "./randomized_fire_pixel_art_32x32.png"
# random_fire_canvas.save(randomized_file_path)

# randomized_file_path


from PIL import Image, ImageDraw

# Create a 32x32 pixel canvas with a transparent background
canvas_size = (40, 40)
transparent_canvas = Image.new("RGBA", canvas_size, (0, 0, 0, 0))

# Draw a small pixel art fire manually
draw = ImageDraw.Draw(transparent_canvas)

# Define the fire shape using simple pixel blocks
# Core of the fire (yellow)
draw.rectangle([4, 30, 36, 40], fill=(255, 223, 0, 255))  # Bright yellow core

# Outer flames (orange)
draw.rectangle([0, 20, 40, 30], fill=(255, 165, 0, 255))  # Base flame layer
draw.rectangle([4, 10, 36, 20], fill=(255, 140, 0, 255))  # Middle flame layer

# Top flames (red)
draw.rectangle([8, 0, 32, 10], fill=(255, 69, 0, 255))   # Topmost flame

# Save the resulting transparent PNG file
file_path = "./fire_pixel_art_40x40.png"
transparent_canvas.save(file_path)

file_path
