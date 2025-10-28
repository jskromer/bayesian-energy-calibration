# CMVP Non-Routine Adjustment Teaching Example
## Server Room Addition in Year 2

### Executive Summary

This teaching example demonstrates how to handle **non-routine adjustments** in Measurement & Verification (M&V) according to IPMVP guidelines. The case study examines a server room addition mid-way through Year 2 and shows how to properly adjust energy consumption to isolate routine operations from non-routine events.

---

## Scenario Overview

**Building**: Medium Office (4,982 m², 53,628 ft²)
**Location**: San Francisco, CA (Climate Zone 3C)
**HVAC**: Packaged Rooftop VAV with DX Cooling
**M&V Period**: 2 years (Year 1 baseline, Year 2 reporting)

### Timeline

| Period | Description | Equipment Density | Status |
|--------|-------------|-------------------|--------|
| **Year 1** (Jan-Dec) | Normal office operations | 10.76 W/m² | Baseline Period |
| **Year 2** (Jan-Jun) | Normal office operations | 10.76 W/m² | Routine Operations |
| **Year 2** (Jul 1) | **Server room added** | Core_mid: 50.76 W/m² | **Non-Routine Event** |
| **Year 2** (Jul-Dec) | Server room operating | Mixed (10.76 + server loads) | Non-Routine Period |

---

## Non-Routine Event Details

### What Changed?

**Event**: IT department converted 550 m² of Core_mid zone into a server room

**Specifications**:
- **Date**: July 1, Year 2 (mid-year installation)
- **Area**: Core_mid zone (~550 m² / 5,920 ft²)
- **Equipment Load**: +40 W/m² (4 kW/m² increase)
- **New Total**: 50.76 W/m² (was 10.76 W/m²)
- **Increase**: 372% in affected zone
- **Operation**: 24/7 continuous operation
- **Expected Annual Impact**: ~192,000 kWh/year if operated full year

### Why Is This Non-Routine?

Per IPMVP definition, a **non-routine adjustment** is needed when:

✓ **One-time occurrence**: Server room addition is not a recurring event
✓ **Not representative**: Doesn't reflect normal building operations
✓ **Material impact**: Large enough to affect M&V results
✓ **Outside M&V scope**: Not part of the ECM being measured
✓ **Documented**: Clear start date and impact quantifiable

---

## IPMVP Guidelines for Non-Routine Adjustments

### Section 4.5: Non-Routine Adjustments

From IPMVP Volume I:

> *"Non-routine adjustments account for changes in energy use that are not routine consequences of the facility operation...These adjustments must be applied to both baseline and reporting period energy data."*

### Examples of Non-Routine Events

**Typically Require Adjustment**:
- ✓ Addition/removal of major equipment (server room, production line)
- ✓ Change in operating hours outside normal business variation
- ✓ Building additions or demolitions
- ✓ Occupancy changes > 20% from baseline
- ✓ One-time special events

**Typically DO NOT Require Adjustment** (routine variations):
- ✗ Normal weather variations (handled by weather normalization)
- ✗ Seasonal occupancy changes within historical range
- ✗ Normal equipment cycling and maintenance
- ✗ Day-to-day operational variations

---

## M&V Analysis Approach

### Step 1: Quantify the Non-Routine Impact

**Method**: Simulation modeling (IPMVP Option D - Calibrated Simulation)

**Baseline Model (Year 1)**:
- Equipment density: 10.76 W/m²
- All zones as designed
- Normal office operations

**Year 2 Model (with Server Room)**:
- Core_mid equipment density: 50.76 W/m²
- Increase: +40 W/m² × 550 m² = 22 kW
- Operating period: 6 months (July-December)
- Expected increase: ~96,000 kWh for 6 months

### Step 2: Calculate Non-Routine Adjustment

```
Non-Routine Adjustment = Energy attributable to non-routine event
                       = Increase in Jul-Dec due to server room
                       = ΔE_server_room
```

**Calculation**:
```
Server Room Annual Load:
  Power = 40 W/m² × 550 m² = 22,000 W = 22 kW
  Annual Energy = 22 kW × 8,760 hrs = 192,720 kWh/year

6-Month Operation (Jul-Dec):
  Energy = 192,720 kWh/year ÷ 2 = 96,360 kWh
```

### Step 3: Apply Adjustment to Year 2

**Reported Year 2 Energy**: E_Year2_reported
**Less: Non-Routine Adjustment**: -96,360 kWh
**Adjusted Year 2 (Routine)**: E_Year2_adjusted

**Formula**:
```
E_Year2_adjusted = E_Year2_reported - E_nonroutine

Where:
  E_nonroutine = Energy from server room (Jul-Dec only)
```

