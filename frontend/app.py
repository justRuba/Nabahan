# frontend/app.py
# Nabahan Streamlit Dashboard - 4 Page Layout
# No Emojis - Green Branding - Professional Theme

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st
import pandas as pd
import plotly.express as px
import sqlite3

from agent.nabahan_logic import (
    nabahan_agent,
    get_filter_options,
    get_kpi_stats,
    get_activity_chart_data,
    get_nature_chart_data
)
from agent.config import PRIMARY_COLOR, SECONDARY_COLOR, PRIMARY_GRADIENT, GREEN_SHADES, DB_PATH

# Base path for CSV files
BASE_DIR = Path(__file__).parent.parent
CSV_LOOKUP_PATH = BASE_DIR / "Data" / "raw" / "lookup"

# Page config
st.set_page_config(
    page_title="Nabahan Pro | نبهان",
    page_icon="N",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Hide sidebar completely
st.markdown("""
<style>
    [data-testid="stSidebar"] {display: none;}
    [data-testid="stSidebarNav"] {display: none;}
</style>
""", unsafe_allow_html=True)

# Main CSS - Green Branding, IBM Plex Sans Arabic, RTL, Navigation Bar
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+Arabic:wght@400;500;600;700&display=swap');

    html, body, [class*="css"], .stMarkdown, p, h1, h2, h3, h4, span, div {{
        font-family: 'IBM Plex Sans Arabic', sans-serif !important;
        direction: rtl;
        text-align: right;
    }}

    .block-container {{
        padding-top: 0.5rem !important;
        max-width: 1400px;
    }}

    /* Navigation Bar */
    .nav-container {{
        background: white;
        padding: 15px 30px;
        border-bottom: 1px solid #e5e7eb;
        margin-bottom: 20px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        direction: rtl;
    }}

    .brand-name {{
        font-family: 'IBM Plex Sans Arabic', sans-serif !important;
        font-size: 2rem !important;
        font-weight: 700 !important;
        background: {PRIMARY_GRADIENT};
        -webkit-background-clip: text !important;
        -webkit-text-fill-color: transparent !important;
        background-clip: text !important;
        margin: 0 !important;
    }}

    .nav-buttons {{
        display: flex;
        gap: 10px;
        justify-content: center;
        flex: 1;
        margin: 0 50px;
    }}

    .nav-btn {{
        background: transparent;
        border: none;
        padding: 10px 25px;
        font-family: 'IBM Plex Sans Arabic', sans-serif;
        font-size: 1rem;
        font-weight: 600;
        color: #374151;
        cursor: pointer;
        position: relative;
        transition: all 0.3s ease;
    }}

    .nav-btn:hover {{
        color: {PRIMARY_COLOR};
    }}

    .nav-btn.active {{
        color: {PRIMARY_COLOR};
    }}

    .nav-btn.active::after {{
        content: '';
        position: absolute;
        bottom: -5px;
        left: 0;
        right: 0;
        height: 3px;
        background: {PRIMARY_GRADIENT};
        border-radius: 2px;
    }}

    /* Logo Styling */
    .logo-text {{
        font-family: 'IBM Plex Sans Arabic', sans-serif !important;
        font-size: 2.5rem !important;
        font-weight: 700 !important;
        background: {PRIMARY_GRADIENT};
        -webkit-background-clip: text !important;
        -webkit-text-fill-color: transparent !important;
        background-clip: text !important;
        margin: 0 !important;
        line-height: 1.2;
    }}

    .text-gradient {{
        background: {PRIMARY_GRADIENT};
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-weight: 700;
    }}

    /* Tab Highlight - Green */
    .stTabs [data-baseweb="tab-highlight"] {{
        background-color: {SECONDARY_COLOR} !important;
    }}

    .stTabs [data-baseweb="tab-list"] {{
        gap: 8px;
        direction: rtl;
    }}

    .stTabs [data-baseweb="tab"] {{
        background: white;
        border-radius: 8px 8px 0 0;
        border: 1px solid #e5e7eb;
        border-bottom: none;
        padding: 10px 20px;
        font-weight: 600;
    }}

    .stTabs [aria-selected="true"] {{
        background: {PRIMARY_COLOR} !important;
        color: white !important;
    }}

    /* KPI Cards */
    .kpi-card {{
        background: white;
        border-radius: 12px;
        padding: 20px;
        border: 1px solid #e5e7eb;
        border-top: 4px solid {SECONDARY_COLOR};
        text-align: center;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
    }}

    .kpi-card h2 {{
        color: {SECONDARY_COLOR};
        margin: 0;
        font-size: 2rem;
        font-weight: 700;
    }}

    .kpi-card p {{
        color: #4b5563;
        margin: 5px 0 0 0;
        font-size: 1rem;
        font-weight: 500;
    }}

    /* Gradient KPI Card */
    .kpi-gradient {{
        background: {PRIMARY_GRADIENT};
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 4px 12px rgba(47,179,142,0.3);
    }}

    .kpi-gradient h2 {{
        color: white;
        margin: 0;
        font-size: 2rem;
        font-weight: 700;
    }}

    .kpi-gradient p {{
        color: rgba(255,255,255,0.9);
        margin: 5px 0 0 0;
        font-size: 1rem;
        font-weight: 500;
    }}

    /* Modern KPI Card for Projects */
    .kpi-modern {{
        background: white;
        border-radius: 16px;
        padding: 24px;
        border: 1px solid #e5e7eb;
        border-right: 4px solid {PRIMARY_COLOR};
        text-align: center;
        box-shadow: 0 4px 16px rgba(0,0,0,0.08);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }}

    .kpi-modern:hover {{
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(0,0,0,0.12);
    }}

    .kpi-modern h2 {{
        color: {PRIMARY_COLOR};
        margin: 0;
        font-size: 2.2rem;
        font-weight: 700;
    }}

    .kpi-modern p {{
        color: #4b5563;
        margin: 8px 0 0 0;
        font-size: 1rem;
        font-weight: 600;
    }}

    /* Filter button styled like dropdown */
    .filter-btn {{
        background: white !important;
        border: 1px solid #e5e7eb !important;
        color: #374151 !important;
        border-radius: 8px !important;
        font-weight: 500 !important;
        padding: 8px 16px !important;
    }}

    .filter-btn:hover {{
        border-color: {PRIMARY_COLOR} !important;
        color: {PRIMARY_COLOR} !important;
    }}

    /* Table improvements */
    .stDataFrame {{
        border-radius: 12px;
        overflow: hidden;
        width: 100% !important;
    }}

    .stDataFrame td, .stDataFrame th {{
        padding: 12px 16px !important;
        font-size: 0.95rem !important;
    }}

    /* Insights Box */
    .insights-box {{
        background: linear-gradient(135deg, {PRIMARY_COLOR}15, {SECONDARY_COLOR}10);
        border-radius: 12px;
        padding: 20px;
        border-right: 4px solid {PRIMARY_COLOR};
        margin: 1rem 0;
    }}

    /* Info Banner */
    .info-banner {{
        background: #fafafa;
        border-radius: 12px;
        padding: 20px;
        border: 1px solid #e5e7eb;
        border-right: 4px solid {PRIMARY_COLOR};
        margin-bottom: 1.5rem;
    }}

    .info-banner h4 {{
        margin: 0 0 10px 0;
        color: {SECONDARY_COLOR};
        font-weight: 700;
    }}

    .info-banner p {{
        margin: 0;
        color: #374151;
        font-size: 1rem;
    }}

    /* About Page Sections */
    .about-section {{
        background: white;
        border-radius: 12px;
        padding: 30px;
        border: 1px solid #e5e7eb;
        margin-bottom: 1.5rem;
    }}

    .about-section h3 {{
        color: {SECONDARY_COLOR};
        margin: 0 0 15px 0;
        font-weight: 700;
    }}

    .contact-card {{
        background: {PRIMARY_GRADIENT};
        border-radius: 12px;
        padding: 25px;
        text-align: center;
        color: white;
    }}

    .contact-card h4 {{
        margin: 0 0 15px 0;
        font-weight: 700;
    }}

    .contact-card p {{
        margin: 5px 0;
        font-size: 1.1rem;
    }}

    /* Streamlit Button Override for Nav */
    div[data-testid="column"] .stButton > button {{
        background: transparent !important;
        border: none !important;
        color: #374151 !important;
        font-weight: 600 !important;
        padding: 10px 20px !important;
        border-radius: 0 !important;
        position: relative;
    }}

    div[data-testid="column"] .stButton > button:hover {{
        color: {PRIMARY_COLOR} !important;
        background: transparent !important;
    }}

    /* Active nav button */
    .nav-active > button {{
        color: {PRIMARY_COLOR} !important;
        border-bottom: 3px solid {PRIMARY_COLOR} !important;
    }}

    /* Buttons */
    .stButton > button {{
        background: {PRIMARY_GRADIENT} !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
    }}

    .stButton > button:hover {{
        opacity: 0.9 !important;
    }}

    /* Chat Input */
    .stChatInput > div {{
        border-color: {PRIMARY_COLOR} !important;
    }}

    /* Dataframe - Full Width */
    .stDataFrame {{
        border-radius: 12px;
        overflow: hidden;
        width: 100% !important;
    }}

    /* Search Box */
    .stTextInput > div > div > input {{
        border-color: {PRIMARY_COLOR} !important;
        border-radius: 8px !important;
    }}

    /* Multiselect */
    .stMultiSelect > div {{
        border-color: #e5e7eb !important;
    }}

    /* Hide Streamlit Branding */
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    header {{visibility: hidden;}}

    /* Scrollbar */
    ::-webkit-scrollbar {{
        width: 6px;
        height: 6px;
    }}
    ::-webkit-scrollbar-thumb {{
        background: {PRIMARY_COLOR};
        border-radius: 3px;
    }}

    /* Filter section */
    .filter-section {{
        background: #fafafa;
        border-radius: 12px;
        padding: 15px;
        margin-bottom: 20px;
        border: 1px solid #e5e7eb;
    }}
</style>
""", unsafe_allow_html=True)


def load_csv_options(filename):
    """Load options from CSV lookup file."""
    try:
        filepath = CSV_LOOKUP_PATH / filename
        df = pd.read_csv(filepath, encoding='utf-8-sig')
        # Get first column values
        col = df.columns[0]
        return df[col].dropna().unique().tolist()
    except Exception:
        return []


def init_state():
    """Initialize session state."""
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 'home'
    if 'filter_options' not in st.session_state:
        st.session_state.filter_options = get_filter_options()
    if 'last_result' not in st.session_state:
        st.session_state.last_result = None


def render_header():
    """Render navigation bar with brand on right and 4 centered buttons."""
    # In RTL layout, first column = rightmost position
    # Layout: [brand | spacer | nav1 | nav2 | nav3 | nav4 | spacer]
    col_brand, col_spacer1, col_nav1, col_nav2, col_nav3, col_nav4, col_spacer2 = st.columns([1.5, 0.3, 1, 1, 1, 1, 0.3])

    # Brand on far right (first column in RTL)
    with col_brand:
        st.markdown('<h1 class="logo-text">نبهان</h1>', unsafe_allow_html=True)

    # Four navigation pages: Home, Tenders, Projects, About
    pages = [
        ('home', 'الرئيسية', col_nav1),
        ('tenders', 'المنافسات', col_nav2),
        ('projects', 'المشاريع', col_nav3),
        ('about', 'من نحن', col_nav4)
    ]

    for page_key, page_name, col in pages:
        with col:
            is_active = st.session_state.current_page == page_key
            # Style active button with green bottom border
            if is_active:
                st.markdown(f'''
                <div style="text-align: center; padding: 10px 0; border-bottom: 3px solid {PRIMARY_COLOR};">
                    <span style="color: {PRIMARY_COLOR}; font-weight: 700; font-size: 1rem;">{page_name}</span>
                </div>
                ''', unsafe_allow_html=True)
            else:
                if st.button(page_name, key=f"nav_{page_key}", use_container_width=True):
                    st.session_state.current_page = page_key
                    st.session_state.last_result = None
                    st.rerun()

    st.divider()


def calculate_table_height(row_count, row_height=35, header_height=40, max_height=800, min_height=200):
    """Calculate dynamic table height based on row count."""
    calculated = header_height + (row_count * row_height)
    return max(min_height, min(calculated, max_height))


def get_tenders_data():
    """Fetch all tenders data."""
    try:
        with sqlite3.connect(DB_PATH) as conn:
            df = pd.read_sql_query("""
                SELECT
                    url as 'الرابط',
                    tender_name as 'اسم المنافسة',
                    tender_number as 'رقم المنافسة',
                    reference_number as 'الرقم المرجعي',
                    tender_purpose as 'الغرض',
                    tender_status as 'الحالة',
                    government_entity as 'الجهة الحكومية',
                    execution_location as 'مكان التنفيذ',
                    tender_type as 'نوع المنافسة',
                    competition_activity as 'النشاط',
                    submission_deadline as 'موعد التقديم',
                    opening_date as 'تاريخ الفتح',
                    tender_document_value as 'قيمة الوثيقة',
                    contract_duration as 'مدة العقد'
                FROM tenders_full_details
                ORDER BY submission_deadline DESC
            """, conn)
            return df
    except Exception:
        return pd.DataFrame()


def get_projects_data():
    """Fetch all future projects data without duration sorting."""
    try:
        with sqlite3.connect(DB_PATH) as conn:
            df = pd.read_sql_query("""
                SELECT
                    id as 'الرقم',
                    project_name as 'اسم المشروع',
                    government_entity as 'الجهة',
                    quarter as 'الربع السنوي',
                    year as 'السنة',
                    execution_location as 'مكان التنفيذ',
                    project_nature as 'طبيعة المشروع',
                    project_description as 'وصف المشروع',
                    project_status as 'الحالة',
                    expected_duration_days as 'المدة (ايام)',
                    expected_duration_months as 'المدة (اشهر)',
                    expected_duration_years as 'المدة (سنوات)'
                FROM future_projects
                ORDER BY year DESC, quarter DESC
            """, conn)
            return df
    except Exception:
        return pd.DataFrame()


# =============================================
# PAGE 1: HOME (الرئيسية)
# =============================================
def render_home_page():
    """Render home page with chat interface."""

    # Info banner
    st.markdown('''
    <div class="info-banner">
        <h4>كيفية استخدام المساعد الذكي</h4>
        <p>
            اسال نبهان اي سؤال حول البيانات، مثل: "ما هي اكثر الانشطة طلبا؟" او "كم عدد المناقصات في الرياض؟"
            سيقوم النظام باستخراج البيانات وتقديم التحليلات المناسبة.
        </p>
    </div>
    ''', unsafe_allow_html=True)

    # Title
    st.markdown('''
    <h2 style="font-size: 1.8rem; font-weight: 700; margin: 1.5rem 0;">
        استعلم عن <span class="text-gradient">المنافسات الحكومية</span>
    </h2>
    ''', unsafe_allow_html=True)

    # Chat input
    prompt = st.chat_input("اطرح سؤالك هنا...")

    if prompt:
        with st.spinner("جاري تحليل البيانات..."):
            result = nabahan_agent(prompt, None)
            st.session_state.last_result = result

    # Display results
    if st.session_state.last_result:
        result = st.session_state.last_result

        # Insights first
        st.markdown(f'''
        <div class="insights-box">
            <p style="font-size: 1.1rem; line-height: 1.8;">{result["insights"]}</p>
        </div>
        ''', unsafe_allow_html=True)

        # Data table with all columns - full width and dynamic height
        if not result["data"].empty:
            st.subheader("البيانات المستخرجة")
            table_height = calculate_table_height(len(result["data"]))
            st.dataframe(
                result["data"],
                width='stretch',
                height=table_height
            )

            # Chart if applicable
            df = result["data"]
            if len(df.columns) >= 2:
                label_col = df.columns[0]
                val_col = None
                for col in df.columns[1:]:
                    if pd.api.types.is_numeric_dtype(df[col]):
                        val_col = col
                        break

                if val_col and result.get("chart_type") != "none":
                    chart_type = result.get("chart_type", "bar")

                    if chart_type == "pie":
                        fig = px.pie(
                            df.head(10),
                            names=label_col,
                            values=val_col,
                            hole=0.4,
                            color_discrete_sequence=GREEN_SHADES
                        )
                    elif chart_type == "line":
                        fig = px.line(
                            df,
                            x=label_col,
                            y=val_col,
                            color_discrete_sequence=[PRIMARY_COLOR]
                        )
                    else:
                        fig = px.bar(
                            df.head(15),
                            x=val_col,
                            y=label_col,
                            orientation='h',
                            color=val_col,
                            color_continuous_scale=GREEN_SHADES
                        )
                        fig.update_yaxes(categoryorder='total ascending')

                    fig.update_layout(
                        font_family="IBM Plex Sans Arabic",
                        margin=dict(l=150, r=20, t=20, b=20),
                        plot_bgcolor="rgba(0,0,0,0)",
                        paper_bgcolor="rgba(0,0,0,0)",
                        coloraxis_showscale=False
                    )
                    st.plotly_chart(fig, use_container_width=True)

        # Clear button
        if st.button("مسح النتائج"):
            st.session_state.last_result = None
            st.rerun()

    else:
        # Default KPI cards
        render_kpi_cards()
        st.write("")
        render_charts()


def render_kpi_cards():
    """Render KPI metric cards."""
    stats = get_kpi_stats()

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(f'''
        <div class="kpi-card">
            <h2>{stats["tenders"]:,}</h2>
            <p>اجمالي المنافسات</p>
        </div>
        ''', unsafe_allow_html=True)

    with col2:
        st.markdown(f'''
        <div class="kpi-card">
            <h2>{stats["projects"]:,}</h2>
            <p>المشاريع المستقبلية</p>
        </div>
        ''', unsafe_allow_html=True)

    with col3:
        st.markdown(f'''
        <div class="kpi-card">
            <h2>{stats["entities"]:,}</h2>
            <p>الجهات الحكومية</p>
        </div>
        ''', unsafe_allow_html=True)

    with col4:
        st.markdown(f'''
        <div class="kpi-card">
            <h2>{stats["activities"]:,}</h2>
            <p>الانشطة الاساسية</p>
        </div>
        ''', unsafe_allow_html=True)


def render_charts():
    """Render default dashboard charts."""
    st.subheader("احصائيات السوق العامة")

    tab1, tab2 = st.tabs(["انشطة المنافسات", "طبيعة المشاريع"])

    with tab1:
        act_df = get_activity_chart_data()
        if not act_df.empty:
            fig = px.bar(
                act_df,
                x='count',
                y='activity',
                orientation='h',
                color='count',
                color_continuous_scale=GREEN_SHADES
            )
            fig.update_layout(
                font_family="IBM Plex Sans Arabic",
                margin=dict(l=180, r=20, t=20, b=20),
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                coloraxis_showscale=False,
                yaxis_title="",
                xaxis_title="عدد المنافسات"
            )
            fig.update_yaxes(categoryorder='total ascending')
            st.plotly_chart(fig, use_container_width=True)

    with tab2:
        nat_df = get_nature_chart_data()
        if not nat_df.empty:
            fig = px.pie(
                nat_df,
                names='project_nature',
                values='count',
                hole=0.4,
                color_discrete_sequence=GREEN_SHADES
            )
            fig.update_layout(
                font_family="IBM Plex Sans Arabic",
                margin=dict(l=20, r=20, t=20, b=20)
            )
            st.plotly_chart(fig, use_container_width=True)


# =============================================
# PAGE 2: TENDERS (المنافسات)
# =============================================
def render_tenders_page():
    """Render tenders page with CSV-based filters."""

    st.markdown('''
    <h2 style="font-size: 1.8rem; font-weight: 700; margin-bottom: 1.5rem;">
        <span class="text-gradient">المنافسات الحكومية</span>
    </h2>
    ''', unsafe_allow_html=True)

    # Load data
    df = get_tenders_data()

    if df.empty:
        st.warning("لا توجد بيانات متاحة")
        return

    # Load filter options from CSV files
    entities_options = load_csv_options("Government Entity.csv")
    regions_options = load_csv_options("regions.csv")
    tender_types_options = load_csv_options("tender_types.csv")

    # Search box
    search_term = st.text_input(
        "البحث",
        placeholder="ابحث باسم المنافسة او الرقم المرجعي...",
        label_visibility="collapsed"
    )

    # Filters Section
    st.markdown('<div class="filter-section">', unsafe_allow_html=True)
    st.markdown("**تصفية النتائج**")

    col1, col2, col3 = st.columns(3)

    with col1:
        entity_filter = st.multiselect(
            "الجهة الحكومية",
            options=entities_options[:50] if entities_options else df['الجهة الحكومية'].dropna().unique().tolist()[:50],
            placeholder="اختر الجهة"
        )

    with col2:
        type_filter = st.multiselect(
            "نوع المنافسة",
            options=tender_types_options if tender_types_options else df['نوع المنافسة'].dropna().unique().tolist(),
            placeholder="اختر النوع"
        )

    with col3:
        region_filter = st.multiselect(
            "المنطقة",
            options=regions_options if regions_options else [],
            placeholder="اختر المنطقة"
        )

    # Small white clear button
    col_clear, col_space = st.columns([1, 5])
    with col_clear:
        st.markdown("""
            <style>
            .clear-btn-container button {
                background-color: white !important;
                color: #666 !important;
                border: 1px solid #ddd !important;
                padding: 0.3rem 1rem !important;
                font-size: 0.85rem !important;
                border-radius: 6px !important;
            }
            .clear-btn-container button:hover {
                background-color: #f8f8f8 !important;
                border-color: #bbb !important;
            }
            </style>
        """, unsafe_allow_html=True)
        st.markdown('<div class="clear-btn-container">', unsafe_allow_html=True)
        if st.button("مسح الفلاتر", key="clear_tenders"):
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

    # Apply filters
    filtered_df = df.copy()

    if search_term:
        mask = (
            filtered_df['اسم المنافسة'].astype(str).str.contains(search_term, case=False, na=False) |
            filtered_df['الرقم المرجعي'].astype(str).str.contains(search_term, case=False, na=False)
        )
        filtered_df = filtered_df[mask]

    if entity_filter:
        filtered_df = filtered_df[filtered_df['الجهة الحكومية'].isin(entity_filter)]

    if type_filter:
        filtered_df = filtered_df[filtered_df['نوع المنافسة'].isin(type_filter)]

    if region_filter:
        region_mask = filtered_df['مكان التنفيذ'].apply(
            lambda x: any(r in str(x) for r in region_filter) if pd.notna(x) else False
        )
        filtered_df = filtered_df[region_mask]

    # Stats row
    st.markdown(f"**عدد النتائج:** {len(filtered_df):,} منافسة")

    # Format date columns - extract first 10 characters
    date_cols = ['موعد التقديم', 'تاريخ الفتح']
    for col in date_cols:
        if col in filtered_df.columns:
            filtered_df[col] = filtered_df[col].astype(str).str[:10]

    # Calculate dynamic height
    table_height = calculate_table_height(len(filtered_df))

    # Display with link column - full width
    st.dataframe(
        filtered_df,
        column_config={
            "الرابط": st.column_config.LinkColumn(
                "الرابط",
                display_text="فتح",
                help="اضغط لفتح صفحة المنافسة"
            ),
            "الرقم المرجعي": st.column_config.NumberColumn(
                "الرقم المرجعي",
                format="%d"
            ),
            "قيمة الوثيقة": st.column_config.NumberColumn(
                "قيمة الوثيقة",
                format="%.0f ريال"
            )
        },
        width='stretch',
        height=table_height,
        hide_index=True
    )


# =============================================
# PAGE 3: PROJECTS (المشاريع)
# =============================================
def render_projects_page():
    """Render future projects page without duration sorting."""

    st.markdown('''
    <h2 style="font-size: 1.8rem; font-weight: 700; margin-bottom: 1.5rem;">
        <span class="text-gradient">المشاريع المستقبلية</span>
    </h2>
    ''', unsafe_allow_html=True)

    # Load data (no duration sorting)
    df = get_projects_data()

    if df.empty:
        st.warning("لا توجد بيانات متاحة")
        return

    # Modern KPI Cards
    stats = get_kpi_stats()
    unique_entities = df['الجهة'].nunique()
    unique_natures = df['طبيعة المشروع'].nunique()

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(f'''
        <div class="kpi-modern">
            <h2>{stats["projects"]:,}</h2>
            <p>اجمالي المشاريع</p>
        </div>
        ''', unsafe_allow_html=True)

    with col2:
        st.markdown(f'''
        <div class="kpi-modern">
            <h2>{unique_entities:,}</h2>
            <p>الجهات المشاركة</p>
        </div>
        ''', unsafe_allow_html=True)

    with col3:
        st.markdown(f'''
        <div class="kpi-modern">
            <h2>{unique_natures:,}</h2>
            <p>انواع المشاريع</p>
        </div>
        ''', unsafe_allow_html=True)

    st.write("")

    # Search box
    search_term = st.text_input(
        "البحث",
        placeholder="ابحث باسم المشروع او الوصف...",
        label_visibility="collapsed",
        key="project_search"
    )

    # Filters on same row: Year, Quarter, Clear button
    col1, col2, col3 = st.columns([1, 1, 1])

    with col1:
        years = sorted(df['السنة'].dropna().unique().tolist(), reverse=True)
        year_filter = st.multiselect(
            "السنة",
            options=years,
            placeholder="اختر السنة"
        )

    with col2:
        quarters = df['الربع السنوي'].dropna().unique().tolist()
        quarter_filter = st.multiselect(
            "الربع السنوي",
            options=quarters,
            placeholder="اختر الربع"
        )

    with col3:
        st.write("")  # Spacing to align with dropdowns
        st.markdown('<div class="clear-btn-container">', unsafe_allow_html=True)
        if st.button("مسح الفلاتر", key="clear_proj_filters"):
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    # Apply filters
    filtered_df = df.copy()

    if search_term:
        mask = (
            filtered_df['اسم المشروع'].astype(str).str.contains(search_term, case=False, na=False) |
            filtered_df['وصف المشروع'].astype(str).str.contains(search_term, case=False, na=False)
        )
        filtered_df = filtered_df[mask]

    if year_filter:
        filtered_df = filtered_df[filtered_df['السنة'].isin(year_filter)]

    if quarter_filter:
        filtered_df = filtered_df[filtered_df['الربع السنوي'].isin(quarter_filter)]

    # Stats
    st.markdown(f"**عدد النتائج:** {len(filtered_df):,} مشروع")

    # Calculate dynamic height
    table_height = calculate_table_height(len(filtered_df))

    # Display - full width with dynamic height
    st.dataframe(
        filtered_df,
        column_config={
            "الرقم": st.column_config.NumberColumn("الرقم", format="%d"),
            "السنة": st.column_config.NumberColumn("السنة", format="%d"),
            "المدة (ايام)": st.column_config.NumberColumn("المدة (ايام)", format="%d يوم"),
            "المدة (اشهر)": st.column_config.NumberColumn("المدة (اشهر)", format="%d شهر"),
            "المدة (سنوات)": st.column_config.NumberColumn("المدة (سنوات)", format="%.1f سنة")
        },
        width='stretch',
        height=table_height,
        hide_index=True
    )

    # Project nature chart
    st.subheader("توزيع المشاريع حسب الطبيعة")
    nature_counts = filtered_df['طبيعة المشروع'].value_counts().reset_index()
    nature_counts.columns = ['الطبيعة', 'العدد']

    if not nature_counts.empty:
        fig = px.pie(
            nature_counts.head(10),
            names='الطبيعة',
            values='العدد',
            hole=0.4,
            color_discrete_sequence=GREEN_SHADES
        )
        fig.update_layout(
            font_family="IBM Plex Sans Arabic",
            margin=dict(l=20, r=20, t=20, b=20)
        )
        st.plotly_chart(fig, use_container_width=True)


# =============================================
# PAGE 4: ABOUT (من نحن)
# =============================================
def render_about_page():
    """Render about us page."""

    st.markdown('''
    <h2 style="font-size: 1.8rem; font-weight: 700; margin-bottom: 1.5rem;">
        <span class="text-gradient">من نحن</span>
    </h2>
    ''', unsafe_allow_html=True)

    # Vision
    st.markdown('''
    <div class="about-section">
        <h3>الرؤية</h3>
        <p style="font-size: 1.1rem; line-height: 1.8; color: #374151;">
            ان نكون المنصة الرائدة في تحليل بيانات المشتريات الحكومية في المملكة العربية السعودية،
            مما يساهم في تعزيز الشفافية وتمكين القطاع الخاص من اتخاذ قرارات استثمارية مبنية على البيانات.
        </p>
    </div>
    ''', unsafe_allow_html=True)

    # Mission
    st.markdown('''
    <div class="about-section">
        <h3>الرسالة</h3>
        <p style="font-size: 1.1rem; line-height: 1.8; color: #374151;">
            تقديم حلول ذكية لتحليل بيانات المناقصات والمشاريع الحكومية باستخدام تقنيات الذكاء الاصطناعي،
            لمساعدة الشركات والمستثمرين في فهم السوق واستكشاف الفرص المتاحة.
        </p>
    </div>
    ''', unsafe_allow_html=True)

    # Features
    st.markdown('''
    <div class="about-section">
        <h3>مميزات المنصة</h3>
        <ul style="font-size: 1.1rem; line-height: 2; color: #374151; list-style-type: disc; padding-right: 20px;">
            <li>تحليل ذكي للمناقصات والمشاريع الحكومية</li>
            <li>استعلامات طبيعية باللغة العربية</li>
            <li>قاعدة بيانات شاملة ومحدثة</li>
            <li>تقارير واحصائيات تفاعلية</li>
            <li>واجهة سهلة الاستخدام</li>
        </ul>
    </div>
    ''', unsafe_allow_html=True)

    # Contact
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown('''
        <div class="contact-card">
            <h4>تواصل معنا</h4>
            <p>للاستفسارات والدعم الفني</p>
            <p style="font-size: 1.3rem; font-weight: 700; margin-top: 15px;">
                insight.nabahan@gmail.com
            </p>
        </div>
        ''', unsafe_allow_html=True)

    # Footer info
    st.write("")
    st.write("")
    st.markdown('''
    <div style="text-align: center; color: #6b7280; font-size: 0.9rem;">
        <p>نبهان برو 2026 | جميع الحقوق محفوظة</p>
    </div>
    ''', unsafe_allow_html=True)


# =============================================
# PAGE 5: CONTACT (تواصل معنا)
# =============================================
def render_contact_page():
    """Render contact us page."""

    st.markdown('''
    <h2 style="font-size: 1.8rem; font-weight: 700; margin-bottom: 1.5rem;">
        <span class="text-gradient">تواصل معنا</span>
    </h2>
    ''', unsafe_allow_html=True)

    # Contact intro
    st.markdown('''
    <div class="about-section">
        <h3>نسعد بتواصلكم</h3>
        <p style="font-size: 1.1rem; line-height: 1.8; color: #374151;">
            فريق نبهان مستعد دائما للاجابة على استفساراتكم وتقديم الدعم الفني اللازم.
            لا تترددوا في التواصل معنا عبر القنوات التالية.
        </p>
    </div>
    ''', unsafe_allow_html=True)

    # Contact cards
    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f'''
        <div class="contact-card">
            <h4>البريد الالكتروني</h4>
            <p style="font-size: 1.3rem; font-weight: 700; margin-top: 15px;">
                insight.nabahan@gmail.com
            </p>
        </div>
        ''', unsafe_allow_html=True)

    with col2:
        st.markdown(f'''
        <div class="contact-card">
            <h4>الدعم الفني</h4>
            <p style="font-size: 1.1rem; margin-top: 15px;">
                متاحون من الاحد الى الخميس
            </p>
            <p style="font-size: 1rem;">
                9 صباحا - 5 مساء
            </p>
        </div>
        ''', unsafe_allow_html=True)

    st.write("")
    st.write("")

    # FAQ Section
    st.markdown('''
    <div class="about-section">
        <h3>الاسئلة الشائعة</h3>
    </div>
    ''', unsafe_allow_html=True)

    with st.expander("ما هي مصادر البيانات المستخدمة؟"):
        st.write("نستخدم بيانات المشتريات الحكومية المتاحة من منصة اعتماد الرسمية.")

    with st.expander("كيف يمكنني الاستعلام عن المناقصات؟"):
        st.write("يمكنك استخدام صفحة المنافسات للبحث والتصفية، او طرح اسئلتك مباشرة في صفحة الرئيسية.")

    with st.expander("هل البيانات محدثة؟"):
        st.write("نعم، يتم تحديث البيانات بشكل دوري لضمان دقة المعلومات المقدمة.")

    # Footer
    st.write("")
    st.markdown('''
    <div style="text-align: center; color: #6b7280; font-size: 0.9rem;">
        <p>نبهان برو 2026 | جميع الحقوق محفوظة</p>
    </div>
    ''', unsafe_allow_html=True)


# =============================================
# MAIN APPLICATION
# =============================================
def main():
    """Main application."""
    init_state()

    # Header with navigation
    render_header()

    # Route to current page
    if st.session_state.current_page == 'home':
        render_home_page()
    elif st.session_state.current_page == 'tenders':
        render_tenders_page()
    elif st.session_state.current_page == 'projects':
        render_projects_page()
    elif st.session_state.current_page == 'about':
        render_about_page()

    # Footer
    st.markdown(f'''
    <br><hr>
    <p style="text-align: center; color: #6b7280; font-size: 0.9rem;">
        نبهان برو 2026 | منصة تحليل بيانات المشتريات الحكومية
    </p>
    ''', unsafe_allow_html=True)


if __name__ == "__main__":
    main()
