# CryptoChain Analyzer Dashboard

## Student Information
- Name: Marta Navarro
- GitHub username: martanavarroguil5

## Project Title
Bitcoin Proof Explorer

## Chosen AI Approach
Statistical anomaly detection for unusual Bitcoin block inter-arrival times. The first version will use z-scores as an interpretable baseline, then compare it with an Isolation Forest model trained on historical block timing features.

## Module Tracking
- M1 Proof of Work Monitor: Operational - live Blockstream data, proof-of-work target, estimated hash rate, and recent block interval charts are implemented.
- M2 Block Header Analyzer: Operational - the latest 80-byte header is parsed, all six fields are displayed, and Proof of Work is verified locally with hashlib.
- M3 Difficulty History: Operational - recent 2016-block adjustment periods are loaded from the API, plotted, and compared against the 600-second target.
- M4 AI Component: Checkpoint skeleton - anomaly detection approach selected with a live z-score preview; final Isolation Forest evaluation is pending.
- M5-M7 Optional Modules: Not selected yet.

## Current Progress
- Repository cloned and connected to GitHub with the expected classroom structure.
- First API script completed with live Bitcoin data from Blockstream.
- Streamlit dashboard created with automatic refresh and tabs for M1, M2, M3, and M4.
- M1, M2, and M3 are operational for the 29 April checkpoint.
- M4 has a documented anomaly detection skeleton with live feature preview.

## Next Step
- Complete M4 by training and evaluating the Isolation Forest anomaly detector on a larger historical block sample.

## Main Problem or Blocker
- No major blocker right now. The remaining challenge is building a clear evaluation for the final AI model.

## How to Run
```bash
pip install -r requirements.txt
streamlit run app.py
```
