import os
import sys
import time
import re
import ctypes
from commands import CommandsExecutor, screenshot
from gemini_integration import create_chat_completion
from PIL import Image, ImageDraw, ImageFont

# Ensure that the GridVision folder exists
if not os.path.exists('GridVision'):
    os.makedirs('GridVision')

def get_screen_size():
    """Get the actual screen size, accounting for any display scaling."""
    user32 = ctypes.windll.user32
    # Make the process DPI aware
    user32.SetProcessDPIAware()
    screen_width = user32.GetSystemMetrics(0)
    screen_height = user32.GetSystemMetrics(1)
    return screen_width, screen_height

def create_grid_screenshot(screenshot_path, grid_screenshot_path, grid_cols, grid_rows):
    """
    Create a grid overlay on the screenshot and return grid parameters.

    Args:
        screenshot_path (str): Path to the original screenshot image.
        grid_screenshot_path (str): Path to save the grid-overlaid image.
        grid_cols (int): Number of columns in the grid.
        grid_rows (int): Number of rows in the grid.

    Returns:
        tuple: (grid_cell_width, grid_cell_height, grid_cols, grid_rows)
    """
    # Load the screenshot image
    image = Image.open(screenshot_path).convert("RGBA")
    
    # Create an overlay for drawing the grid
    overlay = Image.new("RGBA", image.size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(overlay)

    # Calculate grid cell dimensions
    grid_cell_width = image.width / grid_cols
    grid_cell_height = image.height / grid_rows

    # Load font for the numbers
    try:
        font_size = int(min(grid_cell_width, grid_cell_height) / 4)
        font = ImageFont.truetype("arial.ttf", font_size)
    except IOError:
        font = ImageFont.load_default()

    # Draw the grid with sequential numbers
    number = 1
    for row in range(grid_rows):
        for col in range(grid_cols):
            x0 = col * grid_cell_width
            y0 = row * grid_cell_height
            x1 = x0 + grid_cell_width
            y1 = y0 + grid_cell_height

            # Draw the rectangle for the grid cell
            draw.rectangle([x0, y0, x1, y1], outline=(255, 0, 0, 255), width=2)

            # Prepare the number for the grid cell
            number_text = str(number)

            # Measure text size
            bbox = draw.textbbox((0, 0), number_text, font=font)
            text_width, text_height = bbox[2] - bbox[0], bbox[3] - bbox[1]

            # Calculate position to center the text inside the box
            text_x = x0 + (grid_cell_width - text_width) / 2
            text_y = y0 + (grid_cell_height - text_height) / 2

            # Draw the text (numbers)
            draw.text((text_x, text_y), number_text, font=font, fill=(0, 255, 0, 255))

            # Increment the number for the next grid cell
            number += 1

    # Combine the grid overlay with the original image
    combined = Image.alpha_composite(image, overlay)

    # Save the final image with the grid and numbers
    combined.convert("RGB").save(f'GridVision/{grid_screenshot_path}')

    # Return grid parameters
    return grid_cell_width, grid_cell_height, grid_cols, grid_rows

def crop_to_cell(screenshot_path, grid_params, cell_number, cropped_path):
    """
    Crop the screenshot to the area of the specified grid cell.

    Args:
        screenshot_path (str): Path to the original screenshot image.
        grid_params (tuple): Parameters of the grid (cell width, cell height, cols, rows).
        cell_number (int): The grid cell number to crop to.
        cropped_path (str): Path to save the cropped image.

    Returns:
        tuple: (x_offset, y_offset, cropped_width, cropped_height)
    """
    grid_cell_width, grid_cell_height, grid_cols, grid_rows = grid_params
    total_cells = grid_cols * grid_rows

    # Validate the cell number
    if cell_number < 1 or cell_number > total_cells:
        raise ValueError(f"Cell number must be between 1 and {total_cells}")

    # Calculate the grid cell's row and column
    cell_index = cell_number - 1  # Zero-based index
    col = cell_index % grid_cols
    row = cell_index // grid_cols

    # Calculate the pixel coordinates for the selected cell
    x0 = int(col * grid_cell_width)
    y0 = int(row * grid_cell_height)
    x1 = int(x0 + grid_cell_width)
    y1 = int(y0 + grid_cell_height)

    # Debugging output
    print(f"Cropping to grid cell {cell_number} at row {row}, column {col}")
    print(f"Cropping coordinates: ({x0}, {y0}) to ({x1}, {y1})")

    # Open the original screenshot
    image = Image.open(screenshot_path)
    print(f"Original screenshot size: {image.size}")

    # Crop the selected cell
    cropped_image = image.crop((x0, y0, x1, y1))

    # Save the cropped image
    cropped_image.save(f'GridVision/{cropped_path}')
    print(f"Cropped image saved at {cropped_path}")

    return x0, y0, cropped_image.width, cropped_image.height

def extract_cell_number(text):
    """
    Extract the first cell number mentioned in the text.

    Args:
        text (str): The text to search for the cell number.

    Returns:
        int or None: The extracted cell number, or None if not found.
    """
    match = re.search(r'\bCell\s*(\d+)\b', text, re.IGNORECASE)
    if not match:
        match = re.search(r'\b(\d+)\b', text)
    if match:
        return int(match.group(1))
    return None

def convert_fine_cell_to_coordinates(fine_cell_number, fine_grid_params, x_offset, y_offset, cropped_width, cropped_height, screen_width, screen_height):
    """
    Convert the fine grid cell number into screen pixel coordinates.

    Args:
        fine_cell_number (int): The fine grid cell number.
        fine_grid_params (tuple): Parameters of the fine grid.
        x_offset (int): X offset of the cropped area in the original image.
        y_offset (int): Y offset of the cropped area in the original image.
        cropped_width (int): Width of the cropped image.
        cropped_height (int): Height of the cropped image.
        screen_width (int): Actual screen width.
        screen_height (int): Actual screen height.

    Returns:
        tuple: (x_final, y_final) Screen coordinates.
    """
    fine_grid_cols, fine_grid_rows = fine_grid_params[2], fine_grid_params[3]
    fine_cell_index = fine_cell_number - 1  # Zero-based index
    fine_col = fine_cell_index % fine_grid_cols
    fine_row = fine_cell_index // fine_grid_cols

    # Calculate fine grid cell dimensions
    fine_grid_cell_width = cropped_width / fine_grid_cols
    fine_grid_cell_height = cropped_height / fine_grid_rows

    # Calculate the center of the fine grid cell within the cropped image
    x_fine_in_cropped = fine_col * fine_grid_cell_width + (fine_grid_cell_width / 2)
    y_fine_in_cropped = fine_row * fine_grid_cell_height + (fine_grid_cell_height / 2)

    # Translate to image coordinates using the coarse grid's offset
    x_final_image = x_offset + x_fine_in_cropped
    y_final_image = y_offset + y_fine_in_cropped

    # Get image dimensions
    image = Image.open('screenshot.png')
    image_width, image_height = image.size

    # Calculate scaling factors
    x_scale = screen_width / image_width
    y_scale = screen_height / image_height

    # Adjust coordinates for screen scaling
    x_final = x_final_image * x_scale
    y_final = y_final_image * y_scale

    print(f"Fine grid cell {fine_cell_number} corresponds to screen coordinates ({x_final}, {y_final})")

    return x_final, y_final

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
                    "MOVE x y, LEFT_CLICK, RIGHT_CLICK, TYPE, KEY_PRESS, KEY_RELEASE, WAIT, FINISHED. Here are some examples of how you can use the commands:"
                    "For moving the mouse, you type MOVE x y, followed by the coordinates. Example: MOVE 839 934."
                    "For left click, you simply write: LEFT_CLICK "
                    "For right click, you write: RIGHT_CLICK "
                    "If you want to wait, which you ALWAYS should include between all commands, you write WAIT, followed by the amount of milliseconds. For example: WAIT 50 . The reason for this being important is that many computers cannot handle too fast operations. They need time to process the commands. "
                    "If you want to type something, you first write TYPE, followed by what you want to type. For example: TYPE https://www.youtube.com/ "
                    "If you want to press ctrl, or any other key, you write KEY_PRESS, followed by the name of the key. For example: KEY_PRESS ctrl "
                    "If you want to release the key you have pressed, you write KEY_RELEASE, and then the key. For example: KEY_RELEASE ctrl " 
                    "Lastly, if you are absolutely certain you have completed the task, you can write FINISHED"
                    "To successfully complete tasks, you always give two answers for the request. The first response you give is always a plan on how to solve the task. After you have given this response, the program (or user) will automatically ask you to give the commands. You will only then give the commands. So:\n" 
                    "1. Provide the best plan for completing the task. This plan should be detailed. Describe what cells you want to move to, and so forth. You do this by saying, for example, MOVE cell4. This command will not actually move the cursor, but it will tell our program (or user), that you want to move the cursor to a given location - which will allow our program (or user) to provide you with the coordinates you need, so that you later can use the MOVE x y command.\n" 
                    "2. After getting an automatic response from the program (or user), you provide only commands—following your plan. Avoid explanations, formatting, or extra symbols. If you have stated that you want to MOVE to a cell in the plan, you will first have been provided the coordinates for this cell. You can therefore use the MOVE x y command in this stage.\n"
                    "IMPORTANT: NEVER write FINISHED if you are not certain that the task is completed. You WILL have to go through multiple rounds of commands to complete all tasks. You will often have to move the mouse multiple times, and so forth. NEVER write FINISHED if you are not absolutely certain you are finished!!"
                    "IMPORTANT: When provided with a screenshot, always try to understand the screenshot, and what you need to do next. The screenshots provide important and useful information, that is crucial for you to complete the task. Think of each new screenshot, as a new part of your task. When you get a new screenshot, you will always scratch the old plan, and think of what you should do next - based on the screenshot!"
                    "IMPORTANT: ALWAYS MAKE A NEW PLAN, AFTER RECIEVING A SCREENSHOT."
                )
            },
            {"role": "user", "content": user_request}
        ]

        finished = False
        while not finished:
            # Initial setup
            coarse_grid_cols = 9
            coarse_grid_rows = 9

            screenshot_path = 'screenshot.png'
            grid_screenshot_path = 'grid_screenshot.png'

            # Capture the screenshot and create a coarse grid
            print("Capturing screenshot...")
            screenshot(screenshot_path)
            print("Creating coarse grid overlay...")
            coarse_grid_params = create_grid_screenshot(screenshot_path, grid_screenshot_path, coarse_grid_cols, coarse_grid_rows)

            # Send the coarse grid screenshot to the assistant
            print("Sending coarse grid screenshot to assistant...")
            messages.append({"role": "user", "content": "Please identify the coarse grid cell where the target object is located. Also give a short explination to why you chose this cell. What information did you use to decide that this was the right cell?"})
            plan = create_chat_completion(f'GridVision/{grid_screenshot_path}', messages, request_plan=True)
            if not plan.strip():
                print("Error: No response from the AI assistant.")
                sys.exit(1)
            print(f"AI Assistant Plan:\n{plan}")
            messages.append({"role": "assistant", "content": plan})

            # Check if 'MOVE' is in the plan
            if 'MOVE' in plan.upper():
                # Proceed with cell-finding steps as before
                # Extract the coarse cell number
                coarse_cell_number = extract_cell_number(plan)
                if not coarse_cell_number:
                    print("Error: Could not extract coarse cell number.")
                    sys.exit(1)

                # Crop the screenshot to the coarse cell
                cropped_screenshot_path = 'cropped_screenshot.png'
                print("Cropping to coarse grid cell...")
                x_offset, y_offset, cropped_width, cropped_height = crop_to_cell(
                    screenshot_path, coarse_grid_params, coarse_cell_number, cropped_screenshot_path
                )

                # Fine grid setup
                fine_grid_cols = 5
                fine_grid_rows = 3
                fine_grid_screenshot_path = 'fine_grid_screenshot.png'
                print("Creating fine grid overlay...")
                fine_grid_params = create_grid_screenshot(f'GridVision/{cropped_screenshot_path}', fine_grid_screenshot_path, fine_grid_cols, fine_grid_rows)

                # Send the fine grid screenshot to assistant
                print("Sending fine grid screenshot to assistant...")
                messages.append({"role": "user", "content": "Here is a zoomed-in image of the coarse grid cell you selected. Now, please identify the fine grid cell where the target object is located."})
                plan = create_chat_completion(f'GridVision/{fine_grid_screenshot_path}', messages, request_plan=True)
                if not plan.strip():
                    print("Error: No response from the AI assistant.")
                    sys.exit(1)
                print(f"AI Assistant Plan:\n{plan}")
                messages.append({"role": "assistant", "content": plan})

                # Extract the fine cell number
                fine_cell_number = extract_cell_number(plan)
                if not fine_cell_number:
                    print("Error: Could not extract fine cell number.")
                    sys.exit(1)

                # Get screen dimensions
                print("Retrieving screen size...")
                screen_width, screen_height = get_screen_size()
                print(f"Screen size: {screen_width}x{screen_height}")

                # Calculate the exact coordinates
                print("Calculating exact coordinates...")
                messages.append({"role": "user", "content": "Calculating the exact coordinates of the target object."})
                x_fine, y_fine = convert_fine_cell_to_coordinates(
                    fine_cell_number, fine_grid_params, x_offset, y_offset, cropped_width, cropped_height, screen_width, screen_height
                )
                messages.append({"role": "assistant", "content": f"The object is located at pixel coordinates ({x_fine}, {y_fine})."})

                waitAndAak=bool(input("Do you want to continue? (True/False)"))

                if waitAndAak==True:
                    question=str(input("Do you want to ask a question to the artificial intelligence? (Y/N)"))
                        
                    if question=='Y':
                        AIquestion=str(input("What is your question?"))
                        messages.append({"role": "user", "content": AIquestion})
                        AIanswer=create_chat_completion(f'GridVision/{fine_grid_screenshot_path}', messages, request_plan=False)
                        messages.append({"role": "assistant", "content": AIanswer})
                        print(f"AI Assistant Answer:\n{AIanswer}")
                    else:
                        print("No question asked.")
                else:
                    print("Continuing without asking a question.")

                # Request the command from the assistant
                print("Requesting command from assistant...")
                messages.append({"role": "user", "content": f"The object is located at pixel coordinates ({x_fine}, {y_fine}). Please provide the next command you want to perform. Provide only one command."})
                commands = create_chat_completion(f'GridVision/{fine_grid_screenshot_path}', messages, request_plan=False)
                if not commands.strip():
                    print("Error: No response from the AI assistant.")
                    sys.exit(1)
                print(f"Command Generated:\n{commands}")
                messages.append({"role": "assistant", "content": commands})

            

                # Execute the commands
                print("Executing command...")
                executor = CommandsExecutor(
                    coarse_grid_params, fine_grid_params, x_offset, y_offset, screen_width, screen_height
                )
                finished = executor.execute_commands(commands, fine_cell_number)

            else:
                # No MOVE command in plan
                # Proceed to request next command from assistant
                print("No MOVE command in plan. Proceeding to request next command.")
                # Request the next command from the assistant
                print("Requesting next command from assistant...")
                messages.append({"role": "user", "content": "Please provide the next command you want to perform. Provide only a few commands."})
                commands = create_chat_completion(f'GridVision/{grid_screenshot_path}', messages, request_plan=False)
                if not commands.strip():
                    print("Error: No response from the AI assistant.")
                    sys.exit(1)
                print(f"Command Generated:\n{commands}")
                messages.append({"role": "assistant", "content": commands})

                # Execute the commands
                print("Executing command...")
                # Since we don't have fine grid parameters, we pass None
                executor = CommandsExecutor(
                    coarse_grid_params, None, None, None, None, None
                )
                finished = executor.execute_commands(commands, None)

            if finished:
                print("Task completed.")
            else:
                print("Task not completed.")
                # Wait before retrying
                time.sleep(0.1)

if __name__ == '__main__':
    main()
