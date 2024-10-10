def parse_command(response):
    """Extract a single cell number from the API's response."""
    import re
    
    # Look for phrases like 'cell 5' or 'cell number 5'
    match = re.search(r'cell(?:\s*number)?\s*(\d+)', response, re.IGNORECASE)
    
    if match:
        return int(match.group(1))  # Return the extracted cell number as an integer
    else:
        # If no cell is mentioned, return None to handle it in the main loop
        return None
