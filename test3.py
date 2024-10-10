import os
import google.generativeai as genai
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageGrab

# Configure the API key
genai.configure(api_key="AIzaSyDOgG3PjicRTDuQuBFGLP4lreWBxJqfuMo")  # Replace with your actual API key

# Set up the generation configuration
generation_config = {
    "temperature": 1,
    "top_p": 0.8,
    "top_k": 10,
    "max_output_tokens": 8192,
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

def create_grid_screenshot(screenshot_path, grid_screenshot_path):
    """Create a colorful grid overlay on the screenshot with larger cells."""
    # Load the screenshot image and lighten it slightly
    image = Image.open(screenshot_path).convert("RGBA")
    enhancer = ImageEnhance.Brightness(image)
    image = enhancer.enhance(1.3)  # Lighten the image for better contrast

    # Create an overlay for drawing the grid
    overlay = Image.new("RGBA", image.size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(overlay)

    # Define a list of subtle colors to rotate through for the cells
    cell_colors = [(255, 235, 238, 120), (237, 231, 246, 120), (232, 245, 233, 120),
                   (227, 242, 253, 120), (255, 249, 196, 120)]

    # Increase the size of each grid cell for better OCR
    grid_cell_width = 60   # Width of each grid cell in pixels (increased)
    grid_cell_height = 60  # Height of each grid cell in pixels (increased)
    grid_cols = image.width // grid_cell_width   # Number of columns
    grid_rows = image.height // grid_cell_height  # Number of rows

    # Load font for the numbers
    try:
        font = ImageFont.truetype("arial.ttf", 14)  # Increase font size for readability
    except IOError:
        font = ImageFont.load_default()

    # Draw the grid with colored cells and thicker borders
    number = 1
    for row in range(int(grid_rows)):
        for col in range(int(grid_cols)):
            x0 = col * grid_cell_width
            y0 = row * grid_cell_height
            x1 = x0 + grid_cell_width
            y1 = y0 + grid_cell_height

            # Choose a color from the list in a rotating fashion
            fill_color = cell_colors[number % len(cell_colors)]

            # Draw a filled rectangle for the grid cell
            draw.rectangle([x0, y0, x1, y1], fill=fill_color, outline=(0, 0, 0, 150), width=3)

            # Prepare the number for the grid cell
            number_text = str(number)

            # Measure text size
            bbox = draw.textbbox((0, 0), number_text, font=font)
            text_width, text_height = bbox[2] - bbox[0], bbox[3] - bbox[1]

            # Calculate position to center the text inside the box
            text_x = x0 + (grid_cell_width - text_width) / 2
            text_y = y0 + (grid_cell_height - text_height) / 2

            # Draw the text (numbers) in black for better visibility
            draw.text((text_x, text_y), number_text, font=font, fill=(0, 0, 0, 255))

            # Increment the number for the next grid cell
            number += 1

    # Combine the grid overlay with the lightened image
    combined = Image.alpha_composite(image, overlay)

    # Save the final image with the grid and numbers
    combined.convert("RGB").save(grid_screenshot_path)

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
        return response.text  # Return the generated text
    except Exception as e:
        print("Exception occurred during AI response generation:")
        print(e)
        return ""

def main():
    # Define the paths to the images
    screenshot_path = 'screenshot.png'
    grid_screenshot_path = 'grid_screenshot.png'

    # Create an initial message list with the system prompt
    messages = [
        {"role": "system", "content": (
            "You are an AI assistant that helps users by analyzing screenshots with grid overlays. "
            "The screenshot provided has a grid overlay that divides the screen into numbered cells. "
            "You can refer to objects or locations on the screen by their cell numbers."
        )}
    ]

    print("You can now interact with the AI assistant. Type 'exit' to stop.")

    while True:
        # Get user input from the terminal
        user_input = input("You: ")

        # Exit condition
        if user_input.lower() == 'exit':
            print("Exiting the program.")
            break

        # Take a new screenshot and create a grid overlay before each new request
        take_screenshot(screenshot_path)
        create_grid_screenshot(screenshot_path, grid_screenshot_path)

        # Prepare the images to send
        image_paths = [grid_screenshot_path]

        # Append the user's input to the messages
        messages.append({"role": "user", "content": user_input})

        # Send the images and messages to the AI assistant
        response = create_chat_completion(image_paths, messages)

        # Display the assistant's response
        if response:
            print(f"Assistant: {response}")
            # Append the assistant's response to the messages for context
            messages.append({"role": "assistant", "content": response})
        else:
            print("No response received from the AI.")

if __name__ == "__main__":
    main()
