# Project: Color Name Converter (CNC)
# Author: Timothy Kemiki
# Date: 2025/2026
# Description: A tool to convert hex codes to color names.

import streamlit as st
import csv
import re
from pathlib import Path
from streamlit_searchbox import st_searchbox

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

    /* ── Search engine result cards ── */
    .search-result-card {
        background-color: #1e1e1e;
        border: 1px solid #333;
        border-radius: 10px;
        padding: 0.75rem 1rem;
        margin: 0.5rem 0;
        display: flex;
        align-items: center;
        gap: 1rem;
    }
    .search-result-swatch {
        width: 52px;
        height: 52px;
        border-radius: 8px;
        flex-shrink: 0;
        border: 1px solid #444;
    }
    .search-result-title {
        font-size: 1.05rem;
        font-weight: 700;
        color: #FF8C69;
    }
    .search-result-sub {
        font-size: 0.85rem;
        color: #aaa;
        margin-top: 2px;
    }
    .search-result-badge {
        font-size: 0.75rem;
        background-color: #2e2e2e;
        color: #ccc;
        border: 1px solid #444;
        border-radius: 12px;
        padding: 2px 8px;
        margin-right: 4px;
    }
    .search-stats {
        font-size: 0.8rem;
        color: #888;
        margin: 0.4rem 0 0.75rem 0;
    }
    .no-exact-banner {
        background-color: #2a1a00;
        border-left: 4px solid #FF8C00;
        border-radius: 8px;
        padding: 0.6rem 0.9rem;
        font-size: 0.9rem;
        color: #FFB347;
        margin-bottom: 0.5rem;
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

# ── SEARCH ENGINE HELPERS ────────────────────────────────────────────────────

def hex_to_rgb(hex_code):
    """Convert a hex code string to an (R, G, B) tuple. Returns None if invalid."""
    if not isinstance(hex_code, str):
        return None
    hex_code = hex_code.strip()
    if not hex_code.startswith("#") or len(hex_code) != 7:
        return None
    try:
        h = hex_code.lstrip("#")
        return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))
    except ValueError:
        return None

def color_distance(hex1, hex2):
    """Euclidean distance between two hex colors in RGB space.
    Returns a very large number if either hex code is invalid."""
    rgb1 = hex_to_rgb(hex1)
    rgb2 = hex_to_rgb(hex2)
    if rgb1 is None or rgb2 is None:
        return float('inf')   # push invalid colors to the end of sorted list
    r1, g1, b1 = rgb1
    r2, g2, b2 = rgb2
    return ((r1 - r2) ** 2 + (g1 - g2) ** 2 + (b1 - b2) ** 2) ** 0.5
    
def search_color_names(query, colors_dict, max_results=8):
    """
    Search engine for color names.
    Priority: exact match → starts with query → word starts with query → contains query.
    Returns a list of (name, hex_code, match_type) tuples.
    """
    q = query.strip().lower()
    if not q:
        return []

    exact, starts, word_starts, contains = [], [], [], []

    for name, code in colors_dict.items():
        name_lower = name.lower()
        words = name_lower.split()
        if name_lower == q:
            exact.append((name, code, "exact"))
        elif name_lower.startswith(q):
            starts.append((name, code, "starts_with"))
        elif any(w.startswith(q) for w in words):
            word_starts.append((name, code, "word_match"))
        elif q in name_lower:
            contains.append((name, code, "contains"))

    for tier in (starts, word_starts, contains):
        tier.sort(key=lambda x: x[0])

    return (exact + starts + word_starts + contains)[:max_results]

def search_hex_codes(query, colors_dict, max_results=8):
    """
    Search engine for hex codes.
    Priority: exact match → prefix match → closest by RGB distance.
    Returns a list of (name, hex_code, match_type) tuples.
    """
    if not query or len(query.strip()) == 0:
        return []
        
    q = query.strip().upper()
    if not q.startswith("#"):
        q = "#" + q
    
    # Check if user typed a complete valid hex code (7 characters including #)
    is_complete_hex = len(q) == 7 and validate_code(q)
    
    results = []
    
    if is_complete_hex:
        # EXACT MATCH ONLY - find the color name(s) for this exact hex
        exact_names = convert_code(q, colors_dict)
        if exact_names:
            for name in exact_names[:max_results]:
                results.append(f"{q} - {name}")
        # Return ONLY the exact match(es) - no prefix matches, no closest colors
        return results
        
    # Prefix matches (user is typing partial hex)
    prefix_matches = []
    for name, code in colors_dict.items():
        code_upper = code.upper()
        if code_upper.startswith(q):
            prefix_matches.append((name, code))
    
    prefix_matches.sort(key=lambda x: x[1])
    for name, code in prefix_matches[:max_results]:
        results.append(f"{code} - {name}")
    
    
    return results[:max_results]


