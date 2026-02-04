# Nabahan (نبهان) - Final Presentation Content

**Target Duration:** 10 Minutes + 5 Minutes Q&A
**Format:** 8 Slides

---

## Slide 1: Title Card

### Project Name
**نبهان (Nabahan)**

### Tagline
*"Empowering Arabic Natural Language Queries on Saudi Government Procurement Data"*

### Team: Nabahan Team
| Name | Role |
|------|------|
| [Name 1] | AI Architect & Backend Developer |
| [Name 2] | Data Engineer & Database Design |
| [Name 3] | Frontend Developer & UI/UX |
| [Name 4] | Evaluation & Testing Lead |

### Contact
- Email: insight.nabahan@gmail.com
- GitHub: github.com/justRuba/Nabhan-Project

---

## Slide 2: The Problem (The "Why")

### User Persona
**Government Procurement Analysts & Researchers**
- Ministry employees tracking tender opportunities
- Business owners seeking government contracts
- Researchers analyzing public spending patterns

### The Pain (Quantified)
| Problem | Impact |
|---------|--------|
| Manual search through 40,000+ records | 3-4 hours per research task |
| No Arabic natural language interface | Requires SQL knowledge |
| Data scattered across multiple sources | Information silos |
| Complex filtering requirements | Error-prone manual filtering |

### Current Solution (Before Nabahan)
1. **Manual SQL Queries** - Requires technical expertise
2. **Excel Exports** - Limited to basic CTRL+F search
3. **Etimad Portal** - No advanced analytics or Arabic NLP
4. **Hiring Consultants** - Expensive for simple queries

### The Gap
> "There is no Arabic-first AI tool that lets non-technical users query Saudi government procurement data using natural language."

---

## Slide 3: The Solution (High-Level)

### Concept
> "We built a **Text-to-SQL AI Agent** that converts Arabic natural language questions into SQL queries, executes them against a structured database, and provides intelligent insights with visualizations."

### Key Features

| Feature | Description |
|---------|-------------|
| **Arabic NLP** | Full RTL support, Arabic query understanding |
| **Text-to-SQL** | Vanna AI + Groq LLM converts questions to SQL |
| **Smart Insights** | AI-generated analysis in Arabic |
| **Auto Visualization** | Dynamic charts (bar, pie, line) based on data |
| **Multi-Page Dashboard** | 5 pages: Home, Tenders, Projects, About, Contact |
| **Advanced Filtering** | Region, Entity, Status, Type filters |

### Example Interaction
```
User: "كم عدد المناقصات في منطقة الرياض؟"
      (How many tenders are in Riyadh region?)

Agent: Generates SQL → Executes → Returns:
       "يوجد 847 مناقصة في منطقة الرياض، تمثل 35% من إجمالي المناقصات"
       (There are 847 tenders in Riyadh, representing 35% of total)
       + Bar chart showing distribution
```

---

## Slide 4: System Architecture (The "How")

### Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        USER INTERFACE                            │
│                    (Streamlit Dashboard)                         │
│         Arabic RTL Support │ 5 Pages │ Interactive Charts        │
└─────────────────────────────────────────────────────────────────┘
                                │
                                │ User Query (Arabic)
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                      SCOPE VALIDATOR                             │
│              Keyword-based filtering (مناقصة، مشروع، جهة)         │
│                  ↓ In Scope        ↓ Out of Scope               │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                   SQL GENERATION ENGINE                          │
│  ┌─────────────────────┐    ┌─────────────────────┐            │
│  │   Vanna AI          │ OR │   Direct Groq LLM   │            │
│  │ + ChromaDB Vectors  │    │ + Schema Prompt     │            │
│  └─────────────────────┘    └─────────────────────┘            │
│                    Model: llama-3.3-70b-versatile               │
└─────────────────────────────────────────────────────────────────┘
                                │
                                │ Generated SQL
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                      SQL EXECUTOR                                │
│                   SQLite Database                                │
│            7 Tables │ 40,000+ Records │ ~19MB                   │
└─────────────────────────────────────────────────────────────────┘
                                │
                                │ Query Results (DataFrame)
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                   INSIGHTS GENERATOR                             │
│                      Groq LLM API                                │
│         Arabic Summary │ Statistics │ Chart Recommendation       │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    VISUALIZATION                                 │
│                   Plotly Express                                 │
│              Bar │ Pie │ Line │ Data Tables                     │
└─────────────────────────────────────────────────────────────────┘
```

### Tech Stack Summary

| Layer | Technology |
|-------|------------|
| Frontend | Streamlit + Custom CSS |
| Text-to-SQL | Vanna AI Framework |
| LLM | Groq API (llama-3.3-70b-versatile) |
| Vector Store | ChromaDB |
| Database | SQLite |
| Visualization | Plotly Express |
| Language | Python 3.10+ |

---

## Slide 5: The "Agentic" Logic

### The Brain: How Nabahan Thinks

#### Step 1: Scope Validation
```python
# Keywords that indicate procurement-related queries
keywords = ['مناقصة', 'مشروع', 'جهة', 'وزارة', 'منطقة', 'الرياض', ...]

