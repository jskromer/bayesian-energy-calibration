#!/bin/bash

set -e

CONTAINER_NAME="energyplus-mcp"
APP_PATH="/workspace/energyplus-mcp-server/streamlit_app.py"
STREAMLIT_BIN="/workspace/energyplus-mcp-server/.venv/bin/streamlit"
PID_FILE="/tmp/energyplus-streamlit.pid"

if ! docker info > /dev/null 2>&1; then
    echo "Error: Docker is not running. Please start Docker Desktop."
    exit 1
fi

if [ ! "$(docker ps -q -f name=${CONTAINER_NAME})" ]; then
    echo "Starting ${CONTAINER_NAME} container..."
    if [ "$(docker ps -aq -f name=${CONTAINER_NAME})" ]; then
        docker start ${CONTAINER_NAME} > /dev/null
    else
        echo "Container doesn't exist. Run: docker compose up -d"
        exit 1
    fi
fi

echo "Stopping any existing Streamlit process in ${CONTAINER_NAME}..."
docker exec ${CONTAINER_NAME} bash -lc "if [ -f ${PID_FILE} ]; then kill \$(cat ${PID_FILE}) 2>/dev/null || true; rm -f ${PID_FILE}; fi"

echo "Starting Streamlit dashboard..."
docker exec -d ${CONTAINER_NAME} bash -lc "nohup ${STREAMLIT_BIN} run ${APP_PATH} --server.address 0.0.0.0 --server.port 8501 > /tmp/energyplus-streamlit.log 2>&1 & echo \$! > ${PID_FILE}"

echo ""
echo "Streamlit is starting."
echo "Open: http://localhost:8501"
echo "Logs: docker exec ${CONTAINER_NAME} tail -f /tmp/energyplus-streamlit.log"
