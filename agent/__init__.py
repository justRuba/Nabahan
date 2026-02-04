# agent/__init__.py
# Nabahan AI Agent Package

from agent.nabahan_logic import (
    nabahan_agent,
    execute_sql,
    get_filter_options,
    get_kpi_stats,
    get_activity_chart_data,
    get_nature_chart_data
)

from agent.config import (
    GROQ_API_KEY,
    GROQ_MODEL_NAME,
    DB_PATH,
    OUT_OF_SCOPE_MESSAGE,
    PRIMARY_COLOR,
    SECONDARY_COLOR
)

__all__ = [
    'nabahan_agent',
    'execute_sql',
    'get_filter_options',
    'get_kpi_stats',
    'get_activity_chart_data',
    'get_nature_chart_data',
    'GROQ_API_KEY',
    'GROQ_MODEL_NAME',
    'DB_PATH',
    'OUT_OF_SCOPE_MESSAGE',
    'PRIMARY_COLOR',
    'SECONDARY_COLOR'
]
