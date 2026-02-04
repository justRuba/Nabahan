# frontend/components/sidebar_filters.py
# Collapsible Sidebar Filters with Hamburger Menu
# ================================================

import streamlit as st
from typing import Dict, List, Callable, Optional


def get_hamburger_css() -> str:
    """Return CSS for hamburger menu and collapsible sidebar."""
    return """
    <style>
        /* Hamburger Button Container */
        .hamburger-container {
            position: fixed;
            top: 14px;
            left: 60px;
            z-index: 1000;
        }

        /* Hamburger Button */
        .hamburger-button {
            display: flex;
            flex-direction: column;
            justify-content: space-around;
            width: 30px;
            height: 25px;
            background: transparent;
            border: none;
            cursor: pointer;
            padding: 0;
            z-index: 1001;
        }

        .hamburger-button:focus {
            outline: none;
        }

        .hamburger-line {
            width: 30px;
            height: 3px;
            background-color: #1f77b4;
            border-radius: 2px;
            transition: all 0.3s ease;
        }

        /* Hamburger Animation when open */
        .hamburger-button.open .hamburger-line:nth-child(1) {
            transform: rotate(45deg) translate(5px, 5px);
        }

        .hamburger-button.open .hamburger-line:nth-child(2) {
            opacity: 0;
        }

        .hamburger-button.open .hamburger-line:nth-child(3) {
            transform: rotate(-45deg) translate(7px, -6px);
        }

        /* Sidebar Overlay */
        .sidebar-overlay {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0, 0, 0, 0.5);
            z-index: 998;
            opacity: 0;
            visibility: hidden;
            transition: opacity 0.3s ease, visibility 0.3s ease;
        }

        .sidebar-overlay.visible {
            opacity: 1;
            visibility: visible;
        }

        /* Custom Sidebar Panel */
        .filter-sidebar {
            position: fixed;
            top: 0;
            left: -350px;
            width: 350px;
            height: 100%;
            background-color: #ffffff;
            box-shadow: 2px 0 10px rgba(0, 0, 0, 0.2);
            z-index: 999;
            transition: left 0.3s ease;
            overflow-y: auto;
            direction: rtl;
        }

        .filter-sidebar.open {
            left: 0;
        }

        /* Sidebar Header */
        .sidebar-header {
            background: linear-gradient(135deg, #1f77b4 0%, #0d47a1 100%);
            color: white;
            padding: 20px;
            text-align: center;
        }

        .sidebar-header h2 {
            margin: 0;
            font-size: 1.5rem;
        }

        .sidebar-header p {
            margin: 5px 0 0 0;
            opacity: 0.8;
            font-size: 0.9rem;
        }

        /* Filter Section */
        .filter-section {
            padding: 15px 20px;
            border-bottom: 1px solid #e0e0e0;
        }

        .filter-section-title {
            display: flex;
            align-items: center;
            gap: 10px;
            font-weight: bold;
            color: #333;
            margin-bottom: 10px;
        }

        .filter-section-icon {
            font-size: 1.2rem;
        }

        /* Filter Badge */
        .filter-badge {
            display: inline-block;
            background-color: #1f77b4;
            color: white;
            padding: 2px 8px;
            border-radius: 12px;
            font-size: 0.75rem;
            margin-left: 5px;
        }

        /* Clear Filters Button */
        .clear-filters-btn {
            width: calc(100% - 40px);
            margin: 20px;
            padding: 12px;
            background-color: #f44336;
            color: white;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-size: 1rem;
            transition: background-color 0.2s ease;
        }

        .clear-filters-btn:hover {
            background-color: #d32f2f;
        }

        /* Active Filters Summary */
        .active-filters-summary {
            background-color: #e3f2fd;
            padding: 15px 20px;
            margin: 10px 20px;
            border-radius: 8px;
            border-left: 4px solid #1f77b4;
        }

        .active-filters-summary h4 {
            margin: 0 0 10px 0;
            color: #1f77b4;
        }

        .active-filter-tag {
            display: inline-block;
            background-color: #1f77b4;
            color: white;
            padding: 4px 10px;
            border-radius: 15px;
            font-size: 0.8rem;
            margin: 3px;
        }

        /* Close button for sidebar */
        .close-sidebar-btn {
            position: absolute;
            top: 15px;
            right: 15px;
            background: rgba(255, 255, 255, 0.2);
            border: none;
            color: white;
            width: 30px;
            height: 30px;
            border-radius: 50%;
            cursor: pointer;
            font-size: 1.2rem;
            display: flex;
            align-items: center;
            justify-content: center;
        }

        .close-sidebar-btn:hover {
            background: rgba(255, 255, 255, 0.3);
        }
    </style>
    """


