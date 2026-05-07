# 🛡️ TenderMind AI
### AI-powered Tender Evaluation System for CRPF Procurement

> **Reducing 30-45 days of manual bid evaluation to under 2 minutes.**

---

## 🌐 Live Demo

**Try it here:** https://huggingface.co/spaces/gargi-14/TenderMind-AI

---

## 💡 What is TenderMind AI?

TenderMind AI is an intelligent procurement evaluation platform built for Indian paramilitary forces (CRPF). It uses AI to:

- Automatically extract eligibility criteria from tender documents
- Evaluate multiple bidders against those criteria instantly
- Give a three-verdict decision: **Eligible / Not Eligible / Needs Manual Review**
- Explain every decision with clause references (no black box)
- Flag suspicious patterns automatically (fraud detection)
- Maintain a tamper-proof blockchain-style audit trail

---

## ✨ Key Features

| Feature | Description |
|---|---|
| 📄 AI Criteria Extraction | Upload any tender PDF/DOCX — AI reads and extracts all eligibility criteria |
| ⚖️ Three-Verdict System | Eligible / Not Eligible / Needs Manual Review (not just pass/fail) |
| 🔍 Explainable Decisions | Every verdict shows which clause was checked and why |
| 🚨 Fraud Detection | AI flags suspicious or inconsistent information automatically |
| 🔗 Blockchain Audit Trail | Every action logged with SHA-256 hash chain — tamper proof |
| 📊 Bidder Dashboard | Side-by-side ranking of all bidders by score |
| 🆓 Zero Cost | Entire system runs for free |

---

## 🎯 How to Use (Live Demo)

### Step 1 — Upload Tender
1. Go to the live demo link above
2. Click **"Upload Tender"** in the sidebar
3. Upload a tender PDF, DOCX, or TXT file
4. Click **"Extract Criteria"**
5. AI will extract all eligibility criteria in ~30 seconds

### Step 2 — Evaluate Bidders
1. Click **"Evaluate Bidders"** in the sidebar
2. Enter the Tender ID (shown after uploading)
3. Enter the company name
4. Upload the bidder's document
5. Click **"Evaluate Bidder"**
6. See the instant verdict with full explanation

### Step 3 — View Dashboard
1. Click **"Dashboard"** to see all bidders ranked by score
2. Click **"Audit Log"** to see the blockchain hash chain

---

## 🧪 Demo Files

Use these sample files to test the system:

### demo_tender.txt
```
CRPF TENDER - BODY ARMOUR VESTS
Tender No: CRPF/2025/EQUIP/0042

ELIGIBILITY CRITERIA:
C1. Annual Turnover: Minimum INR 5 Crore in last 3 financial years (MANDATORY)
C2. Defence Experience: Minimum 3 years supplying to defence/paramilitary forces (MANDATORY)
C3. BIS Certification: Valid BIS IS 17051 certification required (MANDATORY)
C4. GST Registration: Valid GST number mandatory (MANDATORY)
C5. MSME Registration: Preference given to MSME firms (OPTIONAL)

Quantity: 500 units. EMD: INR 2,50,000.
```

### bidder1_apex.txt → Expected: ✅ Eligible
```
Company: Apex Defence Solutions Pvt Ltd
GST Number: 07AABCA1234A1Z5 (Active)
Annual Turnover: FY2022: Rs 7.2 Crore, FY2023: Rs 8.9 Crore, FY2024: Rs 10.1 Crore
Defence Supply Experience: 7 years. Clients: CRPF (2019-2024), BSF (2021-2024)
BIS Certification: IS 17051:2022, valid till March 2027
MSME Registration: UDYAM-DL-09-0012345
```

### bidder2_cheap.txt → Expected: ❌ Not Eligible
```
Company: Cheap Fabric House
GST: Not registered
Turnover: Rs 80 lakhs in FY2024
Experience: We make school uniforms since 2020
BIS: Not applicable
```

### bidder3_kaveri.txt → Expected: ⚠️ Needs Manual Review
```
Company: Kaveri Tactical Pvt Ltd
GST: 29AAGCK5678B1Z3 (Valid)
Annual Turnover: FY2024: Rs 6.1 Crore (only 1 year data)
Defence Experience: Supplied to Karnataka State Police only
BIS Certification: Applied, approval pending
MSME: Registered
```

---

## 🏗️ Tech Stack

| Layer | Technology | Cost |
|---|---|---|
| Frontend | React + Vite | Free |
| Backend | FastAPI (Python) | Free |
| AI Engine | OpenRouter API | Free |
| Database | SQLite | Free |
| Audit Trail | SHA-256 Hash Chain | Free |
| File Parsing | pdfplumber + python-docx | Free |
| Hosting | Hugging Face Spaces | Free |

**Total infrastructure cost: ₹0**

---

## 🚀 Run Locally

### Prerequisites
- Python 3.12+
- Node.js LTS
- OpenRouter API key (free at openrouter.ai)

### Step 1 — Get API key
1. Go to **openrouter.ai** → Sign up → Create API key
2. Open `backend/config.py` and paste your key:
```python
import os
GEMINI_API_KEY = os.getenv("OPENROUTER_KEY", "your-key-here")
```

### Step 2 — Set up and run backend
```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python -m uvicorn main:app --port 8000
```

### Step 3 — Set up and run frontend
Open a new terminal:
```bash
cd frontend
npm install
npm run dev
```

Open **http://localhost:5173**

---

## 📁 Project Structure

```
TenderMind/
├── backend/
│   ├── main.py          ← FastAPI server
│   ├── config.py        ← API key config
│   ├── db.py            ← SQLite + audit trail
│   ├── requirements.txt
│   ├── Dockerfile
│   ├── static/          ← Built React frontend
│   ├── routes/
│   │   ├── tender.py    ← Tender upload & extraction
│   │   ├── bidder.py    ← Bidder evaluation
│   │   └── report.py    ← Dashboard & audit log
│   └── utils/
│       ├── ai.py        ← AI evaluation engine
│       └── extract.py   ← PDF/DOCX text extraction
└── frontend/
    ├── src/
    │   ├── pages/
    │   │   ├── Home.jsx
    │   │   ├── TenderUpload.jsx
    │   │   ├── EvaluateBidders.jsx
    │   │   ├── Dashboard.jsx
    │   │   └── AuditLog.jsx
    │   ├── App.jsx
    │   └── index.css
    └── vite.config.js
```

---

## 👥 Team Teen Titans

Built for hackathon demonstration of AI in government procurement.
