# Nabahan (نبهان) - Saudi Government Procurement AI Agent

A Text-to-SQL AI Agent that enables natural language queries on Saudi government procurement data in Arabic, powered by **Vanna AI** and **Groq LLM**.

## Project Overview

Nabahan is an intelligent analytics platform that allows users to query Saudi government tenders and future projects using natural Arabic language. The system leverages **Vanna AI framework** with **Groq LLM** (via OpenAI-compatible API) to convert user questions into SQL queries, executes them against a structured database, and provides insightful analysis with visualizations.

### Key Features

- **Vanna AI Text-to-SQL**: Industry-leading text-to-SQL framework trained on your schema
- **Groq LLM Integration**: Ultra-fast inference using llama-3.3-70b-versatile model
- **Natural Language Processing**: Ask questions in Arabic and get instant answers
- **Schema Training**: Vanna learns your database schema for accurate SQL generation
- **Smart Insights**: AI-generated analysis and recommendations for each query
- **Interactive Dashboard**: 5-page Streamlit application with full RTL Arabic support
- **Dynamic Visualizations**: Auto-generated charts based on query results
- **Advanced Filtering**: Multi-criteria filtering for tenders and projects
- **Evaluation System**: Comprehensive metrics and visualization for agent performance

---

## Project Structure

```
Final_Project/
│
├── agent/                          # Core AI Agent Module
│   ├── __init__.py                 # Package initializer
│   ├── config.py                   # Configuration, prompts, and constants
│   ├── nabahan_logic.py            # Main agent logic and SQL generation
│   └── vanna_setup.py              # Vanna AI + Groq integration
│
├── frontend/                       # Streamlit Web Application
│   ├── __init__.py                 # Package initializer
│   ├── app.py                      # Main Streamlit application (5 pages)
│   ├── components/                 # Reusable UI components
│   │   ├── __init__.py
│   │   ├── chat_interface.py       # AI chat component
│   │   ├── sidebar_filters.py      # Filter sidebar component
│   │   └── visualizations.py       # Chart components
│   └── styles/                     # CSS styling
│       └── __init__.py
│
├── evaluation/                     # Evaluation & Metrics System
│   ├── __init__.py                 # Package initializer
│   ├── eval_suite.py               # Original evaluation pipeline
│   ├── metrics.py                  # Retrieval Accuracy, Fidelity, Latency
│   ├── visualize.py                # Charts generation (Matplotlib)
│   ├── run_evaluation.py           # Complete evaluation runner
│   ├── test_cases.json             # 20 test cases for evaluation
│   └── logs/                       # Evaluation log files
│
├── Data/                           # Data Files
│   ├── raw/                        # Original scraped data
│   │   ├── core/
│   │   │   ├── future_projects.csv
│   │   │   └── nabahan_full_details.csv
│   │   ├── lookup/
│   │   │   ├── Government Entity.csv
│   │   │   ├── Primary Activity.csv
│   │   │   ├── regions.csv
│   │   │   ├── tender_types.csv
│   │   │   └── ... (other lookup tables)
│   │   └── scraping/
│   │       └── etimad_tenders_full.csv
│   └── processed/                  # Cleaned data files
│       ├── core/
│       │   ├── future_projects_clean.csv
│       │   └── nabahan_full_details_clean.csv
│       └── lookup/
│           └── ... (cleaned lookup tables)
│
├── Database/                       # SQLite Database
│   └── nabahan.db                  # Main database (~19MB, 40K+ records)
│
├── presentation/                   # Presentation Materials
│   ├── PRESENTATION_CONTENT.md     # 8-slide presentation content
│   └── EVALUATION_PIPELINE.md      # Evaluation pipeline documentation
│
├── logs/                           # Application logs
│
├── .streamlit/                     # Streamlit Configuration
│   ├── config.toml                 # Theme and server settings
│   └── secrets.toml.example        # API keys template
│
├── .env                            # Environment variables (API keys)
├── .gitignore                      # Git ignore rules
├── requirements.txt                # Python dependencies
├── architecture.md                 # System architecture documentation
└── README.md                       # This file
```

---

## Detailed File Descriptions

### Agent Module (`agent/`)

