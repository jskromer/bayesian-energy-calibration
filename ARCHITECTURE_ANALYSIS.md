# Bayesian Energy Calibration Architecture Analysis

## 1. CURRENT BAYESIAN CALIBRATION IMPLEMENTATION

### Core Libraries & Methods
- **PyMC 5.10.4**: Probabilistic programming for Bayesian inference
- **ArviZ 0.17.1**: Posterior analysis and visualization
- **Sampling Algorithm**: NUTS (No U-Turn Sampler) - state-of-the-art HMC
- **MCMC Configuration**: 2 independent chains, 1,000 draws per chain, 500 tuning iterations
- **Convergence**: R-hat = 1.0, ESS = 1,221-2,886 (excellent)

### Published Priors (Literature-based)
| Parameter | Distribution | Mean | Std Dev | Source |
|-----------|-------------|------|---------|--------|
| Wall R-value | Normal | 13.0 | 3.0 | DOE Building Energy Codes (2015-2018) |
| Roof R-value | Normal | 30.0 | 5.0 | ASHRAE 90.2 |
| Window U-factor | Normal | 0.35 | 0.08 | NREL Window Technology |
| Infiltration (ACH) | LogNormal | ln(0.35) | 0.3 | LBNL Sherman & Chan (2006) |
| Heating Efficiency | Normal | 0.85 | 0.05 | ASHRAE Equipment Standards |
| Cooling COP | Normal | 3.2 | 0.3 | ASHRAE Equipment Standards |
| Lighting Power Density | Normal | 0.8 | 0.2 | ASHRAE 90.1 |
| Occupant Density | Normal | 2.5 | 0.5 | US Census Bureau |

### Energy Model Components
**Likelihood Function**: Building physics-based surrogate model
- **Heat Transfer**: UA·ΔT approach for envelope losses
- **Climate Data**: HDD/CDD (Heating/Cooling Degree Days) for specific regions
- **Internal Gains**: Lighting, equipment, and occupancy loads
- **HVAC Modeling**: Seasonal efficiency factors for heating/cooling
- **Observation Noise**: Normal likelihood with estimated measurement uncertainty

### Calibration Workflow
```
Published Priors → PyMC Model Definition → NUTS Sampling → Posterior Distributions
                        ↓
                  Building Physics Model
                  (UA approach)
                        ↓
                  Monthly Energy Data
                  (Likelihood)
```

---

## 2. DIGITAL TWIN ARCHITECTURE (DTABM Framework)

### Three Synchronized Models

**DTABM_Baseline** (Frozen Reference)
- Calibrated pre-retrofit baseline model
- Never changes - snapshot of "as-audited" condition
- Used as M&V reference point for savings calculations
- Annual Energy: 449,389 kWh/year (example)

**DTABM_Operational** (Live Tracking)
- Real-time digital twin updated monthly with meter data
- Detects performance drift and faults (>10% deviation triggers alert)
- Continuous monitoring and anomaly detection
- Automated monthly calibration updates

**DTActual** (Post-ECM Model)
- Created when first ECM is implemented
- Version-controlled (increments with each change)
- Reflects actual retrofit improvements
- Post-retrofit validation against measured performance

### Operational Workflow
Monthly Update Cycle:
1. Get actual energy from meter
2. Run DTABM_Operational prediction
3. Calculate deviation
4. If < 5%: OK, continue monitoring
5. If 5-10%: Warning flag for trend review
6. If > 10%: Alert - investigate for faults/anomalies

---

## 3. GEARS INTEGRATION STATUS & OPPORTUNITIES

### Current Status: NOT INTEGRATED
- Gears (energy asset simulator with dueling digital twins) is mentioned in requirements
- BUT not yet implemented in codebase
- No "Gears" references found in code
- DTABM framework appears to be the current digital twin approach

### How GEARS Could Be Integrated

**Option A: As a Replacement for EnergyPlus Surrogate**
- Use Gears for physics-based simulations instead of UA·ΔT simplified model
- More accurate building physics for Bayesian calibration likelihood
- Better handling of complex HVAC and control interactions
- Faster than full EnergyPlus, more accurate than surrogate

