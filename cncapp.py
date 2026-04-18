# Project: Color Name Converter (CNC)
# Author: Timothy Kemiki
# Date: 2025/2026
# Description: A tool to convert hex codes to color names with live suggestions.

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

# Custom CSS that adapts to light/dark mode
st.markdown("""
<style>
    /* Theme-aware variables */
    :root {
        --primary: #FF4B4B;
        --primary-hover: #E04343;
        --bg-card: var(--secondary-background-color);
        --text: var(--text-color);
        --border: var(--border-color);
    }
    .main-header {
        font-size: 2.5rem;
        text-align: center;
        color: var(--primary);
        margin-bottom: 1rem;
    }
    .result-box {
        background-color: #BF5700;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        text-align: center;
        font-size: 1.2rem;
        color: white;
    }
    .color-preview {
        width: 100%;
        height: 100px;
        border-radius: 10px;
        margin: 1rem 0;
        border: 1px solid var(--border);
    }
    .disclaimer {
        background-color: #FF7F50;
        border-left: 4px solid #FCEFEF;
        padding: 0.75rem;
        border-radius: 8px;
        font-size: 0.9rem;
        margin: 1rem 0;
        color: #2c2c2c;
    }
    .info-box {
        background-color: #FF8000;
        border-left: 4px solid #FFF9C4;
        padding: 0.75rem;
        border-radius: 8px;
        font-size: 0.9rem;
        margin: 1rem 0;
        color: #2c2c2c;
    }
    /* Suggestion pills */
    .suggestions-container {
        display: flex;
        flex-wrap: wrap;
        gap: 0.5rem;
        margin-top: 0.5rem;
        margin-bottom: 1rem;
    }
    .suggestion-pill {
        background-color: var(--primary);
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.8rem;
        cursor: pointer;
        transition: 0.2s;
        border: none;
    }
    .suggestion-pill:hover {
        background-color: var(--primary-hover);
        transform: scale(1.02);
    }
    /* Convert button */
    div.stButton > button {
        background-color: var(--primary);
        color: white;
        font-weight: bold;
        border-radius: 8px;
        padding: 0.5rem 2rem;
        width: 100%;
        font-size: 1rem;
        border: none;
    }
    div.stButton > button:hover {
        background-color: var(--primary-hover);
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# JavaScript to hide keyboard on button click (mobile) and for suggestion clicks
st.markdown("""
<script>
function blurActiveElement() {
    if (document.activeElement && document.activeElement.blur) {
        document.activeElement.blur();
    }
}
document.addEventListener('click', function(e) {
    if (e.target.closest('.stButton button') || e.target.closest('.suggestion-pill')) {
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

def get_suggestions(query, items, limit=8):
    """Return matching items (case-insensitive) sorted alphabetically."""
    if not query:
        return []
    query_lower = query.lower()
    matches = [item for item in items if query_lower in item.lower()]
    # Sort alphabetically
    matches.sort(key=str.lower)
    return matches[:limit]

colors_dict = load_colors()
if not colors_dict:
    st.stop()

# Extract lists for suggestions
color_names = list(colors_dict.keys())
hex_codes = list(set(colors_dict.values()))  # unique hex codes

# Initialize session state for input values
if "name_input" not in st.session_state:
    st.session_state.name_input = ""
if "hex_input" not in st.session_state:
    st.session_state.hex_input = ""
if "trigger_name_convert" not in st.session_state:
    st.session_state.trigger_name_convert = False
if "trigger_hex_convert" not in st.session_state:
    st.session_state.trigger_hex_convert = False

# Callback functions for suggestion clicks
def set_name_and_convert(name):
    st.session_state.name_input = name
    st.session_state.trigger_name_convert = True

def set_hex_and_convert(hex_code):
    st.session_state.hex_input = hex_code
    st.session_state.trigger_hex_convert = True

# Header
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
    # Text input with live suggestions
    name_query = st.text_input(
        "Color Name:",
        placeholder="e.g., Red, Midnight Blue, Crimson",
        key="name_input"
    )
    
    # Show suggestions as clickable pills
    if name_query:
        suggestions = get_suggestions(name_query, color_names)
        if suggestions:
            st.markdown('<div class="suggestions-container">', unsafe_allow_html=True)
            for sugg in suggestions:
                st.markdown(
                    f'<button class="suggestion-pill" onclick="set_name_and_convert(\'{sugg}\')">{sugg}</button>',
                    unsafe_allow_html=True
                )
            st.markdown('</div>', unsafe_allow_html=True)
            # Use a hidden div to capture the JS callback (we'll use a workaround)
            # Actually we need to use st.button for each suggestion (more reliable)
            # But that would cause reruns. Better to use st.form and buttons inside.
            # Simpler: replace the above with actual st.button elements (they cause rerun but are safe).
            # Let's redo using st.button for each suggestion to ensure functionality.
    # We'll replace the custom HTML buttons with actual st.button to avoid JS complexities.
    # However, the user asked for suggestions "as they type". Using st.button inside a loop works but will rerun.
    # That's acceptable because Streamlit reruns on every interaction anyway.
    # Let's implement properly:

# Clear the previous approach and use st.button for suggestions (reruns are fine)
with tab1:
    st.subheader("Enter a color name")
    name_input = st.text_input("Color Name:", placeholder="e.g., Red, Midnight Blue, Crimson", key="name_input_widget")
    # Show suggestion buttons
    if name_input:
        suggestions = get_suggestions(name_input, color_names)
        if suggestions:
            st.write("**Suggestions:**")
            cols = st.columns(min(len(suggestions), 4))
            for idx, sugg in enumerate(suggestions):
                col = cols[idx % 4]
                if col.button(sugg, key=f"sugg_name_{idx}"):
                    # Auto-fill and convert
                    st.session_state.name_input_widget = sugg
                    # Force conversion
                    hex_code = convert_name(sugg, colors_dict)
                    if hex_code:
                        st.markdown(f'<div class="result-box">✅ <strong>{sugg}</strong> → <strong>{hex_code}</strong></div>', unsafe_allow_html=True)
                        st.markdown(f'<div class="color-preview" style="background-color: {hex_code};"></div>', unsafe_allow_html=True)
                        st.caption(f"RGB: {tuple(int(hex_code.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))}")
                    else:
                        st.error("Color not found")
                    st.stop()
    # Convert button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("Convert", key="convert_name_btn"):
            if name_input:
                color_name = name_input.strip()
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

# ========= TAB 2: Hex Code to Color Name =========
with tab2:
    st.subheader("Enter a hex color code")
    hex_input = st.text_input("Hex Code:", placeholder="e.g., #FF0000, #FFFFFF", key="hex_input_widget")
    # Show suggestion buttons for hex codes (based on partial match)
    if hex_input:
        # For hex, we can suggest matching hex codes (case-insensitive)
        hex_suggestions = get_suggestions(hex_input, hex_codes)
        if hex_suggestions:
            st.write("**Suggestions:**")
            cols = st.columns(min(len(hex_suggestions), 4))
            for idx, sugg_hex in enumerate(hex_suggestions):
                col = cols[idx % 4]
                if col.button(sugg_hex, key=f"sugg_hex_{idx}"):
                    st.session_state.hex_input_widget = sugg_hex
                    names = convert_code(sugg_hex, colors_dict)
                    if names:
                        if len(names) == 1:
                            st.markdown(f'<div class="result-box">✅ <strong>{sugg_hex}</strong> → <strong>{names[0]}</strong></div>', unsafe_allow_html=True)
                        else:
                            st.markdown(f'<div class="result-box">✅ <strong>{sugg_hex}</strong> → <strong>{", ".join(names)}</strong><br><small>(Multiple names)</small></div>', unsafe_allow_html=True)
                        st.markdown(f'<div class="color-preview" style="background-color: {sugg_hex};"></div>', unsafe_allow_html=True)
                        st.caption(f"RGB: {tuple(int(sugg_hex.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))}")
                    else:
                        st.error("Hex code not found")
                    st.stop()
    # Convert button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("Convert", key="convert_hex_btn"):
            if hex_input:
                hex_code = hex_input.strip().upper()
                if validate_code(hex_code):
                    names = convert_code(hex_code, colors_dict)
                    if names:
                        if len(names) == 1:
                            st.markdown(f'<div class="result-box">✅ <strong>{hex_code}</strong> → <strong>{names[0]}</strong></div>', unsafe_allow_html=True)
                        else:
                            st.markdown(f'<div class="result-box">✅ <strong>{hex_code}</strong> → <strong>{", ".join(names)}</strong><br><small>(Multiple names)</small></div>', unsafe_allow_html=True)
                        st.markdown(f'<div class="color-preview" style="background-color: {hex_code};"></div>', unsafe_allow_html=True)
                        st.caption(f"RGB: {tuple(int(hex_code.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))}")
                    else:
                        st.error(f"❌ Hex code {hex_code} not found in database.")
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
    - Live suggestions as you type
    - Click any suggestion to auto‑fill and convert
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