---

## Teaching Points for CMVP Professionals

### 1. **When to Apply Non-Routine Adjustments**

**Decision Tree**:

```
Is the change:
├─ A one-time event? YES →
│  ├─ Material impact (>5% of baseline)? YES →
│  │  ├─ Outside ECM scope? YES →
│  │  │  └─ APPLY NON-ROUTINE ADJUSTMENT ✓
│  │  └─ Part of ECM? NO →
│  │     └─ Include in savings calculation
│  └─ Immaterial impact (<5%)? →
│     └─ Document but may not need adjustment
└─ Recurring/routine? NO →
   └─ No adjustment needed (normal variation)
```

### 2. **Impact on Savings Calculations**

#### **Scenario A: No ECM, Just Non-Routine Event**

```
Year 1 Baseline:          400,000 kWh
Year 2 Reported:          496,360 kWh  (+96,360 kWh from servers)
Non-Routine Adjustment:   -96,360 kWh
Year 2 Adjusted:          400,000 kWh

Routine Change:           0 kWh  ← No ECM, so no savings
```

**Interpretation**: Building operations are unchanged; increase is entirely due to server room.

#### **Scenario B: LED Retrofit + Non-Routine Event**

```
Year 1 Baseline:          400,000 kWh
ECM Savings (LED):        -40,000 kWh  (expected)
Year 2 with LED Only:     360,000 kWh  (what it would be)
Year 2 Reported:          456,360 kWh  (LED + servers)
Non-Routine Adjustment:   -96,360 kWh  (servers)
Year 2 Adjusted:          360,000 kWh

Routine Change:           -40,000 kWh  ← Correct ECM savings!
```

**Interpretation**: Without adjustment, savings would appear to be only -40,000 + 96,360 = +56,360 kWh (increase!). The adjustment correctly isolates the -40,000 kWh ECM savings.

### 3. **Documentation Requirements**

Per IPMVP, document:

✓ **Event description**: What changed, when, where
✓ **Quantification method**: How impact was calculated
✓ **Data sources**: Nameplate data, submittals, measurements
✓ **Operating schedule**: Hours of operation
✓ **Start/end dates**: Exact timing of event
✓ **Uncertainty**: ±% accuracy of adjustment

**Example Documentation**:

```
Non-Routine Adjustment: Server Room Addition
Date: July 1, Year 2
Location: Core_mid zone (2nd floor, 550 m²)
Equipment: 40 W/m² of IT equipment (servers, networking)
Schedule: 24/7 continuous operation
Calculation Method: Nameplate ratings + operating hours
Energy Impact: 96,360 kWh (July-December Year 2)
Uncertainty: ±10% (based on nameplate vs. actual loads)
Documentation: Server room design drawings, equipment submittals
```

### 4. **Option C vs. Option D Considerations**

#### **IPMVP Option C** (Whole Building)

**Challenge**: Difficult to isolate non-routine from routine changes

**Approach**:
- Regression model with explanatory variables
- Add binary variable for "server room period"
- Coefficient = non-routine impact

**Model**:
```
E = β₀ + β₁×HDD + β₂×CDD + β₃×OccDays + β₄×ServerRoom + ε

Where:
  ServerRoom = 0 (pre-July) or 1 (post-July)
  β₄ = estimated non-routine adjustment
```

#### **IPMVP Option D** (Calibrated Simulation)

**Advantage**: Can model non-routine event explicitly

**Approach**:
1. Calibrate baseline model to Year 1 data
2. Run two Year 2 scenarios:
   - With server room
   - Without server room (routine operations)
3. Difference = non-routine adjustment

**This is what we demonstrated!**

### 5. **Common Mistakes to Avoid**

❌ **Ignoring non-routine events**: Leads to incorrect savings
❌ **Adjusting routine variations**: Over-adjustment reduces accuracy
❌ **Inconsistent periods**: Apply adjustment to same period in baseline and reporting
❌ **Double-counting**: Don't adjust for same event twice
❌ **Poor documentation**: Hard to defend adjustments in verification

### 6. **M&V Plan Considerations**

**Include in M&V Plan**:

```markdown
## Section 7: Non-Routine Adjustments

7.1 Threshold for Adjustment
    - Events exceeding 5% of baseline energy
    - One-time, non-recurring changes
    - Outside scope of ECM being measured

7.2 Quantification Method
    - Primary: Engineering calculations (nameplate + hours)
    - Secondary: Short-term metering if available
    - Tertiary: Simulation modeling

7.3 Documentation Requirements
    - Event notification within 30 days
    - Quantification within 60 days
    - Include in quarterly reports

7.4 Approval Process
    - M&V contractor proposes adjustment
    - Owner reviews documentation
    - Both parties agree before applying
```

