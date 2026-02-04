# agent/nabahan_logic.py
# Nabahan AI Agent - Core Logic with Vanna AI + Groq Integration

import sqlite3
import pandas as pd
import json
import re
from typing import Dict, Any, Optional, List
from groq import Groq

from agent.config import (
    GROQ_API_KEY,
    GROQ_MODEL_NAME,
    DB_PATH,
    SQL_SYSTEM_PROMPT,
    INSIGHTS_SYSTEM_PROMPT,
    OUT_OF_SCOPE_MESSAGE,
    VALID_CHART_TYPES
)

# Initialize Groq client
groq_client = Groq(api_key=GROQ_API_KEY)

# Vanna integration flag - set to True to use Vanna for SQL generation
# Note: Keep False on Windows due to console encoding issues with Arabic text
USE_VANNA = False

# Lazy-loaded Vanna instance
_vanna = None


def get_vanna():
    """Get Vanna instance (lazy initialization)."""
    global _vanna
    if _vanna is None and USE_VANNA:
        try:
            from agent.vanna_setup import get_trained_vanna
            _vanna = get_trained_vanna()
        except Exception as e:
            print(f"Vanna initialization failed: {e}")
            return None
    return _vanna


def execute_sql(sql_query: str) -> pd.DataFrame:
    """Execute SQL query on SQLite database."""
    try:
        with sqlite3.connect(DB_PATH) as conn:
            return pd.read_sql_query(sql_query, conn)
    except Exception as e:
        raise Exception(f"SQL error: {str(e)}")


