"""
ATES Architecture Diagram Generator
Produces a professional cloud-style PNG architecture diagram for the
AI-based Tender Evaluation System (ATES).
"""

import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import matplotlib.patheffects as pe

# ── Canvas ────────────────────────────────────────────────────────────────────
FIG_W, FIG_H = 22, 16
fig, ax = plt.subplots(figsize=(FIG_W, FIG_H))
ax.set_xlim(0, FIG_W)
ax.set_ylim(0, FIG_H)
ax.axis("off")

# ── Colour palette ────────────────────────────────────────────────────────────
BG          = "#0F1923"   # deep navy background
LANE_AI     = "#0D2137"   # AI pipeline lane
LANE_INFRA  = "#0D1F2D"   # infrastructure lane
LANE_CROSS  = "#111D2B"   # cross-cutting lane

C_BLUE      = "#1A6EBD"   # primary module fill
C_BLUE_LT   = "#2589D8"   # lighter blue
C_TEAL      = "#0E8A7A"   # teal accent
C_PURPLE    = "#6B3FA0"   # purple accent
C_ORANGE    = "#C96A1A"   # orange accent
C_RED       = "#B03030"   # red accent
C_GREEN     = "#1E7A45"   # green accent
C_GREY      = "#2A3A4A"   # neutral grey
C_GOLD      = "#A07820"   # gold accent

TEXT_MAIN   = "#E8F0F8"
TEXT_SUB    = "#8AAAC8"
TEXT_LABEL  = "#FFFFFF"
ARROW_CLR   = "#4A9FD4"
ARROW_CROSS = "#6ABFA0"

# ── Background ────────────────────────────────────────────────────────────────
fig.patch.set_facecolor(BG)
ax.set_facecolor(BG)

# ── Helper: rounded box ───────────────────────────────────────────────────────
def box(ax, x, y, w, h, fill, label, sublabel="", icon="",
        border="#3A6A9A", alpha=0.92, lw=1.5, radius=0.35):
    rect = FancyBboxPatch(
        (x, y), w, h,
        boxstyle=f"round,pad=0,rounding_size={radius}",
        linewidth=lw, edgecolor=border,
        facecolor=fill, alpha=alpha, zorder=3
    )
    ax.add_patch(rect)
    # top colour bar
    bar = FancyBboxPatch(
        (x, y + h - 0.28), w, 0.28,
        boxstyle=f"round,pad=0,rounding_size={radius}",
        linewidth=0, facecolor=border, alpha=0.7, zorder=4
    )
    ax.add_patch(bar)
    # icon + label
    cx = x + w / 2
    if icon:
        ax.text(cx, y + h - 0.14, icon, ha="center", va="center",
                fontsize=9, color=TEXT_LABEL, zorder=5, fontweight="bold")
    if sublabel:
        ax.text(cx, y + h / 2 + 0.18, label,
                ha="center", va="center", fontsize=8.2, color=TEXT_LABEL,
                fontweight="bold", zorder=5)
        ax.text(cx, y + h / 2 - 0.22, sublabel,
                ha="center", va="center", fontsize=6.8, color=TEXT_SUB,
                zorder=5, style="italic")
    else:
        ax.text(cx, y + h / 2, label,
                ha="center", va="center", fontsize=8.4, color=TEXT_LABEL,
                fontweight="bold", zorder=5)

# ── Helper: arrow ─────────────────────────────────────────────────────────────
def arrow(ax, x1, y1, x2, y2, color=ARROW_CLR, lw=1.6,
          style="->", rad=0.0, label=""):
    ax.annotate(
        "", xy=(x2, y2), xytext=(x1, y1),
        arrowprops=dict(
            arrowstyle=style, color=color, lw=lw,
            connectionstyle=f"arc3,rad={rad}",
        ), zorder=6
    )
    if label:
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        ax.text(mx + 0.05, my + 0.12, label, fontsize=6.2,
                color=color, ha="center", zorder=7)

# ── Helper: lane background ───────────────────────────────────────────────────
def lane(ax, x, y, w, h, fill, title, title_color="#4A9FD4"):
    rect = FancyBboxPatch(
        (x, y), w, h,
        boxstyle="round,pad=0,rounding_size=0.5",
        linewidth=1, edgecolor="#1E3A5A",
        facecolor=fill, alpha=0.55, zorder=1
    )
    ax.add_patch(rect)
    ax.text(x + 0.25, y + h - 0.28, title,
            fontsize=7.5, color=title_color, fontweight="bold",
            va="top", zorder=2, alpha=0.85)