| File | Description |
|------|-------------|
| `__init__.py` | Exports main functions: `nabahan_agent`, `get_filter_options`, `get_kpi_stats` |
| `config.py` | All configuration including API keys, database path, SQL prompts, insight prompts, color scheme, and table names |
| `nabahan_logic.py` | Core agent logic with functions for SQL generation, execution, insight generation, scope validation, and filter application |
| `vanna_setup.py` | Vanna AI integration using ChromaDB vector store and Groq LLM via OpenAI-compatible API. Includes training functions and 15 sample Q&A pairs |

### Frontend Module (`frontend/`)

| File | Description |
|------|-------------|
| `app.py` | Main Streamlit application with 4 pages: Home (AI Chat), Tenders, Projects, About. Includes all styling, navigation, and data display logic |
| `components/chat_interface.py` | Reusable chat interface component for AI queries |
| `components/sidebar_filters.py` | Filter sidebar with region, entity, and status filters |
| `components/visualizations.py` | Chart generation components using Plotly |

### Evaluation Module (`evaluation/`)

| File | Description |
|------|-------------|
| `eval_suite.py` | Original evaluation class with relevancy and faithfulness scoring |
| `metrics.py` | **New** - Calculates 3 metrics: Retrieval Accuracy (0/1), Generation Fidelity (0/1), Latency (seconds) |
| `visualize.py` | **New** - Generates charts: bar charts, pie charts, latency analysis, dashboard using Matplotlib with `plt.savefig()` |
| `run_evaluation.py` | **New** - Complete pipeline that runs tests, calculates metrics, generates visualizations, and saves CSV reports |
| `test_cases.json` | 20 test cases covering: count queries, region filters, aggregations, distributions, lookups, and out-of-scope questions |

### Data Directory (`Data/`)

| Folder | Contents |
|--------|----------|
| `raw/core/` | Original tender and project data from Etimad platform |
| `raw/lookup/` | Reference tables: government entities, regions, tender types, activities, statuses |
| `raw/scraping/` | Raw scraped data from Etimad website |
| `processed/core/` | Cleaned and formatted core data files |
| `processed/lookup/` | Cleaned lookup table files |

### Database (`Database/`)

| File | Description |
|------|-------------|
| `nabahan.db` | SQLite database containing 7 tables with 40,000+ records of Saudi government procurement data |

### Presentation Materials (`presentation/`)

| File | Description |
|------|-------------|
| `PRESENTATION_CONTENT.md` | Complete 8-slide presentation structure with speaker notes, demo script, and technical specs. Covers: Title, Problem, Solution, Architecture, Agentic Logic, Live Demo, Evaluation, and Challenges/Future Work |
| `EVALUATION_PIPELINE.md` | Detailed documentation of the evaluation system including pipeline architecture, metrics definitions (Retrieval Accuracy, Generation Fidelity, Latency), test case structure, output formats, and visualization charts |

---

## Database Schema

### Tables Overview

| Table | Records | Description |
|-------|---------|-------------|
| `tenders_full_details` | 2,414 | Current government tenders with full details |
| `future_projects` | 37,764 | Planned future government projects |
| `government_entity` | 1,681 | List of Saudi government entities |
| `regions` | 13 | Saudi Arabian administrative regions |
| `tender_statuses` | 7 | Tender status types |
| `tender_types` | 13 | Types of tenders/competitions |
| `primary_activity` | 19 | Primary activity categories |

### Key Columns

**tenders_full_details:**
- `tender_name`, `tender_number`, `reference_number`
- `government_entity`, `tender_status`, `tender_type`
- `competition_activity`, `execution_location`
- `submission_deadline`, `opening_date`, `tender_document_value`

**future_projects:**
- `project_name`, `project_description`, `government_entity`
- `project_nature`, `project_status`, `execution_location`
- `year`, `quarter`, `expected_duration_days`

---

## System Architecture

```
User Query (Arabic)
       |
       v
+------------------+
|   Scope Check    |  --> Out of scope? Return message
+------------------+
       |
       v
+------------------+
|    Vanna AI      |  --> Text-to-SQL Framework (optional)
|  + Groq LLM API  |  --> Generate SQL (llama-3.3-70b-versatile)
+------------------+
       |
       v
+------------------+
|  SQLite Database |  --> Execute query
+------------------+
       |
       v
+------------------+
|  Groq LLM API    |  --> Generate insights + chart recommendation
+------------------+
       |
       v
+------------------+
|  Streamlit UI    |  --> Display results, insights, and charts
+------------------+
```

---

