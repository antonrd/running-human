from PIL import Image, ImageDraw

def draw_rhombus_with_pillow():
    # Create an image with a white background
    canvas_size = 40, 60
    image = Image.new("RGBA", canvas_size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)

    # Define the coordinates for the rhombus
    # Center the rhombus in the image
    rhombus = [
        (20, 0),  # Top point
        (40, 30),  # Right point
        (20, 60),  # Bottom point
        (0, 30)   # Left point
    ]

    # Draw the rhombus with a purple fill
    draw.polygon(rhombus, fill=(151, 57, 240, 255), outline="black")

    # Save or show the image
    image.show()
    image.save("purple_rhombus.png")

# Call the function to draw the rhombus
draw_rhombus_with_pillow()
