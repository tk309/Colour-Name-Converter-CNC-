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
    """Convert a hex code string to an (R, G, B) tuple."""
    h = hex_code.lstrip("#")
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

def color_distance(hex1, hex2):
    """Euclidean distance between two hex colors in RGB space."""
    r1, g1, b1 = hex_to_rgb(hex1)
    r2, g2, b2 = hex_to_rgb(hex2)
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
    q = query.strip().upper()
    if q and not q.startswith("#"):
        q = "#" + q

    if not q or q == "#":
        return []

    # Exact match
    exact_names = convert_code(q, colors_dict)
    if exact_names:
        return [(n, q, "exact") for n in exact_names]

    # Prefix search — user is still typing (e.g. "#FF4")
    prefix_results = [
        (name, code, "prefix")
        for name, code in colors_dict.items()
        if code.upper().startswith(q)
    ]
    prefix_results.sort(key=lambda x: x[1])
    if prefix_results:
        return prefix_results[:max_results]

    # Closest colors by RGB distance — only for full valid hex codes
    if validate_code(q):
        scored = sorted(
            colors_dict.items(),
            key=lambda item: color_distance(q, item[1])
        )
        return [(name, code, "closest") for name, code in scored[:max_results]]

    return []

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



with tab1:
    st.subheader("Enter a color name")
    
    # Single text input
    user_input = st.text_input(
        "Color name",
        placeholder="Start typing (e.g., R, Re, Red...)",
        key="single_input"
    )
    
    # Only show suggestions if user typed something
    if user_input and user_input.strip():
        query = user_input.strip().lower()
        matches = [
            name for name in sorted(colors_dict.keys())
            if name.lower().startswith(query)
        ][:20]  # Show top 20
        
        if matches:
            # Create a container that looks like a dropdown
            with st.container():
                st.markdown("---")  # separator
                for name in matches:
                    # Each suggestion is a button that looks like a dropdown item
                    if st.button(
                        name,
                        key=f"sugg_{name}",
                        use_container_width=True,
                        type="secondary"
                    ):
                        # When clicked, show the color results
                        results = search_color_names(name, colors_dict, max_results=8)
                        if results:
                            st.markdown(
                                f'<div class="search-stats">🔎 {len(results)} result(s) for "<strong>{name}</strong>"</div>',
                                unsafe_allow_html=True
                            )
                            render_result_cards(results)
                        st.rerun()  # Clear the suggestions after selection
        elif len(query) > 0:
            st.info(f"No colors start with '{query}'")
    else:
        st.caption("⌨️ Type a letter – suggestions will appear below")
# ========= TAB 2: Hex to Color Name =========
with tab2:
    st.subheader("Enter a hex color code")

    # Live partial-hex search — results update as you type
    live_hex = st.text_input(
        "Live hex search:",
        placeholder="Start typing — e.g. #FF, #FF4B, #FF4B4B",
        key="live_hex_input",
        help="Results update as you type. Prefix matches appear first; closest colors shown for a full 6-digit code."
    )

    if live_hex:
        live_q = live_hex.strip()
        if not live_q.startswith("#"):
            live_q = "#" + live_q
        results = search_hex_codes(live_q, colors_dict, max_results=8)
        if results:
            match_types = {r[2] for r in results}
            if "closest" in match_types and "exact" not in match_types:
                st.markdown(
                    f'<div class="no-exact-banner">⚠️ No exact match for <strong>{live_q.upper()}</strong>. '
                    f'Showing the {len(results)} visually closest color(s):</div>',
                    unsafe_allow_html=True
                )
            else:
                st.markdown(
                    f'<div class="search-stats">🔎 {len(results)} result(s) for "<strong>{live_q.upper()}</strong>"</div>',
                    unsafe_allow_html=True
                )
            render_result_cards(results)
        elif len(live_q) > 1:
            st.info("No colors match that prefix yet. Keep typing…")



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
