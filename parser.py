def parse_command(line: str) -> tuple[str, list]:
    """Parse a command line into command and arguments."""
    line = line.strip()
    if not line:
        return "", []

    # Handle commands with colons or special formats
    if ':' in line:
        command_part, args_part = line.split(':', 1)
        command = command_part.strip().upper()
        args = args_part.strip().split()
    else:
        parts = line.split()
        command = parts[0].strip().upper()
        args = parts[1:] if len(parts) > 1 else []

    return command, args
