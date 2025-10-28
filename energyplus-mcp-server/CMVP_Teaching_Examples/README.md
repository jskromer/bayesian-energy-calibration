# CMVP Teaching Examples

This folder contains two complete CMVP teaching examples with EnergyPlus simulation demonstrations.

---

## Contents

### 📚 Example 1: Interactive Effects from Lighting Retrofit

**Files**:
- `CMVP_Interactive_Effects_Teaching_Example.md` - Complete teaching document
- `CMVP_Interactive_Effects_Comparison.csv` - Monthly comparison data

**Scenario**: 50% LED lighting retrofit in medium office building

**Demonstrates**:
- ✓ Interactive effects between ECMs and HVAC systems
- ✓ Cooling energy reduction (beneficial interaction)
- ✓ Heating energy penalty (adverse interaction)
- ✓ Seasonal variation in interactive effects (0.1% to 35.5%)
- ✓ Climate zone dependency
- ✓ Cost vs. energy impact differences

**Key Results**:
- Electricity savings: 43,557 kWh/year (10.8%)
- Heating penalty: 3,742 kWh/year (10.8% increase in gas)
- Net site energy savings: 39,815 kWh/year (9.1%)
- Interactive effects ratio: 8.6%

**CMVP Topics**:
- IPMVP Option D (Calibrated Simulation)
- Interactive effects quantification
- Option C regression considerations
- Seasonal analysis

---

### 📚 Example 2: Non-Routine Adjustment in Year 2

**Files**:
- `cmvp_nonroutine_demo.py` - Simulation script (runnable)
- `cmvp_nonroutine_analysis.py` - Analysis script (runnable)
- `CMVP_NonRoutine_Adjustment_Teaching_Example.md` - Complete teaching document
- `CMVP_NonRoutine_Adjustment_Analysis.csv` - Monthly breakdown
- `CMVP_NonRoutine_Summary.json` - Summary data

**Scenario**: Server room added July 1 in Year 2 (mid-year non-routine event)

**Demonstrates**:
- ✓ IPMVP Section 4.5: Non-routine adjustments
- ✓ When to apply adjustments (decision tree)
- ✓ Quantification methods
- ✓ Impact on savings calculations
- ✓ Documentation requirements
- ✓ M&V reporting format

**Event Details**:
- Date: July 1, Year 2
- Load: +40 W/m² equipment (server room)
- Area: 550 m² (Core_mid zone)
- Impact: ~96,000 kWh for 6 months
- Adjustment: Exclude from routine operations

**CMVP Topics**:
- IPMVP Option D (Calibrated Simulation)
- Non-routine vs. routine changes
- Adjustment formulas
- Option C vs. Option D comparison
- Uncertainty assessment

---

## How to Use These Examples

### For Teaching:

1. **Lecture Material**: Use the markdown documents as handouts or presentation slides
2. **Class Discussion**: Use the scenario descriptions and discussion questions
3. **Exercises**: Have students calculate adjustments using the provided data
4. **Case Studies**: Compare and contrast the two examples

### For Practice:

**Interactive Effects Example**:
- Review the monthly breakdown to see seasonal patterns
- Calculate interactive effects ratio for different climates
- Discuss when effects would be larger/smaller

**Non-Routine Adjustment Example**:
1. Run the simulation: `python cmvp_nonroutine_demo.py`
2. Analyze results: `python cmvp_nonroutine_analysis.py`
3. Review the adjustment calculations
4. Modify the scenario (change date, load, etc.)

---

## Learning Objectives

After studying these examples, CMVP candidates should be able to:

### Interactive Effects:
- ✓ Define interactive effects and explain why they occur
- ✓ Identify ECMs that will have significant interactive effects
- ✓ Quantify interactive effects using simulation or calculation
- ✓ Explain how climate zone affects magnitude of interactions
- ✓ Distinguish between energy and cost impacts
- ✓ Incorporate interactive effects into savings estimates

### Non-Routine Adjustments:
- ✓ Define non-routine adjustments per IPMVP
- ✓ Identify when adjustments are required vs. optional
- ✓ Calculate non-routine adjustment using multiple methods
- ✓ Apply adjustments correctly to baseline and reporting periods
- ✓ Document non-routine events for M&V reports
- ✓ Explain impact on savings calculations and uncertainty

---

## Technical Details

