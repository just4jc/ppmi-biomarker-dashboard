#!/bin/bash
# 
# PPMI Dashboard Launch Script
# Quick setup and launch script for the PPMI biomarker dashboard
#

echo "🧠 PPMI Parkinson's Disease Biomarker Dashboard"
echo "=============================================="

# Change to the correct directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "📂 Working directory: $SCRIPT_DIR"

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed or not in PATH"
    echo "Please install Python 3.8 or higher"
    exit 1
fi

echo "✅ Python 3 found: $(python3 --version)"

# Check if pip is available
if ! command -v pip &> /dev/null; then
    echo "⚠️  pip not found, trying pip3"
    if ! command -v pip3 &> /dev/null; then
        echo "❌ pip is not installed"
        exit 1
    else
        PIP_CMD="pip3"
    fi
else
    PIP_CMD="pip"
fi

# Install requirements if needed
echo "📦 Checking and installing requirements..."
if [ -f "requirements.txt" ]; then
    $PIP_CMD install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "❌ Failed to install requirements"
        exit 1
    fi
    echo "✅ Requirements installed successfully"
else
    echo "⚠️  requirements.txt not found, skipping installation"
fi

# Run tests
echo "🧪 Running tests..."
if [ -f "test_dashboard.py" ]; then
    python3 test_dashboard.py
    if [ $? -ne 0 ]; then
        echo "❌ Tests failed. Please check the issues above."
        echo "💡 Common solutions:"
        echo "   - Ensure PPMI data files are in the correct directory structure"
        echo "   - Check that all CSV files exist and are readable"
        echo "   - Verify file paths in data_loader.py"
        exit 1
    fi
    echo "✅ All tests passed!"
else
    echo "⚠️  test_dashboard.py not found, skipping tests"
fi

# Launch dashboard
echo ""
echo "🚀 Launching PPMI Dashboard..."
echo "📋 Dashboard will be available at: http://localhost:8501"
echo "🔄 To stop the dashboard, press Ctrl+C"
echo ""

if [ -f "ppmi_dashboard.py" ]; then
    streamlit run streamlit_app.py
else
    echo "❌ ppmi_dashboard.py not found in current directory"
    echo "Current directory contents:"
    ls -la
    exit 1
fi