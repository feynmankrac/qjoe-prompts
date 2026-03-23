# Quant Job Optimization Engine (QJOE)

## Overview

Deterministic system to filter, score, and generate applications for quant roles.

No LLM in decision. No automation without validation. Full control.

⚠️ No application is ever sent automatically. Human validation is mandatory.

---
## System Architecture

```mermaid
flowchart LR

%% ENTRY POINTS
subgraph Entry Points
    A1[orchestrator.py]
    A2[orchestrator_spontaneous.py]
    A3[api.py]
end

%% CORE PIPELINE
subgraph Core Pipeline
    B1[extract.py]
    B2[normalize.py]
    B3[gate.py]
    B4[score.py]
    B5[pipeline.py]
end

%% APPLICATION GENERATION
subgraph Application Layer
    C1[template_mapper.py]
    C2[cover_letter.py]
    C3[email_generator.py]
    C4[patch_latex_cv.py]
    C5[latex_compiler.py]
end

%% SUPPORT MODULES
subgraph Support
    D1[job_memory.py]
    D2[logger.py]
    D3[language_strategy.py]
    D4[application_mode.py]
end

%% INFRA
subgraph Infra
    E1[gmail_client.py]
    E2[sheet_client.py]
    E3[drive_uploader.py]
end

%% FLOW
A1 --> B5
A2 --> B5
A3 --> B5

B5 --> B1
B5 --> B2
B5 --> B3
B5 --> B4

B5 --> C1
B5 --> C2
B5 --> C3
B5 --> C4
B5 --> C5

B5 --> D1
B5 --> D2
B5 --> D3
B5 --> D4

C3 --> E1
B5 --> E2
C5 --> E3
```

## Core Principles

- 100% deterministic pipeline  
- No LLM in decision-making  
- No hallucination (missing data → null)  
- Human-in-the-loop mandatory  
- Robustness over complexity  

---

## Pipeline

COLLECT → EXTRACT → NORMALIZE → GATE → SCORE → GENERATE → VALIDATE → TRACK

---

## What It Does

- Extracts structured data from job offers  
- Filters out irrelevant roles (reporting-heavy, non-quant, etc.)  
- Scores opportunities (0–100, deterministic)  
- Generates CV + email automatically  
- Prepares drafts (no auto-send)  
- Tracks results for optimization  

---

## Decision Rule

- Score ≥ 50 → GREEN  
- Score < 50 → RED  

No override. No grey zone.

---

## Tech Stack

Python (FastAPI) • Google Sheets • Gmail API • VPS  

---

## Status

- End-to-end pipeline operational  
- Deterministic scoring implemented  
- Application generation functional  
- Manual validation workflow active  

---

## Why QJOE

Most job application tools rely on AI, leading to inconsistent and opaque decisions.

QJOE ensures:
- transparency  
- reproducibility  
- strategic control  

---

## Author

Quantitative Finance — Market Risk, Quant Risk, Derivatives
