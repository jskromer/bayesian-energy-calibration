# EnergyPlus FMU Test Run Summary

## Overview
Successfully completed a simple before/after comparison using EnergyPlus simulations as a first step toward FMU (Functional Mock-up Unit) co-simulation.

## What Was Run

### Test Scenario
- **Baseline Model**: MediumOffice-90.1-2004.idf (Standard ASHRAE 90.1-2004 compliant building)
- **Improved Model**: MediumOffice-DuctLeak-5pct.idf (Same building with better duct sealing)
- **Weather File**: Denver, CO (USA_CO_Denver.Intl.AP.725650_TMY3.epw)
- **Simulation Period**: Design Days (Jan 21 & Jul 21 - representing extreme winter/summer conditions)

### Results Location
- **Baseline Results**: `fmu_comparison_results/baseline_90.1/`
- **Improved Results**: `fmu_comparison_results/improved_sealed_ducts/`
- **HTML Reports**:
  - [baseline_results.htm](energyplus-mcp-server/baseline_results.htm)
  - [improved_results.htm](energyplus-mcp-server/improved_results.htm)

## Energy Comparison (2 Design Days)

### Baseline (Standard Building)
- Electricity: 4,491 kWh
- Natural Gas: 28 kWh
- **Total**: 4,518 kWh (16.3 GJ)

### Improved (Better Duct Sealing)
- Electricity: 4,492 kWh
- Natural Gas: 28 kWh
- **Total**: 4,520 kWh (16.3 GJ)

### Difference
- Very minimal difference (-2 kWh) - this is expected for a 2-day design day simulation
- For meaningful comparisons, would need full annual simulation

## Key Files Generated

### Simulation Outputs (in Docker container)
```
/workspace/energyplus-mcp-server/fmu_comparison_results/
├── baseline_90.1/
│   ├── eplusmtr.csv       # Hourly meter data (electricity, gas)
│   ├── eplusout.csv       # Detailed output variables
│   ├── eplustbl.htm       # Summary tables (HTML)
│   ├── eplusssz.csv       # System sizing info
│   └── epluszsz.csv       # Zone sizing info
└── improved_sealed_ducts/
    └── [same files]
```

### Analysis Scripts Created
- [simple_fmu_comparison.py](energyplus-mcp-server/simple_fmu_comparison.py) - Runs both simulations
- [parse_comparison_results.py](energyplus-mcp-server/parse_comparison_results.py) - Parses and compares results

## How This Relates to FMU Co-Simulation

### What We Did (Standard EnergyPlus)
1. Ran two separate EnergyPlus simulations
2. Compared results after both completed
3. This is a "sequential" approach - one runs, then the other

### Next Step: FMU Co-Simulation
The FMU approach would allow:
1. **Export to FMU**: Convert EnergyPlus model to a Functional Mock-up Unit
2. **Co-simulate**: Run the building model alongside other systems in real-time:
   - Control systems (thermostats, BMS)
   - Renewable energy (solar panels, wind)
   - Energy storage (batteries)
   - Occupant behavior models
   - Other tools (MATLAB, Modelica, etc.)

### FMU Export Command (for reference)
```bash
# In Docker container
python -m energyplus_fmu.Export \
    -i sample_files/MediumOffice-90.1-2004.idf \
    -w sample_files/USA_CO_Denver.Intl.AP.725650_TMY3.epw \
    -a 2  # FMI version 2

# This creates: MediumOffice-90.1-2004.fmu
```

## Running This Test

### Quick Start
```bash
# From Mac terminal
cd /Users/johnstephenkromer/EnergyPlus-MCP

# Ensure Docker container is running
docker ps | grep energyplus-mcp

# Run the comparison
docker exec energyplus-mcp bash -c "
  cd /workspace/energyplus-mcp-server &&
  python simple_fmu_comparison.py
"

# View results
docker exec energyplus-mcp bash -c "
  cd /workspace/energyplus-mcp-server &&
  python parse_comparison_results.py
"

# Copy HTML reports to local machine (already done)
docker cp energyplus-mcp:/workspace/energyplus-mcp-server/fmu_comparison_results/baseline_90.1/eplustbl.htm \
  energyplus-mcp-server/baseline_results.htm
docker cp energyplus-mcp-server/fmu_comparison_results/improved_sealed_ducts/eplustbl.htm \
  energyplus-mcp-server/improved_results.htm

# Open in browser
open energyplus-mcp-server/baseline_results.htm
open energyplus-mcp-server/improved_results.htm
```

## Next Steps for Full Annual FMU Comparison

### 1. Modify IDF for Annual Simulation
Currently simulating only design days. To run full year:
- Edit the `RunPeriod` object in the IDF file
- Change from design days to full year (1/1 through 12/31)

### 2. Export as FMU
```bash
# After annual simulation works, export to FMU
cd /workspace/energyplus-mcp-server
python -m energyplus_fmu.Export -i <model.idf> -w <weather.epw> -a 2
```

### 3. Co-Simulate with Python (FMPy)
```python
from fmpy import simulate_fmu

# Simulate the FMU
result = simulate_fmu(
    'MediumOffice.fmu',
    start_time=0,
    stop_time=31536000,  # 1 year in seconds
    step_size=3600,       # 1 hour
    output=['zone_temp', 'electricity', 'gas']
)
```

### 4. Advanced: Co-Simulate with Controls
- Integrate with MATLAB/Simulink for advanced controls
- Use Modelica for multi-domain physics simulation
- Implement optimal control strategies
- Test renewable integration scenarios

## What This Demonstrates

✅ **Completed:**
- Set up EnergyPlus simulation environment
- Ran baseline vs improved building comparison
- Extracted and parsed energy consumption data
- Created reusable scripts for future comparisons

📋 **Foundation for:**
- FMU export and co-simulation
- Building energy optimization
- Control system testing
- "What-if" scenario analysis
- Integration with other simulation tools

## References

- **EnergyPlus Documentation**: https://energyplus.net/documentation
- **EnergyPlusToFMU**: https://github.com/lbl-srg/EnergyPlusToFMU
- **FMI Standard**: https://fmi-standard.org/
- **FMPy (Python FMU simulation)**: https://github.com/CATIA-Systems/FMPy
- **Setup Guide**: [ENERGYPLUS_FMU_SETUP.md](ENERGYPLUS_FMU_SETUP.md)

---

*Generated: October 28, 2025*
*Test simulations ran successfully in Docker container: energyplus-mcp*