---

## Reporting Example

### M&V Report - Year 2

**Table 1: Annual Energy Performance**

| Period | Reported Consumption (kWh) | Non-Routine Adjustment (kWh) | Adjusted Consumption (kWh) | Notes |
|--------|---------------------------|------------------------------|---------------------------|-------|
| Year 1 Baseline | 400,000 | - | 400,000 | Normal operations |
| Year 2 Reporting | 496,360 | -96,360 | 400,000 | Server room Jul-Dec |

**Table 2: Non-Routine Adjustment Detail**

| Event | Period | Energy Impact (kWh) | Calculation Method | Uncertainty |
|-------|--------|---------------------|-------------------|-------------|
| Server Room Addition | Jul-Dec Year 2 | 96,360 | Nameplate (22 kW) × 4,380 hrs | ±10% |

**Narrative**:

> "In July Year 2, the facility converted 550 m² of office space into an IT server room. This non-routine event added 22 kW of continuous load, resulting in 96,360 kWh of additional energy use from July-December. Per IPMVP guidelines, this energy has been excluded from the savings calculation as it represents a change in facility use outside the scope of the ECM being measured. The adjustment was calculated using equipment nameplate ratings and verified operating schedules."

---

## Key Formulas

### Non-Routine Adjustment

```
E_adjusted = E_reported - E_nonroutine

Where:
  E_adjusted = Energy consumption adjusted for routine operations
  E_reported = Measured/reported energy consumption
  E_nonroutine = Energy from non-routine events
```

### Avoided Energy Use (Savings)

```
Savings = E_baseline_adj - E_reporting_adj

Where both periods are adjusted for non-routine events
```

### Uncertainty

```
U_total = √(U_baseline² + U_reporting² + U_adjustment²)

Include uncertainty of non-routine adjustment!
```

---

## Exercise Questions for Students

1. **A factory adds a second shift (4pm-12am) starting in March of Year 2. Is this a non-routine adjustment?**
   - Answer: Depends. If second shift is temporary (1-2 months), YES. If it's a permanent operational change, NO - it's a routine change in facility operation.

2. **How would you handle a 2-week plant shutdown for annual maintenance?**
   - Answer: Typically NO adjustment needed if shutdown occurs every year at similar time (routine). Adjust baseline period to exclude shutdown weeks for fair comparison.

3. **Server room added but also implemented cooling efficiency ECM. How to handle?**
   - Answer: Apply non-routine adjustment for server room. Measure cooling ECM savings separately. Document that some cooling savings offset server heat load.

4. **Non-routine event impact is ±15% uncertain. How does this affect overall M&V?**
   - Answer: Increases total uncertainty. If adjustment is large (>20% of baseline), may dominate uncertainty budget. Consider short-term metering to reduce uncertainty.

5. **When should you use simulation vs. measurement for non-routine adjustments?**
   - Answer: Measurement preferred when event is ongoing and submeter available. Simulation better for estimating past events or when metering not feasible. Engineering calculation acceptable for simple, well-documented loads.

---

## Conclusion

Non-routine adjustments are a critical aspect of M&V that ensure:

✓ **Fair comparison** between baseline and reporting periods
✓ **Accurate savings** calculations that reflect only the ECM impact
✓ **Credibility** of M&V results with stakeholders
✓ **Compliance** with IPMVP standards

The key is to:
1. **Identify** non-routine events early
2. **Quantify** impact using best available data
3. **Document** thoroughly for verification
4. **Apply** adjustments consistently to both periods
5. **Communicate** clearly in M&V reports

---

## References

- IPMVP (International Performance Measurement & Verification Protocol) Volume I, Section 4.5
- ASHRAE Guideline 14: Measurement of Energy, Demand, and Water Savings
- FEMP M&V Guidelines: Measurement and Verification for Performance-Based Contracts, Version 4.0
- EVO 10200: Uncertainty Assessment for IPMVP

---

## Files Generated

1. **cmvp_nonroutine_demo.py** - Simulation script
2. **cmvp_nonroutine_analysis.py** - Analysis script
3. **CMVP_NonRoutine_Adjustment_Analysis.csv** - Monthly comparison data
4. **CMVP_NonRoutine_Summary.json** - Results summary
5. **This document** - Complete teaching guide

---

**For CMVP Training**: This example can be used to demonstrate IPMVP Option D (Calibrated Simulation) and the proper handling of non-routine adjustments. Students should practice identifying when adjustments are needed and calculating their magnitude using multiple methods.
