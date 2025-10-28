# Energy Audit → Calibrated Model → Retrofit Analysis Workflow

## Complete M&V (Measurement & Verification) Process

This document describes the complete workflow from initial energy audit through calibrated baseline model to retrofit analysis with uncertainty quantification.

---

## Workflow Overview

```
┌─────────────────┐
│  STEP 1:        │
│  Energy Audit   │──→ Building data, utility bills, site observations
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  STEP 2:        │
│  Initial Model  │──→ EnergyPlus model from audit data
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  STEP 3:        │
│  Calibration    │──→ Bayesian parameter tuning to match bills
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  STEP 4:        │
│  Baseline Model │──→ Validated, calibrated baseline
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  STEP 5:        │
│  Retrofit ECMs  │──→ Test energy conservation measures
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  STEP 6:        │
│  M&V Report     │──→ Savings with uncertainty (IPMVP)
└─────────────────┘
```

---

## STEP 1: Energy Audit

### What Was Collected

✅ **Building Characteristics**
- 25,000 sq ft office building
- Built 1995, 3 floors
- 75 occupants
- Operating hours: 7 AM - 6 PM weekdays

✅ **Envelope Data**
- Walls: R-11 (brick veneer + batt insulation)
- Roof: R-15 (built-up + rigid insulation)
- Windows: Double-pane, U=0.55, SHGC=0.60, WWR=35%
- Infiltration: Estimated 12 ACH50 (visible gaps)

✅ **HVAC Systems**
- **RTU-1**: 15 tons, EER 10.5, 80% AFUE gas heat, serves floors 1-2
  - ⚠️ Economizer NOT working
  - Estimated 15% duct leakage
- **RTU-2**: 10 tons, EER 11.0, 82% AFUE gas heat, serves floor 3
  - Economizer working
  - Estimated 15% duct leakage

✅ **Lighting**
- Interior: T8 fluorescent, 1.54 W/sqft average
- No occupancy sensors
- No daylight sensors
- Lights left on after hours

✅ **Equipment**
- Computers, monitors, printers: typical office density
- Equipment left on 24/7 (no power management)
- 1.2 W/sqft plug load density

✅ **Utility Bills (12 months)**
- **Electricity**: 424,300 kWh/year @ $0.12/kWh
- **Natural Gas**: 15,930 therms/year @ $1.10/therm
- **Total Cost**: $68,439/year

✅ **Energy Use Intensity**
- Electric EUI: 17.0 kWh/sqft/year
- Gas EUI: 63.7 kBTU/sqft/year

### Key Findings

| Issue | Impact | Priority |
|-------|--------|----------|
| RTU-1 economizer broken | Lost free cooling | High |
| 15% duct leakage | Wasted conditioned air | High |
| No lighting controls | Unnecessary runtime | Medium |
| 24/7 equipment operation | Wasted plug loads | Medium |
| High infiltration | Heat loss/gain | Medium |
| Old inefficient windows | High U-factor | Low (costly) |

---

## STEP 2: Initial Model Creation

### Model Development Process

```python
# Pseudo-code for model creation from audit data

def create_initial_model(audit_data):
    """Build EnergyPlus IDF from audit data"""

    # 1. Building geometry
    - Create 3-floor building: 25,000 sqft total
    - 13 ft floor-to-floor height
    - Window-to-wall ratio: 0.35
    - Orientation: Assume rectangular, long axis E-W

    # 2. Construction assemblies
    - Walls: R-11 (from audit)
    - Roof: R-15 (from audit)
    - Windows: U=0.55, SHGC=0.60 (from audit)
    - Infiltration: 0.5 ACH (converted from blower door)

    # 3. HVAC systems
    - RTU-1: 15 tons, EER 10.5, 80% heating efficiency
      - DISABLE economizer (broken per audit!)
      - Duct leakage: 15%
    - RTU-2: 10 tons, EER 11.0, 82% heating efficiency
      - ENABLE economizer
      - Duct leakage: 15%
    - Thermostats: 70/73°F occ, 65/78°F unocc

    # 4. Lighting
    - Interior LPD: 1.54 W/sqft
    - Schedule: 7 AM - 6 PM + some after-hours
    - No controls (per audit)

    # 5. Plug loads
    - Equipment: 1.2 W/sqft
    - 24/7 operation (no power management)

    # 6. Occupancy
    - 75 people, 7 AM - 6 PM weekdays
    - Closed weekends

    return idf_model
```

