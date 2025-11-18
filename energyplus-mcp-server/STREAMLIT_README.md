# Interactive Bayesian Calibration Streamlit App

This Streamlit app allows users to interactively adjust prior distributions and rerun the Bayesian building energy calibration in real-time.

## Features

- **Interactive Prior Controls**: Sliders for all 8 parameter priors
- **Real-time Calibration**: Run MCMC sampling with custom settings
- **Live Visualizations**: Posterior distributions, trace plots, convergence diagnostics
- **Download Results**: Export summary statistics and prior specifications

## Local Installation & Usage

1. **Install dependencies**:
   ```bash
   pip install -r requirements-streamlit.txt
   ```

2. **Run the app**:
   ```bash
   streamlit run streamlit_app.py
   ```

3. **Open in browser**:
   The app will automatically open at `http://localhost:8501`

## How to Use

1. **Adjust Priors** (Sidebar):
   - Wall Insulation R-Value
   - Roof Insulation R-Value
   - Window U-Factor
   - Infiltration Rate
   - Heating Efficiency
   - Cooling COP
   - Lighting Power Density
   - Occupant Count

2. **Configure MCMC Settings**:
   - Samples per chain (default: 1000)
   - Tuning samples (default: 500)
   - Number of chains (default: 2)

3. **Run Calibration**:
   - Click the "🚀 Run Calibration" button
   - Wait 1-2 minutes for MCMC sampling to complete

4. **Explore Results**:
   - **Posterior Distributions**: See how data updated your priors
   - **Convergence Diagnostics**: Check R-hat, ESS, and divergences
   - **Summary Statistics**: View parameter estimates with credible intervals
   - **Download Results**: Export CSV and JSON files

## Deploy to Streamlit Cloud

1. **Push to GitHub**:
   ```bash
   git add streamlit_app.py requirements-streamlit.txt
   git commit -m "Add interactive Streamlit calibration app"
   git push
   ```

2. **Deploy to Streamlit Cloud**:
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Connect your GitHub repository
   - Select `streamlit_app.py` as the main file
   - Deploy!

3. **Your app will be live at**:
   ```
   https://share.streamlit.io/[username]/[repo-name]/streamlit_app.py
   ```

## Deploy to Other Platforms

### Hugging Face Spaces

1. Create a new Space on [huggingface.co/spaces](https://huggingface.co/spaces)
2. Choose "Streamlit" as the SDK
3. Upload `streamlit_app.py` and `requirements-streamlit.txt`
4. Your app will be live!

### Render

1. Create a new Web Service on [render.com](https://render.com)
2. Connect your GitHub repository
3. Set build command: `pip install -r requirements-streamlit.txt`
4. Set start command: `streamlit run streamlit_app.py --server.port=$PORT --server.address=0.0.0.0`

## Performance Notes

- **Fast Mode**: Use 500 samples, 1 chain (~30 seconds)
- **Standard Mode**: Use 1000 samples, 2 chains (~1-2 minutes)
- **High Quality**: Use 2000 samples, 4 chains (~3-5 minutes)

## Architecture

The app consists of:

1. **Sidebar**: Interactive controls for all prior parameters
2. **Main Panel**: Measured data display and results
3. **Calibration Engine**: PyMC Bayesian inference model
4. **Visualization**: ArviZ plots and custom matplotlib charts
5. **Export**: CSV and JSON download functionality

## Building Energy Model

The simplified physics model includes:

- **Heat Transfer**: Through walls, roof, and windows (using U-values)
- **Infiltration**: Air leakage losses
- **HVAC**: Heating efficiency (AFUE) and cooling COP
- **Internal Gains**: Lighting power density and occupant heat
- **Climate**: Heating/Cooling degree days for New York

## References

All default priors are based on published building science literature:

- **ASHRAE**: HVAC equipment standards and building fundamentals
- **DOE**: Building Energy Codes Program (2015-2018 stock)
- **NREL**: Residential Building Stock Assessment and Window Database
- **LBNL**: Sherman & Chan (2006) - Infiltration research
- **US Census Bureau**: Household occupancy statistics (2020)

## Troubleshooting

**Slow performance?**
- Reduce number of samples or chains
- Use fewer tuning samples

**Convergence issues (R-hat > 1.01)?**
- Increase tuning samples
- Check if priors are too narrow
- Review trace plots for issues

**Divergences?**
- Widen prior distributions
- Increase tuning samples
- Check for parameter identifiability

## Future Enhancements

Potential additions:
- [ ] Upload custom measured data (CSV)
- [ ] Select different climate zones
- [ ] Compare multiple calibration runs
- [ ] Export full posterior traces
- [ ] Integration with EnergyPlus for detailed simulation
- [ ] Retrofit scenario analysis

---

**Built with**: PyMC 5.26.1, ArviZ 0.22.0, Streamlit 1.28+