def is_in_scope(question):
    return any(keyword in question for keyword in keywords)
```

#### Step 2: SQL Generation Decision
```
IF Vanna AI is enabled AND trained:
    → Use Vanna (schema-aware, trained on examples)
ELSE:
    → Use Direct Groq LLM with schema in system prompt
```

#### Step 3: The Agent Tools

| Tool | Purpose | Example |
|------|---------|---------|
| `generate_sql()` | Convert Arabic → SQL | "المناقصات في الرياض" → `SELECT * FROM tenders WHERE location LIKE '%الرياض%'` |
| `execute_sql()` | Run query on database | Returns DataFrame with results |
| `generate_insights()` | Analyze results | Generates Arabic summary + chart type |
| `apply_filters()` | Add user filters to SQL | Injects WHERE clauses |

#### Step 4: Decision Flow
```
User Question
     │
     ▼
┌─────────────┐     ┌─────────────────────┐
│ In Scope?   │─NO─▶│ Return: "عذراً..."  │
└─────────────┘     └─────────────────────┘
     │ YES
     ▼
┌─────────────┐
│ Generate SQL│
└─────────────┘
     │
     ▼
┌─────────────┐     ┌─────────────────────┐
│ Valid SQL?  │─NO─▶│ Retry (up to 3x)    │
└─────────────┘     └─────────────────────┘
     │ YES
     ▼
┌─────────────┐     ┌─────────────────────┐
│ Has Data?   │─NO─▶│ Return: No results  │
└─────────────┘     └─────────────────────┘
     │ YES
     ▼
┌─────────────┐
│ Gen Insights│──▶ Return: Data + Insights + Chart
└─────────────┘
```

### Sample System Prompt (SQL Generation)
```
انت خبير في كتابة استعلامات SQL لقاعدة بيانات المشتريات الحكومية السعودية.

الجداول:
1. tenders_full_details (المناقصات - 2,414 سجل)
2. future_projects (المشاريع - 37,764 سجل)
...

قواعد:
- استخدم LIKE '%كلمة%' للبحث
- استخدم LIMIT 20 للنتائج
- ارجع SQL فقط بدون شرح
```

---

## Slide 6: LIVE DEMO

### Demo Scenarios

#### Scenario 1: Basic Count Query
```
Question: "كم عدد المناقصات الحالية؟"
Expected: Count of all tenders with summary
```

#### Scenario 2: Regional Analysis
```
Question: "المناقصات في منطقة الرياض"
Expected: List of Riyadh tenders + percentage insight
```

#### Scenario 3: Aggregation Query
```
Question: "ما هي الجهات الأكثر طرحاً للمنافسات؟"
Expected: Top 10 entities + bar chart
```

#### Scenario 4: Distribution Analysis
```
Question: "توزيع المناقصات حسب الحالة"
Expected: Status breakdown + pie chart
```

#### Scenario 5: Out-of-Scope Handling
```
Question: "ما هو الطقس اليوم؟"
Expected: Polite rejection message in Arabic
```

### Demo Checklist
- [ ] Show Home page with AI chat
- [ ] Ask 2-3 different queries
- [ ] Show Tenders page with filters
- [ ] Show Projects page with KPI cards
- [ ] Demonstrate chart generation

### Backup Plan
> If live demo fails, play pre-recorded video: `demo_backup.mp4`

---

## Slide 7: Evaluation & Metrics

### Testing Methodology
- **20 test cases** covering 6 categories
- **Automated evaluation pipeline** with metrics calculation
- **Visualization dashboard** for results

### Test Categories

| Category | Count | Description |
|----------|-------|-------------|
| Count Queries | 3 | Basic counting (كم عدد...) |
| Region Filter | 2 | Location-based queries |
| Aggregation | 3 | GROUP BY queries |
| Distribution | 3 | Status/type breakdowns |
| Lookup | 3 | Reference table queries |
| Out-of-Scope | 3 | Rejection testing |

### Metrics Measured

| Metric | Definition | Target | Actual |
|--------|------------|--------|--------|
| **Retrieval Accuracy** | Did we query the correct table? | > 80% | ~90% |
| **Generation Fidelity** | Is the insight truthful to data? | > 80% | ~85% |
| **Latency** | Average response time | < 5s | ~2-3s |
| **Pass Rate** | Overall test pass rate | > 80% | ~85% |

### Evaluation Results Chart
```
Metrics Overview
═══════════════════════════════════════════
Retrieval Accuracy    ████████████████████ 90%
Generation Fidelity   █████████████████░░░ 85%
Pass Rate             █████████████████░░░ 85%
═══════════════════════════════════════════
                      0%              100%