# ══════════════════════════════════════════════════════════════════════════════
# TITLE
# ══════════════════════════════════════════════════════════════════════════════
ax.text(FIG_W / 2, 15.55,
        "AI-Based Tender Evaluation System (ATES)",
        ha="center", va="center", fontsize=17, color=TEXT_MAIN,
        fontweight="bold", zorder=10)
ax.text(FIG_W / 2, 15.18,
        "Enterprise Architecture  ·  MCP-Style Modular Pipeline",
        ha="center", va="center", fontsize=9.5, color=TEXT_SUB, zorder=10)

# ── Divider line ──────────────────────────────────────────────────────────────
ax.plot([0.5, 21.5], [14.95, 14.95], color="#1E3A5A", lw=1, zorder=2)

# ══════════════════════════════════════════════════════════════════════════════
# LANE 1 — External Entry (top)
# ══════════════════════════════════════════════════════════════════════════════
lane(ax, 0.4, 13.3, 21.2, 1.5, LANE_CROSS, "  EXTERNAL ENTRY POINTS", "#6ABFA0")

# API Gateway
box(ax, 1.0, 13.55, 3.2, 1.0, C_TEAL,
    "API Gateway", "Rate Limiting · Auth", "[GW]",
    border="#0E8A7A")

# Document Ingestion Gateway
box(ax, 5.2, 13.55, 3.5, 1.0, C_TEAL,
    "Document Ingestion", "Gateway · Multi-format", "[IN]",
    border="#0E8A7A")

# Admin Dashboard
box(ax, 9.8, 13.55, 3.2, 1.0, C_PURPLE,
    "Admin Dashboard", "Config · Monitoring", "[ADM]",
    border="#6B3FA0")

# Monitoring & Logging
box(ax, 14.2, 13.55, 3.5, 1.0, C_ORANGE,
    "Monitoring & Logging", "Metrics · Alerts · Logs", "[MON]",
    border="#C96A1A")

# Pipeline Orchestrator
box(ax, 18.3, 13.55, 3.1, 1.0, C_GOLD,
    "Pipeline Orchestrator", "Sequencing · Retry", "[ORC]",
    border="#A07820")

# ══════════════════════════════════════════════════════════════════════════════
# LANE 2 — AI Processing Pipeline
# ══════════════════════════════════════════════════════════════════════════════
lane(ax, 0.4, 7.8, 21.2, 5.3, LANE_AI, "  AI PROCESSING PIPELINE", "#4A9FD4")

# Row A — OCR + NLP + Semantic (y ≈ 11.2)
ROW_A_Y = 11.1

box(ax, 1.0, ROW_A_Y, 3.2, 1.55, C_BLUE,
    "OCR Engine", "PDF·DOCX·IMG·XLSX", "[OCR]",
    border=C_BLUE_LT)

box(ax, 5.2, ROW_A_Y, 3.5, 1.55, C_BLUE,
    "NLP Processor", "Clause Eval · Confidence", "[NLP]",
    border=C_BLUE_LT)

box(ax, 9.8, ROW_A_Y, 3.5, 1.55, C_BLUE,
    "Semantic Matching", "Engine · Embeddings", "[SEM]",
    border=C_BLUE_LT)

# Row B — Eligibility Classifier (centre, y ≈ 9.0)
ROW_B_Y = 9.0

box(ax, 5.5, ROW_B_Y, 5.5, 1.55, C_GREEN,
    "Eligibility Evaluation Engine",
    "Eligible · Cond. Eligible · Ineligible", "[ELG]",
    border="#1E7A45", lw=2.0)

# Review Interface (right of classifier)
box(ax, 12.5, ROW_B_Y, 3.5, 1.55, C_PURPLE,
    "Manual Review Interface",
    "Annotate · Override · Approve", "[REV]",
    border="#6B3FA0")

# Report Generator (far right)
box(ax, 17.2, ROW_B_Y, 3.9, 1.55, C_BLUE,
    "Evaluation Report Gen.",
    "PDF · JSON · Signed", "[RPT]",
    border=C_BLUE_LT)

# Row C — Ruleset Manager (left, y ≈ 8.0)
box(ax, 1.0, ROW_B_Y, 3.2, 1.55, C_GREY,
    "Eligibility Ruleset", "Manager · Versioned", "[RLS]",
    border="#3A5A7A")