def render_result_cards(results):
    """Render search-engine-style result cards with swatch, name, hex, RGB, and match badge."""
    badge_labels = {
        "exact":       ("✅ Exact match",    "#1a3a1a", "#4CAF50"),
        "starts_with": ("🔤 Name match",     "#1a2a3a", "#42A5F5"),
        "word_match":  ("🔤 Word match",     "#1a2a3a", "#42A5F5"),
        "contains":    ("🔍 Contains",       "#2a2a1a", "#FFC107"),
        "prefix":      ("🔢 Prefix match",   "#1a2a3a", "#42A5F5"),
        "closest":     ("🎯 Closest color",  "#2a1a1a", "#FF7043"),
    }

    for name, code, match_type in results:
        rgb = hex_to_rgb(code)
        label, bg, fg = badge_labels.get(match_type, ("🔍 Match", "#2a2a2a", "#ccc"))
        st.markdown(f"""
        <div class="search-result-card">
            <div class="search-result-swatch" style="background-color:{code};"></div>
            <div style="flex:1; min-width:0;">
                <div class="search-result-title">{name}</div>
                <div class="search-result-sub">{code} &nbsp;·&nbsp; RGB({rgb[0]}, {rgb[1]}, {rgb[2]})</div>
                <div style="margin-top:6px;">
                    <span class="search-result-badge"
                          style="background:{bg}; color:{fg}; border-color:{fg}55;">
                        {label}
                    </span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

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



def search_colors(query: str, **kwargs) -> list:
    """Return color names that start with the query."""
    if not query or len(query.strip()) == 0:
        return []  # No dropdown until user types
    query_lower = query.strip().lower()
    matches = [
        name for name in sorted(colors_dict.keys())
        if name.lower().startswith(query_lower)
    ]
    return matches[:50]  # Limit results

with tab1:
    st.subheader("Enter a color name")
    
    selected_name = st_searchbox(
        search_function=search_colors,
        placeholder="Type a letter (e.g., R, B, G)...",
        key="color_searchbox",
        clearable=True,
        default=None
    )
    
    if selected_name:
        results = search_color_names(selected_name, colors_dict, max_results=8)
        if results:
            st.markdown(
                f'<div class="search-stats">🔎 {len(results)} result(s) for "<strong>{selected_name}</strong>"</div>',
                unsafe_allow_html=True
            )
            render_result_cards(results)
            
# ========= TAB 2: Hex to Color Name =========

def search_hex_codes_autocomplete(query: str, **kwargs) -> list:
    """
    Search function for hex codes.
    Returns formatted strings that look like "HexCode - ColorName"
    Dropdown appears only after typing.
    """
    if not query or len(query.strip()) == 0:
        return []
    
    query = query.strip().upper()
    if not query.startswith("#"):
        query = "#" + query
    
    results = []
    
    # 1. Prefix matches (user is typing partial hex)
    prefix_matches = []
    for name, code in colors_dict.items():
        code_upper = code.upper()
        if code_upper.startswith(query):
            prefix_matches.append((name, code))
    
    # Sort prefix matches by hex code
    prefix_matches.sort(key=lambda x: x[1])
    
    # Add formatted strings for prefix matches
    for name, code in prefix_matches[:15]:  # Limit to 15
        results.append(f"{code} - {name}")
    
    # 2. If user typed a complete valid hex (6 digits), add closest matches
    if len(query) == 7 and validate_code(query):  # Full hex like #FF0000
        # Find closest colors by RGB distance
        scored = sorted(
            colors_dict.items(),
            key=lambda item: color_distance(query, item[1])
        )
        for name, code in scored[:8]:  # Add top 8 closest
            formatted = f"{code} - {name}"
            if formatted not in results:  # Avoid duplicates
                results.append(formatted)
    
    return results[:20]  # Return max 20 results

with tab2:
    st.subheader("Enter a hex color code")
    
    selected_hex_result = st_searchbox(
        search_function=search_hex_codes_autocomplete,
        placeholder="Start typing hex code (e.g., F, FF, FF4, #FF0000)...",
        key="hex_searchbox",
        clearable=True,
        default=None
    )
    
    # Parse the selection (format: "#FF0000 - Red")
    if selected_hex_result:
        # Extract hex code and color name from the formatted string
        if " - " in selected_hex_result:
            hex_code, color_name = selected_hex_result.split(" - ", 1)
        else:
            hex_code = selected_hex_result
            color_name = None
        
        # Display the selected color details
        if hex_code and validate_code(hex_code):
            # Find matching color names
            matching_names = convert_code(hex_code, colors_dict)
            
            if matching_names:
                # Show results as cards
                results_to_show = [(name, hex_code, "exact") for name in matching_names]
                render_result_cards(results_to_show)
            elif color_name:
                # If we have the name from the selection
                results_to_show = [(color_name, hex_code, "exact")]
                render_result_cards(results_to_show)
            else:
                # No exact match found, show closest colors
                st.markdown(
                    f'<div class="no-exact-banner">⚠️ No exact match for <strong>{hex_code}</strong>. '
                    f'But you selected it from suggestions!</div>',
                    unsafe_allow_html=True
                )
        else:
            st.error(f"❌ Invalid hex code format: {hex_code}")


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
