def parse_command(line):
    """Parse a single line command."""
    tokens = line.strip().split()
    if not tokens:
        return None, None

    command = tokens[0].upper()
    args = tokens[1:]
    return command, args
