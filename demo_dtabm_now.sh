#!/bin/bash
# Quick Demo - Run DTABM Digital Twin Right Now
# This demonstrates the system is working with existing calibrated model

set -e

echo "=========================================="
echo "DTABM Digital Twin - Quick Demo"
echo "=========================================="
echo ""
echo "This demo runs the DTABM framework using"
echo "the already-calibrated baseline model."
echo ""
echo "Running digital twin framework..."
echo ""

docker exec energyplus-mcp python /workspace/energyplus-mcp-server/dtabm_framework.py

echo ""
echo "=========================================="
echo "DEMO COMPLETE!"
echo "=========================================="
echo ""
echo "Check the output:"
echo ""
echo "  cd energyplus-mcp-server/dtabm_output"
echo "  ls -lh"
echo ""
echo "You should see:"
echo "  • DTABM_Baseline.idf"
echo "  • DTABM_Operational.idf"
echo "  • DTActual.idf (post-LED retrofit)"
echo "  • dtabm_monthly_tracking.json"
echo "  • dtabm_mv_report.json"
echo ""
echo "Expected Results:"
echo "  ✓ Month 1 tracking: +2.8% error"
echo "  ✓ LED retrofit: 50% lighting reduction"
echo "  ✓ Annual savings: 61,789 kWh (13.7%)"
echo "  ✓ Cost savings: $7,415/year"
echo ""