def generate_sql(question: str, filters: Optional[Dict] = None) -> str:
    """Generate SQL using Vanna AI or Groq LLM (based on USE_VANNA flag)."""

    sql = None

    # Try Vanna first if enabled
    if USE_VANNA:
        vn = get_vanna()
        if vn:
            try:
                sql = vn.generate_sql(question)
                if sql:
                    sql = sql.strip()
            except Exception as e:
                print(f"Vanna SQL generation failed: {e}, falling back to Groq")
                sql = None

    # Fall back to direct Groq if Vanna not used or failed
    if sql is None:
        # Build filter context
        filter_text = ""
        if filters:
            parts = []
            if filters.get('regions'):
                parts.append(f"المناطق: {', '.join(filters['regions'])}")
            if filters.get('government_entity'):
                parts.append(f"الجهات: {', '.join(filters['government_entity'][:5])}")
            if filters.get('tender_statuses'):
                parts.append(f"الحالات: {', '.join(filters['tender_statuses'])}")
            if parts:
                filter_text = f"\nالفلاتر: {' | '.join(parts)}"

        user_prompt = f"السؤال: {question}{filter_text}\n\nSQL:"

        try:
            completion = groq_client.chat.completions.create(
                model=GROQ_MODEL_NAME,
                messages=[
                    {"role": "system", "content": SQL_SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0,
                max_tokens=500
            )

            sql = completion.choices[0].message.content.strip()

        except Exception as e:
            raise Exception(f"SQL generation error: {str(e)}")

    # Clean SQL
    sql = re.sub(r'```sql\s*', '', sql)
    sql = re.sub(r'```\s*', '', sql)
    sql = sql.strip()

    # Fix circular references
    sql = re.sub(r'WITH\s+future_projects\s+AS', 'WITH fp_data AS', sql, flags=re.IGNORECASE)
    sql = re.sub(r'WITH\s+tenders_full_details\s+AS', 'WITH t_data AS', sql, flags=re.IGNORECASE)

    # Apply filters
    if filters:
        sql = apply_filters(sql, filters)

    return sql


def apply_filters(sql: str, filters: Dict) -> str:
    """Apply filters to SQL query."""
    where_parts = []

    if filters.get('regions'):
        conds = [f"execution_location LIKE '%{r}%'" for r in filters['regions']]
        where_parts.append(f"({' OR '.join(conds)})")

    if filters.get('government_entity'):
        ents = [f"'{e}'" for e in filters['government_entity']]
        where_parts.append(f"government_entity IN ({', '.join(ents)})")

    if filters.get('tender_statuses'):
        conds = [f"tender_status LIKE '%{s}%'" for s in filters['tender_statuses']]
        where_parts.append(f"({' OR '.join(conds)})")

    if not where_parts:
        return sql

    filter_clause = ' AND '.join(where_parts)
    sql_upper = sql.upper()

    if 'WHERE' in sql_upper:
        idx = sql_upper.find('WHERE') + 5
        sql = sql[:idx] + f" {filter_clause} AND" + sql[idx:]
    else:
        for kw in ['GROUP BY', 'ORDER BY', 'LIMIT']:
            if kw in sql_upper:
                idx = sql_upper.find(kw)
                sql = sql[:idx] + f" WHERE {filter_clause} " + sql[idx:]
                break
        else:
            sql += f" WHERE {filter_clause}"

    return sql


def generate_insights(question: str, data: pd.DataFrame, sql: str) -> Dict[str, Any]:
    """Generate Arabic insights using Groq."""

    if data.empty:
        return {"insights": OUT_OF_SCOPE_MESSAGE, "chart_type": "none"}

    # Prepare data summary
    cols = ', '.join(data.columns.tolist())
    rows_str = data.head(15).to_string(index=False)

    numeric_stats = ""
    for col in data.select_dtypes(include=['number']).columns:
        numeric_stats += f"\n{col}: مجموع={data[col].sum():.0f}, متوسط={data[col].mean():.1f}"

    user_prompt = f"""السؤال: {question}

SQL: {sql}

البيانات ({len(data)} صف):
الاعمدة: {cols}

{rows_str}
{numeric_stats}

حلل البيانات واجب بـ JSON."""

    try:
        completion = groq_client.chat.completions.create(
            model=GROQ_MODEL_NAME,
            messages=[
                {"role": "system", "content": INSIGHTS_SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.3,
            response_format={"type": "json_object"}
        )

        resp = json.loads(completion.choices[0].message.content)
        insights = resp.get('insights', OUT_OF_SCOPE_MESSAGE)
        chart = resp.get('chart_type', 'none').lower()

        if chart not in VALID_CHART_TYPES:
            chart = 'none'

        return {"insights": insights, "chart_type": chart}

    except Exception as e:
        return {"insights": f"خطا في التحليل: {str(e)}", "chart_type": "none"}


def is_in_scope(question: str) -> bool:
    """Check if question is within database scope."""
    keywords = [
        'مناقصة', 'مناقصات', 'منافسة', 'منافسات', 'مشروع', 'مشاريع',
        'جهة', 'جهات', 'حكومية', 'وزارة', 'هيئة', 'منطقة', 'مناطق',
        'الرياض', 'مكة', 'جدة', 'نشاط', 'انشطة', 'حالة', 'نوع',
        'عدد', 'كم', 'اجمالي', 'توزيع', 'احصائيات', 'سنة', 'ربع'
    ]
    return any(kw in question for kw in keywords)


def nabahan_agent(question: str, filters: Optional[Dict] = None) -> Dict[str, Any]:
    """
    Main agent function.
    Returns: {status, data, insights, chart_type, sql}
    """

    # Check scope
    if not is_in_scope(question):
        return {
            "status": "out_of_scope",
            "data": pd.DataFrame(),
            "insights": OUT_OF_SCOPE_MESSAGE,
            "chart_type": "none",
            "sql": ""
        }

    for attempt in range(3):
        try:
            # Generate SQL
            sql = generate_sql(question, filters)

            # Validate
            if not sql or 'SELECT' not in sql.upper():
                continue

            # Execute
            data = execute_sql(sql)

            if data.empty and attempt < 2:
                continue

            if data.empty:
                return {
                    "status": "no_data",
                    "data": pd.DataFrame(),
                    "insights": OUT_OF_SCOPE_MESSAGE,
                    "chart_type": "none",
                    "sql": sql
                }

            # Generate insights
            result = generate_insights(question, data, sql)

            return {
                "status": "success",
                "data": data,
                "insights": result["insights"],
                "chart_type": result["chart_type"],
                "sql": sql
            }

        except Exception as e:
            if attempt == 2:
                return {
                    "status": "error",
                    "data": pd.DataFrame(),
                    "insights": OUT_OF_SCOPE_MESSAGE,
                    "chart_type": "none",
                    "sql": "",
                    "error": str(e)
                }

    return {
        "status": "error",
        "data": pd.DataFrame(),
        "insights": OUT_OF_SCOPE_MESSAGE,
        "chart_type": "none",
        "sql": ""
    }


def get_filter_options() -> Dict[str, List[str]]:
    """Get filter options from database."""
    options = {}

    try:
        with sqlite3.connect(DB_PATH) as conn:
            # Regions
            df = pd.read_sql_query("SELECT region_name FROM regions ORDER BY region_name", conn)
            options['regions'] = df['region_name'].dropna().tolist()

            # Statuses
            df = pd.read_sql_query("SELECT status_name FROM tender_statuses ORDER BY status_name", conn)
            options['tender_statuses'] = df['status_name'].dropna().tolist()

            # Top entities
            df = pd.read_sql_query("""
                SELECT government_entity, COUNT(*) as c
                FROM tenders_full_details
                GROUP BY government_entity
                ORDER BY c DESC LIMIT 50
            """, conn)
            options['government_entity'] = df['government_entity'].dropna().tolist()

    except Exception:
        options = {'regions': [], 'tender_statuses': [], 'government_entity': []}

    return options


def get_kpi_stats() -> Dict[str, int]:
    """Get KPI statistics."""
    try:
        with sqlite3.connect(DB_PATH) as conn:
            tenders = conn.execute("SELECT COUNT(*) FROM tenders_full_details").fetchone()[0]
            projects = conn.execute("SELECT COUNT(*) FROM future_projects").fetchone()[0]
            entities = conn.execute("SELECT COUNT(*) FROM government_entity").fetchone()[0]
            activities = conn.execute("SELECT COUNT(*) FROM primary_activity").fetchone()[0]
        return {
            'tenders': tenders,
            'projects': projects,
            'entities': entities,
            'activities': activities
        }
    except Exception:
        return {'tenders': 0, 'projects': 0, 'entities': 0, 'activities': 0}


def get_activity_chart_data() -> pd.DataFrame:
    """Get top activities for chart."""
    try:
        with sqlite3.connect(DB_PATH) as conn:
            return pd.read_sql_query("""
                SELECT competition_activity as activity, COUNT(*) as count
                FROM tenders_full_details
                WHERE competition_activity IS NOT NULL
                GROUP BY competition_activity
                ORDER BY count DESC LIMIT 10
            """, conn)
    except Exception:
        return pd.DataFrame()


def get_nature_chart_data() -> pd.DataFrame:
    """Get project nature distribution."""
    try:
        with sqlite3.connect(DB_PATH) as conn:
            return pd.read_sql_query("""
                SELECT project_nature, COUNT(*) as count
                FROM future_projects
                WHERE project_nature IS NOT NULL
                GROUP BY project_nature
                ORDER BY count DESC LIMIT 8
            """, conn)
    except Exception:
        return pd.DataFrame()
