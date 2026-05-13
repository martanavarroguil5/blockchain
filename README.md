# ProofLab Bitcoin

## Student Information
- Name: Marta Navarro
- GitHub username: martanavarroguil5

## Project Title
ProofLab Bitcoin: una visita guiada por la prueba de trabajo

## Chosen AI Approach
Statistical anomaly detection for unusual Bitcoin block inter-arrival times. The dashboard uses z-scores as an interpretable baseline and compares them with an Isolation Forest model trained on recent historical block timing features.

The app is now designed as a guided explanation rather than a collection of isolated technical answers: it starts from live Bitcoin data, verifies one real block header locally, explains difficulty adjustment, and then uses the timing context as input for the AI module.

## Module Tracking
- M1 Red en directo: Operativo - usa datos live de Blockstream, objetivo de proof-of-work, hash rate estimado y graficas de intervalos con notas explicativas.
- M2 Header: Operativo - parsea el header de 80 bytes, explica sus seis campos y verifica el Proof of Work localmente con hashlib.
- M3 Dificultad: Operativo - carga periodos recientes de ajuste de 2016 bloques, los grafica y los interpreta frente al objetivo de 600 segundos.
- M4 IA: Operativo - genera features temporales live, calcula un baseline z-score y usa Isolation Forest para ordenar candidatos anomalos.
- M5-M7 Optional Modules: Not selected yet.

## Current Progress
- Repository cloned and connected to GitHub with the expected classroom structure.
- First API script completed with live Bitcoin data from Blockstream.
- Streamlit dashboard rebranded as ProofLab Bitcoin with a clearer visual hierarchy and Spanish explanatory copy.
- M1, M2, and M3 are operational for the 29 April checkpoint.
- M4 is now implemented as a final AI module with live feature engineering, unsupervised model training, baseline comparison, and an anomaly candidate table.

## Next Step
- Run the Streamlit app, review the final visual presentation, capture screenshots, and prepare the repository for submission.

## Main Problem or Blocker
- No major blocker right now. M4 is unsupervised, so the evaluation reports anomaly rate, agreement with statistical tail thresholds, and ranked candidate inspection instead of supervised accuracy.
- The main design goal is clarity for a reviewer who has not built the project: each module now explains what the viewer is seeing, why it matters, and how to interpret the result.

## How to Run
```bash
pip install -r requirements.txt
streamlit run app.py
```

<!-- student-repo-auditor:teacher-feedback:start -->
## Teacher Feedback

### Kick-off Review

Review time: 2026-04-29 20:44 CEST
Status: Amber

Strength:
- I can see the dashboard structure integrating the checkpoint modules.

Improve now:
- The README should now reflect the checkpoint more explicitly, including progress, blockers, and updated module status.

Next step:
- Update the README so progress, blockers, module status, and next step match the checkpoint format exactly.
<!-- student-repo-auditor:teacher-feedback:end -->