**Option B: Parallel Twin Execution**
```
Input Parameters
    ↓
┌─────────────────────┐
│  DTABM_Baseline     │ ← EnergyPlus baseline
├─────────────────────┤
│  Gears_Baseline     │ ← Gears dueling twin for cross-validation
└─────────────────────┘
```

**Option C: Gears for Real-Time Operations**
- Use Gears for fast hourly/sub-hourly predictions
- DTABM_Operational updates using Gears instead of monthly simulations
- Enable real-time control system optimization

---

## 4. PARAMETERS BEING CALIBRATED

### Primary Parameters (8 building/system parameters)
1. Wall insulation R-value
2. Roof insulation R-value
3. Window U-factor
4. Infiltration (ACH - Air Changes per Hour)
5. Heating system efficiency
6. Cooling system COP (Coefficient of Performance)
7. Lighting power density
8. Occupant count

### Secondary Parameters (step3_bayesian_calibration.py)
- Building scale factor (geometry/size multiplier)
- Infiltration multiplier (allows deviation from baseline audit)
- Plug load multiplier (equipment/plug loads)

---

## 5. DATA FLOW & PROCESSING

### Complete Data Pipeline

```
PHASE 1: ENERGY AUDIT
├─ Building characteristics (geometry, construction)
├─ HVAC equipment specs
├─ Lighting system details
└─ Occupancy patterns
    ↓
PHASE 2: INITIAL MODEL CREATION
├─ Convert audit data to EnergyPlus IDF
├─ Set default parameters
├─ Assign weather file (TMY3 data)
└─ Validate model syntax
    ↓
PHASE 3: TRAINING DATA GENERATION
├─ Latin Hypercube Sampling (LHS) for efficient space coverage
├─ 8-20 EnergyPlus simulations with varied parameters
├─ Extract annual energy for each combination
└─ Build training dataset (parameter vectors → energy outputs)
    ↓
PHASE 4: SURROGATE MODEL BUILD
├─ Gaussian Process Regression on training data
├─ RBF kernel with ConstantKernel scaling
├─ ~30x-100x faster than EnergyPlus
└─ Provides uncertainty estimates (std deviation)
    ↓
PHASE 5: BAYESIAN INFERENCE
├─ Define priors (from published literature)
├─ Set up PyMC probabilistic model
├─ Define likelihood (building physics)
├─ NUTS sampling (2,000 posterior samples)
└─ Convergence diagnostics
    ↓
PHASE 6: POSTERIOR ANALYSIS
├─ Parameter estimate distributions
├─ Uncertainty quantification
├─ Model validation
└─ Savings predictions
```

### Key Data Sources
- **Building Audit**: Spreadsheet/database with envelope, HVAC, lighting data
- **Utility Bills**: Monthly electricity consumption (kWh)
- **Weather Data**: TMY3 weather files (hourly temperature, solar, wind)
- **EnergyPlus Output**: Annual energy consumption from simulations
- **Published Priors**: Academic literature on building parameters

### Processing Outputs
- **posterior_trace.nc**: Full MCMC trace (NetCDF format)
- **posterior_summary.csv**: Mean, std, credible intervals for each parameter
- **published_priors.json**: Prior specification for reproducibility
- **dtabm_registry.json**: Digital twin model versions and status

---

## 6. EXISTING MONTE CARLO & UNCERTAINTY QUANTIFICATION

### Currently Implemented

**Monte Carlo Sampling**
- NUTS (MCMC) algorithm generates posterior samples
- 2,000 samples per parameter from posterior distribution
- Full uncertainty propagation through building physics model
- Output: Posterior predictive distributions for annual energy

**Uncertainty Quantification**
- Parameter uncertainties: Full posterior distributions
- Total energy: 95% CI = [17,758 - 21,332] kWh/year
- Credible intervals for monthly and annual predictions
- Measurement noise modeled in likelihood

**Parameter Sweep (Limited)**
- Latin Hypercube Sampling for training data generation (8-20 samples)
- Grid search in step3_bayesian_calibration.py (20³ = 8,000 evaluations)
- NOT a true global sensitivity analysis

### Missing/Incomplete
- **No formal sensitivity analysis** (Sobol indices, Morris screening)
- **No global parameter sweeps** prior to Bayesian calibration
- **No surrogate-based optimization** (only grid search)
- **No factorial designs** for interaction analysis

