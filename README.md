# Quant Job Optimization Engine (QJOE)

## Overview

QJOE is a deterministic system designed to optimize quantitative finance job applications.

It automates the full pipeline from job collection to application preparation, while enforcing strict rule-based decision making.

The system focuses on:
- extracting factual information from job offers
- scoring opportunities based on predefined criteria
- generating tailored application materials

⚠️ No application is ever sent automatically. Human validation is required.

---

## Core Principles

- Deterministic decision-making (no AI in scoring or filtering)
- No hallucination: missing information is set to `null`
- Human-in-the-loop at all times
- Strict alignment with predefined criteria
- Robustness over complexity

---

## Pipeline
COLLECT
→ EXTRACT_JOB
→ NORMALIZE_JOB
→ GATE
→ SCORE
→ PREPARE_APPLICATION
→ NOTIFY
→ HUMAN_APPROVE
→ TRACK


---

## Key Features

### Job Extraction

- Converts raw job descriptions into structured JSON
- Only explicit information is extracted
- No inference or interpretation

---

### Normalization

- Maps extracted data into controlled categories
- Standardizes fields such as:
  - role type
  - seniority
  - quant intensity
  - technical flags (pricing, risk, etc.)

---

### Gating (Hard Filters)

Automatic rejection of roles that do not fit target criteria:
- reporting-heavy roles
- PhD-only positions
- hardcore C++ roles
- non-quant positions

---

### Scoring System

- Fully deterministic scoring (0–100)
- Based only on predefined rules

Decision:
- Score ≥ 50 → GREEN
- Score < 50 → RED

No intermediate or AI-based validation.

---

### Application Generation

- CV and email templates generated automatically
- Based on role category (Risk, Pricing, Energy, etc.)
- Fully standardized output

---

### Email Drafting

- Gmail draft creation
- Optional batching via BCC for manual sending

---

### Tracking

The system stores:
- extracted job data
- normalized data
- score and decision
- application status

This enables performance monitoring and future optimization.

---

## Tech Stack

- Python (FastAPI)
- Google Sheets (data storage)
- Gmail API (draft generation)
- VPS deployment (optional)

---

## Current Status

- End-to-end pipeline operational
- Deterministic scoring implemented
- Application generation functional
- Manual validation workflow in place

---

## Roadmap

- Job crawling integration
- Application performance tracking
- Improved batching system (BCC strategy)
- Infrastructure optimization

---

## Motivation

Most job application tools rely heavily on AI, leading to inconsistent and non-transparent decisions.

QJOE is built to ensure:
- full control over decision logic
- reproducibility
- strict alignment with personal career goals

---

## Author

Quantitative finance graduate with a focus on:
- Market Risk
- Quantitative Risk
- Derivatives
