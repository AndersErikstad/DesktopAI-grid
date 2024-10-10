from pynput.mouse import Controller as MouseController, Button
from pynput.keyboard import Controller as KeyboardController, Key
from PIL import ImageGrab
import time
from parser import parse_command

mouse = MouseController()
keyboard = KeyboardController()

def move(x, y):
    """Move the mouse to the specified coordinates."""
    mouse.position = (int(float(x)), int(float(y)))

def left_click():
    """Perform a left mouse click."""
    mouse.click(Button.left, 1)

def right_click():
    """Perform a right mouse click."""
    mouse.click(Button.right, 1)

def drag_drop(x1, y1, x2, y2):
    """Drag from (x1, y1) to (x2, y2)."""
    mouse.position = (int(float(x1)), int(float(y1)))
    mouse.press(Button.left)
    time.sleep(0.1)
    mouse.position = (int(float(x2)), int(float(y2)))
    time.sleep(0.1)
    mouse.release(Button.left)

def type_text(text, delay=0.02):
    """Type the given text with a slight delay between each character."""
    for char in text:
        time.sleep(delay)
        keyboard.press(char)
        keyboard.release(char)

def key_press(key):
    """Press a keyboard key."""
    key = get_key(key)
    keyboard.press(key)

def key_release(key):
    """Release a keyboard key."""
    key = get_key(key)
    keyboard.release(key)

def screenshot(filename='screenshot.png'):
    """Take a screenshot and save it."""
    image = ImageGrab.grab()
    image.save(filename)

def wait(milliseconds):
    """Pause execution for a specified number of milliseconds."""
    time.sleep(float(milliseconds) / 1000.0)

def get_key(key_str):
    """Convert string to pynput Key object if necessary."""
    special_keys = {
        'alt': Key.alt,
        'alt_l': Key.alt_l,
        'alt_r': Key.alt_r,
        'backspace': Key.backspace,
        'caps_lock': Key.caps_lock,
        'cmd': Key.cmd,
        'cmd_r': Key.cmd_r,
        'ctrl': Key.ctrl,
        'ctrl_l': Key.ctrl_l,
        'ctrl_r': Key.ctrl_r,
        'delete': Key.delete,
        'down': Key.down,
        'end': Key.end,
        'enter': Key.enter,
        'esc': Key.esc,
        'f1': Key.f1,
        'f2': Key.f2,
        'f3': Key.f3,
        'f4': Key.f4,
        'f5': Key.f5,
        'f6': Key.f6,
        'f7': Key.f7,
        'f8': Key.f8,
        'f9': Key.f9,
        'f10': Key.f10,
        'f11': Key.f11,
        'f12': Key.f12,
        'home': Key.home,
        'insert': Key.insert,
        'left': Key.left,
        'page_down': Key.page_down,
        'page_up': Key.page_up,
        'right': Key.right,
        'shift': Key.shift,
        'shift_l': Key.shift_l,
        'shift_r': Key.shift_r,
        'space': Key.space,
        'tab': Key.tab,
        'up': Key.up,
        'win': Key.cmd, 
        'windows': Key.cmd 
    }
    return special_keys.get(key_str.lower(), key_str)

class CommandsExecutor:
    def __init__(self, grid_params):
        self.grid_cell_width, self.grid_cell_height, self.grid_cols, self.grid_rows = grid_params

    def update_grid_params(self, grid_params):
        self.grid_cell_width, self.grid_cell_height, self.grid_cols, self.grid_rows = grid_params

    def cell_number_to_coordinates(self, cell_number):
        """Convert a cell number to pixel coordinates (center of the cell)."""
        cell_number -= 1 
        col = cell_number % int(self.grid_cols)
        row = cell_number // int(self.grid_cols)

        x = (col + 0.5) * self.grid_cell_width
        y = (row + 0.5) * self.grid_cell_height

        return x, y

    def execute_commands(self, command_text):
        """Parse and execute commands from a block of text."""
        finished = False
        valid_commands = {'MOVE', 'LEFT_CLICK', 'RIGHT_CLICK', 'DRAG_DROP', 'TYPE', 'KEY_PRESS',
                          'KEY_RELEASE', 'SCREENSHOT', 'WAIT', 'FINISHED', 'MOVE_TO_CELL', 'DRAG_DROP_FROM_CELL'}

        for line in command_text.strip().split('\n'):
            command, args = parse_command(line)

            if command not in valid_commands:
                print(f"Unknown command: {command}")
                continue

            if command == 'MOVE' and len(args) == 2:
                move(*args)
            elif command == 'MOVE_TO_CELL' and len(args) == 1:
                x, y = self.cell_number_to_coordinates(int(args[0]))
                move(x, y)
            elif command == 'LEFT_CLICK':
                left_click()
            elif command == 'RIGHT_CLICK':
                right_click()
            elif command == 'DRAG_DROP' and len(args) == 4:
                drag_drop(*args)
            elif command == 'DRAG_DROP_FROM_CELL' and len(args) == 4 and args[2] == 'TO_CELL':
                x1, y1 = self.cell_number_to_coordinates(int(args[0]))
                x2, y2 = self.cell_number_to_coordinates(int(args[3]))
                drag_drop(x1, y1, x2, y2)
            elif command == 'TYPE':
                text = ' '.join(args)
                type_text(text)
            elif command == 'KEY_PRESS' and len(args) == 1:
                key_press(args[0])
            elif command == 'KEY_RELEASE' and len(args) == 1:
                key_release(args[0])
            elif command == 'WAIT' and len(args) == 1:
                wait(args[0])
            elif command == 'SCREENSHOT':
                screenshot()
            elif command == 'FINISHED':
                finished = True
                print("Task completed.")
        return finished
