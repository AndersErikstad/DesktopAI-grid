from PIL import Image, ImageDraw, ImageFont, ImageEnhance

# Load the screenshot image and darken it slightly
image = Image.open('screenshot.png').convert("RGBA")
enhancer = ImageEnhance.Brightness(image)
image = enhancer.enhance(0.7)  # Darken the image by reducing brightness (adjust this value if needed)

# Create an overlay for drawing the grid
overlay = Image.new("RGBA", image.size, (255, 255, 255, 0))
draw = ImageDraw.Draw(overlay)

# Grid specifications based on the resolution (1920x1080)
grid_cell_width = 40   # Width of each grid cell in pixels
grid_cell_height = 40  # Height of each grid cell in pixels
grid_cols = image.width // grid_cell_width   # Number of columns
grid_rows = image.height // grid_cell_height  # Number of rows

# Adjust the grid cell dimensions to exactly fit the image
grid_cell_width = image.width / grid_cols
grid_cell_height = image.height / grid_rows

# Load font for the numbers
try:
    font = ImageFont.truetype("arial.ttf", 12)
except IOError:
    font = ImageFont.load_default()

# Draw the grid with sequential numbers
number = 1
for row in range(int(grid_rows)):
    for col in range(int(grid_cols)):
        x0 = col * grid_cell_width
        y0 = row * grid_cell_height
        x1 = x0 + grid_cell_width
        y1 = y0 + grid_cell_height

        # Draw the rectangle for the grid cell (outline only, no fill color)
        draw.rectangle(
            [x0, y0, x1, y1],
            outline=(255, 255, 255, 100)  # Semi-transparent white outline
        )

        # Prepare the number for the grid cell
        number_text = str(number)

        # Measure text size
        bbox = draw.textbbox((0, 0), number_text, font=font)
        text_width, text_height = bbox[2] - bbox[0], bbox[3] - bbox[1]

        # Calculate position to center the text inside the box
        text_x = x0 + (grid_cell_width - text_width) / 2
        text_y = y0 + (grid_cell_height - text_height) / 2

        # Draw the text (numbers) fully opaque
        draw.text(
            (text_x, text_y),
            number_text,
            font=font,
            fill=(255, 255, 255, 255)  # White text, fully opaque
        )

        # Increment the number for the next grid cell
        number += 1

# Combine the grid overlay with the darkened image
combined = Image.alpha_composite(image, overlay)

# Save the final image with the grid and numbers
combined.convert("RGB").save('grid_screenshot.png')
