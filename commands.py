from pynput.mouse import Controller as MouseController, Button
from pynput.keyboard import Controller as KeyboardController, Key
from PIL import ImageGrab
import time
from parser import parse_command
import ctypes

mouse = MouseController()
keyboard = KeyboardController()

def get_screen_size():
    """Get the actual screen size, accounting for any display scaling."""
    user32 = ctypes.windll.user32
    # Make the process DPI aware
    user32.SetProcessDPIAware()
    screen_width = user32.GetSystemMetrics(0)
    screen_height = user32.GetSystemMetrics(1)
    return screen_width, screen_height

def move(x, y):
    """Move the mouse to the specified coordinates."""
    x = float(x)
    y = float(y)

    # Get screen size
    screen_width, screen_height = get_screen_size()

    # Ensure coordinates are within screen bounds
    x = max(0, min(x, screen_width - 1))
    y = max(0, min(y, screen_height - 1))

    print(f"Moving mouse to ({x}, {y})")
    mouse.position = (int(x), int(y))

def left_click():
    """Perform a left mouse click."""
    print("Performing left click.")
    mouse.click(Button.left, 1)

def right_click():
    """Perform a right mouse click."""
    print("Performing right click.")
    mouse.click(Button.right, 1)

def drag_drop(x1, y1, x2, y2):
    """Drag from (x1, y1) to (x2, y2)."""
    print(f"Dragging from ({x1}, {y1}) to ({x2}, {y2})")
    move(x1, y1)
    mouse.press(Button.left)
    time.sleep(0.1)
    move(x2, y2)
    time.sleep(0.1)
    mouse.release(Button.left)

def type_text(text, delay=0.02):
    """Type the given text with a slight delay between each character."""
    print(f"Typing text: {text}")
    for char in text:
        time.sleep(delay)
        keyboard.press(char)
        keyboard.release(char)

def key_press(key):
    """Press a keyboard key."""
    key = get_key(key)
    print(f"Pressing key: {key}")
    keyboard.press(key)

def key_release(key):
    """Release a keyboard key."""
    key = get_key(key)
    print(f"Releasing key: {key}")
    keyboard.release(key)

def screenshot(filename='screenshot.png'):
    """Take a screenshot and save it."""
    print(f"Taking screenshot and saving to {filename}")
    image = ImageGrab.grab()
    image.save(filename)

def wait(milliseconds):
    """Pause execution for a specified number of milliseconds."""
    print(f"Waiting for {milliseconds} milliseconds")
    time.sleep(float(milliseconds) / 1000.0)

def get_key(key_str):
    """Convert string to pynput Key object if necessary."""
    special_keys = {
        'enter': Key.enter,
        'return': Key.enter,
        'space': Key.space,
        'backspace': Key.backspace,
        'tab': Key.tab,
        'esc': Key.esc,
        'escape': Key.esc,
        'shift': Key.shift,
        'ctrl': Key.ctrl,
        'alt': Key.alt,
        'cmd': Key.cmd,
        'windows': Key.cmd,
        'left': Key.left,
        'right': Key.right,
        'up': Key.up,
        'down': Key.down,
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
        'end': Key.end,
        'page_up': Key.page_up,
        'page_down': Key.page_down,
        'insert': Key.insert,
        'delete': Key.delete,
        'win': Key.cmd,
    }
    key = special_keys.get(key_str.lower())
    if key:
        return key
    elif len(key_str) == 1:
        return key_str.lower()
    else:
        raise ValueError(f"Unknown key: {key_str}")

class CommandsExecutor:
    def __init__(self, coarse_grid_params, fine_grid_params, x_offset, y_offset, screen_width, screen_height):
        self.coarse_grid_params = coarse_grid_params
        self.fine_grid_params = fine_grid_params
        self.x_offset = x_offset
        self.y_offset = y_offset
        self.screen_width = screen_width
        self.screen_height = screen_height

    def execute_commands(self, command_text, fine_cell_number):
        """Parse and execute commands from a block of text."""
        finished = False
        valid_commands = {
            'MOVE': move,
            'LEFT_CLICK': left_click,
            'RIGHT_CLICK': right_click,
            'DRAG_DROP': drag_drop,
            'TYPE': type_text,
            'KEY_PRESS': key_press,
            'KEY_RELEASE': key_release,
            'WAIT': wait,
            'FINISHED': lambda: None,
            'MOUSE_MOVE': move,
            'MOUSE_CLICK': left_click
        }

        for line in command_text.strip().split('\n'):
            if not line.strip():
                continue
            command, args = parse_command(line)

            command = command.strip().upper()
            print(f"Executing command: '{command}' with args: {args}")

            if command not in valid_commands:
                print(f"Unknown command: {command}")
                continue

            func = valid_commands[command]

            try:
                if command in ['MOVE', 'MOUSE_MOVE']:
                    if len(args) == 2:
                        func(args[0], args[1])
                    else:
                        print(f"Invalid arguments for {command}")
                elif command in ['LEFT_CLICK', 'MOUSE_CLICK']:
                    func()
                elif command == 'RIGHT_CLICK':
                    func()
                elif command == 'DRAG_DROP':
                    if len(args) == 4:
                        func(args[0], args[1], args[2], args[3])
                    else:
                        print(f"Invalid arguments for {command}")
                elif command == 'TYPE':
                    text = ' '.join(args)
                    func(text)
                elif command == 'KEY_PRESS':
                    if len(args) == 1:
                        func(args[0])
                    else:
                        print(f"Invalid arguments for {command}")
                elif command == 'KEY_RELEASE':
                    if len(args) == 1:
                        func(args[0])
                    else:
                        print(f"Invalid arguments for {command}")
                elif command == 'WAIT':
                    if len(args) == 1:
                        func(args[0])
                    else:
                        print(f"Invalid arguments for {command}")
                elif command == 'FINISHED':
                    finished = True
            except Exception as e:
                print(f"Error executing command '{command}': {e}")

        return finished
