#!/usr/bin/env python3
"""
Visualize Bayesian calibration results
"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import arviz as az
from pathlib import Path

output_dir = Path("/workspace/energyplus-mcp-server/bayesian_calibration_results")
trace_file = output_dir / "posterior_trace.nc"

# Load the trace
print("Loading posterior trace...")
trace = az.from_netcdf(trace_file)

# Create visualizations
fig_dir = output_dir / "figures"
fig_dir.mkdir(exist_ok=True)

print("\nCreating visualizations...")

# 1. Posterior distributions
print("  - Posterior distributions plot")
fig, axes = plt.subplots(3, 3, figsize=(15, 12))
axes = axes.flatten()

params = [
    ("wall_r_value", "Wall R-value (h·ft²·°F/Btu)", 13.0, 15.0),
    ("roof_r_value", "Roof R-value (h·ft²·°F/Btu)", 30.0, 28.0),
    ("window_u_factor", "Window U-factor (Btu/h·ft²·°F)", 0.35, 0.32),
    ("infiltration_ach", "Infiltration (ACH)", 0.35, 0.40),
    ("heating_efficiency", "Heating Efficiency", 0.85, 0.88),
    ("cooling_cop", "Cooling COP", 3.2, 3.4),
    ("lighting_power_density", "Lighting Power Density (W/ft²)", 0.8, 0.75),
    ("occupant_count", "Occupant Count", 2.5, 3.0),
]

for idx, (param_name, param_label, prior_mean, true_val) in enumerate(params):
    ax = axes[idx]

    # Get posterior samples
    posterior_samples = trace.posterior[param_name].values.flatten()

    # Plot posterior distribution
    ax.hist(posterior_samples, bins=30, alpha=0.6, color='steelblue',
            density=True, label='Posterior')

    # Add vertical lines for prior mean and true value
    ax.axvline(prior_mean, color='orange', linestyle='--', linewidth=2,
               label=f'Prior mean: {prior_mean:.2f}')
    ax.axvline(true_val, color='red', linestyle='-', linewidth=2,
               label=f'True value: {true_val:.2f}')
    ax.axvline(posterior_samples.mean(), color='blue', linestyle='-.', linewidth=2,
               label=f'Posterior mean: {posterior_samples.mean():.2f}')

    ax.set_xlabel(param_label)
    ax.set_ylabel('Density')
    ax.legend(fontsize=8)
    ax.grid(alpha=0.3)

# Remove extra subplot
axes[-1].remove()

plt.tight_layout()
plt.savefig(fig_dir / "posterior_distributions.png", dpi=150, bbox_inches='tight')
print(f"    Saved to: {fig_dir / 'posterior_distributions.png'}")
plt.close()

# 2. Trace plots
print("  - Trace plots")
az.plot_trace(trace, var_names=[
    "wall_r_value", "roof_r_value", "window_u_factor",
    "heating_efficiency", "cooling_cop"
], compact=True)
plt.tight_layout()
plt.savefig(fig_dir / "trace_plots.png", dpi=150, bbox_inches='tight')
print(f"    Saved to: {fig_dir / 'trace_plots.png'}")
plt.close()

# 3. Posterior predictive check
print("  - Forest plot (parameter comparison)")
az.plot_forest(trace, var_names=[
    "wall_r_value", "roof_r_value", "window_u_factor",
    "infiltration_ach", "heating_efficiency", "cooling_cop",
    "lighting_power_density", "occupant_count"
], combined=True, figsize=(10, 8))
plt.tight_layout()
plt.savefig(fig_dir / "forest_plot.png", dpi=150, bbox_inches='tight')
print(f"    Saved to: {fig_dir / 'forest_plot.png'}")
plt.close()

# 4. Comparison bar chart
print("  - Parameter comparison bar chart")
comparison_df = pd.read_csv(output_dir / "calibration_comparison.csv")

fig, ax = plt.subplots(figsize=(12, 8))

x = np.arange(len(comparison_df))
width = 0.25

bars1 = ax.bar(x - width, comparison_df['prior_mean'], width,
               label='Prior Mean', alpha=0.8, color='orange')
bars2 = ax.bar(x, comparison_df['posterior_mean'], width,
               label='Posterior Mean', alpha=0.8, color='steelblue')
bars3 = ax.bar(x + width, comparison_df['true_value'], width,
               label='True Value', alpha=0.8, color='red')

ax.set_xlabel('Parameter', fontsize=12)
ax.set_ylabel('Value', fontsize=12)
ax.set_title('Bayesian Calibration: Prior vs Posterior vs True Values', fontsize=14)
ax.set_xticks(x)
ax.set_xticklabels(comparison_df['parameter'], rotation=45, ha='right')
ax.legend()
ax.grid(alpha=0.3, axis='y')

plt.tight_layout()
plt.savefig(fig_dir / "parameter_comparison.png", dpi=150, bbox_inches='tight')
print(f"    Saved to: {fig_dir / 'parameter_comparison.png'}")
plt.close()

# 5. Error analysis
print("  - Error analysis plot")
fig, ax = plt.subplots(figsize=(10, 6))

bars = ax.bar(comparison_df['parameter'], comparison_df['error_percent'],
              color='steelblue', alpha=0.7)

# Color bars based on error magnitude
colors = ['green' if err < 15 else 'orange' if err < 30 else 'red'
          for err in comparison_df['error_percent']]
for bar, color in zip(bars, colors):
    bar.set_color(color)

ax.axhline(y=10, color='green', linestyle='--', alpha=0.5, label='Good (<10%)')
ax.axhline(y=25, color='orange', linestyle='--', alpha=0.5, label='Fair (<25%)')

ax.set_xlabel('Parameter', fontsize=12)
ax.set_ylabel('Error (%)', fontsize=12)
ax.set_title('Posterior Estimate Error from True Values', fontsize=14)
ax.set_xticklabels(comparison_df['parameter'], rotation=45, ha='right')
ax.legend()
ax.grid(alpha=0.3, axis='y')

plt.tight_layout()
plt.savefig(fig_dir / "error_analysis.png", dpi=150, bbox_inches='tight')
print(f"    Saved to: {fig_dir / 'error_analysis.png'}")
plt.close()

print("\n" + "=" * 80)
print("VISUALIZATION COMPLETE!")
print(f"All plots saved to: {fig_dir}")
print("=" * 80)
