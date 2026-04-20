# Project: Color Name Converter (CNC)
# Author: Timothy Kemiki
# Date: 2025/2026
# Description: A real-time live search engine for colors.

import streamlit as st
import csv
import re
from pathlib import Path
from st_keyup import st_keyup  # New import for live keystroke tracking

st.set_page_config(
    page_title="Color Search Engine",
    page_icon="🎨",
    layout="centered"
)

st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        text-align: center;
        color: #FF4B4B;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        text-align: center;
        color: #666;
        margin-bottom: 2rem;
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
        border: 1px solid #ddd;
    }
    .partial-match-preview {
        height: 40px;
        border-radius: 5px;
        border: 1px solid #ccc;
        margin-bottom: 15px;
    }
    .disclaimer {
        background-color: #FF7F50;
        border-left: 4px solid #FCEFEF;
        padding: 0.75rem;
        border-radius: 8px;
        font-size: 0.9rem;
        margin: 1rem 0;
        color: white;
    }
    /* Hide the default st_keyup label for a cleaner look */
    div[data-testid="stKeyup"] label {
        display: none;
    }
</style>
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

def get_rgb(hex_code):
    """Helper to convert hex to RGB tuple."""
    hex_clean = hex_code.lstrip('#')
    return tuple(int(hex_clean[i:i+2], 16) for i in (0, 2, 4))

def display_main_result(title, hex_code):
    """Helper to render the main search result card."""
    st.markdown(f'<div class="result-box">✅ {title}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="color-preview" style="background-color: {hex_code};"></div>', unsafe_allow_html=True)
    st.caption(f"RGB: {get_rgb(hex_code)}")

colors_dict = load_colors()
if not colors_dict:
    st.stop()

# Header
st.markdown('<h1 class="main-header">🎨 Color Search</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Start typing a name (e.g., "Crimson") or hex code (e.g., "#DC143C")</p>', unsafe_allow_html=True)

# ---------------------------------------------------------
# THE LIVE OMNI-SEARCH BAR
# debounce=300 means it waits 300ms after the user stops typing to search (prevents lag)
# ---------------------------------------------------------
query = st_keyup(
    "Search:", 
    placeholder="Type to search colors instantly...", 
    key="live_search", 
    debounce=300
)

# Live processing as the user types
if query:
    query_clean = query.strip()
    
    # 1. Check if the input looks like a hex code (with or without #)
    if re.match(r"^#?[a-fA-F0-9]{1,6}$", query_clean) and any(char.isdigit() for char in query_clean):
        # We treat it as hex if it matches the pattern and contains numbers 
        # (to avoid treating names like "AABB" as hex prematurely)
        hex_query = query_clean if query_clean.startswith('#') else f"#{query_clean}"
        hex_query = hex_query.upper()
        
        # Exact match
        matching_names = [name for name, hx in colors_dict.items() if hx == hex_query]
        
        if matching_names:
            title = f"<strong>{hex_query}</strong> → <strong>{', '.join(matching_names)}</strong>"
            display_main_result(title, hex_query)
            
        # Live Hex Suggestions (e.g., they typed "#FF", show all starting with #FF)
        elif len(hex_query) < 7:
            st.markdown(f"**Suggestions starting with `{hex_query}`:**")
            hex_suggestions = [(name, hx) for name, hx in colors_dict.items() if hx.startswith(hex_query)][:12]
            
            if hex_suggestions:
                cols = st.columns(3)
                for idx, (pm_name, pm_hex) in enumerate(hex_suggestions):
                    with cols[idx % 3]:
                        st.markdown(f"**{pm_name}**<br>`{pm_hex}`", unsafe_allow_html=True)
                        st.markdown(f'<div class="partial-match-preview" style="background-color: {pm_hex};"></div>', unsafe_allow_html=True)
            else:
                st.caption("No matching hex codes found yet.")

    # 2. Treat input as a Color Name
    else:
        search_term = query_clean.title().replace("’", "'")
        search_lower = query_clean.lower()
        
        # Look for an exact match first
        exact_match_hex = colors_dict.get(search_term)
        
        # Look for partial matches (Live suggestions)
        partial_matches = []
        for name, hx in colors_dict.items():
            if search_lower in name.lower() and name != search_term:
                partial_matches.append((name, hx))
        
        # Display logic
        if exact_match_hex:
            title = f"<strong>{search_term}</strong> → <strong>{exact_match_hex}</strong>"
            display_main_result(title, exact_match_hex)
        
        if partial_matches:
            if exact_match_hex:
                st.divider()
                st.subheader("Similar colors:")
            else:
                st.markdown(f"**Suggestions for '{query_clean}':**")
            
            # Limit to 12 partial matches for clean UI
            partial_matches = sorted(partial_matches, key=lambda x: x[0])[:12]
            
            # Display in a grid
            cols = st.columns(3)
            for idx, (pm_name, pm_hex) in enumerate(partial_matches):
                with cols[idx % 3]:
                    st.markdown(f"**{pm_name}**<br>`{pm_hex}`", unsafe_allow_html=True)
                    st.markdown(f'<div class="partial-match-preview" style="background-color: {pm_hex};"></div>', unsafe_allow_html=True)

        if not exact_match_hex and not partial_matches:
            st.error(f"❌ No colors found matching '{query_clean}'.")

# Sidebar
with st.sidebar:
    st.header("ℹ️ ABOUT")
    st.markdown("""
    This search engine seamlessly finds colors by their **name** or **hexadecimal code** in real-time.
    
    **Try typing:**
    - `Red`
    - `Bl` (Watch the suggestions appear!)
    - `#FF`
    """)
    st.markdown("""
    <div class="disclaimer">
    📌 <strong>NOTE:</strong> Uses a limited color database.
    </div>
    """, unsafe_allow_html=True)
    
    if colors_dict:
        import random
        st.header("🎲 Random Discovery")
        if st.button("I'm Feeling Lucky"):
            random_name = random.choice(list(colors_dict.keys()))
            random_code = colors_dict[random_name]
            st.markdown(f"**{random_name}** → `{random_code}`")
            st.markdown(f'<div style="background-color:{random_code}; height:50px; border-radius:5px; border: 1px solid #ccc;"></div>', unsafe_allow_html=True)