# ══════════════════════════════════════════════════════════════════════════════
# LANE 3 — Cross-Cutting Services
# ══════════════════════════════════════════════════════════════════════════════
lane(ax, 0.4, 4.5, 21.2, 3.1, LANE_CROSS,
     "  CROSS-CUTTING SECURITY & AUDIT SERVICES", "#C06060")

box(ax, 1.0, 4.75, 4.5, 1.8, C_RED,
    "Cryptographic Security Layer",
    "SHA-256 · AES-256-GCM · RSA/ECDSA · TLS 1.3", "[SEC]",
    border="#B03030", lw=2.0)

box(ax, 7.0, 4.75, 7.5, 1.8, "#1A3A5A",
    "Blockchain Audit Layer",
    "Append-Only · Hash-Chained · Tamper-Evident · JSON/CSV Export", "[AUD]",
    border="#2A6A9A", lw=2.0)

box(ax, 16.0, 4.75, 5.2, 1.8, C_GREY,
    "Key Management Service",
    "KMS · HSM Integration · Key Rotation", "[KMS]",
    border="#3A5A7A")

# ══════════════════════════════════════════════════════════════════════════════
# LANE 4 — Data Layer
# ══════════════════════════════════════════════════════════════════════════════
lane(ax, 0.4, 1.0, 21.2, 3.2, LANE_INFRA,
     "  DATA & STORAGE LAYER", "#6A9A6A")

box(ax, 1.0, 1.3, 3.5, 1.9, C_GREY,
    "Primary Database", "App State · Tenders · Users", "[DB]",
    border="#3A5A7A")

box(ax, 5.5, 1.3, 3.5, 1.9, C_GREY,
    "Document Object Store", "Encrypted · Multi-format", "[OBJ]",
    border="#3A5A7A")

box(ax, 10.0, 1.3, 3.5, 1.9, "#1A2A3A",
    "Audit Chain Store", "Append-Only · Isolated", "[ACH]",
    border="#2A5A7A")

box(ax, 14.5, 1.3, 3.5, 1.9, C_GREY,
    "Evaluation Report Store", "Encrypted · 7-yr Retention", "[ERS]",
    border="#3A5A7A")

box(ax, 19.0, 1.3, 2.6, 1.9, C_GREY,
    "Model Registry", "Embedding Models", "[MDL]",
    border="#3A5A7A")

# ══════════════════════════════════════════════════════════════════════════════
# ARROWS — External Entry → Pipeline
# ══════════════════════════════════════════════════════════════════════════════
# API GW → Doc Ingestion
arrow(ax, 4.2, 14.05, 5.2, 14.05, color=ARROW_CROSS, lw=1.8)
# Doc Ingestion → OCR Engine
arrow(ax, 6.95, 13.55, 2.6, 12.65, color=ARROW_CLR, lw=1.8, rad=0.1)
# Pipeline Orchestrator → OCR
arrow(ax, 19.85, 13.55, 2.6, 12.65, color="#C0A030", lw=1.5, rad=-0.15)

# ══════════════════════════════════════════════════════════════════════════════
# ARROWS — AI Pipeline flow
# ══════════════════════════════════════════════════════════════════════════════
# OCR → NLP
arrow(ax, 4.2, 11.875, 5.2, 11.875, color=ARROW_CLR, lw=2.0)
# OCR → Semantic
arrow(ax, 4.2, 11.875, 9.8, 11.875, color=ARROW_CLR, lw=1.5, rad=-0.2,
      label="Document Object")
# NLP → Eligibility Classifier
arrow(ax, 6.95, 11.1, 7.5, 10.55, color=ARROW_CLR, lw=2.0)
# Semantic → Eligibility Classifier
arrow(ax, 11.55, 11.1, 9.5, 10.55, color=ARROW_CLR, lw=2.0)
# Ruleset Manager → NLP
arrow(ax, 2.6, 9.0, 6.95, 11.1, color="#5A8AAA", lw=1.4, rad=0.15,
      label="Ruleset")
# Ruleset Manager → Semantic
arrow(ax, 4.2, 9.775, 9.8, 11.1, color="#5A8AAA", lw=1.2, rad=-0.1)
# Eligibility Classifier → Review Interface (escalation)
arrow(ax, 11.0, 9.775, 12.5, 9.775, color="#9A60C0", lw=1.8,
      label="Escalate")
# Eligibility Classifier → Report Gen (direct)
arrow(ax, 11.0, 9.775, 17.2, 9.775, color=ARROW_CLR, lw=1.5, rad=-0.2,
      label="Auto")
