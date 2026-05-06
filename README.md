# Tender-Mind-Ai
AI-Based Tender Evaluation &amp; Eligibility Analysis for Government Procurement using OCR, NLP, Explainable AI &amp; Blockchain Audit Trails.

## What is TenderMind AI?
An AI-powered tender evaluation system for CRPF procurement. It reads tender documents, extracts eligibility criteria, and evaluates bidders automatically — reducing 30-45 days of manual work to under 2 minutes.

---

## Prerequisites

Install these before anything else:

| Tool | Download Link |
|---|---|
| Python 3.12+ | https://python.org/downloads — ⚠️ Check "Add to PATH" during install |
| Node.js LTS | https://nodejs.org |
| VS Code (recommended) | https://code.visualstudio.com |

---

## Project Structure

```
TenderMind/
├── backend/          ← Python FastAPI server (AI brain)
│   ├── main.py
│   ├── config.py     ← Put your API key here
│   ├── db.py
│   ├── routes/
│   │   ├── tender.py
│   │   ├── bidder.py
│   │   └── report.py
│   └── utils/
│       ├── extract.py
│       └── ai.py
└── frontend/         ← React web interface
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

## Step 1 — Get your FREE API Key

1. Go to **https://openrouter.ai**
2. Sign up with Google
3. Click **"Keys"** → **"Create Key"**
4. Copy the key (starts with `sk-or-...`)
5. Open `backend/config.py` and paste it:

```python
GEMINI_API_KEY = "sk-or-paste-your-key-here"
```

---

## Step 2 — Set up the Backend

Open **PowerShell** and run these commands:

```powershell
cd Desktop\TenderMind\backend
python -m venv venv
venv\Scripts\activate
pip install fastapi uvicorn python-multipart pdfplumber python-docx requests
```

---

## Step 3 — Start the Backend

```powershell
cd Desktop\TenderMind\backend
venv\Scripts\activate
python -m uvicorn main:app --port 8000
```

✅ You should see: `Application startup complete.`

Verify at: **http://localhost:8000** → should show `{"status":"TenderMind AI is running"}`

---

## Step 4 — Set up the Frontend

Open a **NEW PowerShell window** and run:

```powershell
cd Desktop\TenderMind\frontend
npm install
```

---

## Step 5 — Start the Frontend

```powershell
cd Desktop\TenderMind\frontend
npm run dev
```

✅ You should see: `VITE ready on http://localhost:5173`

---

## Step 6 — Open the App

Go to **http://localhost:5173** in your browser.

---

## Step 7 — Run the Demo

Use these 4 demo files (create them as plain .txt files):

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

### bidder1_apex.txt (Eligible)
```
Company: Apex Defence Solutions Pvt Ltd
GST Number: 07AABCA1234A1Z5 (Active)
Annual Turnover: FY2022: Rs 7.2 Crore, FY2023: Rs 8.9 Crore, FY2024: Rs 10.1 Crore
Defence Supply Experience: 7 years. Clients: CRPF (2019-2024), BSF (2021-2024)
BIS Certification: IS 17051:2022, valid till March 2027
MSME Registration: UDYAM-DL-09-0012345
```

### bidder2_cheap.txt (Not Eligible)
```
Company: Cheap Fabric House
GST: Not registered
Turnover: Rs 80 lakhs in FY2024
Experience: We make school uniforms since 2020
BIS: Not applicable
```

### bidder3_kaveri.txt (Needs Review)
```
Company: Kaveri Tactical Pvt Ltd
GST: 29AAGCK5678B1Z3 (Valid)
Annual Turnover: FY2024: Rs 6.1 Crore (only 1 year data)
Defence Experience: Supplied to Karnataka State Police only
BIS Certification: Applied, approval pending
MSME: Registered
```

### Demo Flow:
1. **Upload Tender** → upload `demo_tender.txt` → AI extracts 5 criteria
2. **Evaluate Bidders** → add Apex Defence + `bidder1_apex.txt` → **Eligible ✅**
3. **Evaluate Bidders** → add Cheap Fabric + `bidder2_cheap.txt` → **Not Eligible ❌**
4. **Evaluate Bidders** → add Kaveri Tactical + `bidder3_kaveri.txt` → **Needs Review ⚠️**
5. **Dashboard** → see all 3 ranked by score
6. **Audit Log** → show tamper-proof blockchain hash chain

---

## Every Time You Restart

You need to run both servers every time:

**Terminal 1 — Backend:**
```powershell
cd Desktop\TenderMind\backend
venv\Scripts\activate
python -m uvicorn main:app --port 8000
```

**Terminal 2 — Frontend:**
```powershell
cd Desktop\TenderMind\frontend
npm run dev
```

Then open **http://localhost:5173**

---

## Tech Stack

| Layer | Technology | Cost |
|---|---|---|
| Frontend | React + Vite | Free |
| Backend | FastAPI (Python) | Free |
| AI Engine | OpenRouter (LLaMA/GPT) | Free |
| Database | SQLite | Free |
| Audit Trail | SHA-256 Hash Chain | Free |
| File Parsing | pdfplumber + python-docx | Free |

**Total cost: ₹0**

---

## Key Features

- **AI Criteria Extraction** — Automatically reads tender PDFs/DOCX and extracts all eligibility criteria
- **Three-Verdict System** — Eligible / Not Eligible / Needs Manual Review (not just pass/fail)
- **Explainable Decisions** — Every verdict shows which clause was checked, what was found, and why
- **Fraud Detection** — AI flags suspicious patterns automatically
- **Blockchain Audit Trail** — Every action is logged with a SHA-256 hash chain (tamper-proof)
- **VPRS Score** — Vendor Performance Rating Score out of 100
- **Bidder Comparison** — Side-by-side ranking of all bidders

---

## Troubleshooting

| Problem | Fix |
|---|---|
| `venv\Scripts\activate` fails | Run `Set-ExecutionPolicy RemoteSigned` first |
| `No module named uvicorn` | Run `pip install uvicorn` inside venv |
| Backend not starting | Make sure you activated venv first |
| Frontend CORS error | Make sure `vite.config.js` has the proxy config |
| AI returns error | Check your OpenRouter API key in `config.py` |
| Port already in use | Change `--port 8000` to `--port 8001` |
