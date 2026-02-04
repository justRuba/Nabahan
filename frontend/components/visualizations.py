# frontend/components/visualizations.py
# Visualization Components for Nabahan Dashboard
# ===============================================

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Optional, List, Dict, Any


def get_visualization_css() -> str:
    """Return CSS styles for visualizations."""
    return """
    <style>
        /* Chart Container */
        .chart-container {
            background-color: white;
            border-radius: 12px;
            padding: 20px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
            margin: 10px 0;
        }

        /* Chart Title */
        .chart-title {
            font-size: 1.2rem;
            font-weight: bold;
            color: #333;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 2px solid #1f77b4;
        }

        /* Metric Cards */
        .metric-card {
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            border-radius: 12px;
            padding: 20px;
            text-align: center;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        }

        .metric-value {
            font-size: 2.5rem;
            font-weight: bold;
            color: #1f77b4;
        }

        .metric-label {
            font-size: 1rem;
            color: #666;
            margin-top: 5px;
        }

        .metric-delta-positive {
            color: #4caf50;
            font-size: 0.9rem;
        }

        .metric-delta-negative {
            color: #f44336;
            font-size: 0.9rem;
        }

        /* Data Table */
        .data-table-container {
            background-color: white;
            border-radius: 12px;
            padding: 15px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        }

        /* No Data Message */
        .no-data-message {
            text-align: center;
            padding: 40px;
            color: #666;
        }

        .no-data-icon {
            font-size: 3rem;
            margin-bottom: 15px;
        }
    </style>
    """


# Color palette for consistent styling
COLOR_PALETTE = [
    '#1f77b4',  # Blue
    '#ff7f0e',  # Orange
    '#2ca02c',  # Green
    '#d62728',  # Red
    '#9467bd',  # Purple
    '#8c564b',  # Brown
    '#e377c2',  # Pink
    '#7f7f7f',  # Gray
    '#bcbd22',  # Olive
    '#17becf',  # Cyan
]


def render_bar_chart(
        data: pd.DataFrame,
        x_col: str,
        y_col: str,
        title: str = "",
        orientation: str = 'v',
        color_col: Optional[str] = None,
        show_values: bool = True
) -> go.Figure:
    """
    Render a bar chart using Plotly.

    Args:
        data: DataFrame with chart data
        x_col: Column name for x-axis
        y_col: Column name for y-axis
        title: Chart title
        orientation: 'v' for vertical, 'h' for horizontal
        color_col: Optional column for color grouping
        show_values: Whether to show values on bars

    Returns:
        Plotly Figure object
    """
    if orientation == 'h':
        fig = px.bar(
            data,
            x=y_col,
            y=x_col,
            orientation='h',
            color=color_col,
            color_discrete_sequence=COLOR_PALETTE,
            title=title
        )
    else:
        fig = px.bar(
            data,
            x=x_col,
            y=y_col,
            color=color_col,
            color_discrete_sequence=COLOR_PALETTE,
            title=title
        )

    if show_values:
        fig.update_traces(texttemplate='%{value:,.0f}', textposition='outside')

    fig.update_layout(
        font=dict(family="Arial", size=12),
        title_font_size=16,
        showlegend=color_col is not None,
        margin=dict(l=20, r=20, t=60, b=20),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )

    return fig


def render_pie_chart(
        data: pd.DataFrame,
        names_col: str,
        values_col: str,
        title: str = "",
        hole: float = 0.4
) -> go.Figure:
    """
    Render a pie/donut chart using Plotly.

    Args:
        data: DataFrame with chart data
        names_col: Column name for slice labels
        values_col: Column name for slice values
        title: Chart title
        hole: Size of the donut hole (0 for pie, >0 for donut)

    Returns:
        Plotly Figure object
    """
    fig = px.pie(
        data,
        names=names_col,
        values=values_col,
        title=title,
        hole=hole,
        color_discrete_sequence=COLOR_PALETTE
    )

    fig.update_traces(
        textposition='inside',
        textinfo='percent+label'
    )

    fig.update_layout(
        font=dict(family="Arial", size=12),
        title_font_size=16,
        margin=dict(l=20, r=20, t=60, b=20)
    )

    return fig


def render_line_chart(
        data: pd.DataFrame,
        x_col: str,
        y_col: str,
        title: str = "",
        color_col: Optional[str] = None,
        markers: bool = True
) -> go.Figure:
    """
    Render a line chart using Plotly.

    Args:
        data: DataFrame with chart data
        x_col: Column name for x-axis
        y_col: Column name for y-axis
        title: Chart title
        color_col: Optional column for multiple lines
        markers: Whether to show markers on data points

    Returns:
        Plotly Figure object
    """
    fig = px.line(
        data,
        x=x_col,
        y=y_col,
        color=color_col,
        markers=markers,
        title=title,
        color_discrete_sequence=COLOR_PALETTE
    )

    fig.update_layout(
        font=dict(family="Arial", size=12),
        title_font_size=16,
        showlegend=color_col is not None,
        margin=dict(l=20, r=20, t=60, b=20),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(showgrid=True, gridwidth=1, gridcolor='#f0f0f0'),
        yaxis=dict(showgrid=True, gridwidth=1, gridcolor='#f0f0f0')
    )

    return fig


