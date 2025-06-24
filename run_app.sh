if ! hash python 2>/dev/null; then
    if ! hash python3 2>/dev/null; then
        echo "python is not installed"
        exit 1
    fi
    pyt="python3"
else
    pyt="python"
fi

# Check if the virtual environment exists
if [ ! -d "./venv" ]; then
    echo "Creating virtual environment..."
    $pyt -m venv ./venv
fi

# Activate the virtual environment
source ./venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install requirements if needed
pip install -r tools/build/requirements.txt

# Run the main application
$pyt benchmarkapp/main.py