# Review Interface → Report Gen
arrow(ax, 16.0, 9.775, 17.2, 9.775, color="#9A60C0", lw=1.8)

# ══════════════════════════════════════════════════════════════════════════════
# ARROWS — Pipeline → Cross-cutting
# ══════════════════════════════════════════════════════════════════════════════
# All pipeline → Audit Chain (dashed style via multiple short arrows)
for sx, sy in [(2.6, 9.0), (6.95, 9.0), (11.55, 9.0),
               (8.25, 9.0), (14.25, 9.0), (19.15, 9.0)]:
    arrow(ax, sx, sy, 10.75, 6.55, color="#3A7AAA", lw=1.0, rad=0.0)

# Report Gen → Crypto (sign)
arrow(ax, 19.15, 9.0, 3.25, 6.55, color="#C06060", lw=1.5, rad=0.2,
      label="Sign")
# Crypto → KMS
arrow(ax, 5.5, 5.65, 16.0, 5.65, color="#C06060", lw=1.5)

# ══════════════════════════════════════════════════════════════════════════════
# ARROWS — Cross-cutting → Data Layer
# ══════════════════════════════════════════════════════════════════════════════
arrow(ax, 3.25, 4.75, 2.75, 3.2, color="#AA4040", lw=1.5)   # Crypto → Primary DB
arrow(ax, 10.75, 4.75, 11.75, 3.2, color="#3A7AAA", lw=1.8)  # Audit → Audit Store
arrow(ax, 6.95, 9.0, 7.25, 3.2, color=ARROW_CLR, lw=1.2, rad=0.1)  # Pipeline → Doc Store
arrow(ax, 19.15, 9.0, 16.25, 3.2, color=ARROW_CLR, lw=1.2, rad=0.1)  # Report → Report Store

# ══════════════════════════════════════════════════════════════════════════════
# ARROWS — Admin Dashboard & Monitoring
# ══════════════════════════════════════════════════════════════════════════════
arrow(ax, 11.4, 13.55, 11.4, 10.65, color="#9A60C0", lw=1.4, rad=0.0,
      label="Config")
arrow(ax, 15.95, 13.55, 15.95, 10.65, color="#C06A1A", lw=1.4, rad=0.0,
      label="Metrics")

# ══════════════════════════════════════════════════════════════════════════════
# LEGEND
# ══════════════════════════════════════════════════════════════════════════════
legend_x, legend_y = 0.55, 4.2
legend_items = [
    (C_TEAL,    "Entry / Gateway"),
    (C_BLUE,    "AI Processing Module"),
    (C_GREEN,   "Classification Engine"),
    (C_PURPLE,  "Review / Admin"),
    (C_RED,     "Security Layer"),
    ("#1A3A5A", "Audit / Blockchain"),
    (C_GREY,    "Infrastructure / Data"),
    (C_GOLD,    "Orchestration"),
]
ax.text(legend_x, legend_y + 0.15, "LEGEND",
        fontsize=7, color=TEXT_SUB, fontweight="bold", zorder=10)
for i, (color, label) in enumerate(legend_items):
    lx = legend_x + (i % 4) * 5.3
    ly = legend_y - 0.45 - (i // 4) * 0.55
    rect = FancyBboxPatch((lx, ly), 0.35, 0.28,
                          boxstyle="round,pad=0,rounding_size=0.05",
                          facecolor=color, edgecolor="#3A6A9A",
                          linewidth=0.8, zorder=10)
    ax.add_patch(rect)
    ax.text(lx + 0.45, ly + 0.14, label,
            fontsize=6.8, color=TEXT_SUB, va="center", zorder=10)

# ── Footer ────────────────────────────────────────────────────────────────────
ax.plot([0.5, 21.5], [0.88, 0.88], color="#1E3A5A", lw=0.8, zorder=2)
ax.text(FIG_W / 2, 0.55,
        "ATES v1.0  ·  MCP-Style Modular Architecture  ·  Enterprise Grade  ·  "
        "Blockchain-Audited  ·  Cryptographically Secured",
        ha="center", va="center", fontsize=7, color=TEXT_SUB, zorder=10)

# ══════════════════════════════════════════════════════════════════════════════
# EXPORT
# ══════════════════════════════════════════════════════════════════════════════
os.makedirs("generated-diagrams", exist_ok=True)
out_path = "generated-diagrams/ates-architecture.png"
plt.savefig(out_path, dpi=180, bbox_inches="tight",
            facecolor=BG, edgecolor="none")
plt.close()
print(f"Diagram saved → {out_path}")
