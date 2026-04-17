import csv
import re



def load_colors(filename):
    # Empty Dict to store color names and code
    colors_dict = {}
    # Open 'filename' in read-mode(r)
    with open(filename, mode="r") as file:
        # Read each row in CSV file as a dictionary
        reader = csv.DictReader(file)
        # Iterate through the rows
        for row in reader:
            # Add name and code as key-value pairs to empty dict 'colors_dict'
            colors_dict[row["name"]] = row["code"]
    # Return 'colors_dict' now containing key-value pairs of names and code of each color
    return colors_dict

    
def main():
    # Pass CSV file as input to load function
    colors_dict = load_colors("colors.csv")
    # Get input from user
    color = input("Color: ").strip()
    # If user inputs color code
    if color.startswith("#"):
        # Convert user's input to uppercase
        color = color.upper()
        # If return value is True
        if validate_code(color):
             cc = convert_code(color, colors_dict)
             if cc:
                 # Handles where multiple keys have same value
                 print("Color Name:", ", ".join(cc))
             else:
                 print("Color code not found")
        # If return value is False
        else:
            print("Invalid color code")
    # If user inputs color name
    else:
        # Convert input to title case
        color = color.title()
        # Replace "’" with "'"
        color = color.replace("’", "'")
        # If return value is True
        if validate_name(color):
             cn = convert_name(color, colors_dict)
             if cn:
                 print("Color Code:", cn)
             else:
                 print("Color name not found")
        # If return value is False
        else:
            print("Invalid color name")


# Validate user's code input
def validate_code(valid):
    # Give a pattern that you expect as input
    pattern = r"^#[a-fA-F0-9]{6}$"
    match = re.search(pattern, valid, re.IGNORECASE)
    if match:
        return True
    else:
        return False

# Convert color code to color name
def convert_code(code, colors_dict):
    # Create an Empty list
    names = []
    # Iterate through the dictionary items(both keys and values)
    for name, hex_code in colors_dict.items():
        # Check if the value matches the input color code.
        if hex_code == code:
            names.append(name)
    if names:
        # Return names[] with matching color names
        return names
    # If no matches found in names[]
    return None


# Validate user's color name
def validate_name(valid):
    pattern = r"[a-zA-Z\s'’]+"
    # match only when the entire input is a string of letters
    match = re.fullmatch(pattern, valid, re.IGNORECASE)
    if match:
        return True
    else:
        return False

# Convert color name to color code
def convert_name(name, colors_dict):
    if name in colors_dict:
        return colors_dict[name]
    # If color name is not in the dictionary
    return None




if __name__ == "__main__":
    main()
