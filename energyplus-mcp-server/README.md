# Bayesian Building Energy Model Calibration

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![PyMC](https://img.shields.io/badge/PyMC-5.26.1-green.svg)](https://www.pymc.io/)

Bayesian calibration of residential building energy models using **published priors from peer-reviewed building science literature**. This project demonstrates a scientifically rigorous approach to parameter estimation and uncertainty quantification in building energy modeling.

## 🌐 Live Demo

**[View Interactive Results →](https://github.com/jskromer/bayesian-energy-calibration/tree/main)**

## 📊 Key Results

### Posterior Distribution for Total Annual Energy

- **Mean**: 19,490 kWh/year
- **95% Credible Interval**: [17,758 - 21,332] kWh/year
- **Standard Deviation**: 891 kWh/year (4.6% CV)
- **Model Accuracy**: +1.6% vs measured data

### Best Parameter Estimates

| Parameter | Error | Quality |
|-----------|-------|---------|
| Heating Efficiency | 4.8% | ✅ Excellent |
| Cooling COP | 8.3% | ✅ Excellent |
| Infiltration | 13.3% | ✅ Good |

### MCMC Convergence

- **R-hat**: 1.0000 (perfect convergence ✓)
- **Effective Sample Size**: 1,221 - 2,886 (excellent ✓)
- **Divergences**: 0 (no issues ✓)

## 🎯 Project Overview

This project calibrates a single-family house energy model for New York climate using:

1. **Published Priors** from authoritative sources:
   - ASHRAE (HVAC Equipment Standards)
   - DOE Building Energy Codes (Residential Stock, 2015-2018)
   - NREL (Window Technology Database, 2010-2020)
   - LBNL (Sherman & Chan, 2006 - Infiltration Research)
   - US Census Bureau (Occupancy Statistics, 2020)

2. **Bayesian Inference** with PyMC:
   - NUTS (No U-Turn Sampler) - state-of-the-art Hamiltonian Monte Carlo
   - 2,000 posterior samples from 2 independent chains
   - Full uncertainty quantification

3. **Building Physics Model**:
   - UA·ΔT heat transfer calculations
   - Heating/Cooling Degree Days (HDD/CDD)
   - Internal gains and HVAC efficiency modeling

## 📁 Repository Structure

```
.
├── bayesian_calibration_results/     # All results and website
│   ├── index.html                     # Interactive results website
│   ├── figures/                       # 9 publication-quality plots
│   ├── posterior_trace.nc             # Full MCMC trace (NetCDF)
│   ├── posterior_summary.csv          # Statistical summaries
│   ├── published_priors.json          # Prior specifications
│   └── README.md                      # Results documentation
│
├── bayesian_house_calibration.py     # Main calibration script
├── visualize_bayesian_results.py     # Visualization generation
├── analyze_total_energy_posterior.py # Total energy analysis
│
├── BAYESIAN_CALIBRATION_SUMMARY.md   # Full methodology report
├── BAYESIAN_QUICK_START.md           # Quick start guide
├── DEPLOYMENT_GUIDE.md               # Web deployment instructions
└── README.md                          # This file
```

## 🚀 Quick Start

### Prerequisites

```bash
pip install pymc arviz pandas matplotlib numpy scipy
```

### Run the Calibration

```bash
# Run Bayesian calibration
python3 bayesian_house_calibration.py

# Generate visualizations
python3 visualize_bayesian_results.py

# Analyze total energy posterior
python3 analyze_total_energy_posterior.py
```

### View Results

Open `bayesian_calibration_results/index.html` in your browser.

## 📖 Documentation

- **[Deployment Guide](DEPLOYMENT_GUIDE.md)** - How to publish to the web
- **[Full Calibration Report](BAYESIAN_CALIBRATION_SUMMARY.md)** - Detailed methodology and results
- **[Quick Start Guide](BAYESIAN_QUICK_START.md)** - How to use for real buildings

## 🌐 Deploy to GitHub Pages

### Automated Deployment

```bash
./deploy-to-github.sh
```

Follow the prompts to deploy to GitHub Pages.

### Manual Deployment

1. Create a new repository on GitHub
2. Push this code:
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/YOUR_USERNAME/bayesian-energy-calibration.git
   git push -u origin main
   ```
3. Enable GitHub Pages in repository Settings → Pages
4. Your site will be live at: `https://YOUR_USERNAME.github.io/bayesian-energy-calibration/`

See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for more options (Netlify, Vercel, AWS S3, etc.).

## 📊 Published Prior Sources

All prior distributions are based on peer-reviewed research:

| Parameter | Source | Citation |
|-----------|--------|----------|
| Wall/Roof R-values | DOE, ASHRAE | Building Energy Codes, ASHRAE 90.2 |
| Window U-factor | NREL | Window Technology Database |
| Infiltration | LBNL | Sherman & Chan (2006) LBNL-53356 |
| HVAC Efficiency | ASHRAE | HVAC Equipment Standards |
| Lighting | ASHRAE | ASHRAE 90.1 Residential |
| Occupancy | US Census | American Community Survey (2020) |

## 📚 Key References

1. **Sherman, M. H., & Chan, R.** (2006). *Building Airtightness: Research and Practice*. Lawrence Berkeley National Laboratory. LBNL-53356.

2. **Heo, Y., Choudhary, R., & Augenbroe, G. A.** (2012). *Calibration of building energy models for retrofit analysis under uncertainty*. Energy and Buildings, 47, 550-560.

3. **Chong, A., & Menberg, K.** (2018). *Guidelines for the Bayesian calibration of building energy models*. Energy and Buildings, 174, 527-547.

4. **ASHRAE** (2021). *ASHRAE Handbook—Fundamentals*. American Society of Heating, Refrigerating and Air-Conditioning Engineers.

## 🔬 Methodology Highlights

### Bayesian Framework

- **Prior**: Published distributions from building science literature
- **Likelihood**: Building physics model with monthly energy data
- **Posterior**: MCMC sampling (NUTS algorithm) combines prior + data
- **Result**: Full probability distributions for all parameters

### MCMC Sampling

- Algorithm: NUTS (No U-Turn Sampler)
- Chains: 2 independent chains
- Samples: 1,000 draws per chain (+ 500 tuning)
- Total: 2,000 posterior samples
- Convergence: R-hat = 1.0 (perfect)

### Uncertainty Quantification

- Parameter uncertainties: Full posterior distributions
- Total energy: 95% CI = [17,758 - 21,332] kWh/year
- Propagated through building physics model
- Credible intervals for all outputs

## 📈 Visualizations

The analysis includes 9 publication-quality figures:

1. **Posterior Distributions** - How data updated prior beliefs
2. **Total Energy Posterior** - Annual energy with credible intervals
3. **MCMC Trace Plots** - Convergence diagnostics
4. **Cumulative Distribution** - Percentiles and measured value
5. **Forest Plot** - Parameter credible intervals
6. **Monthly Energy Posteriors** - Uncertainty in monthly predictions
7. **Parameter Comparison** - Prior vs Posterior vs True
8. **Error Analysis** - Calibration accuracy
9. **Box Plot Summary** - Total energy statistics

## 💡 Applications

This methodology can be applied to:

- **Building Retrofit Analysis**: Quantify energy savings with uncertainty
- **Model Calibration**: Use utility bills to improve model accuracy
- **Risk Assessment**: Understand prediction uncertainty
- **Policy Analysis**: Inform building codes with probabilistic estimates
- **Research**: Defensible parameter estimation for publications

## 🤝 Contributing

Contributions welcome! Please feel free to:

- Report bugs or issues
- Suggest improvements
- Add new building types
- Extend to EnergyPlus integration
- Add more published priors

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **ASHRAE** for HVAC equipment standards
- **DOE** for Building Energy Codes data
- **NREL** for Window Technology database
- **LBNL** for infiltration research (Sherman & Chan, 2006)
- **US Census Bureau** for occupancy statistics
- **PyMC Development Team** for excellent probabilistic programming tools

## 📧 Contact

For questions or collaboration:

- Open an issue on GitHub
- Email: [your-email@example.com]

---

**Generated using PyMC 5.26.1 with published priors from building science literature**

⭐ If you find this useful, please star this repository!
