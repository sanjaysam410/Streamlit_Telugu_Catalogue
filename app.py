import streamlit as st
import pandas as pd
import math
import random

# ==============================================================================
# 1. CONFIG & STYLING
# ==============================================================================
st.set_page_config(
    page_title="Telugu Search Engine",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="collapsed" # Collapsed by default to focus on search
)

# Custom CSS for "Search Engine" Feel
st.markdown("""
<style>
    /* Global Cleanliness */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .block-container {padding-top: 1.5rem; padding-bottom: 2rem;}

    /* Hero Section Styling */
    .hero-container {
        text-align: center;
        margin-bottom: 30px;
    }
    .hero-title {
        font-size: 3rem;
        font-weight: 800;
        color: #ff4b4b;
        margin-bottom: 0px;
    }
    .hero-subtitle {
        font-size: 1.2rem;
        color: #666;
        margin-bottom: 20px;
    }

    /* Search Bar Adjustment */
    div[data-testid="stTextInput"] input {
        border-radius: 30px;
        border: 2px solid #ddd;
        padding: 15px 25px;
        font-size: 1.1rem;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        transition: all 0.3s ease;
    }
    div[data-testid="stTextInput"] input:focus {
        border-color: #ff4b4b;
        box-shadow: 0 5px 15px rgba(255, 75, 75, 0.2);
    }

    /* Result Stats Styling */
    .result-stats {
        color: #888;
        font-size: 0.9rem;
        margin-bottom: 15px;
    }

    /* Card Grid Container */
    .grid-container {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
        gap: 25px;
        padding: 10px 0;
    }

    /* Individual Book Card */
    .book-card {
        background-color: white;
        border: 1px solid #f0f0f0;
        border-radius: 12px;
        transition: transform 0.2s, box-shadow 0.2s;
        height: 100%;
        display: flex;
        flex-direction: column;
        overflow: hidden;
    }
    .book-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 8px 20px rgba(0,0,0,0.08);
        border-color: #ffcccb;
        background-color: #fff9f9;
    }

    /* Metrics Container */
    .metrics-container {
        background-color: #f9f9f9;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 30px;
        border: 1px solid #eee;
    }
</style>
""", unsafe_allow_html=True)


# ==============================================================================
# 2. DATA LOADING & OMNI-SEARCH PREP
# ==============================================================================
@st.cache_data
def load_and_prep_data():
    file_path = "final_catalogue.csv"
    try:
        # Load File
        df = pd.read_csv(file_path, encoding='utf-8')
    except Exception as e:
        st.error(f"Error loading database: {e}")
        return pd.DataFrame()

    # Normalize Columns (Map Publication Date to Year if Year missing)
    if 'Publication Date' in df.columns and 'Year' not in df.columns:
        df['Year'] = df['Publication Date']
    elif 'Publication Date' in df.columns and 'Year' in df.columns:
        # Fill missing Year with Publication Date
        df['Year'] = df['Year'].fillna(df['Publication Date'])

    # --- CLEANING HAPPPENS HERE ---
    # We strip whitespace and treat 'unknown', 'nan' as None to "Smart Hide" them in UI
    def clean_value(val):
        if pd.isna(val): return None
        s = str(val).strip()
        if s.lower() in ['unknown', 'nan', 'null', '', 'none']: return None
        return s

    for col in df.columns:
        if df[col].dtype == 'object':
            df[col] = df[col].apply(clean_value)

    # Create Numeric Year for Filtering
    df['Year_Numeric'] = pd.to_numeric(df['Year'], errors='coerce')

    # --- SEARCH INDEX ---
    # Create a single blob column to search against
    # Combines Title, Author, Year, Category, Language into one string for Omni-Search
    df['Search_Blob'] = (
        df['Book Title'].fillna('') + " " + 
        df['Author(s)'].fillna('') + " " + 
        df['Year'].fillna('').astype(str) + " " + 
        df['Category'].fillna('') + " " + 
        df['Language'].fillna('')
    ).str.lower()

    return df

data = load_and_prep_data()

if data.empty:
    st.warning("Database is empty or could not be loaded.")
    st.stop()


# ==============================================================================
# 3. HEADER & HERO SEARCH ("Google-like")
# ==============================================================================
col_spacer1, col_hero, col_spacer2 = st.columns([1, 2, 1])

with col_hero:
    st.markdown("""
        <div class="hero-container">
            <div class="hero-title">Telugu Digital Archive</div>
            <div class="hero-subtitle">Discover 1.5 Lakh+ Books • History • Literature</div>
        </div>
    """, unsafe_allow_html=True)
    
    # MAIN SEARCH BAR
    search_query = st.text_input(
        "Search",
        placeholder="Search for 'Ramayana', '1950', 'Viswanatha'...",
        label_visibility="collapsed"
    )

