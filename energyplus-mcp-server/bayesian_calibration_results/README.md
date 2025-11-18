# Bayesian Building Energy Model Calibration - Results

## 🌐 View the Interactive Website

**[View Live Demo →](https://bayesian-calibration-results.vercel.app)**

Or open locally in your browser:

```
file:///workspace/energyplus-mcp-server/bayesian_calibration_results/index.html
```

Or run a local web server:

```bash
cd /workspace/energyplus-mcp-server/bayesian_calibration_results
python3 -m http.server 8000
# Then open: http://localhost:8000
```

## 📊 Quick Summary

### Posterior Distribution for Total Annual Energy

- **Mean**: 19,490 kWh/year
- **Median**: 19,470 kWh/year
- **Std Dev**: 891 kWh/year (4.6% CV)
- **95% CI**: [17,758 - 21,332] kWh/year
- **Measured**: 19,178 kWh/year (within 50% CI ✓)

### Best Parameter Estimates

1. **Heating Efficiency**: 4.8% error ✓
2. **Cooling COP**: 8.3% error ✓
3. **Infiltration**: 13.3% error ✓

### MCMC Convergence

- **R-hat**: 1.0000 (perfect convergence ✓)
- **ESS**: 1,221 - 2,886 (excellent ✓)
- **Divergences**: 0 (no issues ✓)

## 📁 Files in This Directory

### Data Files
- `posterior_trace.nc` - Full MCMC trace (363 KB)
- `posterior_summary.csv` - Statistical summaries
- `calibration_comparison.csv` - Prior/Posterior/True comparison
- `total_energy_summary.json` - Total energy statistics
- `total_energy_posterior_samples.npy` - Posterior samples for total energy
- `monthly_energy_posterior_samples.npy` - Monthly energy posteriors
- `published_priors.json` - Prior specifications with sources

### Documentation
- `index.html` - **Interactive website** ← Start here!
- `TOTAL_ENERGY_POSTERIOR.md` - Total energy analysis
- `README.md` - This file

### Figures (All PNG Images)
- `posterior_distributions.png` - Parameter posteriors vs priors
- `total_energy_posterior.png` - Total energy posterior PDF
- `total_energy_cdf.png` - Cumulative distribution
- `trace_plots.png` - MCMC convergence traces
- `forest_plot.png` - Credible intervals
- `monthly_energy_posterior.png` - Monthly energy distributions
- `parameter_comparison.png` - Prior vs Posterior vs True
- `error_analysis.png` - Calibration accuracy
- `total_energy_boxplot.png` - Summary box plot

## 🚀 What This Demonstrates

This analysis showcases a **scientifically rigorous approach** to building energy model calibration:

1. **Published Priors**: All priors based on peer-reviewed research
   - ASHRAE (HVAC standards)
   - DOE Building Energy Codes
   - NREL (Window technology)
   - LBNL (Sherman & Chan, 2006 - Infiltration)
   - US Census Bureau (Occupancy)

2. **Bayesian Inference**: PyMC with NUTS sampler
   - State-of-the-art MCMC algorithm
   - 2,000 posterior samples
   - Perfect convergence diagnostics

3. **Uncertainty Quantification**: Full posterior distributions
   - Not just point estimates
   - Credible intervals for all parameters
   - Propagated uncertainty to total energy

## 📚 References

1. Sherman, M. H., & Chan, R. (2006). Building Airtightness: Research and Practice. LBNL-53356.
2. Heo, Y., et al. (2012). Calibration of building energy models for retrofit analysis. Energy and Buildings, 47, 550-560.
3. Chong, A., & Menberg, K. (2018). Guidelines for Bayesian calibration. Energy and Buildings, 174, 527-547.
4. ASHRAE (2021). ASHRAE Handbook—Fundamentals.

## 💡 How to Apply This to Real Buildings

1. **Collect Data**: 12-24 months of utility bills + building audit
2. **Modify Priors**: Use building-specific information if available
3. **Run Calibration**: Execute `bayesian_house_calibration.py`
4. **Check Diagnostics**: Ensure R-hat < 1.01, ESS > 400
5. **Analyze Results**: Use posterior for energy predictions

---

**Generated**: November 2025
**Software**: PyMC 5.26.1, ArviZ 0.22.0
**Building**: Single Family House, New York Climate
