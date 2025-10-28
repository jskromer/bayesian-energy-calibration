# EnergyPlusToFMU Installation & New Jersey Project Setup

This guide covers:
1. Installing EnergyPlusToFMU for FMI co-simulation
2. Running the New Jersey fault detection analysis
3. Docker container management

---

## 1. EnergyPlusToFMU Installation

### What is EnergyPlusToFMU?

EnergyPlusToFMU exports EnergyPlus simulations as Functional Mock-up Units (FMUs) for co-simulation with other tools (Modelica, MATLAB/Simulink, etc.).

### Software Requirements

- Python 2.6, 2.7, or 3.x
- C compiler and linker
- C++ compiler and linker
- EnergyPlus installation

### Installation Methods

#### Option A: Install in Docker Container (Recommended)

```bash
# Start Docker container
cd /Users/johnstephenkromer/EnergyPlus-MCP
docker compose up -d energyplus-mcp

# Enter container
docker exec -it energyplus-mcp bash

# Install EnergyPlusToFMU
cd /workspace
git clone https://github.com/lbl-srg/EnergyPlusToFMU.git
cd EnergyPlusToFMU

# Install dependencies
apt-get update
apt-get install -y build-essential gcc g++ make

# Install EnergyPlusToFMU
python setup.py install

# Verify installation
python -c "import energyplus_fmu; print('EnergyPlusToFMU installed successfully!')"
```

#### Option B: Install Locally (macOS)

```bash
# Install Xcode Command Line Tools (for C/C++ compiler)
xcode-select --install

# Clone EnergyPlusToFMU
cd ~/Downloads
git clone https://github.com/lbl-srg/EnergyPlusToFMU.git
cd EnergyPlusToFMU

# Install
python3 setup.py install

# Or install with pip
pip3 install energyplus-fmu
```

### Creating an FMU from EnergyPlus

```bash
# Basic usage
python -m energyplus_fmu.Export \
    -i /path/to/model.idf \
    -w /path/to/weather.epw \
    -a 2  # FMI version (1 or 2)

# This creates: model.fmu
```

---

## 2. New Jersey Project Setup

### Step 1: Start Docker Container

```bash
cd /Users/johnstephenkromer/EnergyPlus-MCP

# Check if Docker is running
docker ps

# If not running, start it
docker compose up -d energyplus-mcp

# Enter container
docker exec -it energyplus-mcp bash
```

### Step 2: Download New Jersey Weather File

Inside the Docker container:

```bash
cd /workspace/energyplus-mcp-server/sample_files

# Newark International Airport (most common)
curl -L -o USA_NJ_Newark.Intl.AP.725020_TMY3.epw \
  'https://energyplus-weather.s3.amazonaws.com/north_and_central_america_wmo_region_4/USA/NJ/USA_NJ_Newark.Intl.AP.725020_TMY3/USA_NJ_Newark.Intl.AP.725020_TMY3.epw'

# OR Atlantic City (coastal)
curl -L -o USA_NJ_Atlantic.City.Intl.AP.724070_TMY3.epw \
  'https://energyplus-weather.s3.amazonaws.com/north_and_central_america_wmo_region_4/USA/NJ/USA_NJ_Atlantic.City.Intl.AP.724070_TMY3/USA_NJ_Atlantic.City.Intl.AP.724070_TMY3.epw'

# Verify download
ls -lh USA_NJ*.epw
```

### Step 3: Customize New Jersey Fault Detection Script

Edit `/workspace/energyplus-mcp-server/new_jersey_fault_detection.py`:

```python
# Line ~390: Update these settings

# Building configuration
building_name = "Your NJ Building Name"
idf_path = "sample_files/YourBuilding.idf"  # Your IDF file

# New Jersey weather
weather_file = "sample_files/USA_NJ_Newark.Intl.AP.725020_TMY3.epw"

# Observed energy from utility bills (kWh/year)
observed_energy_kwh = 850000  # Replace with your actual annual consumption

# Number of training simulations (8-10 recommended)
n_training_simulations = 8
```

### Step 4: Run New Jersey Fault Detection

```bash
cd /workspace/energyplus-mcp-server

# Run the analysis
uv run new_jersey_fault_detection.py

# This will:
# 1. Run 8 simulations across infiltration parameter space
# 2. Build Gaussian Process surrogate model
# 3. Perform Bayesian fault detection
# 4. Generate counterfactual savings analysis
# 5. Create visualizations: nj_fault_analysis.png
# 6. Save results: nj_fault_results.csv
```

### Step 5: Copy Results to Local Machine

From your Mac terminal (outside Docker):

```bash
cd /Users/johnstephenkromer/EnergyPlus-MCP/energyplus-mcp-server

# Copy visualization
docker cp energyplus-mcp:/workspace/energyplus-mcp-server/nj_fault_analysis.png .

# Copy CSV results
docker cp energyplus-mcp:/workspace/energyplus-mcp-server/nj_fault_results.csv .

# Open results
open nj_fault_analysis.png
open nj_fault_results.csv
```

---

## 3. New Jersey Utility Rate Information

### Electricity Rates (Commercial)

- **Newark/North NJ:** ~$0.15-0.17/kWh
- **Atlantic City/South NJ:** ~$0.14-0.16/kWh
- **Peak demand charges:** $10-20/kW

### Natural Gas Rates (Commercial)

- **North NJ:** ~$1.20-1.40/therm
- **South NJ:** ~$1.10-1.30/therm

### Utility Companies

- **PSE&G** (Public Service Electric & Gas) - North/Central NJ
- **Jersey Central Power & Light (JCP&L)** - Central/West NJ
- **Atlantic City Electric** - South NJ

