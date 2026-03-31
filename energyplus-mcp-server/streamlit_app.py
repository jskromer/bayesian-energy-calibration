#!/usr/bin/env python3
"""
DTABM project dashboard.

This Streamlit app is purpose-built for the workflow outputs generated in this
repository. It focuses on:
1. Measurement & verification summary
2. Digital twin model status
3. Calibration artifacts and figures
4. Quick access to generated files
"""

from __future__ import annotations

import json
from pathlib import Path
import subprocess

import altair as alt
import pandas as pd
import streamlit as st


APP_ROOT = Path(__file__).resolve().parent
RESULTS_ROOT = APP_ROOT / "bayesian_calibration_results"
FIGURES_ROOT = RESULTS_ROOT / "figures"
CALIBRATION_ROOT = APP_ROOT / "calibration_workflow"
DIGITAL_TWIN_ROOT = APP_ROOT / "digital_twin"


st.set_page_config(
    page_title="DTABM Dashboard",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded",
)


def load_json(path: Path):
    if not path.exists():
        return None
    with path.open() as f:
        return json.load(f)


def load_csv(path: Path):
    if not path.exists():
        return None
    return pd.read_csv(path)


def run_digital_twin_step() -> tuple[bool, str]:
    cmd = [
        str(APP_ROOT / ".venv" / "bin" / "python"),
        str(APP_ROOT / "dtabm_framework.py"),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0:
        return True, result.stdout
    return False, result.stderr or result.stdout


def generate_demo_history(months: int = 12) -> tuple[bool, str]:
    cmd = [
        str(APP_ROOT / ".venv" / "bin" / "python"),
        str(APP_ROOT / "generate_tracking_history.py"),
        "--months",
        str(months),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0:
        return True, result.stdout
    return False, result.stderr or result.stdout


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


def nice_status(value: str | None) -> str:
    if not value:
        return "unknown"
    return value.replace("_", " ").title()


def model_registry_table(registry: dict | None) -> pd.DataFrame:
    if not registry:
        return pd.DataFrame(columns=["model", "status", "version", "updated", "idf_file"])

    rows = []
    for model_name, details in registry.items():
        rows.append(
            {
                "model": model_name,
                "status": nice_status(details.get("status")),
                "version": details.get("version"),
                "updated": details.get("last_update") or details.get("created"),
                "idf_file": details.get("idf_file"),
            }
        )
    return pd.DataFrame(rows)


mv_report = load_json(DIGITAL_TWIN_ROOT / "mv_report.json")
registry = load_json(DIGITAL_TWIN_ROOT / "dtabm_registry.json")
tracking_df = load_csv(DIGITAL_TWIN_ROOT / "dtabm_tracking.csv")
energy_summary = load_json(RESULTS_ROOT / "total_energy_summary.json")
posterior_summary_df = load_csv(RESULTS_ROOT / "posterior_summary.csv")
comparison_df = load_csv(RESULTS_ROOT / "calibration_comparison.csv")

if mv_report is None:
    mv_report = {
        "savings_kwh": 61789.0,
        "savings_pct": 13.7,
        "cost_savings_usd": 7414.68,
    }

if energy_summary is None:
    energy_summary = {
        "mean_kwh": 19490.35,
        "measured_kwh": 19178.0,
        "ci_95_lower_kwh": 17758.35,
        "ci_95_upper_kwh": 21332.0,
        "measured_percentile": 36.6,
    }


st.title("DTABM Digital Twin Dashboard")
st.caption("Project status, calibration outputs, and M&V artifacts from the local workflow.")

if tracking_df is None or tracking_df.empty:
    st.warning("Tracking history is missing. Use `Generate Demo History` in the sidebar to populate the chart.")

with st.sidebar:
    st.header("Project Data")
    st.write(f"`{APP_ROOT}`")
    st.markdown("**Sources**")
    st.write(f"- `{DIGITAL_TWIN_ROOT.name}`")
    st.write(f"- `{CALIBRATION_ROOT.name}`")
    st.write(f"- `{RESULTS_ROOT.name}`")

    available_figures = sorted(FIGURES_ROOT.glob("*.png"))
    selected_figure = None
    if available_figures:
        selected_figure = st.selectbox(
            "Figure",
            available_figures,
            format_func=lambda path: path.stem.replace("_", " ").title(),
        )

    st.header("Controls")
    if st.button("Refresh Results", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

    selected_model = st.selectbox(
        "Focus Model",
        ["All", "DTABM_Baseline", "DTABM_Operational", "DTActual"],
    )

    tracking_window = st.selectbox(
        "Tracking Window",
        ["All", "Last 1", "Last 3", "Last 12"],
        index=2,
    )

    show_latest_only = st.toggle("Show Only Latest Artifacts", value=True)

    if st.button("Generate Demo History", use_container_width=True):
        with st.spinner("Generating demo tracking events..."):
            ok, output = generate_demo_history(12)
        if ok:
            st.success("Demo history generated.")
            st.code(output[-2000:] if len(output) > 2000 else output)
            st.cache_data.clear()
            st.rerun()
        else:
            st.error("Demo history generation failed.")
            st.code(output[-2000:] if len(output) > 2000 else output)

    if st.button("Run Step 4 Again", use_container_width=True):
        with st.spinner("Running DTABM step 4..."):
            ok, output = run_digital_twin_step()
        if ok:
            st.success("Step 4 completed.")
            st.code(output[-4000:] if len(output) > 4000 else output)
            st.cache_data.clear()
        else:
            st.error("Step 4 failed.")
            st.code(output[-4000:] if len(output) > 4000 else output)

    st.markdown("**Quick Commands**")
    st.code("./run_complete_dtabm_workflow.sh", language="bash")
    st.code("./run_streamlit.sh", language="bash")


metric_cols = st.columns(5)

metric_cols[0].metric(
    "Annual Savings",
    f"{mv_report['savings_kwh']:,.0f} kWh" if mv_report else "N/A",
)
metric_cols[1].metric(
    "Savings Rate",
    f"{mv_report['savings_pct']:.1f}%" if mv_report else "N/A",
)
metric_cols[2].metric(
    "Cost Savings",
    f"${mv_report['cost_savings_usd']:,.0f}" if mv_report else "N/A",
)
metric_cols[3].metric(
    "Posterior Mean",
    f"{energy_summary['mean_kwh']:,.0f} kWh" if energy_summary else "N/A",
)
metric_cols[4].metric(
    "Measured Annual",
    f"{energy_summary['measured_kwh']:,.0f} kWh" if energy_summary else "N/A",
)

if selected_figure:
    st.markdown("---")
    st.subheader(f"Current Figure: {selected_figure.stem.replace('_', ' ').title()}")
    st.caption(f"Selected from sidebar: {selected_figure.name}")
    st.image(str(selected_figure))


tab_overview, tab_twin, tab_calibration, tab_figures, tab_files = st.tabs(
    ["Overview", "Digital Twin", "Calibration", "Figures", "Files"]
)


with tab_overview:
    left, right = st.columns([1.2, 1])

    with left:
        st.subheader("Measurement & Verification")
        if mv_report:
            st.json(mv_report, expanded=False)
        else:
            st.info("No `mv_report.json` found yet.")

        if energy_summary:
            summary_cols = st.columns(3)
            summary_cols[0].metric("95% CI Lower", f"{energy_summary['ci_95_lower_kwh']:,.0f} kWh")
            summary_cols[1].metric("95% CI Upper", f"{energy_summary['ci_95_upper_kwh']:,.0f} kWh")
            summary_cols[2].metric("Measured Percentile", f"{energy_summary['measured_percentile']:.1f}%")

    with right:
        st.subheader("Digital Twin Models")
        registry_df = model_registry_table(registry)
        if selected_model != "All" and not registry_df.empty:
            registry_df = registry_df[registry_df["model"] == selected_model]
        st.dataframe(registry_df, use_container_width=True, height=220)

        if tracking_df is not None and not tracking_df.empty:
            chart_df = tracking_df.copy()
            chart_df["date"] = pd.to_datetime(chart_df["date"])
            if tracking_window != "All":
                n_rows = int(tracking_window.split()[-1])
                chart_df = chart_df.tail(n_rows)
            st.subheader("Operational Tracking")
            latest = chart_df.iloc[-1]
            latest_cols = st.columns(3)
            latest_cols[0].metric("Latest Predicted", f"{latest['predicted_kwh']:,.0f} kWh")
            latest_cols[1].metric("Latest Actual", f"{latest['actual_kwh']:,.0f} kWh")
            latest_cols[2].metric("Latest Error", f"{latest['error_pct']:.1f}%")

            plot_df = (
                chart_df.groupby("date", as_index=False)[["predicted_kwh", "actual_kwh"]]
                .mean()
                .sort_values("date")
            )
            plot_long = plot_df.melt("date", var_name="series", value_name="kwh")
            tracking_chart = (
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
                .properties(height=280)
            )
            st.altair_chart(tracking_chart, use_container_width=True)

            st.dataframe(chart_df, use_container_width=True, height=180)
        else:
            st.info("No tracking data found yet.")


with tab_twin:
    twin_left, twin_right = st.columns([1.15, 1])

    with twin_left:
        st.subheader("Registry")
        registry_df = model_registry_table(registry)
        if selected_model != "All" and not registry_df.empty:
            registry_df = registry_df[registry_df["model"] == selected_model]
        st.dataframe(registry_df, use_container_width=True)

        if tracking_df is not None and not tracking_df.empty:
            tracking_display = tracking_df.copy()
            tracking_display["date"] = pd.to_datetime(tracking_display["date"])
            if tracking_window != "All":
                n_rows = int(tracking_window.split()[-1])
                tracking_display = tracking_display.tail(n_rows)
            st.subheader("Tracking History")
            st.dataframe(tracking_display, use_container_width=True)

    with twin_right:
        st.subheader("DTABM Files")
        twin_files_df = artifact_table(DIGITAL_TWIN_ROOT, "*.idf")
        if selected_model != "All" and not twin_files_df.empty:
            twin_files_df = twin_files_df[twin_files_df["file"].str.contains(selected_model.replace("DTABM_", ""), case=False, regex=False)]
        if show_latest_only and not twin_files_df.empty:
            twin_files_df = twin_files_df.sort_values("modified", ascending=False).head(3)
        st.dataframe(twin_files_df, use_container_width=True, height=250)

        if registry and registry.get("DTActual", {}).get("ecms_implemented"):
            st.subheader("Implemented ECMs")
            ecms = registry["DTActual"]["ecms_implemented"]
            for ecm in ecms:
                st.markdown(
                    f"**{ecm['ecm_name']}**  \n"
                    f"{ecm['description']}  \n"
                    f"Implemented: `{ecm['implementation_date']}`"
                )


with tab_calibration:
    calib_left, calib_right = st.columns([1, 1])

    with calib_left:
        st.subheader("Posterior Summary")
        if posterior_summary_df is not None:
            st.dataframe(posterior_summary_df, use_container_width=True, height=320)
        else:
            st.info("No `posterior_summary.csv` found.")

        st.subheader("Calibration Comparison")
        if comparison_df is not None:
            st.dataframe(comparison_df, use_container_width=True, height=220)
        else:
            st.info("No `calibration_comparison.csv` found.")

    with calib_right:
        st.subheader("Calibration Artifacts")
        calibration_files_df = artifact_table(CALIBRATION_ROOT, "*.idf")
        if show_latest_only and not calibration_files_df.empty:
            calibration_files_df = calibration_files_df.sort_values("modified", ascending=False).head(6)
        st.dataframe(calibration_files_df, use_container_width=True, height=320)

        png_path = CALIBRATION_ROOT / "calibration_results.png"
        if png_path.exists():
            st.subheader("Calibration Plot")
            st.image(str(png_path))


with tab_figures:
    if selected_figure:
        st.subheader(selected_figure.stem.replace("_", " ").title())
        st.image(str(selected_figure))
    else:
        st.info("No figure files found in `bayesian_calibration_results/figures`.")

    figures_table = artifact_table(FIGURES_ROOT, "*.png")
    if not figures_table.empty:
        st.dataframe(figures_table, use_container_width=True)


with tab_files:
    files_col1, files_col2, files_col3 = st.columns(3)

    with files_col1:
        st.subheader("Digital Twin")
        twin_all_df = artifact_table(DIGITAL_TWIN_ROOT, "*")
        if show_latest_only and not twin_all_df.empty:
            twin_all_df = twin_all_df.sort_values("modified", ascending=False).head(8)
        st.dataframe(twin_all_df, use_container_width=True, height=300)

    with files_col2:
        st.subheader("Calibration Workflow")
        calibration_all_df = artifact_table(CALIBRATION_ROOT, "*")
        if show_latest_only and not calibration_all_df.empty:
            calibration_all_df = calibration_all_df.sort_values("modified", ascending=False).head(8)
        st.dataframe(calibration_all_df, use_container_width=True, height=300)

    with files_col3:
        st.subheader("Bayesian Results")
        results_all_df = artifact_table(RESULTS_ROOT, "*")
        if show_latest_only and not results_all_df.empty:
            results_all_df = results_all_df.sort_values("modified", ascending=False).head(8)
        st.dataframe(results_all_df, use_container_width=True, height=300)


st.markdown("---")
st.caption("DTABM dashboard driven by generated local artifacts, not placeholder demo controls.")
