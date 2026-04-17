# 🎨 Color Name Converter (CNC)

> A Python tool and Web Application that converts standard hex codes into color names vice versa, using a comprehensive CSV database.

📹 **Video Demo:** [Watch on YouTube](https://www.youtube.com/shorts/0B-R-BhlIv0)

## 📖 Description

The CNC (Color Name Converter) is a program designed to bridge the gap between technical hex codes and human-readable color names. It provides two interfaces: a command-line script and a modern Streamlit web application.
This project provides two ways to use the converter:

1.  **Command Line Interface (CLI):** A terminal-based version (`project.py`).
2.  **Web Application:** A modern interface built with **Streamlit** (`cncapp.py`) for browser-based interaction.

**Key Features:**
* **Hex to Name:** Input a hex code (e.g., `#FFFFFF`) to get its name (`White`).
* **Name to Hex:** Input a name (e.g., `white`) to get its hex code (`#FFFFFF`).
* **Multi-Name Support:** If a single hex code corresponds to multiple names in the database, the program returns all of them.
* **Robust Validation:** Uses regular expressions to ensure inputs are formatted correctly before processing.
  
The program uses a CSV file named `colors.csv` containing over 1,000 colors. If an input is not found in the database, the CNC informs the user. If the input format is incorrect, the program identifies it as an invalid name or code.


### 🌐 Web Application Features

The Streamlit app (`cncapp.py`) adds several user-friendly features:

  * **Real-time Color Preview:** Displays a visual block of the color being searched.
  * **RGB Conversion:** Automatically calculates and shows the RGB values alongside the hex code.
  * **Interactive Sidebar:** Includes mode selection (Code to Name or Name to Code) and a "Random Color" generator for discovery.
  * **Optimized Performance:** Uses `@st.cache_data` to ensure the color database loads instantly after the first use.

### 📚 Data Sources

**Main Source:** [The Colors Meaning](https://thecolorsmeaning.com/)
**Other sources:** [ColorXS](https://www.colorxs.com/), [ColorHexa](https://www.colorhexa.com/), [Color-Name](https://color-name.com/), [Vista Create](https://create.vista.com/), [HexColor](https://hexcolor.co/), [ArtyClick](https://colors.artyclick.com/), [Color Designer](https://colordesigner.io/)

-----

## 🛠️ Project Structure

The project consists of the following files:

  * `project.py`: The core logic and CLI implementation.
  * `cncapp.py`: The Streamlit web application.
  * `colors.csv`: The database of names and hex codes.
  * `test_project.py`: The test suite for verifying the logic.
  * `requirements.txt`: List of dependencies (Streamlit).

### 🚀 How to Run

**For the Terminal version:**

```bash
python project.py
```

**For the Web App:**

```bash
pip install streamlit
streamlit run cncapp.py
```

-----

## 🔍 Detailed Code Breakdown (`project.py` & `cncapp.py`)

### 1\. `load_colors(filename)`

This function reads the `colors.csv` and loads it into a dictionary.

  * `colors_dict = {}`: Initializes an empty dictionary.
  * `with open(filename, mode="r") as file:`: Opens the file safely.
  * `reader = csv.DictReader(file)`: Reads each row as a dictionary.
  * The function returns `colors_dict` with color names as keys and hex codes as values.

### 2\. `main()` (in `project.py`)

Handles the CLI flow. It loads the database, takes user input, and determines if the user provided a hex code (starting with `#`) or a name, then routes the data to the appropriate conversion function.

### 3\. `validate_code(valid)`

Ensures the input follows the standard hex format.

  * **Pattern:** `^#[a-fA-F0-9]{6}$`
  * Requires a `#` followed by exactly six hexadecimal characters.

### 4\. `convert_code(code, colors_dict)`

Searches the dictionary for a specific hex code.

  * It iterates through the dictionary and appends all matching names to a list. This handles cases where one hex code has multiple names in the CSV.

### 5\. `validate_name(name)`

Ensures a color name contains only allowed characters.

  * **Pattern:** `[a-zA-Z\s'’]+`
  * Allows letters, spaces, and both straight and curly apostrophes.

### 6\. `convert_name(name, colors_dict)`

Performs a direct lookup. If the name exists as a key in the dictionary, it returns the associated hex code.

### 💡 Special Logic: The Apostrophe Challenge

The program includes `color.replace("’", "'")`. This is crucial because users might type names using curly apostrophes (common on mobile or Mac), while the CSV uses straight apostrophes. This normalization ensures the search doesn't fail due to punctuation style.

-----

## 🧪 Testing (`test_project.py`)

The project uses `pytest` to ensure all core functions work reliably.

  * **`test_load_colors`**: Confirms the CSV loads and correctly maps "Yellow" to `#FFFF00`.
  * **`test_validate_code`**: Ensures valid codes (like `#FFFFFF`) pass and invalid ones (like `#GGGGGG`) fail.
  * **`test_convert_code`**: Verifies that hex codes are successfully mapped back to their names using a dictionary.
  * **`test_validate_name`**: Confirms names like "Red" or "BLUE" are accepted, while names with numbers are rejected.
  * **`test_convert_name`**: Verifies that names are successfully mapped to their hex codes.