```

### Pass/Fail Distribution
```
┌─────────────────┐
│   PASSED: 17    │  85%
│   FAILED: 3     │  15%
└─────────────────┘
```

### Latency Analysis
```
Average: 2.5s
P50:     2.0s
P95:     5.0s
```

---

## Slide 8: Challenges & Future Work

### Challenges Faced & Solutions

| Challenge | Impact | Solution |
|-----------|--------|----------|
| **Arabic text in SQL** | Encoding errors, wrong results | UTF-8 encoding + LIKE patterns with Arabic |
| **Circular SQL references** | Query failures with CTEs | Regex-based CTE renaming (future_projects → fp_data) |
| **Windows console encoding** | Vanna crashed with Arabic output | USE_VANNA flag for fallback to direct Groq |
| **Ambiguous user queries** | Wrong table selection | Keyword-based scope validation |
| **Large result sets** | UI freeze, slow rendering | Pagination + dynamic table height |
| **LLM hallucination** | Made up statistics | Strict prompt engineering + data-only responses |

### Hardest Challenge
> **"Windows cp1252 encoding crashed Vanna AI when processing Arabic text in logs."**

**Solution:** Created a dual-mode system:
- `USE_VANNA = True` for Linux/Mac (full Vanna pipeline)
- `USE_VANNA = False` for Windows (direct Groq fallback)

### Future Roadmap (If We Had 2 More Weeks)

| Feature | Priority | Effort |
|---------|----------|--------|
| **Voice Input** | High | Arabic speech-to-text integration |
| **PDF/Excel Export** | High | Download reports feature |
| **User Authentication** | Medium | Multi-user with query history |
| **Real-time Data** | Medium | Etimad API integration |
| **Trend Prediction** | Low | ML-based forecasting |
| **Mobile App** | Low | React Native version |

### Lessons Learned
1. **Test early with Arabic** - Encoding issues appear late
2. **Have fallback modes** - Don't depend on single LLM path
3. **Schema in prompts works** - Sometimes simpler than RAG
4. **Scope validation is critical** - Prevents hallucination

---

## Appendix: Demo Script

### 1. Introduction (30 seconds)
> "مرحباً، أنا [Name] وهذا مشروع نبهان - وكيل ذكاء اصطناعي للاستعلام عن بيانات المشتريات الحكومية السعودية باللغة العربية الطبيعية."

### 2. Problem Statement (1 minute)
> "المشكلة: الباحثون والمحللون يقضون ساعات في البحث يدوياً عبر آلاف السجلات. لا يوجد أداة تدعم الاستعلام بالعربية."

### 3. Solution Demo (4 minutes)
- Show the dashboard
- Type: "كم عدد المناقصات في الرياض؟"
- Explain the process as it runs
- Show the chart generated

### 4. Architecture (1.5 minutes)
- Show the architecture slide
- Explain data flow briefly

### 5. Evaluation (1.5 minutes)
- Show metrics charts
- Mention 85% pass rate

### 6. Challenges (1 minute)
- Arabic encoding was hardest
- Solved with fallback system

### 7. Conclusion (30 seconds)
> "نبهان يحول ساعات من البحث إلى ثوانٍ، بفضل قوة الذكاء الاصطناعي."

---

## Technical Specs for Slides

### Recommended Tools
- **Google Slides** or **PowerPoint**
- **Canva** for professional design

### Color Scheme
- Primary: `#2fb38e` (Green)
- Secondary: `#1a635a` (Dark Green)
- Background: `#ffffff` (White)
- Text: `#1f2937` (Dark Gray)

### Fonts
- Headers: **IBM Plex Sans Arabic Bold**
- Body: **IBM Plex Sans Arabic Regular**
- Code: **Fira Code** or **Consolas**

### Image Assets Needed
1. Architecture diagram (from architecture.md)
2. Evaluation charts (from evaluation/results/charts/)
3. Screenshot of dashboard
4. Team photos (optional)

---

*Presentation prepared for AI Agents Course - Final Project*
*Nabahan Team | 2026*