### Initial Model Characteristics

**This model represents the building "as-audited" including all deficiencies:**
- ❌ Broken economizer on RTU-1
- ❌ 15% duct leakage (both units)
- ❌ Lights on extended hours (no controls)
- ❌ Equipment on 24/7
- ❌ High infiltration

---

## STEP 3: Model Calibration

### Calibration Methodology

**Goal**: Adjust uncertain parameters so model matches utility bills within ASHRAE Guideline 14 tolerances.

#### ASHRAE Guideline 14 Criteria

| Metric | Monthly | Hourly |
|--------|---------|--------|
| **MBE** (Mean Bias Error) | ±5% | ±10% |
| **CV(RMSE)** (Normalized Root Mean Square Error) | ±15% | ±30% |

### Calibration Parameters (Uncertain)

These are parameters we're unsure about from the audit:

| Parameter | Initial Estimate | Range | Reason for Uncertainty |
|-----------|------------------|-------|------------------------|
| **Infiltration** | 0.5 ACH | 0.3-0.8 | Estimated from visual, no blower door |
| **Plug load schedule** | 24/7 @ 100% | Varies | Don't know actual usage pattern |
| **Lighting after-hours** | 20% on | 10-40% | Anecdotal - lights left on |
| **Occupancy density** | 75 people | 60-90 | Nominal count, varies daily |
| **Thermostat setpoints** | 70/73°F | ±2°F | Actual may differ from stated |
| **Equipment power** | 1.2 W/sqft | 0.8-1.6 | Estimated, not measured |

### Bayesian Calibration Process

```python
import pymc as pm
import numpy as np

def calibrate_model(initial_model, utility_bills):
    """
    Bayesian calibration using PyMC
    Matches model to 12 months of utility bills
    """

    # Observed data from bills
    observed_elec_kwh = np.array([28500, 26800, ..., 29800])  # 12 months
    observed_gas_therms = np.array([2850, 2650, ..., 2680])   # 12 months

    with pm.Model() as calibration_model:
        # Prior distributions for uncertain parameters
        infiltration_ach = pm.TruncatedNormal('infiltration', mu=0.5, sigma=0.1, lower=0.3, upper=0.8)
        plug_load_mult = pm.TruncatedNormal('plug_load', mu=1.0, sigma=0.2, lower=0.7, upper=1.5)
        lighting_afterhours = pm.TruncatedNormal('lighting_afterhours', mu=0.20, sigma=0.1, lower=0.1, upper=0.4)

        # Run EnergyPlus with these parameters
        # (In practice, use surrogate model/emulator for speed)
        simulated_elec = run_energyplus(infiltration_ach, plug_load_mult, lighting_afterhours)

        # Likelihood - how well does model match bills?
        sigma_elec = pm.HalfNormal('sigma_elec', sigma=2000)  # Measurement uncertainty
        pm.Normal('obs_elec', mu=simulated_elec, sigma=sigma_elec, observed=observed_elec_kwh)

        # Sample posterior
        trace = pm.sample(2000, tune=1000, return_inferencedata=True)

    return trace
```

### Calibration Results Example

**After Bayesian calibration:**

| Parameter | Prior Mean | Posterior Mean | 95% Credible Interval |
|-----------|------------|----------------|----------------------|
| Infiltration (ACH) | 0.50 | **0.62** | [0.55, 0.70] |
| Plug load multiplier | 1.00 | **1.15** | [1.05, 1.28] |
| After-hours lighting | 0.20 | **0.28** | [0.22, 0.35] |

**Model vs. Bills Comparison:**

| Month | Actual (kWh) | Model (kWh) | Error |
|-------|--------------|-------------|-------|
| Jan | 28,500 | 28,650 | +0.5% |
| Feb | 26,800 | 26,420 | -1.4% |
| ... | ... | ... | ... |
| Dec | 29,800 | 29,980 | +0.6% |

**Calibration Statistics:**
- MBE (Monthly): **+1.2%** ✅ (within ±5%)
- CV(RMSE): **8.3%** ✅ (within ±15%)

**Model is now CALIBRATED per ASHRAE Guideline 14!**

---

## STEP 4: Validated Baseline Model

### Baseline Model Characteristics

✅ **Calibrated to utility bills** (MBE < 5%, CV(RMSE) < 15%)
✅ **Represents actual building operation** (including deficiencies)
✅ **Uncertainty quantified** (parameter distributions known)
✅ **Ready for retrofit analysis**

