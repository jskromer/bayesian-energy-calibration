# Successful EnergyPlus Annual Simulation

## Summary

✅ **Successfully completed a FULL YEAR building energy simulation!**

After troubleshooting the initial design-day-only results, we now have real annual energy data from an EnergyPlus simulation.

---

## What Was Run

### Building Model
- **Type**: Large Office Building (Reference Building)
- **Standard**: ASHRAE 90.1-2004
- **Location**: Chicago, IL
- **Size**: ~46,320 m² (498,588 ft²)
- **IDF File**: RefBldgLargeOfficeNew2004_Chicago.idf

### Simulation Details
- **Period**: Full calendar year (8760 hours)
- **Weather**: Chicago O'Hare International Airport TMY3 data
- **Timestep**: Hourly
- **Simulation Flag**: `--annual` (forced annual simulation, not design days)

---

## Energy Results

### Annual Site Energy Consumption

**Total Site Energy: 26,113.24 GJ/year**

This equals:
- **7,253,678 kWh/year** (7.25 GWh/year)
- **563.75 MJ/m²/year** (energy use intensity)

### Building Energy Performance
- Energy Use Intensity (EUI): 563.75 MJ/m² = **156.6 kWh/m²/year**
- For comparison, this is typical for a large office building in a cold climate
- ASHRAE 90.1-2004 baseline performance

### Estimated Annual Energy Cost
Assuming typical commercial rates:
- Electricity @ $0.12/kWh: ~$870,000/year
- This is for a 12-story, ~500,000 ft² office building in Chicago

---

## Key Lesson Learned

### The Problem: Zero Results Initially
The initial simulations showed all zeros in the energy tables because:
1. The IDF files were configured for **design day simulations only**
2. Design days are 2-day peak load calculations (winter/summer extreme days)
3. Annual energy tables require a full year simulation
4. SimulationControl object had "Run Simulation for Weather File Run Periods = No"

### The Solution: `--annual` Flag
Using the `--annual` flag in EnergyPlus forces annual simulation:
```bash
energyplus --annual -w weather.epw -d output/ model.idf
```

This overrides the IDF's SimulationControl settings and runs the full year.

---

## Files Generated

### Results Location (in Docker container)
```
/workspace/energyplus-mcp-server/annual_large_office/
```

### Key Output Files
- **eplustbl.htm** (459 KB) - Summary tables with annual energy breakdown
  - Site and Source Energy
  - End Use Energy Consumption
  - Monthly energy profiles
  - Peak demand
  - Component loads

### Copied to Local Machine
```
energyplus-mcp-server/annual_large_office_results.htm
```

**This file is now open in your browser!**

---

## How to View Results

The HTML table file contains comprehensive results:

1. **Site and Source Energy** - Total annual consumption
2. **End Uses** - Breakdown by:
   - Heating
   - Cooling
   - Interior Lighting
   - Interior Equipment
   - Fans
   - Pumps
   - Water Systems
3. **Monthly Profiles** - Energy use by month
4. **Peak Demand** - Maximum power draw
5. **Comfort Summary** - Zone conditions
6. **HVAC Sizing** - Equipment capacities

---

## Scripts Created

### Working Annual Simulation Script
[run_annual_working.py](energyplus-mcp-server/run_annual_working.py)
- Uses known-good example IDF from EnergyPlus installation
- Forces annual simulation with `--annual` flag
- Parses and displays results
- Can be reused as template

### Usage
```bash
# In Docker container
cd /workspace/energyplus-mcp-server
python run_annual_working.py

# Copy results to local machine
docker cp energyplus-mcp:/workspace/energyplus-mcp-server/annual_large_office/eplustbl.htm ./results.htm
open results.htm
```

---

## Next Steps: Before/After Comparison

Now that we have a working annual simulation, you can:

### 1. Create an Improved Building Version
Modify the IDF to test energy conservation measures:
- Better insulation (increase R-values in Materials)
- More efficient windows (lower U-factor)
- Higher efficiency HVAC (improve COP)
- LED lighting (reduce lighting power density)
- Add economizer controls
- Improved air sealing (reduce infiltration)

### 2. Run Comparison
```python
# Run baseline (already done)
baseline_energy = 26113.24  # GJ/year

# Run improved version
# improved_energy = ???

# Calculate savings
savings = baseline_energy - improved_energy
savings_pct = (savings / baseline_energy) * 100
```

### 3. FMU Export (Future)
Once you have two scenarios working, export them as FMUs:
```bash
python -m energyplus_fmu.Export \
    -i RefBldgLargeOfficeNew2004_Chicago.idf \
    -w USA_IL_Chicago-OHare.Intl.AP.725300_TMY3.epw \
    -a 2

# This creates: RefBldgLargeOfficeNew2004_Chicago.fmu
```

Then co-simulate with:
- Control systems
- Renewable energy
- Energy storage
- Occupant behavior models
- Grid interaction models

---

## Technical Details

### Why This Works
1. **Used example IDF**: EnergyPlus installation includes tested example files
2. **Matched weather file**: Chicago IDF with Chicago weather
3. **Annual flag**: Forced full-year simulation
4. **Complete model**: All HVAC, lighting, equipment, and loads defined

### Command Used
```bash
energyplus \
    --annual \
    -w /app/software/EnergyPlusV25-1-0/WeatherData/USA_IL_Chicago-OHare.Intl.AP.725300_TMY3.epw \
    -d /workspace/energyplus-mcp-server/annual_large_office \
    /app/software/EnergyPlusV25-1-0/ExampleFiles/RefBldgLargeOfficeNew2004_Chicago.idf
```

### Simulation Time
- Runtime: ~2 minutes
- Timesteps: 8760 (one per hour for full year)
- Output file size: 459 KB (HTML table)

---

## Comparison to Design Day Simulation

| Aspect | Design Day | Annual |
|--------|------------|--------|
| **Duration** | 2 days | 365 days |
| **Purpose** | Equipment sizing | Energy consumption |
| **Timesteps** | 48 hours | 8,760 hours |
| **Energy Results** | Peak loads (W) | Annual totals (kWh) |
| **Use Case** | HVAC design | Energy analysis, ROI |

---

## References

- **EnergyPlus Documentation**: https://energyplus.net/documentation
- **Reference Buildings**: https://www.energy.gov/eere/buildings/commercial-reference-buildings
- **Weather Data**: https://energyplus.net/weather
- **Building Energy Codes**: https://www.energycodes.gov/

---

## Summary

🎉 **Success!** You now have:
- A working annual building energy simulation
- Real energy consumption data (26,113 GJ/year = 7.25 million kWh/year)
- Understanding of design day vs. annual simulation
- Template script for future simulations
- Foundation for before/after comparisons
- Path to FMU co-simulation

The HTML results file is open in your browser showing comprehensive annual energy performance data!

---

*Generated: October 28, 2025*
*Simulation: RefBldgLargeOfficeNew2004_Chicago - Full Annual Run*
*Total Site Energy: 26,113.24 GJ/year*
