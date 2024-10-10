import sys
import time
from commands import CommandsExecutor, screenshot
from parser import parse_command
from gemini_integration import create_chat_completion
from PIL import Image, ImageDraw, ImageFont, ImageEnhance

def create_grid_screenshot(screenshot_path, grid_screenshot_path):
    """Create a grid overlay on the screenshot and return grid parameters."""
    # Load the screenshot image and darken it slightly
    image = Image.open(screenshot_path).convert("RGBA")
    enhancer = ImageEnhance.Brightness(image)
    image = enhancer.enhance(0.7)  # Darken the image by reducing brightness

    # Create an overlay for drawing the grid
    overlay = Image.new("RGBA", image.size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(overlay)

    # Grid specifications based on the resolution
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
    combined.convert("RGB").save(grid_screenshot_path)

    # Return grid parameters
    return grid_cell_width, grid_cell_height, grid_cols, grid_rows

def main():
    if len(sys.argv) < 2:
        print("Usage: python eptm.py \"Your command here\"")
        sys.exit(1)
    else:
        user_request = sys.argv[1]

        messages = [
            {
                "role": "system",
                "content": (
                    "You are an AI assistant controlling the user's computer. The user will ask you to complete a task on their computer, and you will do this by providing a plan based on screenshots sent to you. The screenshots have grids that allow you to locate where certain objects are located. You should check what cell the object is located in. After making the plan based on the screenshot, the program that you communicate with will prompt you to give commands. These commands allow you to control the computer. New screenshots will automatically be sent to you after you have sent the commands, so that you can analyze the results. If the task is not completed, you will have to provide new commands based on the new screenshot. These, and only these, are the commands you can use: "
                    "MOVE_TO_CELL, LEFT_CLICK, RIGHT_CLICK, TYPE, KEY_PRESS, KEY_RELEASE, WAIT, FINISHED. Here are some examples of how you can use the commands:"
                    "For moving the mouse, you type MOVE_TO_CELL, followed by the cell number. Example: MOVE_TO_CELL 5. This will move the mouse to the center of cell number 5."
                    "For left click, you simply write: LEFT_CLICK "
                    "For right click, you write: RIGHT_CLICK "
                    "If you want to wait, which you ALWAYS should include between all commands, you write WAIT, followed by the amount of milliseconds. For example: WAIT 5 . The reason for this being important is that many computers cannot handle too fast operations. They need time to process the commands. "
                    "If you want to type something, you first write TYPE, followed by what you want to type. For example: TYPE hello "
                    "If you want to press ctrl, or any other key, you write KEY_PRESS, followed by the name of the key. For example: KEY_PRESS ctrl "
                    "If you want to release the key you have pressed, you write KEY_RELEASE, and then the key. For example: KEY_RELEASE ctrl " 
                    "Lastly, if you are absolutely certain you have completed the task, you can write FINISHED"
                    "To successfully complete tasks, you always give two answers for each request. The first response you give is always a plan on how to solve the task. After you have given this response, the user will automatically ask you to give the commands. You will only then give the commands. So:\n" 
                    "1. Provide the best plan for completing the task. This plan should be detailed. Describe what cells you want to move to, and so forth.\n" 
                    "2. After getting an automatic response from the program, you provide only commands—following your plan. Avoid explanations, formatting, or extra symbols.\n"
                    "IMPORTANT: NEVER write FINISHED if you are not certain that the task is completed. You WILL have to go through multiple rounds of commands to complete all tasks. You will often have to move the mouse multiple times, and so forth. NEVER write FINISHED if you are not absolutely certain you are finished!!"
                )
            },
            {"role": "user", "content": user_request}
        ]

        finished = False

        screenshot_path = 'screenshot.png'
        grid_screenshot_path = 'grid_screenshot.png'

        # Take a screenshot and create a grid overlay
        screenshot(screenshot_path)
        grid_params = create_grid_screenshot(screenshot_path, grid_screenshot_path)

        # Create an instance of CommandsExecutor with grid parameters
        executor = CommandsExecutor(grid_params)

        while not finished:

            # Stage 1: Request Plan
            plan = create_chat_completion(grid_screenshot_path, messages)
            if not plan.strip():
                print("Error: No response from the AI assistant.")
                break

            print(f"Plan: {plan}")
            messages.append({"role": "assistant", "content": plan})

            # Stage 2: Request Commands
            messages.append({"role": "user", "content": "Great. Now provide only the commands with no explanations."})
            commands = create_chat_completion(grid_screenshot_path, messages)

            print(f"Commands generated: {commands}")

            if not commands.strip():
                print("Error: No commands received from the AI assistant.")
                break

            messages.append({"role": "assistant", "content": commands})
            finished = executor.execute_commands(commands)

            # Take a new screenshot and generate grid_screenshot.png
            screenshot(screenshot_path)
            grid_params = create_grid_screenshot(screenshot_path, grid_screenshot_path)
            executor.update_grid_params(grid_params)

            time.sleep(1)

            if not finished:
                messages.append({"role": "user", "content": "Analyze the new screenshot and determine the best next action. Make a new plan if the screenshot does not show the expected results. Remember to use MOVE_TO_CELL grid_number—to move the cursor to the given grid."})

        print("Exiting program.")

if __name__ == '__main__':
    main()
