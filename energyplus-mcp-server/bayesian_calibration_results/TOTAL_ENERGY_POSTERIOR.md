# Posterior Distribution for Total Annual Energy Consumption

## Summary Statistics

- **Posterior Mean**: 19,490 kWh/year
- **Posterior Median**: 19,470 kWh/year
- **Posterior Std Dev**: 891 kWh/year
- **Coefficient of Variation**: 4.6%

## Credible Intervals

- **50% CI**: [18,885, 20,088] kWh/year
- **90% CI**: [18,050, 20,988] kWh/year
- **95% CI**: [17,758, 21,332] kWh/year

## Comparison to Measured Data

- **Measured Annual**: 19,178 kWh/year
- **Difference**: +312 kWh/year (+1.6%)
- **Measured Percentile**: 36.6th

### Credible Interval Coverage
- Measured within 50% CI: Yes ✓
- Measured within 90% CI: Yes ✓
- Measured within 95% CI: Yes ✓

## Interpretation

The posterior distribution represents our updated belief about total annual energy
consumption after combining:
1. Published priors from building science literature
2. Monthly energy consumption measurements
3. Building physics model

The 4.6% coefficient of variation indicates low
uncertainty in the total energy prediction.

## Visualizations

- `total_energy_posterior.png` - Posterior PDF with credible intervals
- `total_energy_cdf.png` - Cumulative distribution function
- `monthly_energy_posterior.png` - Monthly energy posteriors (violin plots)
- `total_energy_boxplot.png` - Summary box plot

---
*Generated from 2,000 posterior samples*
