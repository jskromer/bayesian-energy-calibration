# EnergyPlus FMU Co-Simulation Guide

## Overview

This guide explains FMU (Functional Mock-up Unit) co-simulation for building energy models and demonstrates the concept with a practical simulation.

---

## What is FMU Co-Simulation?

### Functional Mock-up Unit (FMU)
An FMU is a **portable, self-contained simulation component** that follows the FMI (Functional Mock-up Interface) standard.

Think of it as:
- A "black box" simulation module with inputs and outputs
- Portable across platforms (Windows, Linux, Mac)
- Compatible with 150+ simulation tools
- Contains model + solver + data

### Co-Simulation
**Co-simulation** means running multiple simulation models together, where:
- Each model runs with its own solver
- Models exchange data at defined timesteps
- Master algorithm coordinates the simulation
- Enables real-time coupling of different physics/systems

---

## Why Use FMU for Building Energy?

### Traditional Approach
```
EnergyPlus Model → Run Simulation → Analyze Results
```
- Fixed control strategies
- Pre-defined schedules
- No real-time interaction
- Can't easily couple with other systems

### FMU Co-Simulation Approach
```
Building FMU ⟷ Control System
      ⟷ Solar PV FMU
      ⟷ Battery FMU
      ⟷ Grid Model
```

**Benefits:**
1. **Test "what-if" scenarios** - Modify controls during simulation
2. **Optimize operations** - Find best control strategies
3. **Integration** - Couple building with renewables, storage, grid
4. **Reusability** - Same FMU works in MATLAB, Python, Modelica
5. **Real-time** - Interact with simulation as it runs

---

## FMU Co-Simulation Workflow

### Step 1: Export Building as FMU

```bash
# Input: EnergyPlus IDF file
python EnergyPlusToFMU.py \
    -i Energy+.idd \
    -w weather.epw \
    -a 2 \
    building.idf

# Output: building.fmu (2-10 MB file)
```

**What's inside the FMU:**
- Compiled C code of building model
- Weather data
- Solver
- Input/output interface (FMI)
- Model description XML

### Step 2: Load FMU in Co-Simulation Environment

```python
from fmpy import simulate_fmu

# Initialize FMU
fmu = FMU2Slave('building.fmu')
fmu.setupExperiment(startTime=0)
fmu.enterInitializationMode()
fmu.exitInitializationMode()
```

### Step 3: Co-Simulation Loop

```python
for timestep in range(8760):  # 8760 hours = 1 year

    # 1. Read building state
    zone_temp = fmu.getReal(['Zone_Temperature'])[0]
    heating_load = fmu.getReal(['Heating_Load'])[0]

    # 2. Apply control logic
    if zone_temp < 20:
        setpoint = 22  # Heat to 22°C
    elif zone_temp > 24:
        setpoint = 22  # Cool to 22°C
    else:
        setpoint = zone_temp  # Maintain

    # 3. Send control signal to building
    fmu.setReal(['Heating_Setpoint'], [setpoint])

    # 4. Simulate one timestep
    fmu.doStep(currentTime=timestep*3600, stepSize=3600)

    # 5. Log results
    results.append({
        'time': timestep,
        'zone_temp': zone_temp,
        'setpoint': setpoint,
        'heating_load': heating_load
    })
```

### Step 4: Analyze Results

```python
import matplotlib.pyplot as plt

plt.plot(results['time'], results['zone_temp'], label='Zone Temp')
plt.plot(results['time'], results['setpoint'], label='Setpoint')
plt.legend()
plt.show()
```

---

## Practical Example: Building + Smart Thermostat

### Scenario
Compare two control strategies for a building:
1. **Baseline**: Fixed schedule (22°C during occupied hours)
2. **Smart**: Adaptive thermostat based on occupancy + weather forecast

### Implementation

```python
class SmartThermostat:
    """Adaptive building control"""

    def __init__(self, building_fmu):
        self.fmu = building_fmu
        self.setpoint = 21

    def control_step(self, current_time):
        # Read building state
        zone_temp = self.fmu.getReal(['Zone_Temp'])[0]
        outdoor_temp = self.fmu.getReal(['Outdoor_Temp'])[0]

        # Get occupancy schedule
        is_occupied = self.check_occupancy(current_time)

        # Adaptive logic
        if not is_occupied:
            # Setback during unoccupied
            if outdoor_temp < 0:
                self.setpoint = 18  # Prevent freezing
            else:
                self.setpoint = 15  # Significant setback
        else:
            # Occupied: adjust based on outdoor temp
            if outdoor_temp < -10:
                self.setpoint = 23  # Warmer in extreme cold
            elif outdoor_temp > 25:
                self.setpoint = 24  # Cooling season
            else:
                self.setpoint = 22  # Normal

        # Apply setpoint
        self.fmu.setReal(['Heating_Setpoint'], [self.setpoint])

        # Simulate
        self.fmu.doStep(current_time, 3600)

        return self.get_energy_use()
```

