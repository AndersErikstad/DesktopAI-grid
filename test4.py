import os
import sys
from test_parser import parse_command  # Import the parser for extracting the cell number
import google.generativeai as genai
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageGrab

# Configure the API key
genai.configure(api_key="AIzaSyDOgG3PjicRTDuQuBFGLP4lreWBxJqfuMo")  # Replace with your actual API key

# Set up the generation configuration
generation_config = {
    "temperature": 0.7,
    "top_p": 0.9,
    "top_k": 40,
    "max_output_tokens": 512,
}

# Initialize the model
model = genai.GenerativeModel(
    model_name="gemini-1.5-pro-002",  # Specify the model name
    generation_config=generation_config
)

def take_screenshot(screenshot_path='screenshot.png'):
    """Take a screenshot and save it."""
    image = ImageGrab.grab()
    image.save(screenshot_path)

from PIL import ImageFont

def create_grid_overlay(image, grid_cols, grid_rows):
    """Create a high-contrast grid overlay on the image with distinctive colors and thicker lines."""
    overlay = Image.new("RGBA", image.size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(overlay)

    grid_cell_width = image.width / grid_cols
    grid_cell_height = image.height / grid_rows

    # Define a set of highly distinctive colors for cells
    cell_colors = [(255, 99, 71, 100),  # Tomato
                   (135, 206, 250, 100),  # Light Sky Blue
                   (144, 238, 144, 100),  # Light Green
                   (255, 228, 181, 100),  # Moccasin
                   (238, 130, 238, 100)]  # Violet

    # Load a bold, larger font for the numbers
    try:
        font = ImageFont.truetype("arial.ttf", 36)  # Bold and large font
    except IOError:
        font = ImageFont.load_default()

    number = 1
    for row in range(grid_rows):
        for col in range(grid_cols):
            x0 = col * grid_cell_width
            y0 = row * grid_cell_height
            x1 = x0 + grid_cell_width
            y1 = y0 + grid_cell_height

            # Use distinctive colors for alternating cells
            fill_color = cell_colors[number % len(cell_colors)]

            # Draw the filled rectangle with semi-transparency
            draw.rectangle([x0, y0, x1, y1], fill=fill_color, outline=(0, 0, 0, 255), width=5)  # Thick black lines

            # Prepare the number for the grid cell
            number_text = str(number)

            # Measure text size for proper centering
            bbox = draw.textbbox((0, 0), number_text, font=font)
            text_width, text_height = bbox[2] - bbox[0], bbox[3] - bbox[1]
            text_x = x0 + (grid_cell_width - text_width) / 2
            text_y = y0 + (grid_cell_height - text_height) / 2

            # Draw the text (numbers) in black with strong opacity
            draw.text((text_x, text_y), number_text, font=font, fill=(0, 0, 0, 255))

            # Increment the number for the next grid cell
            number += 1

    return overlay, grid_cell_width, grid_cell_height


def overlay_grid_on_image(image, overlay):
    """Overlay the grid on the image."""
    combined = Image.alpha_composite(image.convert("RGBA"), overlay)
    return combined.convert("RGB")

def create_chat_completion(image_paths, messages):
    """Send images and messages to the AI model and get the response."""
    # Build prompt parts
    prompt_parts = []

    # Upload images and include them in the prompt
    try:
        for image_path in image_paths:
            image_token = genai.upload_file(image_path)
            prompt_parts.append(image_token)  # Append each image file to the prompt
    except Exception as e:
        print(f"Error uploading image: {e}")
        return ""

    # Build the conversation in the prompt parts
    for message in messages:
        role = message['role']
        content = message['content']
        if role == 'system':
            prompt_parts.append(content)
        elif role == 'user':
            prompt_parts.append(f"User: {content}")
        elif role == 'assistant':
            prompt_parts.append(f"Assistant: {content}")

    # Generate the response using the model's `generate_content` method
    try:
        response = model.generate_content(prompt_parts)
        return response.text.strip()  # Return the generated text
    except Exception as e:
        print("Exception occurred during AI response generation:")
        print(e)
        return ""


def main():
    # Check if the user provided a command
    if len(sys.argv) < 2:
        print("Usage: python script_name.py \"Your command here\"")
        sys.exit(1)
    user_command = sys.argv[1]

    # Paths to images
    screenshot_path = 'screenshot.png'
    grid_image_path = 'grid_image.png'

    # Initial message list with system prompt
    messages = [
        {"role": "system", "content": (
            "You are an AI assistant that helps users by analyzing screenshots with grid overlays. "
            "Each screenshot is divided into a 3x3 grid, consisting of 9 cells. Your task is to reason which cell the object is in. When you do this reasoning, it is very improtant that you actually understand what the object will look like, and then search for where this object is located. If it is close to the given cell number, that means that the object is in that cell. If it is not close, then the object is not in that cell. After you have reasoned and found the cell number, you will be asked to provide the cell number. You will then"
            "and return the cell number (1-9) where the object is located. You can also explain your reasoning to the user. Let's start with the first screenshot."
        )}
    ]

    # Take initial screenshot
    take_screenshot(screenshot_path)
    original_image = Image.open(screenshot_path)

    # Define the fixed 3x3 grid for all zoom levels
    grid_cols, grid_rows = 3, 3

    selected_cells = []  # To store the selected cell at each zoom level
    current_image = original_image.copy()

    # Zoom 3 times, all using a 3x3 grid
    for zoom_level in range(3):
        # Create grid overlay
        overlay, cell_width, cell_height = create_grid_overlay(current_image, grid_cols, grid_rows)
        grid_image = overlay_grid_on_image(current_image, overlay)
        grid_image.save(grid_image_path)

        # Prepare the images to send
        image_paths = [grid_image_path]

        # Prepare the prompt
        if zoom_level == 0:
            # First level, include user's command
            messages.append({"role": "user", "content": f"{user_command}"})
        else:
            # Subsequent levels, instruct the AI to pick the correct cell
            messages.append({"role": "user", "content": (
                "Look at the zoomed-in grid and choose the cell (1-9) where the object is. You may explain your reasoning. It is important that you actually understand what the object is and where it is located."
            )})

        # Send the images and messages to the AI assistant
        response = create_chat_completion(image_paths, messages)

        # Display the assistant's response
        if response:
            print(f"Assistant (Zoom Level {zoom_level + 1}): {response}")
            messages.append({"role": "assistant", "content": response})

            # Use parser to extract the cell number from the response
            cell_number = parse_command(response)

            if cell_number is None or not 1 <= cell_number <= 9:
                print(f"Could not extract a valid cell number from the response: {response}")
                return
            selected_cells.append({
                'cell_number': cell_number,
                'grid_cols': grid_cols,
                'grid_rows': grid_rows,
                'cell_width': cell_width,
                'cell_height': cell_height,
                'image_width': current_image.width,
                'image_height': current_image.height,
            })
        else:
            print("No response received from the AI.")
            return

        # If this is not the final zoom level, zoom into the selected cell
        if zoom_level < 2:
            # Calculate the coordinates of the selected cell
            cell_number = selected_cells[-1]['cell_number']
            col = (cell_number - 1) % grid_cols
            row = (cell_number - 1) // grid_cols
            x0 = col * cell_width
            y0 = row * cell_height
            x1 = x0 + cell_width
            y1 = y0 + cell_height

            # Crop and resize the selected cell to the original image size
            current_image = current_image.crop((x0, y0, x1, y1))
            current_image = current_image.resize(original_image.size, Image.LANCZOS)
        else:
            # Final zoom level, calculate the absolute coordinates for the cursor
            abs_x = 0
            abs_y = 0
            scale_x = 1
            scale_y = 1

            # Iterate over the selected cells to compute the absolute position
            for selection in selected_cells:
                cell_number = selection['cell_number']
                grid_cols = selection['grid_cols']
                grid_rows = selection['grid_rows']
                cell_width = selection['cell_width']
                cell_height = selection['cell_height']
                image_width = selection['image_width']
                image_height = selection['image_height']

                col = (cell_number - 1) % grid_cols
                row = (cell_number - 1) // grid_cols

                # Update absolute position
                abs_x += col * (cell_width * scale_x)
                abs_y += row * (cell_height * scale_y)

                # Update scale for the next level
                scale_x *= cell_width / image_width
                scale_y *= cell_height / image_height

            # Add half of the final cell to get to the center
            final_cell_width = cell_width * scale_x
            final_cell_height = cell_height * scale_y
            abs_x += final_cell_width / 2
            abs_y += final_cell_height / 2

            # Move the cursor to the calculated position
            print(f"Moving cursor to position: ({abs_x}, {abs_y})")
            move_cursor(abs_x, abs_y)
            print("Operation completed.")

def move_cursor(x, y):
    """Move the cursor to the specified coordinates."""
    from pynput.mouse import Controller as MouseController
    mouse = MouseController()
    mouse.position = (int(x), int(y))


if __name__ == "__main__":
    main()
