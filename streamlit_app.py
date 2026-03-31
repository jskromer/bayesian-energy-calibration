#!/usr/bin/env python3
"""
Streamlit Community Cloud demo app.

This app is intentionally lightweight: it reads committed project artifacts and
shows a hosted demo dashboard without Docker, EnergyPlus, or PyMC runtime
requirements.
"""

from __future__ import annotations

import json
from pathlib import Path

import altair as alt
import pandas as pd
import streamlit as st


REPO_ROOT = Path(__file__).resolve().parent
RESULTS_ROOT = REPO_ROOT / "energyplus-mcp-server" / "bayesian_calibration_results"
FIGURES_ROOT = RESULTS_ROOT / "figures"
CALIBRATION_ROOT = REPO_ROOT / "energyplus-mcp-server" / "calibration_workflow"
DIGITAL_TWIN_ROOT = REPO_ROOT / "energyplus-mcp-server" / "digital_twin"


st.set_page_config(
    page_title="DTABM Demo",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded",
)


@st.cache_data
def load_json(path_str: str):
    path = Path(path_str)
    if not path.exists():
        return None
    with path.open() as f:
        return json.load(f)


@st.cache_data
def load_csv(path_str: str):
    path = Path(path_str)
    if not path.exists():
        return None
    return pd.read_csv(path)


def artifact_table(directory: Path, pattern: str) -> pd.DataFrame:
    files = sorted(directory.glob(pattern))
    if not files:
        return pd.DataFrame(columns=["file", "size_kb", "modified"])
    return pd.DataFrame(
        {
            "file": [f.name for f in files],
            "size_kb": [round(f.stat().st_size / 1024, 1) for f in files],
            "modified": [pd.to_datetime(f.stat().st_mtime, unit="s") for f in files],
        }
    )


def registry_table(registry: dict | None) -> pd.DataFrame:
    if not registry:
        return pd.DataFrame(columns=["model", "status", "version", "updated", "idf_file"])

    rows = []
    for model_name, details in registry.items():
        rows.append(
            {
                "model": model_name,
                "status": str(details.get("status", "unknown")).replace("_", " ").title(),
                "version": details.get("version"),
                "updated": details.get("last_update") or details.get("created"),
                "idf_file": details.get("idf_file"),
            }
        )
    return pd.DataFrame(rows)


def fallback_mv_report() -> dict:
    return {
        "savings_kwh": 61789.0,
        "savings_pct": 13.7,
        "cost_savings_usd": 7414.68,
        "baseline_kwh": 449389,
        "actual_kwh": 380000,
        "actual_normalized_kwh": 387600.0,
    }


def fallback_energy_summary() -> dict:
    return {
        "mean_kwh": 19490.35,
        "measured_kwh": 19178.0,
        "ci_95_lower_kwh": 17758.35,
        "ci_95_upper_kwh": 21332.0,
        "measured_percentile": 36.6,
    }


def fallback_tracking_history() -> pd.DataFrame:
    dates = pd.date_range("2025-04-01", periods=12, freq="MS")
    predicted = [35200, 36150, 37400, 38900, 40100, 41350, 42100, 41800, 39600, 38100, 36600, 35800]
    actual = [34700, 36900, 38050, 40200, 43900, 42100, 40500, 38950, 37700, 37250, 35900, 35150]
    df = pd.DataFrame({"date": dates, "predicted_kwh": predicted, "actual_kwh": actual})
    df["error_pct"] = (df["actual_kwh"] - df["predicted_kwh"]) / df["predicted_kwh"] * 100
    df["model_version"] = "demo"
    return df


mv_report = load_json(str(DIGITAL_TWIN_ROOT / "mv_report.json")) or fallback_mv_report()
registry = load_json(str(DIGITAL_TWIN_ROOT / "dtabm_registry.json"))
tracking_df = load_csv(str(DIGITAL_TWIN_ROOT / "dtabm_tracking.csv"))
energy_summary = load_json(str(RESULTS_ROOT / "total_energy_summary.json")) or fallback_energy_summary()
posterior_summary_df = load_csv(str(RESULTS_ROOT / "posterior_summary.csv"))
comparison_df = load_csv(str(RESULTS_ROOT / "calibration_comparison.csv"))

if tracking_df is None or tracking_df.empty:
    tracking_df = fallback_tracking_history()
else:
    tracking_df["date"] = pd.to_datetime(tracking_df["date"])


st.title("DTABM Demo Dashboard")
st.caption("Hosted demo of the Bayesian calibration and digital twin outputs committed in this repository.")

with st.sidebar:
    st.header("Demo Controls")
    selected_model = st.selectbox(
        "Focus Model",
        ["All", "DTABM_Baseline", "DTABM_Operational", "DTActual"],
    )
    tracking_window = st.selectbox(
        "Tracking Window",
        ["All", "Last 3", "Last 6", "Last 12"],
        index=2,
    )
    figure_paths = sorted(FIGURES_ROOT.glob("*.png"))
    selected_figure = None
    if figure_paths:
        selected_figure = st.selectbox(
            "Figure",
            figure_paths,
            format_func=lambda path: path.stem.replace("_", " ").title(),
        )

    st.markdown("**Run Locally**")
    st.code("docker compose up -d\n./run_streamlit.sh", language="bash")