# ==============================================================================
# 4. FACETED SEARCH BAR
# ==============================================================================
filtered_df = data.copy()

if search_query:
    # "Omni-Search" Logic
    query_str = search_query.lower().strip()
    filtered_df = filtered_df[filtered_df['Search_Blob'].str.contains(query_str, case=False)]

# Facets Container (Expander or Visible)
with st.expander("Filter by Category, Language, Publisher, Year", expanded=False):
    f_col1, f_col2, f_col3, f_col4 = st.columns(4)
    
    with f_col1:
        # Category Facet
        cats = sorted(data['Category'].dropna().unique())
        sel_cats = st.multiselect("Category", cats, placeholder="All Categories")
        
    with f_col2:
        # Language Facet
        langs = sorted(data['Language'].dropna().unique())
        sel_langs = st.multiselect("Language", langs, placeholder="All Languages")
        
    with f_col3:
        # Publisher Facet
        pubs = sorted(data['Publisher'].dropna().unique())
        sel_pubs = st.multiselect("Publisher", pubs, placeholder="All Publishers")
        
    with f_col4:
        # Year Facet (Range)
        valid_years = data['Year_Numeric'].dropna()
        if not valid_years.empty:
            min_y, max_y = int(valid_years.min()), int(valid_years.max())
            # Default to full range
            sel_years = st.slider("Year Range", min_y, max_y, (min_y, max_y))
        else:
            sel_years = None
            min_y, max_y = 0, 0

# Apply Facets
if sel_cats:
    filtered_df = filtered_df[filtered_df['Category'].isin(sel_cats)]

if sel_langs:
    filtered_df = filtered_df[filtered_df['Language'].isin(sel_langs)]

if sel_pubs:
    filtered_df = filtered_df[filtered_df['Publisher'].isin(sel_pubs)]

if sel_years and not valid_years.empty:
    # IMPORTANT FIX: Only filter if the user has narrowed the range.
    # If the slider is at (min, max), we include everything (including NaNs).
    # If the user moves the slider, they implicitly want to filter by Year, so we exclude NaNs.
    is_full_range = (sel_years[0] == min_y) and (sel_years[1] == max_y)
    
    if not is_full_range:
        filtered_df = filtered_df[
            (filtered_df['Year_Numeric'] >= sel_years[0]) & 
            (filtered_df['Year_Numeric'] <= sel_years[1])
        ]

# Sidebar removed/minimized since specific facets are requested in main bar
# We keep the sidebar for clean "About" or metadata if needed, but filters are now central.
with st.sidebar:
    st.markdown("### Database Info")
    st.caption(f"Total Books: {len(data):,}")
    if not filtered_df.empty:
        st.caption(f"Showing: {len(filtered_df):,}")
    st.markdown("---")
    st.info("Tip: Use the main search bar for keywords, and filters to narrow down.")


