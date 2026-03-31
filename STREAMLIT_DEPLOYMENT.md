# Deploying the Demo to Streamlit Community Cloud

This repository now has two Streamlit entrypoints:

- Root [`streamlit_app.py`](./streamlit_app.py): lightweight hosted demo for Streamlit Community Cloud
- [`energyplus-mcp-server/streamlit_app.py`](./energyplus-mcp-server/streamlit_app.py): local Docker/EnergyPlus dashboard

For Streamlit Community Cloud, deploy the **root app**.

## Recommended Setup

1. Fork or push the repo to your GitHub account.
2. Go to `https://share.streamlit.io`.
3. Create a new app with:
   - Repository: `YOUR_USERNAME/bayesian-energy-calibration`
   - Branch: `main`
   - Main file path: `streamlit_app.py`

## Why This Version Works Better on Community Cloud

The root app:

- uses committed JSON/CSV/PNG artifacts already in the repo
- does not require Docker
- does not require EnergyPlus
- does not require PyMC at runtime
- uses a lightweight `requirements.txt`

## Local Smoke Test

Before deploying:

```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```

Then open `http://localhost:8501`.

## Notes

- The hosted demo is read-only and artifact-driven.
- The local Docker dashboard remains the right choice for rerunning workflows.
- If committed tracking history is sparse, the hosted app falls back to demo values for the chart and key summary metrics.