## Tech Stack

| Component | Technology |
|-----------|------------|
| Text-to-SQL Framework | Vanna AI |
| LLM | Groq API (llama-3.3-70b-versatile) |
| Vector Store | ChromaDB |
| Database | SQLite |
| Frontend | Streamlit |
| Language | Python 3.10+ |
| Data Processing | Pandas, NumPy |
| Visualization | Plotly, Matplotlib, Seaborn |
| Evaluation | Custom metrics system |

---

## Installation

### Prerequisites

- Python 3.10 or higher
- Groq API key

### Setup

1. Clone the repository:
```bash
git clone https://github.com/justRuba/Nabhan-Project.git
cd Nabhan-Project
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment variables:
```bash
cp .env.example .env
# Edit .env and add your GROQ_API_KEY
```

5. Run the application:
```bash
streamlit run frontend/app.py
```

---

## Usage

### Running the Web Application

```bash
streamlit run frontend/app.py
```

Access at: http://localhost:8501

### Dashboard Pages

| Page | Arabic | Description |
|------|--------|-------------|
| Home | الرئيسية | AI chat interface for natural language queries |
| Tenders | المنافسات | Browse and filter government tenders |
| Projects | المشاريع | Explore future government projects |
| About | من نحن | Platform information and team |
| Contact | تواصل معنا | Contact information and FAQ |

### Running Evaluation

```bash
# Full evaluation (20 test cases)
python evaluation/run_evaluation.py

# Quick test (5 cases)
python evaluation/run_evaluation.py --quick

# Custom test file
python evaluation/run_evaluation.py --test-file path/to/tests.json
```

### Evaluation Output

Results saved to `evaluation/results/`:
- `evaluation_results_TIMESTAMP.csv` - Detailed per-query results
- `evaluation_summary_TIMESTAMP.csv` - Final scores summary
- `charts/` folder with PNG visualizations

---

## Example Queries

| Arabic Query | Description |
|--------------|-------------|
| كم عدد المناقصات في الرياض؟ | Count of tenders in Riyadh |
| ما هي الجهات الاكثر طرحا للمنافسات؟ | Top entities by tender count |
| اعرض المشاريع المستقبلية لعام 2024 | Future projects for 2024 |
| قارن المناقصات حسب النشاط | Compare tenders by activity |
| ما هي انواع المشاريع الاكثر شيوعا؟ | Most common project types |
| توزيع المناقصات حسب الحالة | Tender distribution by status |

---

## Evaluation Metrics

| Metric | Description | Scoring |
|--------|-------------|---------|
| **Retrieval Accuracy** | Did we query the correct table and get relevant data? | 0 or 1 |
| **Generation Fidelity** | Is the generated insight truthful to the data? | 0 or 1 |
| **Latency** | Query response time | Seconds |

### Performance Targets

| Metric | Target | Typical |
|--------|--------|---------|
| Pass Rate | > 80% | ~85% |
| Avg Retrieval Accuracy | > 80% | ~90% |
| Avg Generation Fidelity | > 80% | ~85% |
| Avg Latency | < 5s | ~2-3s |

---

## Configuration

### Environment Variables (`.env`)

```env
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL_NAME=llama-3.3-70b-versatile
```

### Customization (`agent/config.py`)

| Setting | Value |
|---------|-------|
| Primary Color | #2fb38e |
| Secondary Color | #1a635a |
| Font | IBM Plex Sans Arabic |
| Direction | RTL (Right-to-Left) |

---

## Challenges & Solutions

| Challenge | Solution |
|-----------|----------|
| Arabic text in SQL | UTF-8 encoding + LIKE patterns |
| Circular SQL references | Regex-based CTE renaming |
| Ambiguous queries | Keyword-based scope validation |
| Large result sets | Pagination + dynamic table height |
| Windows console encoding | USE_VANNA flag for fallback to direct Groq |

---

## Future Enhancements

- [ ] Voice input support (Arabic speech-to-text)
- [ ] Export to Excel/PDF
- [ ] User authentication and history
- [ ] Real-time data from Etimad API
- [ ] Advanced analytics and trend prediction

---

## Team

**Nabahan Team**
- Project developed for AI Agents course final project

## License

This project is for educational purposes.

## Contact

- Email: insight.nabahan@gmail.com

---

Built with Vanna AI + Groq LLM + Streamlit | 2026
