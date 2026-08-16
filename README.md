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
