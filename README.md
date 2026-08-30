# 🏢 Captrix AI Agent — Enterprise Financial Intelligence Platform

> **Autonomous AI-Powered Financial Auditing, Benford's Law Forensic Engine, DuPont ROE Tree & Solvency Risk Intelligence**

![Captrix AI Agent Banner](https://img.shields.io/badge/Captrix%20AI-Financial%20Intelligence%20Agent-0E49B5?style=for-the-badge&logo=brain&logoColor=white)
![FastAPI](https://img.shields.io/badge/Backend-FastAPI%20%7C%20Python%203.14-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![Next.js 14](https://img.shields.io/badge/Frontend-Next.js%2014%20%7C%20TypeScript-000000?style=for-the-badge&logo=nextdotjs&logoColor=white)
![Security](https://img.shields.io/badge/Security-Multi--Tenant%20Isolated-emerald?style=for-the-badge&logo=shieldcheck&logoColor=white)

---

## 📌 Executive Summary

**Captrix AI Agent** is an enterprise-grade autonomous financial intelligence platform designed for Chief Financial Officers (CFOs), financial analysts, audit teams, and investment managers. 

It ingests accounting workbooks (`.xlsx`, `.csv`, `.ods`, `.tsv`, `.pdf`) across non-standard Charts of Accounts and **all global currencies** (INR `₹`, USD `$`, EUR `€`, GBP `£`, JPY `¥`, CNY `¥`, KRW `₩`, RUB `₽`, TRY `₺`, THB `฿`, VND `₫`, BDT `৳`, ILS `₪`, NGN `₦`, AED, SAR, etc.), normalizes financial statements, executes high-precision quantitative ratio analytics, performs 3-year multi-period trend modeling and **3-Year AI Predictive Forecasting**, calculates corporate finance metrics (NPV, IRR, WACC, Cash Conversion Cycle), conducts **DuPont 3-Step & 5-Step ROE Decomposition**, predicts solvency risk via **Altman Z-Score & Beneish M-Score**, runs **Benford's Law Forensic Audit Testing**, and generates formal **Independent Auditor's Reports & Working Papers**.

---

## 🏗️ Complete End-to-End System Architecture & Execution Workflow

```
 USER UPLOADS FINANCIAL DOCUMENT (.xlsx / .csv / .pdf)
                       │
                       ▼
      DETERMINISTIC INGESTION & PARSING ENGINE
  (Schema Normalization, Multi-Currency Detection)
                       │
                       ▼
  DETERMINISTIC STATEMENT & RATIO CALCULATIONS
                       │
                       ▼
  DUPONT ROE DECOMPOSITION & RISK INTELLIGENCE
  (3-Step / 5-Step ROE Tree, Altman Z-Score & Beneish M-Score)
                       │
                       ▼
  FULL FORENSIC AUDITOR ENGINE & BENFORD'S LAW TESTING
  (Benford Logarithmic Curve, Sloan Accruals Realization Ratio)
                       │
                       ▼
  AUDITOR WORKING PAPERS & OPINION CERTIFICATE GENERATION
  (Unqualified, Qualified, Adverse Opinion + Working Papers WP-101 to WP-104)
                       │
                       ▼
  INTERACTIVE WORKSPACE VIEWERS & EXPORTABLE REPORTS
  (Dashboard Tabs, Excel Multi-Tab Export, PDF Audit Report)
```

---

## 🚀 Key Enterprise Modules

### 1. 🛡️ Full AI Financial Auditor & Forensic Accounting Suite
- **Benford's Law First-Digit Forensic Test** (`auditor_engine.py`): Scans numeric amounts against Logarithmic Benford Distribution ($P(d) = \log_{10}(1 + 1/d)$) to detect human-fabricated numbers or artificial rounding.
- **Sloan Accruals & Cash Realization Engine**: Computes $(\text{Net Income} - \text{Operating Cash Flow}) / \text{Total Assets}$ to test if reported earnings are backed by operational cash flows.
- **Independent Auditor's Opinion Certificate**: Formulates formal audit opinions (**Unqualified**, **Qualified**, **Adverse**, or **Disclaimer of Opinion**) with complete **Auditor Working Papers (WP) Trail** (`WP-101` through `WP-104`).

### 2. 🔍 DuPont ROE Analytical Decomposition Tree
- **3-Step Model** (`dupont_analyzer.py`): $\text{ROE} = \text{Net Profit Margin} \times \text{Asset Turnover} \times \text{Equity Multiplier}$.
- **5-Step Extended Model**: $\text{Tax Burden} \times \text{Interest Burden} \times \text{EBIT Margin} \times \text{Asset Turnover} \times \text{Equity Multiplier}$.
- **Primary Driver Identification**: Automatically classifies whether ROE is driven by Pricing Power, Asset Velocity, or Financial Leverage.

### 3. ⚡ Solvency Risk Intelligence (Altman Z-Score & Beneish M-Score)
- **Altman Z-Score Insolvency Meter** (`risk_analyzer.py`): Predicts 2-year bankruptcy risk (`SAFE ZONE` $Z > 2.99$, `GREY ZONE` $1.81 \le Z \le 2.99$, `DISTRESS ZONE` $Z < 1.81$).
- **Beneish M-Score Forensic Check**: Detects earnings manipulation risks ($M > -1.78$) and total accruals to assets.

### 4. 📈 Multi-Period Trends & 3-Year Predictive AI Forecasting
- **CAGR & YoY Analytics** (`multi_period_analyzer.py`): Calculates 3-year historical CAGR % and Year-over-Year growth rates across statements.
- **3-Year AI Predictive Forecast**: Linear trend projections for $Y+1$, $Y+2$, and $Y+3$ Revenue, Net Profit, Assets, and Net Margin with confidence ranges.

### 5. 🌐 Global Currency Recognition Engine
- Supports all major world currencies: **INR (`₹`)**, **USD (`$`)**, **EUR (`€`)**, **GBP (`£`)**, **JPY (`¥`)**, **CNY (`¥`)**, **KRW (`₩`)**, **RUB (`₽`)**, **TRY (`₺`)**, **THB (`฿`)**, **VND (`₫`)**, **BDT (`৳`)**, **ILS (`₪`)**, **NGN (`₦`)**, **AED**, **SAR**, **QAR**, **KWD**, **OMR**, **BHD**, **SGD**, **HKD**, **CAD**, **AUD**, **NZD**, **CHF**, **SEK**, **NOK**, **DKK**, **MXN**, **BRL**, **ZAR**, etc.

---

## 🧮 Algorithms & Mathematical Models

### A. Benford's Law First-Digit Logarithmic Distribution
$$P(d) = \log_{10}\left(1 + \frac{1}{d}\right), \quad d \in \{1, 2, \dots, 9\}$$

### B. Sloan Accruals Earnings Quality Ratio
$$\text{Accruals Ratio} = \frac{\text{Net Income} - \text{Operating Cash Flow}}{\text{Average Total Assets}}$$

### C. DuPont 3-Step Return on Equity (ROE) Decomposition
$$\text{ROE} = \left(\frac{\text{Net Profit}}{\text{Revenue}}\right) \times \left(\frac{\text{Revenue}}{\text{Total Assets}}\right) \times \left(\frac{\text{Total Assets}}{\text{Total Equity}}\right)$$

### D. Altman Z-Score Bankruptcy Model
$$Z = 1.2 X_1 + 1.4 X_2 + 3.3 X_3 + 0.6 X_4 + 0.999 X_5$$

### E. Compound Annual Growth Rate (CAGR)
$$\text{CAGR} = \left(\frac{\text{Ending Value}}{\text{Beginning Value}}\right)^{\frac{1}{n}} - 1$$

---

## 🔒 Multi-Tenant Privacy & Data Isolation

Captrix AI Agent enforces **Row-Level Tenant Isolation**:
- Every uploaded workbook, evaluation log, audit opinion, history record, PDF report, and chat session is tagged with `user_id`.
- All database queries enforce `filter(Upload.user_id == current_user.id)`.

---

## 📁 Repository & Folder Structure

```
ai-financial-intelligence-platform/
├── backend/                               # FastAPI Python Core Backend
│   ├── app/
│   │   ├── api/                           # REST API Endpoints & Route Handlers
│   │   │   ├── analysis.py                # Financial analysis & metric query endpoints
│   │   │   ├── chat.py                    # AI Financial Copilot chat endpoint
│   │   │   ├── history.py                 # Multi-tenant upload history & management
│   │   │   ├── models_api.py              # AI evaluation & benchmark registry API
│   │   │   ├── reports.py                 # PDF and Excel report download routes
│   │   │   └── upload.py                  # File upload, ingestion, & extraction orchestration
│   │   ├── auth/                          # Security, JWT Token Handling & Password Hashing
│   │   │   └── auth_handler.py            # Authentication dependencies & OAuth2 password bearer
│   │   ├── db/                            # Database Layer
│   │   │   ├── database.py                # SQLAlchemy engine & session management
│   │   │   └── models.py                  # User, Upload, FinancialData, and AuditLog tables
│   │   ├── engine/                        # Core Financial Intelligence & Accounting Engines
│   │   │   ├── accounting_adapters.py     # QuickBooks, Xero, and Tally ERP adapters
│   │   │   ├── ai_insights.py             # Financial health scoring & executive summaries
│   │   │   ├── audit_exceptions.py        # ISA exception compilation & management letter generator
│   │   │   ├── audit_planner.py           # ISA 320 planning & performance materiality calculations
│   │   │   ├── audit_queries.py           # Automated audit query tracking & tick-mark manager
│   │   │   ├── auditor_engine.py          # Forensic accounting, Benford's Law, and Sloan Accruals
│   │   │   ├── canonical_model.py         # Standardized canonical financial schema definitions
│   │   │   ├── currency_engine.py         # Multi-currency matrix, symbol disambiguation & FX rates
│   │   │   ├── document_parser.py         # Multi-format workbook parser (Excel, CSV, PDF, Tally)
│   │   │   ├── document_profiler.py       # Structural document complexity profiler
│   │   │   ├── dupont_analyzer.py         # DuPont 3-step & 5-step ROE decomposition tree
│   │   │   ├── financial_analyzer.py      # Quantitative ratios (Profitability, Liquidity, Solvency)
│   │   │   ├── independent_verifier.py    # Independent source data verification checks
│   │   │   ├── master_system_prompt.py    # AI system prompt rules & accounting boundaries
│   │   │   ├── model_evaluator.py         # AI model evaluation & precision benchmarking
│   │   │   ├── model_registry.py          # Model leaderboard & performance registry
│   │   │   ├── multi_period_analyzer.py   # Multi-year CAGR, YoY, & 3-year trend forecasting
│   │   │   ├── output_validator.py        # Strict source-gating & math consistency validator
│   │   │   ├── quality_engine.py          # Data quality & completeness auditing
│   │   │   ├── reconciliation.py          # Debit/Credit & Net Income mathematical reconciliations
│   │   │   ├── risk_analyzer.py           # Altman Z-Score & Beneish M-Score risk models
│   │   │   ├── statement_generator.py     # Grounded P&L, Balance Sheet, & Cash Flow generator
│   │   │   ├── valuation_engine.py        # DCF, WACC, NPV, and IRR corporate finance valuation
│   │   │   ├── wipro_benchmark.py         # Benchmark baseline ground-truth evaluator
│   │   │   └── working_papers.py          # ISA Lead Schedules (WP-A through WP-H)
│   │   ├── reports/                       # Formal Export Generation
│   │   │   ├── excel_generator.py         # Multi-tab audited Excel workbook export
│   │   │   └── pdf_generator.py           # ReportLab dynamic audited PDF export
│   │   ├── __init__.py
│   │   └── main.py                        # FastAPI application entrypoint & middleware
│   ├── sample_data/                       # Sample test workbooks & sample generator scripts
│   ├── tests/                             # Comprehensive Automated Test Suites (98 Tests)
│   ├── requirements.txt                   # Production Python dependencies
│   └── run_server.py                      # Uvicorn local runner script
│
├── frontend/                              # Next.js 14 TypeScript Frontend
│   ├── src/
│   │   ├── app/                           # Next.js App Router Pages
│   │   │   ├── analysis/                  # Deep Financial Analysis & Statement View
│   │   │   ├── dashboard/                 # Overview Dashboard & KPI Summary
│   │   │   ├── history/                   # Multi-Tenant Upload History & Inspection
│   │   │   ├── login/                     # Secure Authentication Sign-In
│   │   │   ├── register/                  # User Registration Page
│   │   │   ├── forgot-password/           # Password Recovery Page
│   │   │   ├── globals.css                # Global Tailwind CSS Styles & Design Tokens
│   │   │   ├── layout.tsx                 # Root Application Layout & Theme Provider
│   │   │   └── page.tsx                   # Landing Page & Redirect Handler
│   │   ├── components/                    # Modular Interactive UI Components
│   │   │   ├── AIInsightsPanel.tsx        # Strategic AI insights & executive summary cards
│   │   │   ├── AppLayout.tsx              # Authenticated dashboard frame layout
│   │   │   ├── AuditorWorkingPapers.tsx   # ISA Lead Schedules (WP-A to WP-H) & Opinion Viewer
│   │   │   ├── ChatbotDrawer.tsx          # Interactive AI Financial Copilot drawer
│   │   │   ├── CorporateFinanceViewer.tsx # Valuation, DCF, WACC & Capital Budgeting View
│   │   │   ├── DupontViewer.tsx           # DuPont 3-step & 5-step ROE Tree visualization
│   │   │   ├── EvidenceInspectorModal.tsx # Cell-level source evidence inspection modal
│   │   │   ├── FileUploader.tsx           # Drag-and-drop document upload interface
│   │   │   ├── FinancialCharts.tsx        # Recharts visual financial breakdown charts
│   │   │   ├── HealthGauge.tsx            # Animated circular health score gauge
│   │   │   ├── ModelLeaderboardViewer.tsx # AI Model performance leaderboard
│   │   │   ├── MultiPeriodViewer.tsx      # Multi-year historical trends & CAGR comparisons
│   │   │   ├── Navbar.tsx                 # Top navigation bar with user profile & status
│   │   │   ├── RatioGrid.tsx              # Financial Ratios grid with visual progress benchmarks
│   │   │   ├── RiskIntelligenceViewer.tsx # Altman Z-Score & Beneish M-Score meters
│   │   │   ├── Sidebar.tsx                # Side navigation with route links & quick actions
│   │   │   └── StatementViewer.tsx        # Source-gated P&L, Balance Sheet, & Cash Flow tables
│   │   ├── context/                       # React Context Providers
│   │   │   └── AuthContext.tsx            # Multi-tenant user auth state & session storage
│   │   └── lib/                           # Frontend Utilities & API Client
│   │       ├── api.ts                     # Axios HTTP client with JWT interceptor
│   │       └── utils.ts                   # Formatting, date, and currency helper utilities
│   ├── package.json                       # Frontend dependencies & npm scripts
│   ├── tailwind.config.js                 # Tailwind CSS theme & color palette configuration
│   └── tsconfig.json                      # TypeScript compiler configuration
│
├── .agents/                               # Workspace agent customization rules
├── .gitignore                             # Git ignore rules for node_modules, .venv, .db
└── README.md                              # Complete Platform Architecture Documentation
```

---

## 🛠️ Technology Stack

- **Backend**: FastAPI (Python 3.14), SQLAlchemy ORM, Uvicorn, Pytest, Passlib (PBKDF2-SHA256), ReportLab (PDF), OpenPyXL (Excel), Pandas.
- **Frontend**: Next.js 14 (App Router), TypeScript, TailwindCSS, Axios (`api.ts`), Lucide Icons, Recharts.

---

## ⚡ Local Setup & Installation

### Backend Setup
```bash
# 1. Navigate to backend directory
cd backend

# 2. Activate virtual environment and install requirements
.venv\Scripts\python.exe -m pip install -r requirements.txt

# 3. Start FastAPI server
.venv\Scripts\python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Frontend Setup
```bash
# 1. Navigate to frontend directory
cd frontend

# 2. Install dependencies
npm install

# 3. Run development server
npm run dev
```

- **Frontend App**: `http://localhost:3000`
- **Backend API Docs**: `http://localhost:8000/docs`

---

## 📄 License
Enterprise Proprietary Software — Built for Autonomous AI Financial Auditing.