def render_metric_card(
        value: Any,
        label: str,
        delta: Optional[float] = None,
        delta_label: str = "",
        prefix: str = "",
        suffix: str = ""
):
    """
    Render a metric card.

    Args:
        value: The main metric value
        label: Label for the metric
        delta: Optional change value
        delta_label: Label for the delta
        prefix: Prefix for the value (e.g., "$")
        suffix: Suffix for the value (e.g., "%")
    """
    formatted_value = f"{prefix}{value:,}{suffix}" if isinstance(value, (int, float)) else f"{prefix}{value}{suffix}"

    delta_html = ""
    if delta is not None:
        delta_class = "metric-delta-positive" if delta >= 0 else "metric-delta-negative"
        delta_sign = "+" if delta >= 0 else ""
        delta_html = f'<div class="{delta_class}">{delta_sign}{delta:,.1f}% {delta_label}</div>'

    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">{formatted_value}</div>
        <div class="metric-label">{label}</div>
        {delta_html}
    </div>
    """, unsafe_allow_html=True)


def render_data_table(
        data: pd.DataFrame,
        title: str = "",
        max_rows: int = 50,
        height: int = 400
):
    """
    Render a styled data table.

    Args:
        data: DataFrame to display
        title: Optional title for the table
        max_rows: Maximum rows to display
        height: Height of the table in pixels
    """
    if data.empty:
        st.markdown("""
        <div class="no-data-message">
            <div class="no-data-icon">📭</div>
            <p>لا توجد بيانات للعرض</p>
        </div>
        """, unsafe_allow_html=True)
        return

    if title:
        st.markdown(f'<div class="chart-title">{title}</div>', unsafe_allow_html=True)

    st.dataframe(
        data.head(max_rows),
        use_container_width=True,
        height=height
    )


def auto_visualize(
        data: pd.DataFrame,
        plot_type: str = "auto",
        title: str = ""
) -> Optional[go.Figure]:
    """
    Automatically create the best visualization for the data.

    Args:
        data: DataFrame to visualize
        plot_type: Type of plot ("Bar", "Pie", "Line", "auto")
        title: Chart title

    Returns:
        Plotly Figure or None
    """
    if data.empty or len(data.columns) < 1:
        return None

    # Identify column types
    numeric_cols = data.select_dtypes(include=['number']).columns.tolist()
    categorical_cols = data.select_dtypes(include=['object', 'category']).columns.tolist()

    if len(data.columns) < 2:
        return None

    # Determine x and y columns
    x_col = categorical_cols[0] if categorical_cols else data.columns[0]
    y_col = numeric_cols[0] if numeric_cols else data.columns[1]

    # Auto-detect best plot type if not specified
    if plot_type == "auto" or plot_type == "None":
        if len(data) <= 10 and len(numeric_cols) == 1:
            plot_type = "Pie"
        elif len(data) > 20:
            plot_type = "Line"
        else:
            plot_type = "Bar"

    # Create the appropriate chart
    if plot_type == "Bar":
        return render_bar_chart(
            data.head(20),
            x_col=x_col,
            y_col=y_col,
            title=title,
            orientation='h' if len(data) > 5 else 'v'
        )
    elif plot_type == "Pie":
        return render_pie_chart(
            data.head(10),
            names_col=x_col,
            values_col=y_col,
            title=title
        )
    elif plot_type == "Line":
        return render_line_chart(
            data,
            x_col=x_col,
            y_col=y_col,
            title=title
        )

    return None


def render_dashboard_metrics(metrics: List[Dict[str, Any]]):
    """
    Render a row of metric cards.

    Args:
        metrics: List of metric dictionaries with keys:
                 value, label, delta (optional), prefix (optional), suffix (optional)
    """
    cols = st.columns(len(metrics))

    for i, metric in enumerate(metrics):
        with cols[i]:
            render_metric_card(
                value=metric.get('value', 0),
                label=metric.get('label', ''),
                delta=metric.get('delta'),
                delta_label=metric.get('delta_label', ''),
                prefix=metric.get('prefix', ''),
                suffix=metric.get('suffix', '')
            )


def render_chart_with_options(
        data: pd.DataFrame,
        default_type: str = "Bar",
        key_prefix: str = "chart"
):
    """
    Render a chart with user-selectable options.

    Args:
        data: DataFrame to visualize
        default_type: Default chart type
        key_prefix: Prefix for widget keys
    """
    if data.empty:
        st.warning("لا توجد بيانات للرسم البياني")
        return

    # Chart type selector
    col1, col2 = st.columns([3, 1])

    with col2:
        chart_type = st.selectbox(
            "نوع الرسم",
            options=["Bar", "Pie", "Line"],
            index=["Bar", "Pie", "Line"].index(default_type) if default_type in ["Bar", "Pie", "Line"] else 0,
            key=f"{key_prefix}_type"
        )

    # Render chart
    fig = auto_visualize(data, plot_type=chart_type)
    if fig:
        st.plotly_chart(fig, use_container_width=True)


class DashboardSection:
    """A reusable dashboard section component."""

    def __init__(self, title: str, icon: str = "📊"):
        """
        Initialize a dashboard section.

        Args:
            title: Section title
            icon: Emoji icon for the section
        """
        self.title = title
        self.icon = icon

    def render_header(self):
        """Render the section header."""
        st.markdown(f"""
        <div style="margin-bottom: 20px;">
            <h3 style="color: #1f77b4; margin: 0;">
                {self.icon} {self.title}
            </h3>
            <hr style="margin-top: 10px; border: none; border-top: 2px solid #e0e0e0;">
        </div>
        """, unsafe_allow_html=True)

    def __enter__(self):
        """Context manager entry."""
        self.render_header()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        st.markdown("<div style='margin-bottom: 30px;'></div>", unsafe_allow_html=True)
