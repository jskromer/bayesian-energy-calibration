#!/bin/bash
# Quick start script for New Jersey fault detection analysis

echo "================================================================================"
echo "NEW JERSEY FAULT DETECTION - QUICK START"
echo "================================================================================"

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker Desktop first."
    echo ""
    echo "   1. Open Docker Desktop app"
    echo "   2. Wait for Docker to start"
    echo "   3. Run this script again"
    exit 1
fi

echo "✅ Docker is running"

# Start container
echo ""
echo "🚀 Starting EnergyPlus MCP container..."
cd "$(dirname "$0")"
docker compose up -d energyplus-mcp

if [ $? -ne 0 ]; then
    echo "❌ Failed to start container"
    exit 1
fi

echo "✅ Container started"

# Download NJ weather file
echo ""
echo "🌤️  Downloading New Jersey weather file (Newark)..."
docker exec energyplus-mcp bash -c "
    cd /workspace/energyplus-mcp-server/sample_files && \
    if [ ! -f USA_NJ_Newark.Intl.AP.725020_TMY3.epw ]; then
        curl -L -o USA_NJ_Newark.Intl.AP.725020_TMY3.epw \
            'https://energyplus-weather.s3.amazonaws.com/north_and_central_america_wmo_region_4/USA/NJ/USA_NJ_Newark.Intl.AP.725020_TMY3/USA_NJ_Newark.Intl.AP.725020_TMY3.epw'
        echo '✅ Weather file downloaded'
    else
        echo '✅ Weather file already exists'
    fi
"

# Check if dependencies are installed
echo ""
echo "📦 Checking Python dependencies..."
docker exec energyplus-mcp bash -c "
    cd /workspace/energyplus-mcp-server && \
    uv pip list | grep -q arviz || uv pip install arviz matplotlib scikit-learn scipy
"

echo "✅ Dependencies ready"

# Copy script to container
echo ""
echo "📋 Copying analysis script..."
docker cp energyplus-mcp-server/new_jersey_fault_detection.py energyplus-mcp:/workspace/energyplus-mcp-server/

# Run analysis
echo ""
echo "================================================================================"
echo "🔬 Running Bayesian Fault Detection Analysis..."
echo "================================================================================"
echo ""
echo "This will:"
echo "  1. Run 8 EnergyPlus simulations (takes ~2-3 minutes)"
echo "  2. Build Gaussian Process surrogate model"
echo "  3. Perform Bayesian inference (1,000 samples)"
echo "  4. Calculate counterfactual savings"
echo "  5. Generate visualization"
echo ""
echo "Please wait..."
echo ""

docker exec energyplus-mcp bash -c "
    cd /workspace/energyplus-mcp-server && \
    export MPLBACKEND=Agg && \
    uv run new_jersey_fault_detection.py 2>&1 | tail -100
"

# Copy results back
echo ""
echo "================================================================================"
echo "📥 Copying Results to Local Machine..."
echo "================================================================================"

docker cp energyplus-mcp:/workspace/energyplus-mcp-server/nj_fault_analysis.png energyplus-mcp-server/ 2>/dev/null && \
    echo "✅ Copied: nj_fault_analysis.png" || echo "⚠️  Could not copy visualization"

docker cp energyplus-mcp:/workspace/energyplus-mcp-server/nj_fault_results.csv energyplus-mcp-server/ 2>/dev/null && \
    echo "✅ Copied: nj_fault_results.csv" || echo "⚠️  Could not copy CSV"

echo ""
echo "================================================================================"
echo "✅ ANALYSIS COMPLETE!"
echo "================================================================================"
echo ""
echo "📊 Results saved to:"
echo "   - energyplus-mcp-server/nj_fault_analysis.png"
echo "   - energyplus-mcp-server/nj_fault_results.csv"
echo ""
echo "🖼️  Open visualization:"
echo "   open energyplus-mcp-server/nj_fault_analysis.png"
echo ""
echo "📝 View CSV results:"
echo "   open energyplus-mcp-server/nj_fault_results.csv"
echo ""
echo "================================================================================"
