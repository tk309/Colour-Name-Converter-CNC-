from project import validate_code, convert_code, validate_name, convert_name, load_colors


# Test load_colors function
def test_load_colors():
    colors_dict = load_colors("colors.csv")
    assert convert_name("Yellow", colors_dict) == "#FFFF00"

# Test validate_code function
def test_validate_code():
    # Valid color codes
    assert validate_code("#FFFFFF") == True
    assert validate_code("#000000") == True
    # Invalid color codes
    assert validate_code("#GGGGGG") == False
    assert validate_code("123456") == False

# Test convert_code function
def test_convert_code():
    colors_dict = {"Red": "#FF0000", "Green": "#00FF00", "Blue": "#0000FF"}
    # Valid conversions
    assert convert_code("#FF0000", colors_dict) == "Red"
    assert convert_code("#00FF00", colors_dict) == "Green"
    assert convert_code("#0000FF", colors_dict) == "Blue"
    # Invalid conversion
    assert convert_code("#FFFFFg", colors_dict) == None


# Test validate_name function
def test_validate_name():
    # Valid names
    assert validate_name("Red") == True
    assert validate_name("BLUE") == True
    assert validate_name("green") == True
    # Invalid names
    assert validate_name("123Red") == False
    assert validate_name("") == False

# Test convert_name function
def test_convert_name():
    colors_dict = {"Red": "#FF0000", "Green": "#00FF00", "Blue": "#0000FF"}
    # Valid conversions
    assert convert_name("Red", colors_dict) == "#FF0000"
    assert convert_name("Green", colors_dict) == "#00FF00"
    assert convert_name("Blue", colors_dict) == "#0000FF"
    # Invalid conversion
    assert convert_name("", colors_dict) == None
