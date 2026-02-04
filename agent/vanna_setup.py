# agent/vanna_setup.py
# Vanna AI + Groq Integration for Nabahan
# ========================================
# Text-to-SQL using Vanna AI framework with Groq LLM (OpenAI-compatible API)

import sqlite3
from pathlib import Path
from typing import List, Dict, Optional

from openai import OpenAI
from vanna.openai import OpenAI_Chat
from vanna.chromadb import ChromaDB_VectorStore

from agent.config import (
    GROQ_API_KEY,
    GROQ_MODEL_NAME,
    DB_PATH,
    DATABASE_SCHEMA
)


class NabahanVanna(ChromaDB_VectorStore, OpenAI_Chat):
    """
    Custom Vanna class combining ChromaDB for vector storage
    and Groq LLM (via OpenAI-compatible API) for SQL generation.
    """
    def __init__(self, chromadb_config=None, openai_config=None):
        ChromaDB_VectorStore.__init__(self, config=chromadb_config)
        OpenAI_Chat.__init__(self, config=openai_config)


# Global Vanna instance
_vanna_instance: Optional[NabahanVanna] = None


def get_vanna_instance() -> NabahanVanna:
    """
    Get or create the Vanna instance with Groq configuration.
    Uses Groq's OpenAI-compatible API endpoint.
    """
    global _vanna_instance

    if _vanna_instance is None:
        # Create OpenAI client pointing to Groq API
        groq_client = OpenAI(
            api_key=GROQ_API_KEY,
            base_url='https://api.groq.com/openai/v1'
        )

        _vanna_instance = NabahanVanna(
            chromadb_config={},
            openai_config={
                'client': groq_client,
                'model': GROQ_MODEL_NAME
            }
        )

        # Connect to SQLite database
        _vanna_instance.connect_to_sqlite(DB_PATH)

    return _vanna_instance


def get_table_ddl(table_name: str) -> str:
    """
    Extract DDL (CREATE TABLE statement) for a given table.
    """
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute(f"SELECT sql FROM sqlite_master WHERE type='table' AND name='{table_name}'")
            result = cursor.fetchone()
            return result[0] if result else ""
    except Exception:
        return ""


def get_all_ddl() -> str:
    """
    Get DDL for all tables in the database.
    """
    table_names = [
        'tenders_full_details',
        'future_projects',
        'government_entity',
        'regions',
        'tender_statuses',
        'tender_types',
        'primary_activity'
    ]

    ddl_statements = []
    for table_name in table_names:
        ddl = get_table_ddl(table_name)
        if ddl:
            ddl_statements.append(ddl)
    return "\n\n".join(ddl_statements)


def get_training_pairs() -> List[Dict[str, str]]:
    """
    Return sample question-SQL pairs for Vanna training.
    """
    return [
        {
            "question": "كم عدد المناقصات الحالية؟",
            "sql": "SELECT COUNT(*) as total_tenders FROM tenders_full_details"
        },
        {
            "question": "كم عدد المناقصات في منطقة الرياض؟",
            "sql": "SELECT COUNT(*) as riyadh_tenders FROM tenders_full_details WHERE execution_location LIKE '%الرياض%'"
        },
        {
            "question": "ما هي الجهات الحكومية التي لديها أكثر المناقصات؟",
            "sql": "SELECT government_entity, COUNT(*) as tender_count FROM tenders_full_details GROUP BY government_entity ORDER BY tender_count DESC LIMIT 10"
        },
        {
            "question": "كم عدد المشاريع المستقبلية؟",
            "sql": "SELECT COUNT(*) as total_projects FROM future_projects"
        },
        {
            "question": "ما هي المشاريع المخططة لسنة 2024؟",
            "sql": "SELECT project_name, government_entity, project_status FROM future_projects WHERE year = 2024 LIMIT 20"
        },
        {
            "question": "توزيع المناقصات حسب حالتها",
            "sql": "SELECT tender_status, COUNT(*) as count FROM tenders_full_details GROUP BY tender_status ORDER BY count DESC"
        },
        {
            "question": "ما هي المناطق السعودية المتاحة؟",
            "sql": "SELECT region_name FROM regions ORDER BY region_name"
        },
        {
            "question": "ما هي المناقصات المجانية؟",
            "sql": "SELECT tender_name, government_entity FROM tenders_full_details WHERE tender_document_value = 0 OR tender_document_value = 0.0 LIMIT 20"
        },
        {
            "question": "أعلى 5 جهات حكومية من حيث عدد المشاريع المستقبلية",
            "sql": "SELECT government_entity, COUNT(*) as project_count FROM future_projects GROUP BY government_entity ORDER BY project_count DESC LIMIT 5"
        },
        {
            "question": "توزيع المشاريع المستقبلية حسب السنة",
            "sql": "SELECT year, COUNT(*) as project_count FROM future_projects GROUP BY year ORDER BY year"
        },
        {
            "question": "ما هي انواع المنافسات المتاحة؟",
            "sql": "SELECT tender_type_name FROM tender_types ORDER BY tender_type_name"
        },
        {
            "question": "عدد المناقصات حسب النشاط",
            "sql": "SELECT competition_activity, COUNT(*) as count FROM tenders_full_details GROUP BY competition_activity ORDER BY count DESC LIMIT 10"
        },
        {
            "question": "المشاريع في منطقة مكة المكرمة",
            "sql": "SELECT project_name, government_entity FROM future_projects WHERE execution_location LIKE '%مكة%' LIMIT 20"
        },
        {
            "question": "متوسط مدة المشاريع بالأيام",
            "sql": "SELECT AVG(expected_duration_days) as avg_duration FROM future_projects WHERE expected_duration_days IS NOT NULL"
        },
        {
            "question": "عدد الجهات الحكومية",
            "sql": "SELECT COUNT(*) as total_entities FROM government_entity"
        }
    ]