def render_hamburger_button(is_open: bool = False) -> str:
    """
    Render the hamburger menu button HTML.

    Args:
        is_open: Whether the sidebar is currently open

    Returns:
        HTML string for the hamburger button
    """
    open_class = "open" if is_open else ""
    return f"""
    <div class="hamburger-container">
        <button class="hamburger-button {open_class}" onclick="toggleSidebar()">
            <span class="hamburger-line"></span>
            <span class="hamburger-line"></span>
            <span class="hamburger-line"></span>
        </button>
    </div>
    """


def render_filter_sidebar(
        filter_options: Dict[str, List[str]],
        selected_filters: Dict[str, List[str]],
        is_open: bool = False
) -> str:
    """
    Render the filter sidebar HTML.

    Args:
        filter_options: Dictionary of available filter options
        selected_filters: Dictionary of currently selected filters
        is_open: Whether the sidebar is currently open

    Returns:
        HTML string for the filter sidebar
    """
    open_class = "open" if is_open else ""

    # Count active filters
    active_count = sum(len(v) for v in selected_filters.values() if v)

    # Build filter sections
    filter_sections = ""

    # Regions
    regions = filter_options.get('regions', [])
    selected_regions = selected_filters.get('regions', [])
    region_badge = f'<span class="filter-badge">{len(selected_regions)}</span>' if selected_regions else ''
    filter_sections += f"""
    <div class="filter-section">
        <div class="filter-section-title">
            <span class="filter-section-icon">📍</span>
            <span>المناطق {region_badge}</span>
        </div>
        <div id="region-filters">
            <!-- Streamlit multiselect will be rendered here -->
        </div>
    </div>
    """

    # Government Entities
    entities = filter_options.get('government_entity', [])
    selected_entities = selected_filters.get('government_entity', [])
    entity_badge = f'<span class="filter-badge">{len(selected_entities)}</span>' if selected_entities else ''
    filter_sections += f"""
    <div class="filter-section">
        <div class="filter-section-title">
            <span class="filter-section-icon">🏛️</span>
            <span>الجهات الحكومية {entity_badge}</span>
        </div>
        <div id="entity-filters">
            <!-- Streamlit multiselect will be rendered here -->
        </div>
    </div>
    """

    # Tender Statuses
    statuses = filter_options.get('tender_statuses', [])
    selected_statuses = selected_filters.get('tender_statuses', [])
    status_badge = f'<span class="filter-badge">{len(selected_statuses)}</span>' if selected_statuses else ''
    filter_sections += f"""
    <div class="filter-section">
        <div class="filter-section-title">
            <span class="filter-section-icon">📋</span>
            <span>حالة المناقصة {status_badge}</span>
        </div>
        <div id="status-filters">
            <!-- Streamlit multiselect will be rendered here -->
        </div>
    </div>
    """

    # Tender Types
    types = filter_options.get('tender_types', [])
    selected_types = selected_filters.get('tender_types', [])
    type_badge = f'<span class="filter-badge">{len(selected_types)}</span>' if selected_types else ''
    filter_sections += f"""
    <div class="filter-section">
        <div class="filter-section-title">
            <span class="filter-section-icon">📑</span>
            <span>نوع المناقصة {type_badge}</span>
        </div>
        <div id="type-filters">
            <!-- Streamlit multiselect will be rendered here -->
        </div>
    </div>
    """

    # Active filters summary
    active_summary = ""
    if active_count > 0:
        tags = ""
        for region in selected_regions:
            tags += f'<span class="active-filter-tag">{region}</span>'
        for entity in selected_entities[:3]:
            tags += f'<span class="active-filter-tag">{entity[:20]}...</span>'
        for status in selected_statuses:
            tags += f'<span class="active-filter-tag">{status}</span>'
        for t in selected_types:
            tags += f'<span class="active-filter-tag">{t}</span>'

        active_summary = f"""
        <div class="active-filters-summary">
            <h4>✓ الفلاتر النشطة ({active_count})</h4>
            {tags}
        </div>
        """

    return f"""
    <div class="sidebar-overlay {'visible' if is_open else ''}" onclick="toggleSidebar()"></div>
    <div class="filter-sidebar {open_class}">
        <div class="sidebar-header">
            <button class="close-sidebar-btn" onclick="toggleSidebar()">×</button>
            <h2>☰ فلاتر البحث</h2>
            <p>تصفية وتخصيص النتائج</p>
        </div>

        {active_summary}

        {filter_sections}

        <button class="clear-filters-btn" onclick="clearAllFilters()">
            🗑️ مسح جميع الفلاتر
        </button>
    </div>
    """