---

## 7. MAIN ENTRY POINTS & WORKFLOWS

### Standalone Calibration Scripts

**bayesian_house_calibration.py** (437 lines)
- Simplest entry point
- Synthetic data generation
- Published prior definitions
- NUTS sampling
- Result visualization

**step3_bayesian_calibration.py** (405 lines)
- Real building workflow
- EnergyPlus simulation integration
- Gaussian Process surrogate modeling
- Grid search for calibration
- ASHRAE Guideline 14 compliance checking

**bayesian_calibration_pymc.py** (439 lines)
- Advanced integration
- MCP (Model Context Protocol) integration
- Active learning (iterative real simulation calls)
- PyMC MCMC with GP surrogate
- Limits real simulations to ~20

### Interactive Applications

**streamlit_app.py** (489 lines)
- Web-based interactive calibration
- Real-time prior adjustment with sliders
- MCMC recalibration on parameter change
- Live posterior visualizations
- Results download (CSV/JSON)
- **Hosted at**: https://bayesian-energy-calibration-demo.streamlit.app

### Digital Twin Operations

**dtabm_framework.py** (562 lines)
- DTABM_Baseline creation
- DTABM_Operational monthly updates
- DTActual ECM implementation
- Post-ECM validation
- M&V savings calculation
- Anomaly detection logging

### Supporting Workflows

**audit_to_model_workflow.py** (369 lines)
- End-to-end audit → model → calibration → retrofit
- Energy audit data collection template
- Building info to IDF conversion
- Baseline model creation

**fault_detection_bayesian.py** (495 lines)
- Fault detection using Bayesian calibration
- Counterfactual analysis
- Savings prediction with uncertainty
- MCP integration for real simulations

### Visualization & Analysis

**visualize_bayesian_results.py** (80+ lines)
- Posterior distributions vs priors
- MCMC trace convergence plots
- Forest plots (credible intervals)
- Cumulative distributions
- Parameter comparison charts

**analyze_total_energy_posterior.py** (378 lines)
- Total energy posterior analysis
- Monthly energy predictions
- Credible interval calculations
- Detailed error analysis

### FMU Co-Simulation

**fmu_cosim_complete.py** (213 lines)
- EnergyPlus to FMU export
- FMI 2.0 co-simulation loop
- Control system coupling
- Comparison with baseline

---

## 8. ARCHITECTURE DIAGRAM

