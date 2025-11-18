#!/usr/bin/env python3
"""
Analyze the posterior distribution for total annual energy consumption
"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import arviz as az
from pathlib import Path

output_dir = Path("/workspace/energyplus-mcp-server/bayesian_calibration_results")
trace_file = output_dir / "posterior_trace.nc"

print("=" * 80)
print("POSTERIOR DISTRIBUTION FOR TOTAL ANNUAL ENERGY CONSUMPTION")
print("=" * 80)

# Load the trace
print("\nLoading posterior trace...")
trace = az.from_netcdf(trace_file)

# Extract posterior samples for all parameters
print("Extracting posterior samples...")
wall_r_samples = trace.posterior["wall_r_value"].values.flatten()
roof_r_samples = trace.posterior["roof_r_value"].values.flatten()
window_u_samples = trace.posterior["window_u_factor"].values.flatten()
infiltration_samples = trace.posterior["infiltration_ach"].values.flatten()
heating_eff_samples = trace.posterior["heating_efficiency"].values.flatten()
cooling_cop_samples = trace.posterior["cooling_cop"].values.flatten()
lpd_samples = trace.posterior["lighting_power_density"].values.flatten()
occupants_samples = trace.posterior["occupant_count"].values.flatten()

n_samples = len(wall_r_samples)
print(f"Number of posterior samples: {n_samples}")

# Building geometry (same as in calibration)
floor_area = 2000  # ft²
wall_area = 1500   # ft²
roof_area = 2000   # ft²
window_area = 300  # ft²

# Climate data for NY (HDD and CDD)
hdd_monthly = np.array([1100, 950, 800, 450, 200, 50,
                       10, 20, 100, 350, 650, 950])
cdd_monthly = np.array([0, 0, 0, 10, 80, 250,
                       400, 350, 150, 20, 0, 0])

print("\nCalculating total annual energy for each posterior sample...")

# Calculate total annual energy for each posterior sample
total_energy_samples = np.zeros(n_samples)

for i in range(n_samples):
    # Convert R-values to U-factors
    wall_u = 1.0 / wall_r_samples[i]
    roof_u = 1.0 / roof_r_samples[i]

    # Total UA value (includes infiltration effect)
    ua_total = (wall_u * wall_area + roof_u * roof_area +
               window_u_samples[i] * window_area) * (1 + infiltration_samples[i] * 0.1)

    # Annual heating energy (kWh)
    heating_annual = (ua_total * hdd_monthly.sum() * 24) / heating_eff_samples[i] / 3412

    # Annual cooling energy (kWh)
    cooling_annual = (ua_total * cdd_monthly.sum() * 24) / cooling_cop_samples[i] / 3412

    # Internal gains (annual kWh)
    lighting_annual = lpd_samples[i] * floor_area * 8760 / 1000
    plug_loads_annual = occupants_samples[i] * 100 * 12

    # Total annual energy
    total_energy_samples[i] = heating_annual + cooling_annual + lighting_annual + plug_loads_annual

print("\n" + "=" * 80)
print("POSTERIOR STATISTICS FOR TOTAL ANNUAL ENERGY")
print("=" * 80)

mean_energy = np.mean(total_energy_samples)
std_energy = np.std(total_energy_samples)
median_energy = np.median(total_energy_samples)

# Calculate credible intervals
ci_50 = np.percentile(total_energy_samples, [25, 75])
ci_90 = np.percentile(total_energy_samples, [5, 95])
ci_95 = np.percentile(total_energy_samples, [2.5, 97.5])

print(f"\nPosterior Mean:   {mean_energy:,.0f} kWh/year")
print(f"Posterior Median: {median_energy:,.0f} kWh/year")
print(f"Posterior Std:    {std_energy:,.0f} kWh/year")

print(f"\nCredible Intervals:")
print(f"  50% CI: [{ci_50[0]:,.0f}, {ci_50[1]:,.0f}] kWh/year")
print(f"  90% CI: [{ci_90[0]:,.0f}, {ci_90[1]:,.0f}] kWh/year")
print(f"  95% CI: [{ci_95[0]:,.0f}, {ci_95[1]:,.0f}] kWh/year")

# Calculate coefficient of variation
cv = (std_energy / mean_energy) * 100
print(f"\nCoefficient of Variation: {cv:.1f}%")

# Compare to measured data (synthetic)
measured_annual = 19178  # From the synthetic data
print(f"\n" + "-" * 80)
print(f"Comparison to Measured Data:")
print(f"-" * 80)
print(f"Measured Annual Energy: {measured_annual:,} kWh/year")
print(f"Posterior Mean:         {mean_energy:,.0f} kWh/year")
print(f"Difference:             {mean_energy - measured_annual:+,.0f} kWh/year ({(mean_energy - measured_annual)/measured_annual*100:+.1f}%)")

# Check if measured value is within credible intervals
in_50ci = ci_50[0] <= measured_annual <= ci_50[1]
in_90ci = ci_90[0] <= measured_annual <= ci_90[1]
in_95ci = ci_95[0] <= measured_annual <= ci_95[1]

print(f"\nMeasured value within:")
print(f"  50% CI: {'Yes ✓' if in_50ci else 'No ✗'}")
print(f"  90% CI: {'Yes ✓' if in_90ci else 'No ✗'}")
print(f"  95% CI: {'Yes ✓' if in_95ci else 'No ✗'}")

# Calculate posterior predictive percentile
percentile = (np.sum(total_energy_samples <= measured_annual) / n_samples) * 100
print(f"\nMeasured value is at the {percentile:.1f}th percentile of the posterior")

# ============================================================================
# VISUALIZATIONS
# ============================================================================

print("\n" + "=" * 80)
print("CREATING VISUALIZATIONS")
print("=" * 80)

fig_dir = output_dir / "figures"

# 1. Posterior distribution of total energy
print("\n1. Posterior distribution of total annual energy...")
fig, ax = plt.subplots(figsize=(10, 6))

# Histogram
ax.hist(total_energy_samples, bins=50, alpha=0.6, color='steelblue',
        density=True, edgecolor='black', linewidth=0.5)

# Add KDE (kernel density estimate)
from scipy.stats import gaussian_kde
kde = gaussian_kde(total_energy_samples)
x_range = np.linspace(total_energy_samples.min(), total_energy_samples.max(), 200)
ax.plot(x_range, kde(x_range), 'b-', linewidth=2, label='Posterior PDF')

# Add vertical lines
ax.axvline(mean_energy, color='blue', linestyle='-', linewidth=2,
           label=f'Posterior Mean: {mean_energy:,.0f} kWh')
ax.axvline(median_energy, color='cyan', linestyle='--', linewidth=2,
           label=f'Posterior Median: {median_energy:,.0f} kWh')
ax.axvline(measured_annual, color='red', linestyle='-', linewidth=2,
           label=f'Measured: {measured_annual:,} kWh')

# Add credible interval shading
ax.axvspan(ci_95[0], ci_95[1], alpha=0.2, color='blue', label='95% CI')
ax.axvspan(ci_50[0], ci_50[1], alpha=0.3, color='blue', label='50% CI')

ax.set_xlabel('Total Annual Energy Consumption (kWh)', fontsize=12)
ax.set_ylabel('Probability Density', fontsize=12)
ax.set_title('Posterior Distribution of Total Annual Energy Consumption', fontsize=14, fontweight='bold')
ax.legend(loc='upper right')
ax.grid(alpha=0.3)

plt.tight_layout()
plt.savefig(fig_dir / "total_energy_posterior.png", dpi=150, bbox_inches='tight')
print(f"   Saved to: {fig_dir / 'total_energy_posterior.png'}")
plt.close()

# 2. Cumulative distribution
print("\n2. Cumulative distribution function...")
fig, ax = plt.subplots(figsize=(10, 6))

sorted_samples = np.sort(total_energy_samples)
cumulative = np.arange(1, n_samples + 1) / n_samples

ax.plot(sorted_samples, cumulative * 100, 'b-', linewidth=2)
ax.axvline(measured_annual, color='red', linestyle='--', linewidth=2,
           label=f'Measured: {measured_annual:,} kWh ({percentile:.1f}th percentile)')
ax.axhline(50, color='gray', linestyle=':', alpha=0.5)
ax.axhline(90, color='gray', linestyle=':', alpha=0.5)
ax.axhline(95, color='gray', linestyle=':', alpha=0.5)

# Mark key percentiles
for p, label in [(2.5, '2.5%'), (25, '25%'), (50, '50%'), (75, '75%'), (97.5, '97.5%')]:
    val = np.percentile(total_energy_samples, p)
    ax.plot(val, p, 'ro', markersize=8)
    ax.text(val, p + 3, f'{val:,.0f} kWh', ha='center', fontsize=9)

ax.set_xlabel('Total Annual Energy Consumption (kWh)', fontsize=12)
ax.set_ylabel('Cumulative Probability (%)', fontsize=12)
ax.set_title('Cumulative Distribution of Total Annual Energy', fontsize=14, fontweight='bold')
ax.legend()
ax.grid(alpha=0.3)

plt.tight_layout()
plt.savefig(fig_dir / "total_energy_cdf.png", dpi=150, bbox_inches='tight')
print(f"   Saved to: {fig_dir / 'total_energy_cdf.png'}")
plt.close()

# 3. Monthly energy posterior distributions
print("\n3. Monthly energy posterior distributions...")
monthly_energy_samples = np.zeros((n_samples, 12))

for i in range(n_samples):
    wall_u = 1.0 / wall_r_samples[i]
    roof_u = 1.0 / roof_r_samples[i]
    ua_total = (wall_u * wall_area + roof_u * roof_area +
               window_u_samples[i] * window_area) * (1 + infiltration_samples[i] * 0.1)

    for month in range(12):
        heating = (ua_total * hdd_monthly[month] * 24) / heating_eff_samples[i] / 3412
        cooling = (ua_total * cdd_monthly[month] * 24) / cooling_cop_samples[i] / 3412
        lighting = lpd_samples[i] * floor_area * 730 / 1000
        plugs = occupants_samples[i] * 100
        monthly_energy_samples[i, month] = heating + cooling + lighting + plugs

# Create violin plot for monthly distributions
fig, ax = plt.subplots(figsize=(14, 6))

months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
          'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

# Measured monthly data (from calibration)
measured_monthly = np.array([2152, 1937, 1703, 1453, 1186, 1334,
                            1780, 1558, 1172, 1387, 1612, 1905])

positions = np.arange(len(months))
parts = ax.violinplot([monthly_energy_samples[:, i] for i in range(12)],
                      positions=positions, widths=0.7,
                      showmeans=True, showmedians=True)

# Color the violins
for pc in parts['bodies']:
    pc.set_facecolor('steelblue')
    pc.set_alpha(0.6)

# Plot measured values
ax.plot(positions, measured_monthly, 'ro-', linewidth=2, markersize=8,
        label='Measured Monthly Energy')

ax.set_xlabel('Month', fontsize=12)
ax.set_ylabel('Monthly Energy Consumption (kWh)', fontsize=12)
ax.set_title('Posterior Distributions of Monthly Energy Consumption', fontsize=14, fontweight='bold')
ax.set_xticks(positions)
ax.set_xticklabels(months)
ax.legend()
ax.grid(alpha=0.3, axis='y')

plt.tight_layout()
plt.savefig(fig_dir / "monthly_energy_posterior.png", dpi=150, bbox_inches='tight')
print(f"   Saved to: {fig_dir / 'monthly_energy_posterior.png'}")
plt.close()

# 4. Box plot summary
print("\n4. Summary statistics box plot...")
fig, ax = plt.subplots(figsize=(8, 6))

bp = ax.boxplot([total_energy_samples], widths=0.6, patch_artist=True,
                labels=['Total Annual Energy'])

bp['boxes'][0].set_facecolor('steelblue')
bp['boxes'][0].set_alpha(0.6)

# Add measured value
ax.plot(1, measured_annual, 'ro', markersize=12, label='Measured', zorder=5)

# Add text annotations
ax.text(1.3, mean_energy, f'Mean: {mean_energy:,.0f} kWh', fontsize=10)
ax.text(1.3, ci_95[1], f'95th: {ci_95[1]:,.0f} kWh', fontsize=9)
ax.text(1.3, ci_95[0], f'5th: {ci_95[0]:,.0f} kWh', fontsize=9)

ax.set_ylabel('Annual Energy Consumption (kWh)', fontsize=12)
ax.set_title('Posterior Distribution Summary', fontsize=14, fontweight='bold')
ax.legend()
ax.grid(alpha=0.3, axis='y')

plt.tight_layout()
plt.savefig(fig_dir / "total_energy_boxplot.png", dpi=150, bbox_inches='tight')
print(f"   Saved to: {fig_dir / 'total_energy_boxplot.png'}")
plt.close()

# ============================================================================
# SAVE RESULTS
# ============================================================================

print("\n" + "=" * 80)
print("SAVING RESULTS")
print("=" * 80)

# Save total energy posterior samples
np.save(output_dir / "total_energy_posterior_samples.npy", total_energy_samples)
print(f"\n✓ Posterior samples saved to: {output_dir / 'total_energy_posterior_samples.npy'}")

# Save monthly energy posterior samples
np.save(output_dir / "monthly_energy_posterior_samples.npy", monthly_energy_samples)
print(f"✓ Monthly posterior samples saved to: {output_dir / 'monthly_energy_posterior_samples.npy'}")

# Save summary statistics
summary_stats = {
    "mean_kwh": float(mean_energy),
    "median_kwh": float(median_energy),
    "std_kwh": float(std_energy),
    "cv_percent": float(cv),
    "ci_50_lower_kwh": float(ci_50[0]),
    "ci_50_upper_kwh": float(ci_50[1]),
    "ci_90_lower_kwh": float(ci_90[0]),
    "ci_90_upper_kwh": float(ci_90[1]),
    "ci_95_lower_kwh": float(ci_95[0]),
    "ci_95_upper_kwh": float(ci_95[1]),
    "measured_kwh": float(measured_annual),
    "measured_percentile": float(percentile),
    "n_samples": int(n_samples)
}

import json
with open(output_dir / "total_energy_summary.json", "w") as f:
    json.dump(summary_stats, f, indent=2)
print(f"✓ Summary statistics saved to: {output_dir / 'total_energy_summary.json'}")

# Create markdown summary
md_summary = f"""# Posterior Distribution for Total Annual Energy Consumption

