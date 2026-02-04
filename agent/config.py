# agent/config.py
# Nabahan AI Agent Configuration

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(env_path)

def get_api_key():
    """Get API key from environment or Streamlit secrets."""
    # First try environment variable
    api_key = os.getenv("GROQ_API_KEY")
    if api_key:
        return api_key

    # Then try Streamlit secrets (for cloud deployment)
    try:
        import streamlit as st
        if hasattr(st, 'secrets') and 'api_keys' in st.secrets:
            return st.secrets["api_keys"]["GROQ_API_KEY"]
    except Exception:
        pass

    # Fallback (for development only, replace with placeholder)
    return "REPLACE_WITH_YOUR_API_KEY"

# --- API CONFIGURATION ---
GROQ_API_KEY = get_api_key()
GROQ_MODEL_NAME = os.getenv("GROQ_MODEL_NAME", "llama-3.3-70b-versatile")

# --- DATABASE CONFIGURATION ---
BASE_DIR = Path(__file__).parent.parent
DB_PATH = str(BASE_DIR / "Database" / "nabahan.db")
DATABASE_PATH = DB_PATH  # Alias for compatibility

# --- TABLE NAMES ---
TABLE_NAMES = [
    'tenders_full_details',
    'future_projects',
    'government_entity',
    'regions',
    'tender_statuses',
    'tender_types',
    'primary_activity'
]

# --- VANNA DOCUMENTATION ---
VANNA_DOCUMENTATION = """
قاعدة بيانات نبهان للمشتريات الحكومية السعودية.
تحتوي على بيانات المناقصات والمشاريع المستقبلية من منصة اعتماد.

الجداول الرئيسية:
- tenders_full_details: المناقصات الحالية (التفاصيل الكاملة)
- future_projects: المشاريع المستقبلية المخططة
- government_entity: قائمة الجهات الحكومية
- regions: المناطق السعودية (13 منطقة)
- tender_statuses: حالات المناقصات
- tender_types: أنواع المناقصات
- primary_activity: الأنشطة الرئيسية

ملاحظات:
- استخدم LIKE '%كلمة%' للبحث في الموقع (execution_location)
- الأسماء بالعربية، استخدم UTF-8
- استخدم LIMIT للحد من النتائج
"""

# --- EVALUATION CONFIGURATION ---
EVAL_LOG_PATH = str(BASE_DIR / "logs" / "eval_results.csv")

# --- OUT OF SCOPE MESSAGE ---
OUT_OF_SCOPE_MESSAGE = "عذرا، غير متوفرة البيانات اللازمة لتحليل هذا السؤال."

# --- BRANDING ---
PRIMARY_COLOR = "#2fb38e"
SECONDARY_COLOR = "#1a635a"
PRIMARY_GRADIENT = "linear-gradient(135deg, #2fb38e, #1a635a)"
GREEN_SHADES = ['#1a635a', '#2fb38e', '#57cc99', '#80ed99', '#c7f9cc']

# --- DATABASE SCHEMA ---
DATABASE_SCHEMA = """
قاعدة بيانات المشتريات الحكومية السعودية:

1. tenders_full_details (المناقصات الحالية - 2,414 سجل)
   الحقول: tender_name, tender_number, tender_document_value, tender_status,
   tender_type, government_entity, competition_activity, execution_location,
   suppliers_applied, suppliers_awarded, submission_deadline, opening_date

2. future_projects (المشاريع المستقبلية - 37,764 سجل)
   الحقول: project_name, project_nature, project_description, government_entity,
   execution_location, project_status, year, quarter, expected_duration_days

3. government_entity (الجهات الحكومية - 1,681 سجل)
   الحقول: entity_name

4. regions (المناطق السعودية - 13 سجل)
   الحقول: region_name

5. tender_statuses (حالات المناقصات - 7 سجلات)
   الحقول: status_name

6. tender_types (انواع المناقصات - 13 سجل)
   الحقول: tender_type_name

7. primary_activity (الانشطة الرئيسية - 19 سجل)
   الحقول: activity_name
"""

# --- SQL GENERATION PROMPT ---
SQL_SYSTEM_PROMPT = f"""انت خبير في كتابة استعلامات SQL لقاعدة بيانات المشتريات الحكومية السعودية.

{DATABASE_SCHEMA}

قواعد كتابة SQL:
1. استخدم LIKE '%كلمة%' للبحث في execution_location
2. لا تستخدم اسماء الجداول في WITH clauses
3. استخدم LIMIT 20 للنتائج
4. ارجع SQL فقط بدون شرح
5. لا تستخدم markdown

امثلة:
Q: كم عدد المناقصات؟
SQL: SELECT COUNT(*) as total FROM tenders_full_details

Q: المناقصات في الرياض
SQL: SELECT tender_name, government_entity FROM tenders_full_details WHERE execution_location LIKE '%الرياض%' LIMIT 20

Q: اكثر الجهات مناقصات
SQL: SELECT government_entity, COUNT(*) as count FROM tenders_full_details GROUP BY government_entity ORDER BY count DESC LIMIT 10

Q: توزيع المناقصات حسب الحالة
SQL: SELECT tender_status, COUNT(*) as count FROM tenders_full_details GROUP BY tender_status ORDER BY count DESC
"""

# --- INSIGHTS PROMPT ---
INSIGHTS_SYSTEM_PROMPT = """انت محلل بيانات متخصص في المشتريات الحكومية السعودية.

قواعد صارمة:
1. حلل البيانات المقدمة فقط
2. اذا كانت البيانات فارغة، اجب: "عذرا، غير متوفرة البيانات اللازمة لتحليل هذا السؤال."
3. قدم تحليل موجز بالعربية
4. لا تستخدم رموز تعبيرية
5. اذكر الارقام من البيانات

اجب بتنسيق JSON:
{"insights": "التحليل", "chart_type": "bar او pie او line او none"}
"""

# --- VALID CHART TYPES ---
VALID_CHART_TYPES = ["bar", "pie", "line", "none"]
