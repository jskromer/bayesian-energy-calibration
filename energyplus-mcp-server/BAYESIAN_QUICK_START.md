# Bayesian Calibration - Quick Start Guide

## What Was Done

Successfully ran a **Bayesian calibration** of a residential building energy model using:
- **Published priors** from peer-reviewed building science literature
- **PyMC** for probabilistic programming
- **NUTS algorithm** for efficient MCMC sampling
- **Synthetic monthly energy data** for demonstration

## Key Results

### Best Performing Parameters (Low Error)
1. **Heating Efficiency**: 4.8% error - Excellent calibration
2. **Cooling COP**: 8.3% error - Very good calibration
3. **Infiltration**: 13.3% error - Good calibration

### Published Prior Sources

All priors based on authoritative sources:
- **ASHRAE** - HVAC and building standards
- **DOE Building Energy Codes** - Residential building stock
- **NREL** - Window technology database
- **LBNL** - Infiltration research (Sherman & Chan, 2006)
- **US Census Bureau** - Occupancy statistics

### MCMC Convergence

✓ Perfect convergence (R-hat = 1.0)
✓ High effective sample sizes (1,200-2,900)
✓ Zero divergences
✓ 2,000 posterior samples from 2 chains

## Files Generated

```
bayesian_calibration_results/
├── posterior_trace.nc              # Full MCMC trace (NetCDF)
├── posterior_summary.csv           # Statistical summaries
├── calibration_comparison.csv      # Prior vs Posterior vs True
├── published_priors.json           # Prior specifications
└── figures/
    ├── posterior_distributions.png # Posterior PDFs
    ├── trace_plots.png             # MCMC convergence
    ├── forest_plot.png             # Credible intervals
    ├── parameter_comparison.png    # Bar chart comparison
    └── error_analysis.png          # Error by parameter
```

## How to Use This for Real Buildings

### Step 1: Collect Data
```python
# You need:
- Monthly utility bills (12-24 months)
- Building audit data (walls, roof, windows)
- HVAC equipment specs
- Occupancy information
```

### Step 2: Modify the Code
```python
# In bayesian_house_calibration.py:

# Replace synthetic data with real data
measured_monthly = [1200, 1100, 950, ...]  # Your actual kWh data

# Update building geometry
floor_area = YOUR_BUILDING_AREA  # ft²
wall_area = YOUR_WALL_AREA       # ft²
# etc.

# Use actual weather data
hdd_monthly = GET_FROM_WEATHER_FILE()
cdd_monthly = GET_FROM_WEATHER_FILE()
```

### Step 3: Run Calibration
```bash
python3 bayesian_house_calibration.py
```

### Step 4: Analyze Results
```bash
python3 visualize_bayesian_results.py
```

Check:
- R-hat < 1.01 (convergence)
- ESS > 400 (sufficient samples)
- Posterior vs prior comparison
- Error analysis

## Published Priors Used

| Parameter | Source | Citation |
|-----------|--------|----------|
| Wall/Roof R-values | DOE, ASHRAE | Building Energy Codes, ASHRAE 90.2 |
| Window U-factor | NREL | Window Technology Database |
| Infiltration | LBNL | Sherman & Chan (2006) |
| HVAC Efficiency | ASHRAE | HVAC Equipment Standards |
| Lighting | ASHRAE | ASHRAE 90.1 |
| Occupancy | US Census | American Community Survey (2020) |

## Key References

1. **Sherman, M. H., & Chan, R.** (2006). Building Airtightness: Research and Practice. LBNL-53356.

2. **Heo, Y., et al.** (2012). Calibration of building energy models for retrofit analysis under uncertainty. Energy and Buildings, 47, 550-560.

3. **Chong, A., & Menberg, K.** (2018). Guidelines for the Bayesian calibration of building energy models. Energy and Buildings, 174, 527-547.

## Interpretation Guide

### R-hat (Gelman-Rubin statistic)
- < 1.01: Excellent convergence ✓
- 1.01-1.05: Acceptable
- > 1.05: Poor convergence, run more samples

### Effective Sample Size (ESS)
- > 400: Good
- > 1000: Excellent ✓
- < 400: May need more samples

### Error Analysis
- < 10%: Excellent parameter estimate
- 10-25%: Good estimate
- > 25%: Parameter may need more data or better model

## Advanced Options

### More Chains
```python
trace = pm.sample(
    draws=2000,
    tune=1000,
    chains=4,  # Increase to 4 chains
    cores=4    # Parallel sampling
)
```

### Different Prior
```python
# If you have building-specific information
wall_r = pm.Normal("wall_r_value", mu=YOUR_MEAN, sigma=YOUR_STD)
```

### EnergyPlus Integration
For real calibration, replace the simplified physics model with actual EnergyPlus:
1. Generate IDF files with sampled parameters
2. Run EnergyPlus
3. Extract monthly totals
4. Compare to measured data

## Summary Statistics

```
Posterior Means (with 95% credible intervals):
- Wall R-value: 18.8 ± 4.6 h·ft²·°F/Btu
- Roof R-value: 35.7 ± 8.3 h·ft²·°F/Btu
- Window U-factor: 0.08 ± 0.14 Btu/h·ft²·°F
- Infiltration: 0.35 ± 0.21 ACH
- Heating Eff: 0.92 ± 0.10 AFUE
- Cooling COP: 3.12 ± 0.62
- Lighting: 0.51 ± 0.16 W/ft²
- Occupants: 2.38 ± 0.92 people
```

---

**Full Documentation**: See [BAYESIAN_CALIBRATION_SUMMARY.md](BAYESIAN_CALIBRATION_SUMMARY.md)

**Code**: [bayesian_house_calibration.py](bayesian_house_calibration.py)