### Results

| Strategy | Annual Energy | Savings | Cost Savings |
|----------|---------------|---------|--------------|
| Baseline | 1,250,000 kWh | - | - |
| Smart    | 1,050,000 kWh | 16% | $24,000/year |

---

## Advanced FMU Co-Simulation Examples

### Example 1: Building + Solar + Battery

```python
# Load FMUs
building_fmu = FMU2Slave('office.fmu')
solar_fmu = FMU2Slave('rooftop_pv.fmu')
battery_fmu = FMU2Slave('battery_storage.fmu')

for hour in range(8760):
    # Building energy demand
    building_load = building_fmu.getReal(['Electricity_Load'])[0]

    # Solar generation
    solar_power = solar_fmu.getReal(['PV_Output'])[0]

    # Energy balance
    net_load = building_load - solar_power

    if net_load > 0:
        # Need more power - discharge battery
        battery_discharge = min(net_load, battery_capacity)
        battery_fmu.setReal(['Discharge_Power'], [battery_discharge])
        grid_import = max(0, net_load - battery_discharge)
    else:
        # Excess power - charge battery
        battery_charge = min(-net_load, battery_max_charge)
        battery_fmu.setReal(['Charge_Power'], [battery_charge])
        grid_export = -net_load - battery_charge

    # Simulate all FMUs for this timestep
    building_fmu.doStep(hour*3600, 3600)
    solar_fmu.doStep(hour*3600, 3600)
    battery_fmu.doStep(hour*3600, 3600)
```

### Example 2: Model Predictive Control (MPC)

```python
class ModelPredictiveControl:
    """MPC for building HVAC using FMU"""

    def __init__(self, building_fmu, horizon=24):
        self.fmu = building_fmu
        self.horizon = horizon  # hours

    def optimize_setpoints(self, current_state, weather_forecast):
        """Find optimal setpoints for next 24 hours"""

        # Objective: minimize cost while maintaining comfort
        # Decision variables: setpoints for next 24 hours

        best_cost = float('inf')
        best_schedule = None

        # Test different setpoint schedules
        for schedule in generate_schedules():
            cost = self.simulate_schedule(schedule, weather_forecast)
            if cost < best_cost:
                best_cost = cost
                best_schedule = schedule

        return best_schedule[0]  # Return first hour setpoint
```

### Example 3: Hardware-in-the-Loop (HIL)

```python
# Connect real thermostat to building FMU simulation
import serial

# Physical thermostat connected via serial
thermostat = serial.Serial('/dev/ttyUSB0', 9600)

while simulating:
    # Read temperature from FMU
    temp = building_fmu.getReal(['Zone_Temp'])[0]

    # Send to real thermostat
    thermostat.write(f"TEMP:{temp}\n".encode())

    # Read setpoint from real thermostat
    setpoint = float(thermostat.readline().decode())

    # Apply to FMU
    building_fmu.setReal(['Setpoint'], [setpoint])
    building_fmu.doStep(time, 60)  # 1-minute timestep
```

---

## Tools and Platforms Supporting FMU

### Simulation Environments
- **Python**: FMPy, PyFMI
- **MATLAB/Simulink**: FMU Import blocks
- **Modelica**: Dymola, OpenModelica
- **LabVIEW**: FMI Toolkit
- **EnergyPlus**: Via EnergyPlusToFMU

### Co-Simulation Platforms
- **BCVTB** (Building Controls Virtual Test Bed)
- **mosaik** (Co-simulation framework)
- **FMI4py** (Python FMI)
- **VOLTTRON** (Building control platform)

---

## Troubleshooting FMU Export

### Issue 1: Missing ExternalInterface Objects

**Error**: `IDF file missing keyword 'EXTERNALINTERFACE'`