def train_vanna() -> bool:
    """
    Train Vanna on the database schema and sample queries.
    Returns True if training was successful.
    """
    try:
        vn = get_vanna_instance()

        # Train on DDL (database schema)
        ddl = get_all_ddl()
        if ddl:
            vn.train(ddl=ddl)
            print("Trained on DDL schema")

        # Train on documentation
        vn.train(documentation=DATABASE_SCHEMA)
        print("Trained on documentation")

        # Train on sample question-SQL pairs
        training_pairs = get_training_pairs()
        for pair in training_pairs:
            vn.train(
                question=pair["question"],
                sql=pair["sql"]
            )
        print(f"Trained on {len(training_pairs)} Q&A pairs")

        return True

    except Exception as e:
        print(f"Training error: {str(e)}")
        return False


def generate_sql_with_vanna(question: str) -> Optional[str]:
    """
    Generate SQL from natural language question using Vanna.
    """
    try:
        vn = get_vanna_instance()
        sql = vn.generate_sql(question)
        return sql
    except Exception as e:
        print(f"SQL generation error: {str(e)}")
        return None


def ask_vanna(question: str) -> Dict:
    """
    Full Vanna pipeline: generate SQL, run it, and get results.
    Returns dict with sql, dataframe, and any error.
    """
    try:
        vn = get_vanna_instance()

        # Generate SQL
        sql = vn.generate_sql(question)
        if not sql:
            return {"sql": None, "df": None, "error": "Could not generate SQL"}

        # Run SQL
        df = vn.run_sql(sql)

        return {
            "sql": sql,
            "df": df,
            "error": None
        }

    except Exception as e:
        return {
            "sql": None,
            "df": None,
            "error": str(e)
        }


def get_trained_vanna() -> NabahanVanna:
    """
    Get the trained Vanna instance.
    Trains on first call if not already trained.
    """
    vn = get_vanna_instance()

    # Check if we need to train (simple check)
    try:
        # Try to get training data count
        training_data = vn.get_training_data()
        if training_data is None or len(training_data) == 0:
            print("Training Vanna...")
            train_vanna()
    except Exception:
        # If get_training_data fails, train anyway
        print("Initializing Vanna training...")
        train_vanna()

    return vn


if __name__ == "__main__":
    print("=" * 50)
    print("Nabahan Vanna AI Setup")
    print("=" * 50)

    # Initialize and train
    print("\n1. Initializing Vanna with Groq...")
    vn = get_vanna_instance()
    print(f"   Model: {GROQ_MODEL_NAME}")
    print(f"   Database: {DB_PATH}")

    print("\n2. Training Vanna...")
    success = train_vanna()

    if success:
        print("\n3. Testing SQL generation...")
        test_questions = [
            "كم عدد المناقصات؟",
            "ما هي الجهات الاكثر طرحا للمنافسات؟"
        ]

        for q in test_questions:
            print(f"\n   Q: {q}")
            sql = generate_sql_with_vanna(q)
            print(f"   SQL: {sql}")

    print("\n" + "=" * 50)
    print("Setup complete!")