```
┌────────────────────────────────────────────────────────────────────┐
│                 BAYESIAN ENERGY CALIBRATION SYSTEM                 │
└────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│ INPUT LAYER                                                          │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  Energy Audit Data  ←→  Published Priors     ←→  Utility Bills     │
│  (IDF Template)          (Literature)             (Monthly kWh)     │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────────┐
│ SIMULATION LAYER                                                     │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  EnergyPlus (Full Simulation)    ←→  Gaussian Process Surrogate    │
│  - Full physics                       - Fast (~100x faster)        │
│  - 5-30 min per run                   - Uncertainty estimates      │
│  - Training data generation            - Efficient MCMC coupling   │
│                                                                      │
│  Alternative: Gears (Future)                                        │
│  - Dueling digital twins              - Can replace both          │
│  - Faster, more accurate                                            │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────────┐
│ BAYESIAN INFERENCE LAYER                                             │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  PyMC Probabilistic Model                                            │
│  ├─ Prior Distributions (from literature)                           │
│  ├─ Likelihood: Building Physics + Observation Noise                │
│  ├─ NUTS MCMC Sampling                                              │
│  │  ├─ 2 chains                                                     │
│  │  ├─ 1,000 draws per chain                                        │
│  │  └─ 500 tuning iterations                                        │
│  └─ Posterior Sampling (2,000 samples)                              │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────────┐
│ OUTPUT & ANALYSIS LAYER                                              │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  Posterior Distributions          Convergence Diagnostics            │
│  ├─ Parameter means & std         ├─ R-hat (< 1.01)                │
│  ├─ Credible intervals             ├─ ESS (> 400)                  │
│  └─ Uncertainty bands              └─ Divergences (0)              │
│                                                                      │
│  Visualization                     Digital Twin Registry             │
│  ├─ Posterior plots                ├─ DTABM_Baseline               │
│  ├─ Trace convergence              ├─ DTABM_Operational            │
│  ├─ Forest plots                   └─ DTActual                     │
│  └─ Monthly energy bands                                             │
│                                                                      │
│  Streamlit Web App                 REST API (via MCP)               │
│  ├─ Interactive priors              ├─ EnergyPlus tools            │
│  ├─ Real-time calibration           ├─ Model loading/saving        │
│  └─ Live visualization              └─ Simulation calls            │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────────┐
│ OPERATIONAL LAYER (Digital Twin)                                     │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  Monthly Operations Monitoring    │  Retrofit Evaluation             │
│  ├─ Actual energy (meter)         │  ├─ ECM scenarios              │
│  ├─ Predicted energy (model)      │  ├─ Energy savings             │
│  ├─ Deviation analysis            │  ├─ Cost-benefit analysis      │
│  └─ Anomaly detection             │  ├─ Uncertainty bands          │
│                                   │  └─ M&V verification           │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 9. TECHNICAL STACK

### Core Dependencies
- **Python 3.8+**
- **PyMC 5.10.4** - Probabilistic programming
- **ArviZ 0.17.1** - Posterior analysis
- **NumPy 1.24.3** - Numerical computing
- **Pandas 2.0.3** - Data manipulation
- **SciPy 1.11.4** - Scientific computing
- **Matplotlib 3.7.2** - Plotting
- **PyTensor 2.18.6** - Computational graphs (PyMC backend)

### Optional/Advanced
- **scikit-learn** - Gaussian Process surrogate
- **eppy** - EnergyPlus IDF manipulation
- **FMPy** - FMU co-simulation
- **Streamlit** - Web app framework
- **NetworkX** - HVAC diagram generation

### Infrastructure
- **EnergyPlus 25.1.0** - Building energy simulation
- **Docker** - Containerization
- **GitHub** - Version control
- **Streamlit Cloud** - Web deployment

---

## 10. INTEGRATION POINTS FOR MONTE CARLO PARAMETER SWEEPS

### Recommendation 1: Pre-Calibration Sensitivity Analysis
```
BEFORE Bayesian calibration:
1. Run Morris one-at-a-time sensitivity analysis
   - Screens which parameters matter most
   - Reduces dimensionality
   
2. Generate Sobol indices
   - Quantifies parameter interactions
   - Main effects vs interaction effects
   
3. Create parameter importance ranking
   - Focus Bayesian calibration on key parameters
   - Reduces MCMC dimensionality
   
Location: NEW script → sensitivity_analysis.py (before step3)
```

### Recommendation 2: Parameter Sweep During Calibration
```
WITHIN Bayesian calibration:
1. Replace grid search in step3_bayesian_calibration.py
   - Current: Simple 20³ grid
   - Better: Quasi-random Sobol sequence
   - Best: Adaptive space-filling design
   
2. Latin Hypercube Sampling (already used!)
   - Good for training data
   - Consider Latin Supercube for larger samples
   
3. Sequential Design
   - Run initial sweep (8-16 points)
   - Build GP surrogate
   - Identify regions needing refinement
   - Add points in high-uncertainty zones
   - Iterate until convergence
   
Location: Enhance step3_bayesian_calibration.py, bayesian_calibration_pymc.py
```

### Recommendation 3: Post-Calibration Uncertainty Propagation
```
AFTER Bayesian inference:
1. Use posterior samples for MC simulation
   - Already done! 2,000 posterior samples
   - Propagate through energy model
   
2. Generate output distributions
   - Annual energy credible intervals
   - Monthly energy bands
   - Retrofit savings with uncertainty
   
3. Advanced: Nested MC
   - For each posterior sample: run EnergyPlus
   - Propagates both parameter AND model uncertainty
   - More accurate but computationally expensive
   
Location: analyze_total_energy_posterior.py (enhance)
```

---

## 11. RAVEN INTEGRATION OPPORTUNITIES

### What is RAVEN?
**RAVEN** (Reactor Analysis and Verification Engine) from INL
- Advanced framework for uncertainty quantification
- Monte Carlo, adaptive sampling, surrogate modeling
- Sensitivity analysis (Sobol, Morris, etc.)
- Multi-model integration
- Python/C++ hybrid

### Integration Points

#### Option A: Replace PyMC with RAVEN
```
Current: PyMC + GP Surrogate
RAVEN:   Built-in UQ + adaptive sampling