## Summary Statistics

- **Posterior Mean**: {mean_energy:,.0f} kWh/year
- **Posterior Median**: {median_energy:,.0f} kWh/year
- **Posterior Std Dev**: {std_energy:,.0f} kWh/year
- **Coefficient of Variation**: {cv:.1f}%

## Credible Intervals

- **50% CI**: [{ci_50[0]:,.0f}, {ci_50[1]:,.0f}] kWh/year
- **90% CI**: [{ci_90[0]:,.0f}, {ci_90[1]:,.0f}] kWh/year
- **95% CI**: [{ci_95[0]:,.0f}, {ci_95[1]:,.0f}] kWh/year

## Comparison to Measured Data

- **Measured Annual**: {measured_annual:,} kWh/year
- **Difference**: {mean_energy - measured_annual:+,.0f} kWh/year ({(mean_energy - measured_annual)/measured_annual*100:+.1f}%)
- **Measured Percentile**: {percentile:.1f}th

### Credible Interval Coverage
- Measured within 50% CI: {'Yes ✓' if in_50ci else 'No ✗'}
- Measured within 90% CI: {'Yes ✓' if in_90ci else 'No ✗'}
- Measured within 95% CI: {'Yes ✓' if in_95ci else 'No ✗'}

## Interpretation

The posterior distribution represents our updated belief about total annual energy
consumption after combining:
1. Published priors from building science literature
2. Monthly energy consumption measurements
3. Building physics model

The {cv:.1f}% coefficient of variation indicates {'low' if cv < 10 else 'moderate' if cv < 20 else 'high'}
uncertainty in the total energy prediction.

## Visualizations

- `total_energy_posterior.png` - Posterior PDF with credible intervals
- `total_energy_cdf.png` - Cumulative distribution function
- `monthly_energy_posterior.png` - Monthly energy posteriors (violin plots)
- `total_energy_boxplot.png` - Summary box plot

---
*Generated from {n_samples:,} posterior samples*
"""

with open(output_dir / "TOTAL_ENERGY_POSTERIOR.md", "w") as f:
    f.write(md_summary)
print(f"✓ Markdown summary saved to: {output_dir / 'TOTAL_ENERGY_POSTERIOR.md'}")

print("\n" + "=" * 80)
print("ANALYSIS COMPLETE!")
print("=" * 80)
print(f"\nAll results saved to: {output_dir}")