def get_sidebar_js() -> str:
    """Return JavaScript for sidebar interactions."""
    return """
    <script>
        function toggleSidebar() {
            const sidebar = document.querySelector('.filter-sidebar');
            const overlay = document.querySelector('.sidebar-overlay');
            const hamburger = document.querySelector('.hamburger-button');

            if (sidebar) {
                sidebar.classList.toggle('open');
            }
            if (overlay) {
                overlay.classList.toggle('visible');
            }
            if (hamburger) {
                hamburger.classList.toggle('open');
            }
        }

        function clearAllFilters() {
            // Trigger Streamlit to clear filters
            window.parent.postMessage({type: 'streamlit:clearFilters'}, '*');
        }

        // Close sidebar on escape key
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape') {
                const sidebar = document.querySelector('.filter-sidebar');
                if (sidebar && sidebar.classList.contains('open')) {
                    toggleSidebar();
                }
            }
        });
    </script>
    """


class SidebarFilters:
    """
    A reusable class for managing collapsible sidebar filters.
    """

    def __init__(self, filter_options: Dict[str, List[str]]):
        """
        Initialize the sidebar filters.

        Args:
            filter_options: Dictionary of available filter options
        """
        self.filter_options = filter_options
        self._initialize_session_state()

    def _initialize_session_state(self):
        """Initialize session state for filters."""
        if 'sidebar_open' not in st.session_state:
            st.session_state.sidebar_open = False

        if 'selected_filters' not in st.session_state:
            st.session_state.selected_filters = {
                'regions': [],
                'government_entity': [],
                'tender_statuses': [],
                'tender_types': []
            }

    def render(self) -> Dict[str, List[str]]:
        """
        Render the sidebar filters and return selected values.

        Returns:
            Dictionary of selected filter values
        """
        # Inject CSS
        st.markdown(get_hamburger_css(), unsafe_allow_html=True)

        # Render hamburger button (handled by Streamlit's native sidebar toggle)
        # The actual filtering is done in the Streamlit sidebar

        with st.sidebar:
            st.markdown("""
            <div style="text-align: center; padding: 20px; background: linear-gradient(135deg, #1f77b4 0%, #0d47a1 100%); color: white; margin: -1rem -1rem 1rem -1rem; border-radius: 0;">
                <h2 style="margin: 0;">☰ فلاتر البحث</h2>
                <p style="margin: 5px 0 0 0; opacity: 0.8;">تصفية وتخصيص النتائج</p>
            </div>
            """, unsafe_allow_html=True)

            # Region filter
            st.markdown("##### 📍 المناطق")
            selected_regions = st.multiselect(
                "اختر المناطق",
                options=self.filter_options.get('regions', []),
                default=st.session_state.selected_filters.get('regions', []),
                key='filter_regions',
                label_visibility="collapsed"
            )
            st.session_state.selected_filters['regions'] = selected_regions

            st.markdown("---")

            # Government entity filter
            st.markdown("##### 🏛️ الجهات الحكومية")
            entities = self.filter_options.get('government_entity', [])[:100]
            selected_entities = st.multiselect(
                "اختر الجهات",
                options=entities,
                default=[e for e in st.session_state.selected_filters.get('government_entity', []) if e in entities],
                key='filter_entities',
                label_visibility="collapsed"
            )
            st.session_state.selected_filters['government_entity'] = selected_entities

            st.markdown("---")

            # Tender status filter
            st.markdown("##### 📋 حالة المناقصة")
            selected_statuses = st.multiselect(
                "اختر الحالات",
                options=self.filter_options.get('tender_statuses', []),
                default=st.session_state.selected_filters.get('tender_statuses', []),
                key='filter_statuses',
                label_visibility="collapsed"
            )
            st.session_state.selected_filters['tender_statuses'] = selected_statuses

            st.markdown("---")

            # Tender type filter
            st.markdown("##### 📑 نوع المناقصة")
            selected_types = st.multiselect(
                "اختر الأنواع",
                options=self.filter_options.get('tender_types', []),
                default=st.session_state.selected_filters.get('tender_types', []),
                key='filter_types',
                label_visibility="collapsed"
            )
            st.session_state.selected_filters['tender_types'] = selected_types

            st.markdown("---")

            # Clear all button
            if st.button("🗑️ مسح جميع الفلاتر", use_container_width=True):
                st.session_state.selected_filters = {
                    'regions': [],
                    'government_entity': [],
                    'tender_statuses': [],
                    'tender_types': []
                }
                st.rerun()

            # Show active filter count
            active_count = sum(len(v) for v in st.session_state.selected_filters.values())
            if active_count > 0:
                st.success(f"✓ {active_count} فلتر نشط")

        return st.session_state.selected_filters

    def get_active_filters(self) -> Dict[str, List[str]]:
        """
        Get only the active (non-empty) filters.

        Returns:
            Dictionary of active filter values
        """
        return {
            k: v for k, v in st.session_state.selected_filters.items()
            if v
        }
