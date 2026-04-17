# Project: Color Name Converter (CNC)
# Author: Timothy Kemiki
# Date: 2025/2026
# Description: A tool to convert hex codes to color names.

import streamlit as st
import csv
import re
from pathlib import Path

# Set page config
st.set_page_config(
    page_title="Color Name Converter",
    page_icon="🎨",
    layout="centered"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        text-align: center;
        color: #FF4B4B;
        margin-bottom: 1rem;
    }
    .result-box {
        background-color: #8D818C;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        text-align: center;
        font-size: 1.2rem;
    }
    .color-preview {
        width: 100%;
        height: 100px;
        border-radius: 10px;
        margin: 1rem 0;
        border: 1px solid #ddd;
    }
    .disclaimer {
        background-color: #FF7F50;
        border-left: 4px solid #FCEFEF;
        padding: 0.75rem;
        border-radius: 8px;
        font-size: 0.9rem;
        margin: 1rem 0;
    }
    .info-box {
        background-color: #2196F3;
        border-left: 4px solid #E8F4FD;
        padding: 0.75rem;
        border-radius: 8px;
        font-size: 0.9rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Cache the loading of colors.csv for performance
@st.cache_data
def load_colors(filename="colors.csv"):
    """Load colors from CSV into a dictionary."""
    colors_dict = {}
    # Check if file exists
    if not Path(filename).exists():
        st.error(f"File '{filename}' not found. Please make sure it's in the same directory.")
        return {}
    with open(filename, mode="r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            colors_dict[row["name"]] = row["code"]
    return colors_dict

def validate_code(code):
    """Validate hex color code format."""
    pattern = r"^#[a-fA-F0-9]{6}$"
    return bool(re.search(pattern, code, re.IGNORECASE))

def convert_code(code, colors_dict):
    """Convert hex code to color name(s)."""
    code = code.upper()
    names = [name for name, hex_code in colors_dict.items() if hex_code == code]
    return names if names else None

def validate_name(name):
    """Validate color name (only letters, spaces, apostrophes)."""
    pattern = r"^[a-zA-Z\s'’]+$"
    return bool(re.fullmatch(pattern, name, re.IGNORECASE))

def convert_name(name, colors_dict):
    """Convert color name to hex code."""
    # Normalize apostrophes and title case
    name = name.title().replace("’", "'")
    return colors_dict.get(name)

# Load the color dictionary
colors_dict = load_colors()
if not colors_dict:
    st.stop()

# Header
st.markdown('<h1 class="main-header">🎨 Color Name Converter</h1>', unsafe_allow_html=True)
st.markdown("Convert between color names and their hexadecimal codes.")

# === DISCLAIMER (subtle but noticeable) ===
st.markdown("""
<div class="disclaimer">
📌 <strong>Note:</strong> This database contains over 1000 color names and hex codes, but it is not exhaustive. 
If you search for a color name or hex code that isn't in our list, you'll see a "not found" message — this is expected and not an error.
</div>
""", unsafe_allow_html=True)

# Create two tabs for different input methods
tab1, tab2 = st.tabs(["🔍 Color Name → Hex Code", "🔢 Hex Code → Color Name"])

with tab1:
    st.subheader("Enter a color name")
    color_name = st.text_input("Color name:", placeholder="e.g., Red, Midnight Blue, Crimson")
    
    if color_name:
        color_name = color_name.strip()
        if validate_name(color_name):
            hex_code = convert_name(color_name, colors_dict)
            if hex_code:
                st.markdown(f'<div class="result-box">✅ <strong>{color_name.title()}</strong> → <strong>{hex_code}</strong></div>', unsafe_allow_html=True)
                # Show color preview
                st.markdown(f'<div class="color-preview" style="background-color: {hex_code};"></div>', unsafe_allow_html=True)
                st.caption(f"RGB: {tuple(int(hex_code.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))}")
            else:
                st.error(f"❌ Color name '{color_name}' not found in database. Try another name (database covers many but not all colors).")
        else:
            st.error("❌ Invalid color name. Use only letters, spaces, and apostrophes.")

with tab2:
    st.subheader("Enter a hex color code")
    hex_input = st.text_input("Hex code:", placeholder="e.g., #FF0000, #FFFFFF, #663399")
    
    if hex_input:
        hex_input = hex_input.strip().upper()
        if validate_code(hex_input):
            names = convert_code(hex_input, colors_dict)
            if names:
                if len(names) == 1:
                    st.markdown(f'<div class="result-box">✅ <strong>{hex_input}</strong> → <strong>{names[0]}</strong></div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="result-box">✅ <strong>{hex_input}</strong> → <strong>{", ".join(names)}</strong><br><small>(Multiple names exist for this code)</small></div>', unsafe_allow_html=True)
                # Show color preview
                st.markdown(f'<div class="color-preview" style="background-color: {hex_input};"></div>', unsafe_allow_html=True)
                st.caption(f"RGB: {tuple(int(hex_input.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))}")
            else:
                st.error(f"❌ Hex code {hex_input} not found in database. Try another code (database covers many but not all hex codes).")
        else:
            st.error("❌ Invalid hex code. Format: # followed by exactly 6 hex digits (0-9, A-F).")

# Sidebar with additional info
with st.sidebar:
    st.header("ℹ️ About")
    st.markdown("""
    This app converts between **color names** and **hexadecimal codes** using a database of over 1000 colors.
    
    **Features:**
    - Case‑insensitive input
    - Supports multiple names for the same hex code
    - Real‑time color preview
    - RGB values shown
    
    **Examples:**
    - `Red` → `#FF0000`
    - `#FFFFFF` → `White`
    - `#E32636` → `Alizarin Crimson`
    """)
    
    # Repeat disclaimer in sidebar for emphasis
    st.markdown("""
    <div class="info-box">
    📚 <strong>Database coverage:</strong> This tool includes over 1000 common colors, but it is not a complete dictionary of all existing color names or hex codes. If your search returns "not found", it simply means that exact color is not in our list — not that the app is broken.
    </div>
    """, unsafe_allow_html=True)
    
    st.header("📁 Files Required")
    st.markdown("Make sure `colors.csv` is in the same directory as this app.")
    
    # Optional: show a few random colors
    if colors_dict:
        import random
        st.header("🎲 Random Color")
        if st.button("Pick a random color"):
            random_name = random.choice(list(colors_dict.keys()))
            random_code = colors_dict[random_name]
            st.markdown(f"**{random_name}** → `{random_code}`")
            st.markdown(f'<div style="background-color:{random_code}; height:50px; border-radius:5px;"></div>', unsafe_allow_html=True)