### What the Baseline Includes

**Current State (As-Is):**
- RTU-1 economizer broken ❌
- 15% duct leakage
- No lighting controls
- Equipment on 24/7
- Higher infiltration than expected (0.62 ACH calibrated)
- More after-hours usage than expected (28% calibrated)

**Annual Energy:**
- Electricity: 424,300 kWh/year
- Natural Gas: 15,930 therms/year
- Total Cost: $68,439/year

This is our **baseline** for measuring savings.

---

## STEP 5: Retrofit ECM Modeling

### ECM (Energy Conservation Measure) Scenarios

| ECM # | Description | Model Change |
|-------|-------------|--------------|
| **ECM-1** | Fix RTU-1 economizer | Enable economizer in model |
| **ECM-2** | Seal ductwork (15% → 5%) | Reduce duct leakage parameter |
| **ECM-3** | LED lighting + occupancy sensors | 50% LPD reduction + smart scheduling |
| **ECM-4** | Computer power management | 30% plug load reduction after hours |
| **ECM-5** | Air sealing (0.62 → 0.40 ACH) | Reduce infiltration |
| **ECM-6** | All ECMs combined | Implement all simultaneously |

### Running ECM Simulations

```python
def analyze_ecm(baseline_model, ecm_modifications, posterior_params):
    """
    Run ECM simulation with uncertainty propagation
    """

    # Create ECM model by modifying baseline
    ecm_model = modify_model(baseline_model, ecm_modifications)

    # Run simulation N times with samples from posterior
    n_samples = 1000
    savings_distribution = []

    for i in range(n_samples):
        # Sample calibrated parameters
        infiltration = posterior_params['infiltration'][i]
        plug_load_mult = posterior_params['plug_load'][i]

        # Run baseline with these parameters
        baseline_energy = run_energyplus(baseline_model, infiltration, plug_load_mult)

        # Run ECM with these parameters
        ecm_energy = run_energyplus(ecm_model, infiltration, plug_load_mult)

        # Calculate savings
        savings = baseline_energy - ecm_energy
        savings_distribution.append(savings)

    # Analyze savings distribution
    mean_savings = np.mean(savings_distribution)
    ci_low = np.percentile(savings_distribution, 2.5)
    ci_high = np.percentile(savings_distribution, 97.5)

    return mean_savings, (ci_low, ci_high)
```

### ECM Results Example

| ECM | Energy Savings (kWh) | 95% CI | Cost Savings | Investment | Payback |
|-----|----------------------|--------|--------------|------------|---------|
| **ECM-1: Fix Economizer** | 28,500 | [24,200, 32,800] | $3,420 | $2,500 | 0.7 yrs ✅ |
| **ECM-2: Seal Ducts** | 18,700 | [15,300, 22,100] | $2,244 | $8,000 | 3.6 yrs ✅ |
| **ECM-3: LED + Controls** | 31,900 | [29,400, 34,400] | $3,828 | $45,000 | 11.8 yrs |
| **ECM-4: Power Mgmt** | 12,800 | [10,500, 15,100] | $1,536 | $0 | 0.0 yrs ✅ |
| **ECM-5: Air Sealing** | 14,200 | [11,000, 17,400] | $1,704 | $12,000 | 7.0 yrs |
| **ECM-6: All Combined** | 98,400 | [89,200, 107,600] | $11,808 | $67,500 | 5.7 yrs ✅ |

### Interaction Effects

**Note**: ECM-6 savings (98,400 kWh) ≠ Sum of individual ECMs (106,100 kWh)

**Why?** Energy conservation measures interact:
- Fixing economizer reduces cooling load
- Less cooling = less benefit from LED lighting (which reduces cooling further)
- Better envelope = less benefit from HVAC improvements
- This is why we model the combined package!

---

## STEP 6: M&V Report with Uncertainty

### IPMVP Option C: Whole Building Analysis

**Baseline Period**: 12 months pre-retrofit
**Performance Period**: 12 months post-retrofit (future)

### Predicted Savings (All ECMs)

**Energy Savings:**
- Mean: **98,400 kWh/year** (23.2% reduction)
- 95% Confidence Interval: [89,200, 107,600] kWh
- Probability of >20% savings: **92%**

**Cost Savings:**
- Mean: **$11,808/year**
- 95% CI: [$10,704, $12,912]

**Gas Savings:**
- Mean: **2,840 therms/year** (17.8% reduction)
- Cost: **$3,124/year**