### Building Model:
- **Type**: ASHRAE 90.1 Medium Office
- **Size**: 4,982 m² (53,628 ft²)
- **Location**: San Francisco, CA (Climate Zone 3C)
- **HVAC**: 3 Packaged Rooftop VAV units with DX cooling
- **Zones**: 15 conditioned + 3 plenums

### Simulation Software:
- **EnergyPlus**: Version 25.1.0
- **Weather**: TMY3 San Francisco
- **Timestep**: Hourly
- **Period**: Annual (8,760 hours)

### M&V Approach:
- **Method**: IPMVP Option D (Calibrated Simulation)
- **Tools**: EnergyPlus MCP Server
- **Analysis**: Python scripts with pandas

---

## Key IPMVP References

### Interactive Effects:
- IPMVP Volume I, Section 4.4: "Interactive Effects"
- ASHRAE Guideline 14, Section 5.2.3: "Interactions Between Systems"
- FEMP M&V Guidelines, Appendix A: "Interactive Effects"

### Non-Routine Adjustments:
- IPMVP Volume I, Section 4.5: "Routine and Non-Routine Adjustments"
- IPMVP Volume I, Section 8.3: "Adjusting Baseline for Changes"
- EVO 10200: "Uncertainty Assessment for IPMVP"

---

## Discussion Questions

### Interactive Effects:

1. Why is the interactive effects ratio highest in January (35.5%) and lowest in July (0.1%)?

2. How would interactive effects differ if this building were in:
   - Chicago (cold climate)?
   - Phoenix (hot-dry climate)?
   - Miami (hot-humid climate)?

3. If you only metered the lighting circuits, what would you miss?

4. How do interactive effects impact simple payback calculations?

5. When is it acceptable to ignore interactive effects in M&V?

### Non-Routine Adjustments:

1. A factory adds a second shift (4pm-12am) starting in March. Is this non-routine?

2. How would you handle a 2-week annual maintenance shutdown?

3. Server room added AND cooling ECM implemented. How to separate effects?

4. What if the non-routine adjustment uncertainty is ±15%?

5. When should you use measurement vs. simulation for adjustments?

---

## Files Summary

| File | Type | Purpose | Size |
|------|------|---------|------|
| `CMVP_Interactive_Effects_Teaching_Example.md` | Document | Complete teaching guide | ~15 KB |
| `CMVP_Interactive_Effects_Comparison.csv` | Data | Monthly comparison | ~1 KB |
| `CMVP_NonRoutine_Adjustment_Teaching_Example.md` | Document | Complete teaching guide | ~22 KB |
| `cmvp_nonroutine_demo.py` | Script | Run simulations | ~7 KB |
| `cmvp_nonroutine_analysis.py` | Script | Analyze results | ~5 KB |
| `CMVP_NonRoutine_Adjustment_Analysis.csv` | Data | Monthly breakdown | ~1 KB |
| `CMVP_NonRoutine_Summary.json` | Data | Summary stats | ~500 B |

---

## Prerequisites

To run the Python scripts:

```bash
# Ensure you're in the energyplus-mcp-server directory
cd /Users/johnstephenkromer/EnergyPlus-MCP/energyplus-mcp-server

# Install dependencies (if not already installed)
pip install pandas eppy matplotlib

# Run non-routine demo
python CMVP_Teaching_Examples/cmvp_nonroutine_demo.py

# Analyze results
python CMVP_Teaching_Examples/cmvp_nonroutine_analysis.py
```

---

## Related Resources

### In Main Repository:
- `SETUP_COMPLETE.md` - EnergyPlus MCP setup guide
- `API_USAGE_GUIDE.md` - How to use the EnergyPlus API
- `LOCAL_API_SETUP.md` - Running simulations locally

### Sample Models:
- `sample_files/ASHRAE901_OfficeMedium.idf` - Baseline model
- `sample_files/ASHRAE901_OfficeMedium_LED_Retrofit.idf` - With lighting retrofit
- `sample_files/ASHRAE901_OfficeMedium_Year2_ServerRoom.idf` - With server room

---

## Credits

**Generated Using**:
- EnergyPlus v25.1.0
- EnergyPlus MCP Server v0.1.0
- Model Context Protocol

**For**:
- CMVP (Certified Measurement & Verification Professional) Training
- IPMVP Protocol Education
- Building Energy M&V Courses

---

## Questions or Feedback?

These examples are designed for educational use in CMVP training courses. If you have suggestions for improvements or additional scenarios, please provide feedback.

---

**Last Updated**: October 23, 2025
**Examples**: 2 complete CMVP case studies
**Status**: Ready for classroom use
