
# CryptoChain Analyzer Dashboard

## Student Information
- Name: Marta Navarro
- GitHub username: martanavarroguil5

## Project Title
Bitcoin Proof Explorer

## Chosen AI Approach
Statistical anomaly detection for unusual Bitcoin block inter-arrival times. The dashboard uses z-scores as an interpretable baseline and compares them with an Isolation Forest model trained on recent historical block timing features. The app is designed as a guided explanation: it starts from live Bitcoin data, verifies a real block header locally, explains difficulty adjustment, and then uses the timing context as input for the AI module.

## Module Tracking
Use one of these values: `Not started`, `In progress`, `Done`

| Module | Description | Status |
|---|---|---|
| M1 | Proof of Work Monitor: Live data from Blockstream, PoW target, estimated hash rate, interval charts with explanations | Done |
| M2 | Block Header Analyzer: Parses 80-byte header, explains fields, verifies PoW locally | Done |
| M3 | Difficulty History: Loads recent adjustment periods, plots and interprets vs. 600s target | Done |
| M4 | AI Component: Live feature engineering, baseline z-score, Isolation Forest, anomaly candidate table | Done |
| M5-M7 | Optional Modules | Not started |

## Current Progress
- Repository structure matches classroom template and is connected to GitHub.
- Live Bitcoin data API integration and first script completed.
- Streamlit dashboard fully rebranded and organized for clarity.
- M1, M2, and M3 modules are complete and operational.
- M4 AI module implemented: live feature extraction, unsupervised anomaly detection, and candidate ranking.

## Next Step
- Final review of the Streamlit app, visual polish, screenshot capture, and repository submission.

## Main Problem or Blocker
- No major blockers. M4 is unsupervised, so evaluation is based on anomaly rate, agreement with statistical thresholds, and candidate inspection. The main design goal is clarity for reviewers: each module explains what is shown, why it matters, and how to interpret results.

## How to Run
```bash
pip install -r requirements.txt
streamlit run app.py
```
