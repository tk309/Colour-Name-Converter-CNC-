# Project: Color Name Converter (CNC)
# Author: Timothy Kemiki
# Date: 2025/2026
# Description: A tool to convert hex codes to color names.

import streamlit as st
import csv
import re
from pathlib import Path

st.set_page_config(
    page_title="Color Name Converter",
    page_icon="🎨",
    layout="centered"
)

st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        text-align: center;
        color: #FF4B4B;
        margin-bottom: 1rem;
    }
    .result-box {
        background-color: #40E0D0;
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
        background-color: #40E0D0;
        border-left: 4px solid #FCEFEF;
        padding: 0.75rem;
        border-radius: 8px;
        font-size: 0.9rem;
        margin: 1rem 0;
    }
    .info-box {
        background-color: #40E0D0;
        border-left: 4px solid #FFF9C4;
        padding: 0.75rem;
        border-radius: 8px;
        font-size: 0.9rem;
        margin: 1rem 0;
    }
    div.stButton > button {
        background-color: #40E0D0;
        color: white;
        font-weight: bold;
        border-radius: 8px;
        padding: 0.5rem 2rem;
        width: 100%;
        font-size: 1rem;
        border: none;
    }
    div.stButton > button:hover {
        background-color: #E04343;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# JavaScript to hide keyboard on button click (mobile)
st.markdown("""
<script>
function blurActiveElement() {
    if (document.activeElement && document.activeElement.blur) {
        document.activeElement.blur();
    }
}
document.addEventListener('click', function(e) {
    if (e.target.closest('.stButton button')) {
        setTimeout(blurActiveElement, 50);
    }
});
</script>
""", unsafe_allow_html=True)

@st.cache_data
def load_colors(filename="colors.csv"):
    colors_dict = {}
    if not Path(filename).exists():
        st.error(f"File '{filename}' not found.")
        return {}
    with open(filename, mode="r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            colors_dict[row["name"]] = row["code"]
    return colors_dict

def validate_code(code):
    pattern = r"^#[a-fA-F0-9]{6}$"
    return bool(re.search(pattern, code, re.IGNORECASE))

def convert_code(code, colors_dict):
    code = code.upper()
    return [name for name, hex_code in colors_dict.items() if hex_code == code] or None

def validate_name(name):
    pattern = r"^[a-zA-Z\s'’]+$"
    return bool(re.fullmatch(pattern, name, re.IGNORECASE))

def convert_name(name, colors_dict):
    name = name.title().replace("’", "'")
    return colors_dict.get(name)

colors_dict = load_colors()
if not colors_dict:
    st.stop()

st.markdown('<h1 class="main-header">🎨 Color Name Converter</h1>', unsafe_allow_html=True)
st.markdown("Convert between color names and their hexadecimal codes.")

st.markdown("""
<div class="disclaimer">
📌 <strong>NOTE:</strong> This tool uses a limited color database. Some color names or hex codes may not be available.
</div>
""", unsafe_allow_html=True)

tab1, tab2 = st.tabs(["🔍 Color Name → Hex Code", "🔢 Hex Code → Color Name"])

# ========= TAB 1: Color Name to Hex =========
with tab1:
    st.subheader("Enter a color name")
    with st.form(key="name_form"):
        color_name_input = st.text_input("Color Name:", placeholder="e.g., Red, Midnight Blue, Crimson", key="name_input")
        # Center the button using columns
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            submitted_name = st.form_submit_button("Convert")
        
        if submitted_name:
            if color_name_input:
                color_name = color_name_input.strip()
                if validate_name(color_name):
                    hex_code = convert_name(color_name, colors_dict)
                    if hex_code:
                        st.markdown(f'<div class="result-box">✅ <strong>{color_name.title()}</strong> → <strong>{hex_code}</strong></div>', unsafe_allow_html=True)
                        st.markdown(f'<div class="color-preview" style="background-color: {hex_code};"></div>', unsafe_allow_html=True)
                        st.caption(f"RGB: {tuple(int(hex_code.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))}")
                    else:
                        st.error(f"❌ Color name '{color_name}' not found in database.")
                else:
                    st.error("❌ Invalid color name. Use only letters, spaces, and apostrophes.")
            else:
                st.warning("Please enter a color name.")

# ========= TAB 2: Hex to Color Name =========
with tab2:
    st.subheader("Enter a hex color code")
    with st.form(key="hex_form"):
        hex_input_raw = st.text_input("Hex Code:", placeholder="e.g., #FF0000, #FFFFFF", key="hex_input")
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            submitted_hex = st.form_submit_button("Convert")
        
        if submitted_hex:
            if hex_input_raw:
                hex_input = hex_input_raw.strip().upper()
                if validate_code(hex_input):
                    names = convert_code(hex_input, colors_dict)
                    if names:
                        if len(names) == 1:
                            st.markdown(f'<div class="result-box">✅ <strong>{hex_input}</strong> → <strong>{names[0]}</strong></div>', unsafe_allow_html=True)
                        else:
                            st.markdown(f'<div class="result-box">✅ <strong>{hex_input}</strong> → <strong>{", ".join(names)}</strong><br><small>(Multiple names)</small></div>', unsafe_allow_html=True)
                        st.markdown(f'<div class="color-preview" style="background-color: {hex_input};"></div>', unsafe_allow_html=True)
                        st.caption(f"RGB: {tuple(int(hex_input.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))}")
                    else:
                        st.error(f"❌ Hex code {hex_input} not found in database.")
                else:
                    st.error("❌ Invalid hex code. Format: # followed by exactly 6 hex digits.")
            else:
                st.warning("Please enter a hex code.")

# Sidebar
with st.sidebar:
    st.header("ℹ️ ABOUT")
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
    st.markdown("""
    <div class="info-box">
    📚 <strong>Data Source:</strong> Combined from various color databases.
    </div>
    """, unsafe_allow_html=True)
    
    if colors_dict:
        import random
        st.header("🎲 Random Color")
        if st.button("Pick a random color"):
            random_name = random.choice(list(colors_dict.keys()))
            random_code = colors_dict[random_name]
            st.markdown(f"**{random_name}** → `{random_code}`")
            st.markdown(f'<div style="background-color:{random_code}; height:50px; border-radius:5px;"></div>', unsafe_allow_html=True)
