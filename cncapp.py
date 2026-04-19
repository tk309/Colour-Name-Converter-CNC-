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
        background-color: #BF5700;
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
        background-color: #FF8000;
        border-left: 4px solid #FFF9C4;
        padding: 0.75rem;
        border-radius: 8px;
        font-size: 0.9rem;
        margin: 1rem 0;
    }
    div.stButton > button {
        background-color: #FF4B4B;
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

    /* Suggestion item buttons */
    div[data-testid="stVerticalBlock"] div.suggestion-item > div > button {
        background-color: transparent !important;
        color: inherit !important;
        border: 1px solid #555 !important;
        border-radius: 6px !important;
        font-size: 0.88rem !important;
        font-weight: normal !important;
        padding: 0.3rem 0.75rem !important;
        text-align: left !important;
        margin: 2px 0 !important;
    }
    div[data-testid="stVerticalBlock"] div.suggestion-item > div > button:hover {
        background-color: #3a3a3a !important;
        border-color: #FF8C69 !important;
        color: #FF8C69 !important;
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
    pattern = r"^[a-zA-Z\s'']+$"
    return bool(re.fullmatch(pattern, name, re.IGNORECASE))

def convert_name(name, colors_dict):
    name = name.title().replace("'", "'")
    return colors_dict.get(name)

# ── NEW: Autocomplete suggestion helpers ─────────────────────────────────────

def get_name_suggestions(query, colors_dict, max_results=8):
    """Return color names that start with the query string (case-insensitive)."""
    q = query.strip().lower()
    if not q:
        return []
    matches = [name for name in colors_dict if name.lower().startswith(q)]
    return sorted(matches)[:max_results]

def get_hex_suggestions(query, colors_dict, max_results=8):
    """Return (name, hex_code) pairs whose hex code starts with the query string."""
    q = query.strip().upper()
    if not q.startswith("#"):
        q = "#" + q
    if q == "#":
        return []
    matches = [
        (name, code)
        for name, code in colors_dict.items()
        if code.upper().startswith(q)
    ]
    return sorted(matches, key=lambda x: x[1])[:max_results]

# ─────────────────────────────────────────────────────────────────────────────

# Session state — tracks the confirmed (searched) value for each tab
for key, default in [
    ("color_confirmed", ""),
    ("hex_confirmed", ""),
]:
    if key not in st.session_state:
        st.session_state[key] = default

# ─────────────────────────────────────────────────────────────────────────────

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

    color_input = st.text_input(
        "Color Name:",
        placeholder="e.g., Red, Midnight Blue, Crimson",
        key="color_query"
    )

    # ── Autocomplete suggestions ──────────────────────────────────────
    # Only fires once the user starts typing. Shows names that start
    # with whatever has been typed so far. Clicking any suggestion
    # fills it in as the confirmed search and shows the result.
    if color_input:
        suggestions = get_name_suggestions(color_input, colors_dict)
        # Hide the suggestion list once the input exactly matches the confirmed value
        # (i.e. after a suggestion has been tapped or Convert has been clicked)
        already_confirmed = color_input.strip().lower() == st.session_state.color_confirmed.strip().lower()
        if suggestions and not already_confirmed:
            st.markdown(
                '<p style="font-size:0.8rem; color:#999; margin:4px 0 2px 0;">💡 Suggestions — tap to select</p>',
                unsafe_allow_html=True
            )
            for sug in suggestions:
                st.markdown('<div class="suggestion-item">', unsafe_allow_html=True)
                if st.button(sug, key=f"nsug_{sug}", use_container_width=True):
                    st.session_state.color_confirmed = sug
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)
    # ─────────────────────────────────────────────────────────────────

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("Convert", key="color_convert_btn"):
            if color_input:
                if validate_name(color_input.strip()):
                    st.session_state.color_confirmed = color_input.strip()
                else:
                    st.error("❌ Invalid color name. Use only letters, spaces, and apostrophes.")
            else:
                st.warning("Please enter a color name.")

    # Result — shown after Convert is clicked or a suggestion is tapped
    if st.session_state.color_confirmed:
        confirmed = st.session_state.color_confirmed
        hex_code = convert_name(confirmed, colors_dict)
        if hex_code:
            st.markdown(
                f'<div class="result-box">✅ <strong>{confirmed.title()}</strong> → <strong>{hex_code}</strong></div>',
                unsafe_allow_html=True
            )
            st.markdown(
                f'<div class="color-preview" style="background-color: {hex_code};"></div>',
                unsafe_allow_html=True
            )
            st.caption(f"RGB: {tuple(int(hex_code.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))}")
        else:
            st.error(f"❌ Color name '{confirmed}' not found in database.")

# ========= TAB 2: Hex to Color Name =========
with tab2:
    st.subheader("Enter a hex color code")

    hex_input = st.text_input(
        "Hex Code:",
        placeholder="e.g., #FF0000, #FFFFFF",
        key="hex_query"
    )

    # ── Autocomplete suggestions ──────────────────────────────────────
    # As the user types a partial hex code (e.g. "#FF", "#FF4B"),
    # all hex codes in the database that start with those characters
    # are suggested. Tapping one confirms it and shows the result.
    if hex_input:
        hex_suggestions = get_hex_suggestions(hex_input, colors_dict)
        already_confirmed = hex_input.strip().upper().lstrip("#") == st.session_state.hex_confirmed.strip().upper().lstrip("#")
        if hex_suggestions and not already_confirmed:
            st.markdown(
                '<p style="font-size:0.8rem; color:#999; margin:4px 0 2px 0;">💡 Suggestions — tap to select</p>',
                unsafe_allow_html=True
            )
            for name, code in hex_suggestions:
                label = f"{code}  —  {name}"
                st.markdown('<div class="suggestion-item">', unsafe_allow_html=True)
                if st.button(label, key=f"hsug_{code}", use_container_width=True):
                    st.session_state.hex_confirmed = code
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)
    # ─────────────────────────────────────────────────────────────────

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("Convert", key="hex_convert_btn"):
            if hex_input:
                cleaned = hex_input.strip().upper()
                if not cleaned.startswith("#"):
                    cleaned = "#" + cleaned
                if validate_code(cleaned):
                    st.session_state.hex_confirmed = cleaned
                else:
                    st.error("❌ Invalid hex code. Format: # followed by exactly 6 hex digits.")
            else:
                st.warning("Please enter a hex code.")

    # Result — shown after Convert is clicked or a suggestion is tapped
    if st.session_state.hex_confirmed:
        confirmed_hex = st.session_state.hex_confirmed.upper()
        if not confirmed_hex.startswith("#"):
            confirmed_hex = "#" + confirmed_hex
        names = convert_code(confirmed_hex, colors_dict)
        if names:
            if len(names) == 1:
                st.markdown(
                    f'<div class="result-box">✅ <strong>{confirmed_hex}</strong> → <strong>{names[0]}</strong></div>',
                    unsafe_allow_html=True
                )
            else:
                st.markdown(
                    f'<div class="result-box">✅ <strong>{confirmed_hex}</strong> → <strong>{", ".join(names)}</strong><br><small>(Multiple names)</small></div>',
                    unsafe_allow_html=True
                )
            st.markdown(
                f'<div class="color-preview" style="background-color: {confirmed_hex};"></div>',
                unsafe_allow_html=True
            )
            st.caption(f"RGB: {tuple(int(confirmed_hex.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))}")
        else:
            st.error(f"❌ Hex code {confirmed_hex} not found in database.")

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
