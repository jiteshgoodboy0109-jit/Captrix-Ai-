# 🏢 Captrix AI Agent — Enterprise Financial Intelligence Platform

> **Autonomous AI-Powered Financial Auditing, Ratio Analytics, Corporate Finance Valuation & Multi-Year Trend Engine**

![Captrix AI Agent Banner](https://img.shields.io/badge/Captrix%20AI-Financial%20Intelligence%20Agent-0E49B5?style=for-the-badge&logo=brain&logoColor=white)
![FastAPI](https://img.shields.io/badge/Backend-FastAPI%20%7C%20Python%203.14-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![Next.js 14](https://img.shields.io/badge/Frontend-Next.js%2014%20%7C%20TypeScript-000000?style=for-the-badge&logo=nextdotjs&logoColor=white)
![Security](https://img.shields.io/badge/Security-Multi--Tenant%20Isolated-emerald?style=for-the-badge&logo=shieldcheck&logoColor=white)

---

## 📌 Executive Summary

**Captrix AI Agent** is an enterprise-grade autonomous financial intelligence platform designed for Chief Financial Officers (CFOs), financial analysts, audit teams, and investment managers. 

It ingests accounting workbooks (`.xlsx`, `.csv`, `.ods`, `.tsv`) across non-standard Charts of Accounts, normalizes financial statements, executes high-precision quantitative ratio analytics, performs 3-year multi-period trend modeling (CAGR & YoY), calculates corporate finance metrics (NPV, IRR, WACC, Cash Conversion Cycle), and generates **fact-grounded AI executive reports** without hallucinations.

---

## 🎯 1. Business Problems & Solutions Solved by Captrix AI Agent

| Business Challenge / Problem | Traditional Approach (Manual) | Captrix AI Agent Solution |
| :--- | :--- | :--- |
| **Manual Financial Statement Auditing** | Hours of manual data entry, formula checking, and cross-sheet validation in Excel. | **Automated Ingestion & Normalization** in $< 3$ seconds with 0 formula errors. |
| **Inconsistent Accounting Formats** | Custom templates, missing rows, or non-standard line item names cause formula breakage. | **Heuristic Schema Normalization & Fuzzy Token Matching** maps non-standard terms to GAAP/IFRS. |
| **Hidden Financial Distress & Credit Risk** | Ratio calculations are scattered; early warning signals are often missed until audit time. | **Altman Z-Score Hybrid Credit Engine** scores health (0–100) across 4 weighted risk vectors. |
| **Multi-Year Trend & Growth Analysis** | Manual year-over-year alignment across separate annual workbooks is tedious. | **Automated Multi-Period Engine** with side-by-side statement alignment, YoY %, and 3-Year CAGR %. |
| **Data Privacy & Multi-Tenant Security** | Shared drives or insecure web tools risk leaking confidential financial reports. | **Row-Level User Data Isolation** (`Upload.user_id == current_user.id`) with 100% private workspaces. |
| **Static Data vs Interactive Inquiry** | Static PDF/Excel reports cannot answer follow-up questions from board members. | **Grounded AI Copilot Chatbot (RAG)** answers natural language questions using audited numbers. |

---

## 📥 2. Complete System Inputs & Outputs

### 📥 System Inputs
1. **Financial Accounting Workbooks**:
   - Supported File Extensions: `.xlsx`, `.xls`, `.xlsm`, `.xlsb`, `.csv`, `.tsv`, `.ods`, `.txt`.
   - Supported Statements: Income Statements (P&L), Balance Sheets, Cash Flow Statements, Trial Balances, General Ledgers.
2. **User Context & Parameters**:
   - Target Company Name, Industry Sector, Custom Discount Rate ($r$), Tax Rate ($T$).
3. **Conversational Queries**:
   - Natural language questions submitted to the AI CFO Copilot (e.g., *"What is our Working Capital Cycle and how can we optimize inventory?"*).

### 📤 System Outputs
1. **Executive Financial Health Scorecard**:
   - Overall Health Score (0–100) with color-coded status badges (`HEALTHY` 🟢, `WARNING` 🟡, `CRITICAL` 🔴).
2. **4-Vector Ratio Analysis Matrix**:
   - Profitability, Liquidity, Solvency, and Efficiency ratios with industry benchmark progress meters.
3. **Multi-Year Financial Trend Dashboard**:
   - Side-by-side 3-Year Comparative Income Statement & Balance Sheet (FY2023, FY2024, FY2025).
   - YoY Growth Rates (%) and 3-Year Compound Annual Growth Rates (CAGR %).
4. **Corporate Finance Valuation Module**:
   - Capital Budgeting (NPV & IRR), WACC breakdown, and Cash Conversion Cycle (DIO, DSO, DPO).
5. **Grounded AI Audit Report**:
   - Executive summary, key operational strengths, risk vulnerabilities, and strategic CFO recommendations.
6. **Exportable Audit Packages**:
   - Professional PDF Audit Reports and Multi-Tab Formatted Excel Workbooks.

---

## 🧮 3. Algorithms & Mathematical Models

The platform combines **pure deterministic financial mathematics** with **machine learning heuristics**:

### A. Compound Annual Growth Rate (CAGR) Formula
Calculates multi-year annualized growth velocity:
$$\text{CAGR} = \left(\frac{\text{Ending Value}}{\text{Beginning Value}}\right)^{\frac{1}{n}} - 1$$

### B. Net Present Value (NPV) Cash Flow Discounting
Determines the present value of future cash flows discounted at rate $r$:
$$\text{NPV} = \sum_{t=1}^{N} \frac{CF_t}{(1 + r)^t} - CF_0$$

### C. Internal Rate of Return (IRR) Newton-Raphson Root-Finding Algorithm
Calculates the exact discount rate where $\text{NPV}(r) = 0$ using iterative differentiation:
$$r_{n+1} = r_n - \frac{\text{NPV}(r_n)}{\text{NPV}'(r_n)}$$

### D. Weighted Average Cost of Capital (WACC)
Computes blended capital cost across equity and debt:
$$\text{WACC} = \left(\frac{E}{V} \times R_e\right) + \left(\frac{D}{V} \times R_d \times (1 - T)\right)$$

### E. Working Capital Cash Conversion Cycle (CCC) Algorithm
$$\text{CCC} = \text{DIO} + \text{DSO} - \text{DPO}$$
- **Days Inventory Outstanding ($\text{DIO}$)** = $\left(\frac{\text{Inventory}}{\text{COGS}}\right) \times 365$
- **Days Sales Outstanding ($\text{DSO}$)** = $\left(\frac{\text{Accounts Receivable}}{\text{Revenue}}\right) \times 365$
- **Days Payables Outstanding ($\text{DPO}$)** = $\left(\frac{\text{Accounts Payable}}{\text{COGS}}\right) \times 365$

### F. Composite Financial Health Scoring (Altman Z-Score Hybrid)
$$\text{Health Score} = 0.30(\text{Profitability}) + 0.30(\text{Liquidity}) + 0.25(\text{Solvency}) + 0.15(\text{Efficiency})$$

### G. NIST PBKDF2-HMAC-SHA256 Cryptographic Authentication
Protects user credentials with 100,000+ key derivation iterations, eliminating 72-byte truncation limits.

---

## 🤖 4. How Artificial Intelligence Assists the Agent

```
  ┌──────────────────────────┐      ┌──────────────────────────┐      ┌──────────────────────────┐
  │   Uploaded Financial     │ ───► │  Deterministic Python    │ ───► │   Structured Financial   │
  │    Excel / CSV File      │      │    Parser & Math Engine  │      │     Data Context (JSON)  │
  └──────────────────────────┘      └──────────────────────────┘      └────────────┬─────────────┘
                                                                                   │
                                                                                   ▼
  ┌──────────────────────────┐      ┌──────────────────────────┐      ┌──────────────────────────┐
  │   Executive Dashboard,   │ ◄─── │ Grounded LLM Synthesis   │ ◄─── │ Retrieval-Augmented      │
  │ PDF Audit & AI Copilot   │      │ (Zero Hallucination RAG) │      │ Generation (RAG) Prompt  │
  └──────────────────────────┘      └──────────────────────────┘      └──────────────────────────┘
```

1. **Deterministic Processing First**:
   The AI **never** guesses financial numbers. All ratios, statements, and NPV/IRR figures are calculated by deterministic Python math algorithms **before** passing them to the AI model.

2. **Retrieval-Augmented Generation (RAG)**:
   The calculated financial context is injected into a strict system prompt. The LLM (Gemini 1.5 Pro / Flash) functions as an **auditor and strategic interpreter**, explaining *why* ratios changed and recommending actionable CFO initiatives.

3. **Fuzzy Schema Normalization**:
   Heuristic regex algorithms categorize non-standard line item names (e.g. mapping `"Turnover"`, `"Sales"`, `"Gross Inflows"` $\rightarrow$ `Revenue`).

4. **Conversational AI CFO Copilot**:
   Users can chat directly with the agent regarding their specific workbook. The agent references exact line items from the uploaded file to answer questions.

---

## 🔒 5. Multi-Tenant Privacy & Data Isolation

Captrix AI Agent enforces **Row-Level Tenant Isolation**:
- Every uploaded workbook, ratio calculation, history log, PDF report, and chat session is tagged with `user_id`.
- All database queries enforce `filter(Upload.user_id == current_user.id)`.
- If User B attempts to access User A's `upload_id` via URL tampering, the backend returns **`HTTP 404 Access Denied`**.

---

## 🛠️ 6. Technology Stack

- **Backend**: FastAPI (Python 3.14), SQLAlchemy ORM, Uvicorn, Pytest, Passlib (PBKDF2-SHA256), ReportLab (PDF), OpenPyXL (Excel).
- **Frontend**: Next.js 14 (App Router), TypeScript, TailwindCSS, Axios (`api.ts`), Lucide Icons, Recharts.
- **Authentication**: JWT Bearer Tokens + Firebase Auth integration.

---

## ⚡ 7. Local Setup & Installation

### Backend Setup
```bash
# 1. Navigate to backend directory
cd backend

# 2. Activate virtual environment
.venv\Scripts\python.exe -m pip install -r requirements.txt

# 3. Run automated unit & security tests
.venv\Scripts\python.exe -m pytest tests/

# 4. Start FastAPI server
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