# ==============================================================================
# 5. RESULTS CONTROL & SORTING
# ==============================================================================
if not filtered_df.empty:
    
    # Control Row
    c_res, c_sort = st.columns([3, 1])
    
    with c_res:
        st.markdown(f"<div class='result-stats'>Found <b>{len(filtered_df):,}</b> results</div>", unsafe_allow_html=True)
        
    with c_sort:
        sort_opt = st.selectbox(
            "Sort By",
            ["Relevance", "Year (Newest)", "Year (Oldest)", "Title (A-Z)"],
            label_visibility="collapsed"
        )
        
    # Sorting Logic
    if sort_opt == "Year (Newest)":
        filtered_df = filtered_df.sort_values('Year_Numeric', ascending=False, na_position='last')
    elif sort_opt == "Year (Oldest)":
        filtered_df = filtered_df.sort_values('Year_Numeric', ascending=True, na_position='last')
    elif sort_opt == "Title (A-Z)":
        filtered_df = filtered_df.sort_values('Book Title', ascending=True)

    # ==============================================================================
    # 6. PAGINATION & RENDERING
    # ==============================================================================
    ITEMS_PER_PAGE = 20
    if len(filtered_df) > ITEMS_PER_PAGE:
        total_pages = math.ceil(len(filtered_df) / ITEMS_PER_PAGE)
        
        # Page State
        if 'page' not in st.session_state: st.session_state.page = 1
        
        # Pagination Controls (Centered)
        c_p1, c_p2, c_p3 = st.columns([1, 2, 1])
        with c_p2:
            st.markdown(f"<div style='text-align:center'>Page {st.session_state.page} of {total_pages}</div>", unsafe_allow_html=True)
            pp_col, nn_col = st.columns(2)
            with pp_col:
                if st.button("Previous") and st.session_state.page > 1:
                    st.session_state.page -= 1
                    st.rerun()
            with nn_col:
                if st.button("Next") and st.session_state.page < total_pages:
                    st.session_state.page += 1
                    st.rerun()
        
        start = (st.session_state.page - 1) * ITEMS_PER_PAGE
        end = start + ITEMS_PER_PAGE
        view_df = filtered_df.iloc[start:end]
    else:
        view_df = filtered_df

    # RENDER CARDS
    grid_cols = st.columns(4)
    bg_colors = ['#FF9AA2', '#FFB7B2', '#FFDAC1', '#E2F0CB', '#B5EAD7', '#C7CEEA']
    
    for i, (idx, row) in enumerate(view_df.iterrows()):
        col = grid_cols[i % 4]
        
        # Extract Safe Data
        title = row['Book Title'] or "Untitled"
        author = row['Author(s)'] or "Unknown Author"
        year = str(int(row['Year_Numeric'])) if pd.notna(row['Year_Numeric']) else ""
        lang = row['Language'] or ""
        
        color = random.choice(bg_colors)
        
        with col:
            with st.container(border=True):
                # Simple Aesthetic Card
                st.markdown(f"""
                    <div style="height: 120px; background-color: {color}; border-radius: 8px; display: flex; align-items: center; justify-content: center; margin-bottom: 10px;">
                        <span style="font-size: 2.5rem; color: #fff; text-shadow: 0 2px 4px rgba(0,0,0,0.1);">📚</span>
                    </div>
                    <div style="height: 60px; overflow: hidden; margin-bottom: 5px;">
                        <span style="font-weight: 600; font-size: 1rem; color: #333;">{title[:50]}{'...' if len(title)>50 else ''}</span>
                    </div>
                    <div style="font-size: 0.85rem; color: #666; margin-bottom: 2px;">{author[:30]}{'...' if len(author)>30 else ''}</div>
                    <div style="font-size: 0.8rem; color: #999;">{f'{year} • ' if year else ''}{lang}</div>
                """, unsafe_allow_html=True)
                
                if st.button("Details", key=f"d_{idx}", use_container_width=True):
                    st.session_state['sel_book_idx'] = idx
                    st.session_state['sel_book_data'] = row.to_dict()
                    st.session_state['show_d'] = True

else:
    st.markdown("<div style='text-align:center; padding: 50px; color: #888;'>No books found. Try a different keyword like 'History', '1947', or 'Telugu'.</div>", unsafe_allow_html=True)


# ==============================================================================
# 7. DETAILS DIALOG
# ==============================================================================
if st.session_state.get('show_d'):
    book = st.session_state.get('sel_book_data', {})
    
    @st.dialog(book.get('Book Title') or "Book Details")
    def show_modal():
        c1, c2 = st.columns([1, 2])
        with c1:
            st.markdown(f"""
                <div style="background-color: #eee; height: 150px; border-radius: 10px; display: flex; align-items: center; justify-content: center;">
                    <span style="font-size: 4rem;">📖</span>
                </div>
            """, unsafe_allow_html=True)
        with c2:
            st.markdown(f"### {book.get('Book Title')}")
            st.markdown(f"**Author:** {book.get('Author(s)')}")
            if book.get('Year_Numeric') and not pd.isna(book.get('Year_Numeric')):
                st.markdown(f"**Year:** {int(book.get('Year_Numeric'))}")
        
        st.divider()
        st.write("#### Metadata")
        
        # Iterate nicely
        skip_keys = ['Book Title', 'Author(s)', 'Year_Numeric', 'Search_Blob', 'Year', 'URL', 'Link', 'Url', 'link', 'Book title_URL', 'Author_URL', 'Book title', 'Book id']
        for k, v in book.items():
            if k not in skip_keys and v is not None and str(v).strip() != "":
                st.markdown(f"**{k}:** {v}")
        
        st.divider()
        
        # Smart Hyperlink Logic (Hybrid)
        explicit_url = book.get('Book title_URL')
        
        if explicit_url and isinstance(explicit_url, str) and (explicit_url.startswith('http') or explicit_url.startswith('www')):
             st.link_button("Access Digital Copy / డిజిటల్ కాపీని యాక్సెస్ చేయండి", explicit_url, type="primary", use_container_width=True)
        else:
             # Fallback to Google Search
             title = book.get('Book Title') or ""
             author = book.get('Author(s)') or ""
             if title:
                # Construct clean search query
                query = f"{title} {author}".strip()
                search_url = f"https://www.google.com/search?q={query}"
                st.link_button("Search for Copy / కాపీ కోసం వెతకండి", search_url, type="secondary", use_container_width=True)
             else:
                st.info("Visit the library to access this physical copy.")
        
        # Author Profile Logic
        author_url = book.get('Author_URL')
        if author_url and isinstance(author_url, str) and (author_url.startswith('http') or author_url.startswith('www')):
            st.divider()
            st.link_button("View Author Profile / రచయిత వివరాలు", author_url, type="secondary", use_container_width=True)

    show_modal()
