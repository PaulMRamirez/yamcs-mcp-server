#!/bin/bash
# Script to run integration tests locally

set -e

# Check if Yamcs is already running
if curl -f http://localhost:8090/api/ >/dev/null 2>&1; then
    echo "✅ Yamcs is already running on port 8090"
    echo "📊 Using existing Yamcs instance"
    USE_EXISTING_YAMCS=true
else
    echo "🚀 Starting Yamcs Docker container..."
    
    # Stop and remove any existing yamcs container
    docker stop yamcs 2>/dev/null || true
    docker rm yamcs 2>/dev/null || true
    
    # Start Yamcs with simulator
    docker run -d --name yamcs \
      -p 8090:8090 \
      yamcs/example-simulation:latest
    USE_EXISTING_YAMCS=false
fi

echo "⏳ Waiting for Yamcs to be ready..."

# Wait for Yamcs to be healthy
max_attempts=30
attempt=0
while ! curl -f http://localhost:8090/api/ >/dev/null 2>&1; do
    attempt=$((attempt + 1))
    if [ $attempt -ge $max_attempts ]; then
        echo "❌ Yamcs failed to start after ${max_attempts} attempts"
        docker logs yamcs
        exit 1
    fi
    echo "  Attempt $attempt/$max_attempts..."
    sleep 2
done

echo "✅ Yamcs is ready!"

# Show Yamcs info
echo "📊 Yamcs server info:"
curl -s http://localhost:8090/api/ | uv run python -m json.tool | head -20

# Set environment variables
export YAMCS_URL=http://localhost:8090
export YAMCS_INSTANCE=simulator

echo ""
echo "🧪 Running integration tests..."

# Run the integration tests
uv run pytest tests/test_integration.py -v

# Capture exit code
TEST_EXIT_CODE=$?

echo ""

# Only clean up if we started the container
if [ "$USE_EXISTING_YAMCS" = false ]; then
    echo "🧹 Cleaning up..."
    # Stop and remove container
    docker stop yamcs
    docker rm yamcs
else
    echo "📌 Keeping existing Yamcs instance running"
fi

# Exit with test exit code
exit $TEST_EXIT_CODE