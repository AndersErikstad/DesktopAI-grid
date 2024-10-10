# DesktopAI-AA

Write `python eptm.py "Your command"` in the terminal to run the program.

![Build Status](https://img.shields.io/badge/build-passing-brightgreen)
![License](https://img.shields.io/badge/license-MIT-blue)

## Table of Contents
- [Introduction](#introduction)
- [Why This Project is Interesting](#why-this-project-is-interesting)
- [Usage Instructions](#usage-instructions)
- [Example Output](#example-output)
- [Factors Affecting Efficiency](#factors-affecting-efficiency)
- [File Descriptions](#file-descriptions)
- [Credits](#credits)
- [License](#license)

## Introduction

The reason why I find the AI-mouse project interesting is that I believe a similar solution will be the future for computers. I also think that we will gain a lot of knowledge relevant to other potential projects in robotics. (Because navigating on a computer with AI shares many aspects with navigating in the real world with AI)

A mouse is a simple way to navigate a computer. I believe that with a combination of several types of AI, we can create a program that can navigate a computer and thus perform several tasks that currently require humans, such as creating more complex programs.

## Usage Instructions

Run the following command in the terminal:

```bash
python eptm.py "Your command"
```

## Example Output

Here is an illustration of how the output can look:

```
User: Download Minecraft for me
LLM: Analyzing screenshot...        #CV
LLM: Step 1: Open the browser to find the download link for Minecraft.      #LLM
LLM: Looking for browser icon on the desktop...        #CV
LLM: {mouse movement to position (120, 340)}       #EPTM      #LLM
LLM: {left click}      #EPTM      #LLM
LLM: Browser opened.       #CV
LLM: Step 2: Search for Minecraft download.      #LLM
LLM: {mouse movement to search field (400, 70)}      #EPTMT      #LLM
LLM: {left click}      #EPTM      #LLM
LLM: Typing 'Minecraft download'      #LLM
LLM: {press enter}      #EPTM      #LLM
LLM: Search results displayed on the screen       #CV
LLM: Step 3: Click on the official Minecraft website.      #LLM
LLM: Analyzing screenshot... finding 'minecraft.net' link       #CV
LLM: {mouse movement to position (450, 210)}     #EPTMT      #LLM
LLM: {left click}     #EPTMT      #LLM
LLM: Step 4: Find the download button.      #LLM
LLM: Analyzing screenshot...       #CV
LLM: {mouse movement to position (620, 300)}     #EPTMT      #LLM
LLM: {left click}     #EPTMT      #LLM
LLM: Step 5: Confirm download.      #LLM
LLM: Analyzing screenshot... looking for confirmation dialog box       #CV
LLM: {mouse movement to position (510, 420)}     #EPTMT      #LLM
LLM: {left click}     #EPTMT      #LLM
LLM: Download started.       #CV
```

## Factors Affecting Efficiency

- **Quality and Speed**: The performance of the LLM and CV (EPTMT is irrelevant, as its runtime is virtually zero compared to LLM and CV).
  
The faster (more powerful computer, optimized code) the LLM and CV are, the faster the program will naturally be. We want a program that takes less time to solve a given task than a human would. Thus, the program should be relatively fast, and we need a fast LLM and CV. If these are too slow, the product will not appeal to the user.

However, speed alone is not enough. We do not want a dumb LLM or CV, which is very fast, but not able to solve the given task. It is expected that the LLM will make mistakes along the way and then correct those mistakes. For example, if the program is asked to create a functioning chess game, we would not necessarily expect it to do so on the first try. It will likely make mistakes, which it will be able to correct thanks to the CV. The program will use the CV to detect any errors that occur. If the CV detects that the chess program does not work and sees that it has received an error message in the terminal, the program will be able to correct it. This process is expected to repeat several times during the operation. Finally, the program will determine that it has solved the given task and show/give the result to the user. Since this process requires logical thinking, a relatively intelligent LLM (high quality) is desirable.

## File Descriptions

### commands.py

Provides various functions to control the mouse and keyboard:
- `move(x, y)`: Move the mouse to specified coordinates.
- `left_click()`: Perform a left mouse click.
- `right_click()`: Perform a right mouse click.
- `drag_drop(x1, y1, x2, y2)`: Drag from one position to another.
- `type_text(text, delay=0.02)`: Type the given text with a delay.
- `key_press(key)`: Press a keyboard key.
- `key_release(key)`: Release a keyboard key.
- `screenshot(filename)`: Take a screenshot.
- `wait(milliseconds)`: Pause execution for a specified time.
- `get_key(key_str)`: Convert string to pynput Key object.

### eptm.py

Executes commands parsed from text:
- `execute_commands(command_text)`: Parse and execute commands.
- `main()`: Main function to handle user input and generate AI plans and commands.

### openai_integration.py

Integrates with OpenAI to generate plans and commands:
- `image_to_data_url(image_path)`: Convert image to data URL.
- `create_chat_completion(image_path, messages, request_plan=True)`: Generate chat completions from OpenAI.

## Credits

- Contributors: [Anders Erisktad](https://github.com/AndersErisktad), [Andreas-Can](https://github.com/Andreas-Can)

$env:GOOGLE_APPLICATION_CREDENTIALS="C:\Users\andyg\Desktop\DesktopAI\snipsnap-365ef-05565eb3919f.json"