metric_cols = st.columns(5)
metric_cols[0].metric("Annual Savings", f"{mv_report['savings_kwh']:,.0f} kWh")
metric_cols[1].metric("Savings Rate", f"{mv_report['savings_pct']:.1f}%")
metric_cols[2].metric("Cost Savings", f"${mv_report['cost_savings_usd']:,.0f}")
metric_cols[3].metric("Posterior Mean", f"{energy_summary['mean_kwh']:,.0f} kWh")
metric_cols[4].metric("Measured Annual", f"{energy_summary['measured_kwh']:,.0f} kWh")


if selected_figure:
    st.markdown("---")
    st.subheader(selected_figure.stem.replace("_", " ").title())
    st.caption(selected_figure.name)
    st.image(str(selected_figure))


tab_overview, tab_twin, tab_calibration, tab_files = st.tabs(
    ["Overview", "Digital Twin", "Calibration", "Files"]
)


with tab_overview:
    left, right = st.columns([1.1, 1])

    with left:
        st.subheader("M&V Summary")
        mv_cols = st.columns(3)
        mv_cols[0].metric("Baseline", f"{mv_report['baseline_kwh']:,.0f} kWh")
        mv_cols[1].metric("Actual", f"{mv_report['actual_kwh']:,.0f} kWh")
        mv_cols[2].metric("Normalized", f"{mv_report['actual_normalized_kwh']:,.0f} kWh")
        st.json(mv_report, expanded=False)

    with right:
        st.subheader("Posterior Energy Summary")
        ci_cols = st.columns(2)
        ci_cols[0].metric("95% CI Lower", f"{energy_summary['ci_95_lower_kwh']:,.0f} kWh")
        ci_cols[1].metric("95% CI Upper", f"{energy_summary['ci_95_upper_kwh']:,.0f} kWh")
        st.metric("Measured Percentile", f"{energy_summary['measured_percentile']:.1f}%")

    st.subheader("Operational Tracking")
    chart_df = tracking_df.copy()
    if tracking_window != "All":
        n_rows = int(tracking_window.split()[-1])
        chart_df = chart_df.tail(n_rows)
    plot_df = chart_df.groupby("date", as_index=False)[["predicted_kwh", "actual_kwh"]].mean().sort_values("date")
    plot_long = plot_df.melt("date", var_name="series", value_name="kwh")
    chart = (
        alt.Chart(plot_long)
        .mark_line(point=alt.OverlayMarkDef(size=90, filled=True))
        .encode(
            x=alt.X("date:T", title="Date"),
            y=alt.Y("kwh:Q", title="Energy (kWh)"),
            color=alt.Color(
                "series:N",
                title="Series",
                scale=alt.Scale(domain=["predicted_kwh", "actual_kwh"], range=["#1f77b4", "#d62728"]),
            ),
            tooltip=[
                alt.Tooltip("date:T", title="Date"),
                alt.Tooltip("series:N", title="Series"),
                alt.Tooltip("kwh:Q", title="Energy (kWh)", format=",.0f"),
            ],
        )
        .properties(height=320)
    )
    st.altair_chart(chart, use_container_width=True)
    st.dataframe(chart_df, use_container_width=True, height=220)


with tab_twin:
    st.subheader("Digital Twin Registry")
    reg_df = registry_table(registry)
    if selected_model != "All" and not reg_df.empty:
        reg_df = reg_df[reg_df["model"] == selected_model]
    st.dataframe(reg_df, use_container_width=True)

    st.subheader("Digital Twin Files")
    twin_files = artifact_table(DIGITAL_TWIN_ROOT, "*.idf")
    st.dataframe(twin_files, use_container_width=True)


with tab_calibration:
    left, right = st.columns([1, 1])
    with left:
        st.subheader("Posterior Summary")
        if posterior_summary_df is not None:
            st.dataframe(posterior_summary_df, use_container_width=True, height=320)
        else:
            st.info("Posterior summary not found in committed artifacts.")

        st.subheader("Calibration Comparison")
        if comparison_df is not None:
            st.dataframe(comparison_df, use_container_width=True)
        else:
            st.info("Calibration comparison file not found.")

    with right:
        st.subheader("Calibration Files")
        st.dataframe(artifact_table(CALIBRATION_ROOT, "*.idf"), use_container_width=True, height=320)
        calibration_plot = CALIBRATION_ROOT / "calibration_results.png"
        if calibration_plot.exists():
            st.image(str(calibration_plot))


with tab_files:
    col1, col2, col3 = st.columns(3)
    with col1:
        st.subheader("Digital Twin")
        st.dataframe(artifact_table(DIGITAL_TWIN_ROOT, "*"), use_container_width=True, height=280)
    with col2:
        st.subheader("Calibration")
        st.dataframe(artifact_table(CALIBRATION_ROOT, "*"), use_container_width=True, height=280)
    with col3:
        st.subheader("Results")
        st.dataframe(artifact_table(RESULTS_ROOT, "*"), use_container_width=True, height=280)


st.markdown("---")
st.caption("Community Cloud version: lightweight, artifact-driven, and independent of Docker.")
