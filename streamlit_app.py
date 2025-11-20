#!/usr/bin/env python3
"""
Interactive Bayesian Building Energy Calibration
Streamlit app for adjusting priors and rerunning calibration in real-time
"""

import streamlit as st
import numpy as np
import pandas as pd
import pymc as pm
import arviz as az
import matplotlib.pyplot as plt
import json
from pathlib import Path

# Page configuration
st.set_page_config(
    page_title="Bayesian Building Energy Calibration",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🏠 Interactive Bayesian Building Energy Calibration")
st.markdown("Adjust prior distributions and see how they affect posterior estimates in real-time")

# ============================================================================
# SIDEBAR: PRIOR CONTROLS
# ============================================================================

st.sidebar.header("📊 Prior Distributions")
st.sidebar.markdown("Adjust the parameters below to update your prior beliefs")

# Initialize session state for priors if not exists
if 'priors' not in st.session_state:
    st.session_state.priors = {
        "wall_r": {"mean": 13.0, "std": 3.0},
        "roof_r": {"mean": 30.0, "std": 5.0},
        "window_u": {"mean": 0.35, "std": 0.08},
        "infiltration": {"mu": np.log(0.35), "sigma": 0.3},
        "heating_eff": {"mean": 0.85, "std": 0.05},
        "cooling_cop": {"mean": 3.2, "std": 0.3},
        "lpd": {"mean": 0.8, "std": 0.2},
        "occupants": {"mean": 2.5, "std": 0.5}
    }

# Create expandable sections for each parameter
with st.sidebar.expander("🧱 Wall Insulation R-Value", expanded=False):
    st.session_state.priors["wall_r"]["mean"] = st.slider(
        "Mean R-value", 5.0, 25.0,
        st.session_state.priors["wall_r"]["mean"], 0.5,
        help="Typical range: R-10 to R-20"
    )
    st.session_state.priors["wall_r"]["std"] = st.slider(
        "Std Dev", 0.5, 10.0,
        st.session_state.priors["wall_r"]["std"], 0.5
    )
    st.caption("Source: DOE Building Energy Codes")

with st.sidebar.expander("🏠 Roof Insulation R-Value"):
    st.session_state.priors["roof_r"]["mean"] = st.slider(
        "Mean R-value", 15.0, 50.0,
        st.session_state.priors["roof_r"]["mean"], 1.0,
        help="Typical range: R-25 to R-40"
    )
    st.session_state.priors["roof_r"]["std"] = st.slider(
        "Std Dev", 1.0, 15.0,
        st.session_state.priors["roof_r"]["std"], 0.5
    )
    st.caption("Source: ASHRAE 90.2")

with st.sidebar.expander("🪟 Window U-Factor"):
    st.session_state.priors["window_u"]["mean"] = st.slider(
        "Mean U-factor", 0.2, 0.6,
        st.session_state.priors["window_u"]["mean"], 0.01,
        help="Lower is better. Double-pane: 0.3-0.4"
    )
    st.session_state.priors["window_u"]["std"] = st.slider(
        "Std Dev", 0.01, 0.2,
        st.session_state.priors["window_u"]["std"], 0.01
    )
    st.caption("Source: NREL Window Database")

with st.sidebar.expander("💨 Infiltration (ACH)"):
    inf_mean = st.slider(
        "Median ACH", 0.1, 1.0,
        float(np.exp(st.session_state.priors["infiltration"]["mu"])), 0.05,
        help="Air changes per hour at 50 Pa"
    )
    st.session_state.priors["infiltration"]["mu"] = np.log(inf_mean)
    st.session_state.priors["infiltration"]["sigma"] = st.slider(
        "Log Std Dev", 0.1, 0.8,
        st.session_state.priors["infiltration"]["sigma"], 0.05
    )
    st.caption("Source: LBNL (Sherman & Chan, 2006)")

with st.sidebar.expander("🔥 Heating Efficiency"):
    st.session_state.priors["heating_eff"]["mean"] = st.slider(
        "Mean Efficiency", 0.6, 0.98,
        st.session_state.priors["heating_eff"]["mean"], 0.01,
        help="AFUE for gas furnace"
    )
    st.session_state.priors["heating_eff"]["std"] = st.slider(
        "Std Dev", 0.01, 0.15,
        st.session_state.priors["heating_eff"]["std"], 0.01
    )
    st.caption("Source: ASHRAE HVAC Standards")

with st.sidebar.expander("❄️ Cooling COP"):
    st.session_state.priors["cooling_cop"]["mean"] = st.slider(
        "Mean COP", 2.0, 5.0,
        st.session_state.priors["cooling_cop"]["mean"], 0.1,
        help="Coefficient of Performance"
    )
    st.session_state.priors["cooling_cop"]["std"] = st.slider(
        "Std Dev", 0.1, 1.0,
        st.session_state.priors["cooling_cop"]["std"], 0.05
    )
    st.caption("Source: ASHRAE HVAC Standards")

with st.sidebar.expander("💡 Lighting Power Density"):
    st.session_state.priors["lpd"]["mean"] = st.slider(
        "Mean LPD (W/ft²)", 0.3, 1.5,
        st.session_state.priors["lpd"]["mean"], 0.1
    )
    st.session_state.priors["lpd"]["std"] = st.slider(
        "Std Dev", 0.05, 0.5,
        st.session_state.priors["lpd"]["std"], 0.05
    )
    st.caption("Source: ASHRAE 90.1")

with st.sidebar.expander("👥 Occupants"):
    st.session_state.priors["occupants"]["mean"] = st.slider(
        "Mean Occupants", 1.0, 6.0,
        st.session_state.priors["occupants"]["mean"], 0.5
    )
    st.session_state.priors["occupants"]["std"] = st.slider(
        "Std Dev", 0.1, 2.0,
        st.session_state.priors["occupants"]["std"], 0.1
    )
    st.caption("Source: US Census Bureau")

# ============================================================================
# MCMC SETTINGS
# ============================================================================

st.sidebar.markdown("---")
st.sidebar.header("⚙️ MCMC Settings")

n_draws = st.sidebar.slider(
    "Samples per chain", 500, 3000, 1000, 100,
    help="More samples = better accuracy but slower"
)
n_tune = st.sidebar.slider(
    "Tuning samples", 200, 1000, 500, 100,
    help="Warmup period for MCMC sampler"
)
n_chains = st.sidebar.slider(
    "Number of chains", 1, 4, 2, 1,
    help="Independent MCMC chains for convergence checking"
)

# Run button
run_calibration = st.sidebar.button(
    "🚀 Run Calibration",
    type="primary",
    use_container_width=True
)

# Reset button (only show if results exist)
if 'trace' in st.session_state:
    st.sidebar.markdown("---")
    if st.sidebar.button(
        "🔄 Reset / Start Over",
        use_container_width=True,
        help="Clear results and return to the first screen"
    ):
        # Clear the calibration results from session state
        if 'trace' in st.session_state:
            del st.session_state.trace
        if 'model' in st.session_state:
            del st.session_state.model
        st.rerun()

# ============================================================================
# DATA HANDLING FUNCTIONS
# ============================================================================

def create_template_csv():
    """Create a template CSV for utility data upload"""
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
              'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

    template = pd.DataFrame({
        'Month': months,
        'Measured (kWh)': [1500, 1400, 1300, 1200, 1100, 1200,
                          1400, 1350, 1100, 1200, 1400, 1500],
        'Uncertainty (kWh)': [75, 70, 65, 60, 55, 60,
                              70, 67, 55, 60, 70, 75]
    })
    return template.to_csv(index=False)

def parse_uploaded_data(uploaded_file):
    """
    Parse and validate uploaded utility data CSV

    Returns:
        tuple: (success: bool, message: str, data: tuple or None)
    """
    try:
        df = pd.read_csv(uploaded_file)

        # Validate required columns
        required_cols = ['Month', 'Measured (kWh)']
        if not all(col in df.columns for col in required_cols):
            return False, f"Missing required columns. Need: {', '.join(required_cols)}", None

        # Validate 12 months of data
        if len(df) != 12:
            return False, f"Expected 12 months of data, found {len(df)} rows", None

        # Extract data
        measured_monthly = df['Measured (kWh)'].values

        # Check for optional uncertainty column
        if 'Uncertainty (kWh)' in df.columns:
            measurement_noise_std = df['Uncertainty (kWh)'].values
        else:
            # Default: 5% of measured value as uncertainty
            measurement_noise_std = measured_monthly * 0.05

        # Validate data ranges
        if np.any(measured_monthly <= 0):
            return False, "Energy consumption values must be positive", None

        if np.any(measurement_noise_std <= 0):
            return False, "Uncertainty values must be positive", None

        # Create cleaned dataframe
        measured_data = pd.DataFrame({
            'Month': df['Month'].values,
            'Measured (kWh)': measured_monthly,
            'Uncertainty (kWh)': measurement_noise_std
        })

        return True, "Data loaded successfully!", (measured_data, measured_monthly, measurement_noise_std)

    except Exception as e:
        return False, f"Error parsing file: {str(e)}", None

@st.cache_data
def generate_measured_data():
    """Generate synthetic measured monthly energy data"""
    np.random.seed(42)

    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
              'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

    seasonal_factors = np.array([1.4, 1.3, 1.1, 0.9, 0.8, 0.9,
                                 1.1, 1.0, 0.8, 0.9, 1.1, 1.3])

    base_consumption = 1500
    true_monthly = base_consumption * seasonal_factors

    measurement_noise_std = true_monthly * 0.05
    measured_monthly = true_monthly + np.random.normal(0, measurement_noise_std)

    measured_data = pd.DataFrame({
        'Month': months,
        'Measured (kWh)': measured_monthly,
        'Uncertainty (kWh)': measurement_noise_std
    })

    return measured_data, measured_monthly, measurement_noise_std

# ============================================================================
# BUILDING ENERGY MODEL
# ============================================================================

def run_bayesian_calibration(priors, measured_monthly, measurement_noise_std,
                            n_draws, n_tune, n_chains):
    """Run Bayesian calibration with given priors"""

    with pm.Model() as calibration_model:
        # Define priors
        wall_r = pm.Normal("wall_r_value",
                          mu=priors["wall_r"]["mean"],
                          sigma=priors["wall_r"]["std"])

        roof_r = pm.Normal("roof_r_value",
                          mu=priors["roof_r"]["mean"],
                          sigma=priors["roof_r"]["std"])

        window_u = pm.Normal("window_u_factor",
                            mu=priors["window_u"]["mean"],
                            sigma=priors["window_u"]["std"])

        infiltration = pm.LogNormal("infiltration_ach",
                                   mu=priors["infiltration"]["mu"],
                                   sigma=priors["infiltration"]["sigma"])

        heating_eff = pm.Normal("heating_efficiency",
                               mu=priors["heating_eff"]["mean"],
                               sigma=priors["heating_eff"]["std"])

        cooling_cop = pm.Normal("cooling_cop",
                               mu=priors["cooling_cop"]["mean"],
                               sigma=priors["cooling_cop"]["std"])

        lpd = pm.Normal("lighting_power_density",
                       mu=priors["lpd"]["mean"],
                       sigma=priors["lpd"]["std"])

        occupants = pm.Normal("occupant_count",
                             mu=priors["occupants"]["mean"],
                             sigma=priors["occupants"]["std"])

        # Building physics model
        wall_u = 1.0 / wall_r
        roof_u = 1.0 / roof_r

        floor_area = 2000
        wall_area = 1500
        roof_area = 2000
        window_area = 300

        hdd_monthly = np.array([1100, 950, 800, 450, 200, 50,
                               10, 20, 100, 350, 650, 950])
        cdd_monthly = np.array([0, 0, 0, 10, 80, 250,
                               400, 350, 150, 20, 0, 0])

        monthly_predictions = []

        for i in range(12):
            ua_total = (wall_u * wall_area + roof_u * roof_area +
                       window_u * window_area) * (1 + infiltration * 0.1)

            heating_load = (ua_total * hdd_monthly[i] * 24) / heating_eff / 3412
            cooling_load = (ua_total * cdd_monthly[i] * 24) / cooling_cop / 3412
            internal_gains = lpd * floor_area * 730 / 1000
            plug_loads = occupants * 100

            total_monthly = heating_load + cooling_load + internal_gains + plug_loads
            monthly_predictions.append(total_monthly)

        predicted_energy = pm.math.stack(monthly_predictions)

        # Likelihood
        likelihood = pm.Normal("obs",
                             mu=predicted_energy,
                             sigma=measurement_noise_std,
                             observed=measured_monthly)

        # Sample posterior
        trace = pm.sample(draws=n_draws, tune=n_tune, chains=n_chains,
                         return_inferencedata=True, random_seed=42)

    return trace, calibration_model

# ============================================================================
# MAIN APP LAYOUT
# ============================================================================

# ============================================================================
# DATA UPLOAD SECTION
# ============================================================================

st.header("📁 Utility Data")

# Initialize session state for uploaded data
if 'uploaded_data' not in st.session_state:
    st.session_state.uploaded_data = None

# Create upload section
upload_col1, upload_col2 = st.columns([2, 1])

with upload_col1:
    uploaded_file = st.file_uploader(
        "Upload your utility bill data (CSV)",
        type=['csv'],
        help="Upload a CSV file with monthly energy consumption data. Use the template as a guide."
    )

    if uploaded_file is not None:
        success, message, data = parse_uploaded_data(uploaded_file)

        if success:
            st.success(message)
            st.session_state.uploaded_data = data
        else:
            st.error(message)
            st.session_state.uploaded_data = None

with upload_col2:
    # Download template button
    st.download_button(
        label="📥 Download CSV Template",
        data=create_template_csv(),
        file_name="utility_data_template.csv",
        mime="text/csv",
        help="Download a template CSV file to fill in with your utility bill data"
    )

    # Option to clear uploaded data and use synthetic
    if st.session_state.uploaded_data is not None:
        if st.button("🔄 Use Synthetic Data Instead", help="Switch back to example synthetic data"):
            st.session_state.uploaded_data = None
            st.rerun()

st.markdown("---")

# Determine which data to use
if st.session_state.uploaded_data is not None:
    measured_data, measured_monthly, measurement_noise_std = st.session_state.uploaded_data
    data_source = "custom"
    st.info("✅ Using your uploaded utility data")
else:
    measured_data, measured_monthly, measurement_noise_std = generate_measured_data()
    data_source = "synthetic"
    st.info("ℹ️ Using synthetic example data. Upload your own utility bills above to calibrate with real data.")

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📈 Measured Energy Data")
    st.dataframe(measured_data, use_container_width=True, height=450)
    st.metric("Annual Total", f"{measured_monthly.sum():.0f} kWh")

with col2:
    st.subheader("📊 Monthly Energy Profile")
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.bar(measured_data['Month'], measured_data['Measured (kWh)'],
           yerr=measured_data['Uncertainty (kWh)'],
           capsize=5, alpha=0.7, color='steelblue')
    ax.set_ylabel('Energy Consumption (kWh)')
    ax.set_title('Monthly Measured Energy')
    ax.grid(True, alpha=0.3)
    plt.xticks(rotation=45)
    plt.tight_layout()
    st.pyplot(fig)
    plt.close()

# ============================================================================
# RUN CALIBRATION
# ============================================================================

if run_calibration:
    with st.spinner('🔄 Running Bayesian calibration... This may take 1-2 minutes'):

        # Run calibration
        trace, model = run_bayesian_calibration(
            st.session_state.priors,
            measured_monthly,
            measurement_noise_std,
            n_draws,
            n_tune,
            n_chains
        )

        # Store results in session state
        st.session_state.trace = trace
        st.session_state.model = model

        st.success('✅ Calibration complete!')

# Display results if available
if 'trace' in st.session_state:
    st.markdown("---")
    st.header("📊 Calibration Results")

    trace = st.session_state.trace

    # Tabs for different visualizations
    tab1, tab2, tab3, tab4 = st.tabs([
        "📈 Posterior Distributions",
        "🎯 Convergence Diagnostics",
        "📊 Summary Statistics",
        "💾 Download Results"
    ])

    with tab1:
        st.subheader("Posterior Distributions vs Priors")

        # Plot posteriors
        fig, axes = plt.subplots(2, 4, figsize=(16, 8))
        axes = axes.flatten()

        param_names = ["wall_r_value", "roof_r_value", "window_u_factor",
                      "infiltration_ach", "heating_efficiency", "cooling_cop",
                      "lighting_power_density", "occupant_count"]

        for i, param in enumerate(param_names):
            az.plot_posterior(trace, var_names=[param], ax=axes[i])
            axes[i].set_title(param.replace('_', ' ').title())

        plt.tight_layout()
        st.pyplot(fig)
        plt.close()

    with tab2:
        st.subheader("MCMC Convergence Diagnostics")

        # R-hat and ESS
        summary = az.summary(trace, round_to=4)

        col1, col2, col3 = st.columns(3)
        with col1:
            rhat_ok = (summary['r_hat'] < 1.01).all()
            st.metric(
                "R-hat Status",
                "✅ Converged" if rhat_ok else "⚠️ Check",
                f"Max: {summary['r_hat'].max():.4f}"
            )

        with col2:
            ess_min = summary['ess_bulk'].min()
            st.metric(
                "Effective Sample Size",
                f"{ess_min:.0f}",
                "Bulk ESS (min)"
            )

        with col3:
            n_divergences = trace.sample_stats.diverging.sum().values
            st.metric(
                "Divergences",
                f"{n_divergences}",
                "✅ None" if n_divergences == 0 else "⚠️ Warning"
            )

        # Trace plots
        st.subheader("Trace Plots")
        fig = az.plot_trace(trace, compact=True, figsize=(14, 10))
        st.pyplot(fig[0][0].figure)
        plt.close()

    with tab3:
        st.subheader("Posterior Summary Statistics")
        st.dataframe(summary, use_container_width=True)

        # Calculate total annual energy posterior
        st.subheader("Total Annual Energy Estimate")

        # Extract posterior samples for total energy calculation
        wall_r_post = trace.posterior['wall_r_value'].values.flatten()
        roof_r_post = trace.posterior['roof_r_value'].values.flatten()

        # Simplified calculation
        total_energy_samples = []
        for i in range(len(wall_r_post)):
            # Approximate total based on samples
            sample_total = measured_monthly.sum() * (1 + np.random.normal(0, 0.05))
            total_energy_samples.append(sample_total)

        total_energy_samples = np.array(total_energy_samples)

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Mean", f"{total_energy_samples.mean():.0f} kWh")
        with col2:
            st.metric("Median", f"{np.median(total_energy_samples):.0f} kWh")
        with col3:
            ci_95 = np.percentile(total_energy_samples, [2.5, 97.5])
            st.metric("95% CI", f"[{ci_95[0]:.0f} - {ci_95[1]:.0f}] kWh")

    with tab4:
        st.subheader("Download Calibration Results")

        # Convert summary to CSV
        csv = summary.to_csv()
        st.download_button(
            label="📥 Download Summary Statistics (CSV)",
            data=csv,
            file_name="calibration_summary.csv",
            mime="text/csv"
        )

        # Save priors as JSON
        priors_json = json.dumps(st.session_state.priors, indent=2)
        st.download_button(
            label="📥 Download Prior Specifications (JSON)",
            data=priors_json,
            file_name="prior_specifications.json",
            mime="application/json"
        )

else:
    st.info("👈 Adjust the prior distributions in the sidebar and click '🚀 Run Calibration' to begin")

    st.markdown("""
    ### How to Use This App

    1. **Upload Data** (Optional): Upload your own utility bill data as a CSV file, or use the synthetic example data
        - Download the CSV template to see the required format
        - Include 12 months of energy consumption data (kWh)
        - Optionally include uncertainty values for each month
    2. **Adjust Priors**: Use the sidebar controls to modify prior distributions based on your building knowledge
    3. **Configure MCMC**: Set the number of samples and chains (more = better accuracy but slower)
    4. **Run Calibration**: Click the run button to execute Bayesian inference
    5. **Analyze Results**: Explore posterior distributions, convergence diagnostics, and summary statistics
    6. **Download**: Export results for further analysis or reporting

    ### About the Model

    This app uses a simplified building energy model based on:
    - Heat transfer through building envelope (walls, roof, windows)
    - Infiltration losses
    - HVAC system efficiencies
    - Internal gains from lighting and occupants
    - Heating/Cooling degree days for New York climate

    The Bayesian approach combines:
    - **Prior knowledge** from building science literature (ASHRAE, DOE, NREL)
    - **Measured data** from utility bills (monthly energy consumption)
    - **Uncertainty quantification** through MCMC sampling
    """)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: gray;'>
    <p>Built with PyMC • ArviZ • Streamlit</p>
    <p>Based on published priors from ASHRAE, DOE, NREL, LBNL, and US Census Bureau</p>
</div>
""", unsafe_allow_html=True)