### Update Script with Actual Rates

In `new_jersey_fault_detection.py` line ~70:

```python
# Update with your actual utility rates
self.nj_electricity_rate = 0.16  # $/kWh (from your utility bill)
self.nj_gas_rate = 1.25  # $/therm
```

---

## 4. Docker Container Management

### Start Container

```bash
cd /Users/johnstephenkromer/EnergyPlus-MCP
docker compose up -d energyplus-mcp
```

### Stop Container

```bash
docker compose stop energyplus-mcp
```

### Restart Container

```bash
docker compose restart energyplus-mcp
```

### Check Container Status

```bash
docker ps -a | grep energyplus
```

### View Container Logs

```bash
docker logs energyplus-mcp
```

### Remove Container (if needed)

```bash
docker compose down
docker compose up -d  # Recreate
```

---

## 5. Quick Start Commands

### One-Command Setup and Run

```bash
# From Mac terminal
cd /Users/johnstephenkromer/EnergyPlus-MCP

# Start container and run NJ analysis
docker compose up -d energyplus-mcp && \
docker exec energyplus-mcp bash -c "
  cd /workspace/energyplus-mcp-server && \
  curl -L -o sample_files/USA_NJ_Newark.Intl.AP.725020_TMY3.epw \
    'https://energyplus-weather.s3.amazonaws.com/north_and_central_america_wmo_region_4/USA/NJ/USA_NJ_Newark.Intl.AP.725020_TMY3/USA_NJ_Newark.Intl.AP.725020_TMY3.epw' && \
  uv run new_jersey_fault_detection.py
"

# Copy results back
docker cp energyplus-mcp:/workspace/energyplus-mcp-server/nj_fault_analysis.png energyplus-mcp-server/
docker cp energyplus-mcp:/workspace/energyplus-mcp-server/nj_fault_results.csv energyplus-mcp-server/
```

---

## 6. Troubleshooting

### Docker Not Running

```bash
# Check if Docker Desktop is running
open -a Docker

# Wait for Docker to start, then verify
docker ps
```

### Weather File Download Failed

If the S3 link doesn't work, download manually from:
https://energyplus.net/weather

Search for "New Jersey" and download TMY3 format.

### Python Dependencies Missing

```bash
docker exec -it energyplus-mcp bash
cd /workspace/energyplus-mcp-server
uv pip install arviz matplotlib scikit-learn scipy
```

### Visualization Not Generated

Check if matplotlib backend is configured:

```bash
docker exec energyplus-mcp bash -c "
  export MPLBACKEND=Agg
  cd /workspace/energyplus-mcp-server && uv run new_jersey_fault_detection.py
"
```

---

## 7. Expected Output

After running the NJ analysis, you should see:

### Console Output:
```
================================================================================
NEW JERSEY BUILDING - FAULT DETECTION ANALYSIS
================================================================================

🏢 Project Configuration:
   Building: NJ Medium Office
   Location: New Jersey
   Observed Energy: 750,000 kWh/year
   Training Simulations: 8

[8 simulations run...]

✅ GP Surrogate Model Built
   Training points: 8
   Energy range: 726,564 - 771,312 kWh/year

🎯 Bayesian Fault Detection
   Observed energy: 750,000 kWh/year
   ✅ Generated 1000 posterior samples

💡 Counterfactual Analysis: Fix the Leak
   Energy Savings:
      Mean:    9,337 kWh/year
      95% CI: [-874, 19,320] kWh/year

   Cost Savings (@ $0.15/kWh):
      Mean:   $1,401/year
      95% CI: [$-131, $2,898]/year

💡 RECOMMENDATION:
   ⚠️  MAJOR LEAK DETECTED (infiltration 32% above baseline)
   💰 Annual Savings Potential: $1,401
   ✅ RECOMMEND: Immediate air sealing / duct sealing retrofit
```

### Files Generated:
- `nj_fault_analysis.png` - 6-panel visualization
- `nj_fault_results.csv` - 1,000 posterior samples with predictions

---

## 8. Next Steps

1. **Customize for your actual building:**
   - Replace IDF file with your NJ building model
   - Update observed_energy_kwh from utility bills
   - Adjust NJ utility rates

2. **Run sensitivity analysis:**
   - Test different parameters (R-value, setpoints)
   - Compare multiple fault scenarios

3. **Generate report:**
   - Use results for M&V documentation
   - Calculate simple payback period
   - Prepare retrofit proposal

---

## 9. Advanced: FMU Export for Co-Simulation

If you want to export your NJ building as an FMU for co-simulation:

```bash
# In Docker container
cd /workspace/energyplus-mcp-server

# Export baseline model
python -m energyplus_fmu.Export \
    -i sample_files/MediumOffice-90.1-2004.idf \
    -w sample_files/USA_NJ_Newark.Intl.AP.725020_TMY3.epw \
    -a 2

# Export faulty model (with leak)
python -m energyplus_fmu.Export \
    -i sample_files/nj_fault_1.30.idf \
    -w sample_files/USA_NJ_Newark.Intl.AP.725020_TMY3.epw \
    -a 2

# FMUs can be used in:
# - MATLAB/Simulink
# - Dymola/Modelica
# - Python (FMPy library)
# - Other FMI-compliant tools
```

---

## Contact & Support

For issues:
- EnergyPlus: https://energyplus.net/
- EnergyPlusToFMU: https://github.com/lbl-srg/EnergyPlusToFMU
- MCP Server: https://github.com/anthropics/claude-code

Good luck with your New Jersey project!