Advantages:
✓ Seamless MC parameter sweeps
✓ Multiple UQ methodologies
✓ Sensitivity analysis built-in
✓ Better multi-objective optimization
✓ Adaptive sampling reduces simulations

Drawbacks:
✗ Learning curve steeper
✗ Less "Bayesian" focused
✗ Fewer publications for building energy
```

#### Option B: Pre-Process with RAVEN, Calibrate with PyMC
```
RAVEN Phase:
1. Parameter screening (Morris)
2. Space-filling design (Sobol)
3. Run simulations (10-50 points)

PyMC Phase:
1. Build GP on RAVEN results
2. Bayesian inference
3. Posterior visualization

Advantages:
✓ Best of both worlds
✓ Structured sensitivity analysis first
✓ PyMC's Bayesian framework remains
✓ Clearer parameter importance

Drawbacks:
✗ Two-tool workflow
✗ Additional integration code
```

#### Option C: RAVEN for Multi-Model Gears/EnergyPlus
```
When GEARS integrated:
1. Run both EnergyPlus AND Gears simulations
2. RAVEN combines results
3. Compare dueling digital twins
4. Detect when divergence indicates problems

Example:
├─ EnergyPlus Surrogate (slower, more accurate)
├─ Gears Surrogate (faster, for real-time)
└─ RAVEN reconciliation (which is more credible?)
```

### Recommended RAVEN Implementation
**Phase 1 (Next 3-6 months)**: Add Morris sensitivity analysis
```python
# Pre-calibration screening
# Uses 10-20 simulations to identify key parameters
# Natural fit with existing EnergyPlus/GP framework
```

**Phase 2 (6-12 months)**: Sobol indices + parameter importance
```python
# More sophisticated but still using EnergyPlus
# Quantifies interactions between parameters
```

**Phase 3 (12+ months)**: Full RAVEN integration for Gears
```python
# When Gears is operational
# Use RAVEN to manage multi-model comparisons
# Adaptive sampling between models
```

---

## 12. RECOMMENDED ARCHITECTURE ENHANCEMENTS

### Short Term (1-3 months)
1. Add formal sensitivity analysis (Morris → Sobol)
2. Implement adaptive parameter sweep for training data
3. Add validation data hold-out for model checking
4. Create ensemble predictions (multiple models/priors)

### Medium Term (3-6 months)
1. Integrate Gears for dueling digital twins
2. Add RAVEN for comprehensive UQ
3. Implement real-time DTABM_Operational updates
4. Create dashboard with alerts for anomalies

### Long Term (6-12 months)
1. Multi-building calibration framework
2. Automated ECM recommendation engine
3. Integration with utility incentive programs
4. Climate change impact projections

---

## Summary Table: Current vs. Enhanced Architecture

| Aspect | Current | With Monte Carlo | With RAVEN & Gears |
|--------|---------|------------------|-------------------|
| **Calibration** | Bayesian (PyMC) | Bayesian + Sensitivity | Bayesian + Multi-Model |
| **Surrogate** | Gaussian Process | GP + Adaptive Design | RAVEN-managed surrogates |
| **Simulations** | 20-30 for training | 50-100 optimized | 200+ with adaptation |
| **Sensitivity** | None | Morris/Sobol | RAVEN built-in |
| **Real-Time** | DTABM (monthly) | DTABM (hourly possible) | DTABM + Gears hourly |
| **Uncertainty** | Posterior bands | MC propagation | Multi-model ensemble |
| **Execution** | ~2 hours | ~4 hours (more thorough) | ~6+ hours (comprehensive) |

---

## Key Files to Review
1. `bayesian_house_calibration.py` - Main Bayesian model
2. `step3_bayesian_calibration.py` - Full workflow with GP
3. `dtabm_framework.py` - Digital twin operations
4. `bayesian_calibration_pymc.py` - MCP integration
5. `streamlit_app.py` - Interactive interface
6. `BAYESIAN_CALIBRATION_SUMMARY.md` - Detailed methodology