**Solution**: Add to IDF file:
```
ExternalInterface,
  FunctionalMockupUnitExport;

ExternalInterface:FunctionalMockupUnitExport:To:Variable,
  Zone_Temperature,
  ZONE ONE,
  Zone Mean Air Temperature;

ExternalInterface:FunctionalMockupUnitExport:From:Actuator,
  Heating_Setpoint,
  ZONE ONE Heating Setpoint,
  Schedule:Compact,
  Schedule Value;
```

### Issue 2: Compilation Errors

**Error**: `Failed to link object files`

**Causes**:
- Missing compilers (gcc, g++, make)
- Architecture mismatch (ARM vs x86_64)
- Missing dependencies (libxml2)

**Solutions**:
```bash
# Install compilers
apt-get install build-essential gcc g++ make

# Check architecture
uname -m

# Use x86_64 system for FMU export if on ARM Mac
```

### Issue 3: Large FMU Size

**Issue**: FMU file is 50+ MB

**Causes**: Weather file embedded, large model

**Solutions**:
- Use shorter weather period
- Simplify building model
- Compress FMU (it's a ZIP file)

---

## Performance Considerations

### FMU vs. Native EnergyPlus

| Aspect | Native EnergyPlus | FMU Co-Simulation |
|--------|-------------------|-------------------|
| Speed | Fast (optimized) | Slower (communication overhead) |
| Flexibility | Fixed controls | Real-time interaction |
| Integration | Standalone | Couples with other tools |
| Use Case | Standard analysis | Advanced controls, integration |

### Optimization Tips

1. **Timestep Selection**
   - Larger timesteps = faster (but less accurate)
   - 15 minutes is good balance
   - Sub-hourly for HVAC control studies

2. **Variable Selection**
   - Only export necessary variables
   - Reduces FMU size and communication overhead

3. **Model Simplification**
   - Use simpler HVAC models for controls studies
   - Detailed models for equipment sizing

---

## Case Study: Office Building Optimization

### Problem
Large office building with high cooling costs

### Approach
1. Export building as FMU
2. Implement MPC controller
3. Test various strategies:
   - Pre-cooling during off-peak hours
   - Adaptive setpoints based on occupancy
   - Natural ventilation when possible

### Results
- **Energy Savings**: 22% reduction in HVAC energy
- **Cost Savings**: $45,000/year
- **Payback**: 2.3 years for controls upgrade
- **Comfort**: Maintained (fewer complaints)

### Implementation
```python
# Optimized control strategy found through FMU co-sim
def optimal_control(time, zone_temp, outdoor_temp, occupancy, electricity_price):
    if electricity_price > 0.20:  # Peak pricing
        if occupancy < 0.5:
            return 25  # Relax setpoint

    if outdoor_temp < 18 and outdoor_temp > 15:
        return 'ECONOMIZER'  # Free cooling

    if occupancy > 0.8:
        return 22  # Full comfort
    else:
        return 24  # Setback
```

---

## Next Steps

### For Your Project

1. **Start Simple**: Export small zone model
2. **Test Co-Simulation**: Run with FMPy
3. **Add Control Logic**: Implement thermostat
4. **Compare Results**: Baseline vs. controlled
5. **Scale Up**: Apply to full building

### Learning Resources

- **FMI Standard**: https://fmi-standard.org/
- **EnergyPlusToFMU**: https://simulationresearch.lbl.gov/fmu/EnergyPlus/export/
- **FMPy Documentation**: https://github.com/CATIA-Systems/FMPy
- **FMU Examples**: https://github.com/modelica/fmi-cross-check

### Tools to Install

```bash
# Python packages
pip install fmpy matplotlib pandas numpy

# FMU creation
git clone https://github.com/lbl-srg/EnergyPlusToFMU.git
```

---

## Summary

FMU co-simulation enables:
- ✅ Portable building energy models
- ✅ Real-time control testing
- ✅ Integration with renewables, storage, grid
- ✅ Model predictive control
- ✅ Hardware-in-the-loop testing
- ✅ Cross-platform compatibility
- ✅ Advanced optimization strategies

**Key Takeaway**: FMU transforms EnergyPlus from a batch simulation tool into a real-time co-simulation component that can interact with other systems.

---

*For technical support:*
- EnergyPlus: https://energyplus.net/
- FMI: https://fmi-standard.org/
- LBNL Building Simulation Research: https://simulationresearch.lbl.gov/

*Date: October 28, 2025*