**Total Annual Savings: $14,932**

### Economic Analysis

| Metric | Value |
|--------|-------|
| Total Investment | $67,500 |
| Annual Savings | $14,932 |
| Simple Payback | 4.5 years ✅ |
| 10-Year NPV (5% discount) | $47,870 |
| IRR | 18.2% |
| Savings-to-Investment Ratio (SIR) | 2.2 |

**Recommendation: PROCEED** ✅

### Savings Guarantee

With 95% confidence:
- **Minimum savings**: $10,704/year
- **Maximum payback**: 6.3 years

Even in worst-case scenario (2.5th percentile), project still viable.

### Uncertainty Sources Quantified

| Source | Impact on Savings Uncertainty |
|--------|-------------------------------|
| Weather variability | ±3% |
| Occupancy changes | ±2% |
| Equipment operation | ±4% |
| Model calibration | ±5% |
| ECM performance | ±3% |
| **Total Combined** | **±8.9%** |

---

## Implementation & M&V Plan

### Phase 1: Priority ECMs (Year 1)
1. ✅ Fix RTU-1 economizer (0.7 yr payback)
2. ✅ Enable computer power management (free!)
3. ✅ Seal ductwork (3.6 yr payback)

**Year 1 Investment**: $10,500
**Year 1 Savings**: $7,200/year
**Year 1 Payback**: 1.5 years

### Phase 2: Lighting Retrofit (Year 2)
4. LED retrofit + occupancy sensors

**Year 2 Investment**: $45,000
**Year 2 Additional Savings**: $3,800/year
**Cumulative Savings**: $11,000/year

### Phase 3: Air Sealing (Year 3)
5. Weatherization / infiltration reduction

**Year 3 Investment**: $12,000
**Year 3 Additional Savings**: $1,700/year
**Cumulative Savings**: $12,700/year

### Ongoing M&V

**Monthly**:
- Compare utility bills to calibrated baseline (weather-adjusted)
- Track cumulative savings
- Verify ECM performance

**Quarterly**:
- Functional testing (economizer, sensors, etc.)
- Adjust model if needed (occupancy changes, etc.)

**Annually**:
- Full M&V report per IPMVP
- Update savings estimates
- Plan next phase

---

## Key Takeaways

### What This Workflow Provides

1. ✅ **Data-Driven Decisions**: Based on actual building performance, not assumptions
2. ✅ **Calibrated Baseline**: Model matches reality within 5% (ASHRAE Guideline 14)
3. ✅ **Uncertainty Quantification**: Know confidence level of savings predictions
4. ✅ **Risk Management**: Worst-case scenario still shows positive ROI
5. ✅ **Prioritized ECMs**: Focus on high-impact, quick-payback measures first
6. ✅ **Interaction Effects**: Combined package modeled correctly
7. ✅ **M&V-Ready**: Follows IPMVP protocols for verifiable savings

### Industry Standards Met

- ✅ ASHRAE Guideline 14 (calibration criteria)
- ✅ IPMVP (International Performance Measurement & Verification Protocol)
- ✅ FEMP (Federal Energy Management Program) M&V guidelines
- ✅ BPI (Building Performance Institute) standards

---

## Files in This Workflow

### Generated
- **energy_audit_data.json** - Complete audit data
- **baseline_model.idf** - Calibrated EnergyPlus model
- **ecm_models/*.idf** - Individual ECM models
- **calibration_results.csv** - Posterior parameter distributions
- **savings_analysis.csv** - ECM savings with uncertainty

### Scripts
- **audit_to_model_workflow.py** - Step 1: Audit data collection ✅
- **build_initial_model.py** - Step 2: Create EnergyPlus model
- **calibrate_baseline.py** - Step 3: Bayesian calibration
- **run_ecm_analysis.py** - Step 5: Test retrofit scenarios
- **generate_mv_report.py** - Step 6: M&V documentation

---

## Next Steps for Your Project

1. **Customize audit template** with your building's actual data
2. **Collect 12 months utility bills** (required for calibration)
3. **Run initial model** (can use DOE reference building as starting point)
4. **Calibrate to bills** using Bayesian methods
5. **Model your ECMs** (specific to your recommendations)
6. **Generate M&V report** with savings estimates + uncertainty

This provides the complete evidence-based workflow for energy retrofits!

---

*Document Version: 1.0*
*Date: October 28, 2025*
*Standards: ASHRAE Guideline 14, IPMVP*
