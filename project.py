# Project: Colour Name Converter (CNC)
# Author: Timothy Kemiki
# Date: 2024/2025
# Description: A code that convert colour names to hex codes.


import csv
import re



def load_colours(filename):
    # Empty Dict to store colour names and code
    colours_dict = {}
    # Open 'filename' in read-mode(r)
    with open(filename, mode="r") as file:
        # Read each row in CSV file as a dictionary
        reader = csv.DictReader(file)
        # Iterate through the rows
        for row in reader:
            # Add name and code as key-value pairs to empty dict 'colours_dict'
            colours_dict[row["name"]] = row["code"]
    # Return 'colours_dict' now containing key-value pairs of names and code of each colour
    return colours_dict

    
def main():
    # Pass CSV file as input to load function
    colours_dict = load_colours("colors.csv")
    # Get input from user
    colour = input("Colour: ").strip()
    # If user inputs colour code
    if colour.startswith("#"):
        # Convert user's input to uppercase
        colour = colour.upper()
        # If return value is True
        if validate_code(colour):
             cc = convert_code(colour, colours_dict)
             if cc:
                 # Handles where multiple keys have same value
                 print("Colour Name:", ", ".join(cc))
             else:
                 print("Colour code not found")
        # If return value is False
        else:
            print("Invalid colour code")
    # If user inputs colour name
    else:
        # Convert input to title case
        colour = colour.title()
        # Replace "’" with "'"
        colour = colour.replace("’", "'")
        # If return value is True
        if validate_name(colour):
             cn = convert_name(colour, colours_dict)
             if cn:
                 print("Colour Code:", cn)
             else:
                 print("Colour name not found")
        # If return value is False
        else:
            print("Invalid colour name")


# Validate user's code input
def validate_code(valid):
    # Give a pattern that you expect as input
    pattern = r"^#[a-fA-F0-9]{6}$"
    match = re.search(pattern, valid, re.IGNORECASE)
    if match:
        return True
    else:
        return False

# Convert colour code to colour name
def convert_code(code, colours_dict):
    # Create an Empty list
    names = []
    # Iterate through the dictionary items(both keys and values)
    for name, hex_code in colours_dict.items():
        # Check if the value matches the input colour code.
        if hex_code == code:
            names.append(name)
    if names:
        # Return names[] with matching colour names
        return names
    # If no matches found in names[]
    return None


# Validate user's colour name
def validate_name(valid):
    pattern = r"[a-zA-Z\s'’]+"
    # match only when the entire input is a string of letters
    match = re.fullmatch(pattern, valid, re.IGNORECASE)
    if match:
        return True
    else:
        return False

# Convert colour name to colour code
def convert_name(name, colours_dict):
    if name in colours_dict:
        return colours_dict[name]
    # If colour name is not in the dictionary
    return None




if __name__ == "__main__":
    main()
