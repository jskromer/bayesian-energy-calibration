#!/bin/bash
# Complete DTABM Workflow - From Energy Audit to Digital Twin
# This script runs the entire workflow in sequence

set -e  # Exit on error

echo "=========================================="
echo "DTABM Complete Workflow"
echo "From Energy Audit to Digital Twin"
echo "=========================================="
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "Error: Docker is not running. Please start Docker Desktop."
    exit 1
fi

# Start the EnergyPlus container if not running
CONTAINER_NAME="energyplus-mcp"
if [ ! "$(docker ps -q -f name=${CONTAINER_NAME})" ]; then
    echo "Starting EnergyPlus container..."
    if [ "$(docker ps -aq -f name=${CONTAINER_NAME})" ]; then
        docker start ${CONTAINER_NAME}
    else
        echo "Container doesn't exist. Run: docker-compose up -d"
        exit 1
    fi
    sleep 3
fi

echo "Step 1: Collecting Energy Audit Data"
echo "--------------------------------------"
docker exec ${CONTAINER_NAME} python /workspace/energyplus-mcp-server/audit_to_model_workflow.py
echo "✓ Audit data collected"
echo ""

echo "Step 2: Building Initial EnergyPlus Model"
echo "-------------------------------------------"
docker exec ${CONTAINER_NAME} python /workspace/energyplus-mcp-server/step2_build_initial_model.py
echo "✓ Initial model built"
echo ""

echo "Step 3: Bayesian Calibration"
echo "------------------------------"
echo "(This may take 5-10 minutes for 8 simulations...)"
docker exec ${CONTAINER_NAME} python /workspace/energyplus-mcp-server/step3_bayesian_calibration.py
echo "✓ Model calibrated"
echo ""

echo "Step 4: DTABM Digital Twin Framework"
echo "--------------------------------------"
docker exec ${CONTAINER_NAME} python /workspace/energyplus-mcp-server/dtabm_framework.py
echo "✓ Digital Twin operational"
echo ""

echo "=========================================="
echo "WORKFLOW COMPLETE!"
echo "=========================================="
echo ""
echo "Your digital twin is now operational with:"
echo "  • DTABM_Baseline (frozen reference)"
echo "  • DTABM_Operational (live tracking)"
echo "  • DTActual (post-ECM model)"
echo ""
echo "Output files available in:"
echo "  energyplus-mcp-server/dtabm_output/"
echo ""
