#!/bin/bash

# LEAP Agent Environment Setup Script
# This script automates the setup of the LEAP agent evaluation environment

set -e  # Exit on any error

echo "🚀 Setting up LEAP Agent Environment..."

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if conda is installed
if ! command -v conda &> /dev/null; then
    print_error "Conda is not installed. Please install Anaconda or Miniconda first."
    echo "Visit: https://docs.conda.io/en/latest/miniconda.html"
    exit 1
fi

print_status "Conda found: $(conda --version)"

# Create conda environment
ENV_NAME="leap-agent"
print_status "Creating conda environment: $ENV_NAME"

if conda env list | grep -q "^$ENV_NAME "; then
    print_warning "Environment '$ENV_NAME' already exists."
    read -p "Do you want to remove and recreate it? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_status "Removing existing environment..."
        conda env remove -n $ENV_NAME -y
    else
        print_status "Using existing environment..."
    fi
fi

if ! conda env list | grep -q "^$ENV_NAME "; then
    print_status "Creating new conda environment from environment.yml..."
    conda env create -f environment.yml
    print_success "Conda environment created successfully!"
else
    print_status "Updating existing environment..."
    conda env update -f environment.yml --prune
fi

# Activate environment
print_status "Activating environment..."
source $(conda info --base)/etc/profile.d/conda.sh
conda activate $ENV_NAME

# Install third-party dependencies
print_status "Setting up third-party libraries..."

# Create a directory for third-party libraries
THIRD_PARTY_DIR="$HOME/leap_third_party"
mkdir -p $THIRD_PARTY_DIR
cd $THIRD_PARTY_DIR

# Install Jacinle
if [ ! -d "Jacinle" ]; then
    print_status "Cloning Jacinle..."
    git clone https://github.com/vacancy/Jacinle --recursive
else
    print_status "Jacinle already exists, updating..."
    cd Jacinle && git pull && cd ..
fi

# Install Concepts
if [ ! -d "Concepts" ]; then
    print_status "Cloning Concepts..."
    git clone https://github.com/vacancy/Concepts --recursive
else
    print_status "Concepts already exists, updating..."
    cd Concepts && git pull && cd ..
fi

# Set up environment variables
print_status "Setting up environment variables..."

# Create activation script for the conda environment
CONDA_ENV_DIR=$(conda info --envs | grep $ENV_NAME | awk '{print $2}')
ACTIVATE_DIR="$CONDA_ENV_DIR/etc/conda/activate.d"
DEACTIVATE_DIR="$CONDA_ENV_DIR/etc/conda/deactivate.d"

mkdir -p $ACTIVATE_DIR
mkdir -p $DEACTIVATE_DIR

# Create activation script
cat > $ACTIVATE_DIR/leap_env.sh << EOF
#!/bin/bash
# LEAP Agent Environment Variables

export LEAP_THIRD_PARTY_DIR="$THIRD_PARTY_DIR"

# Jacinle
export PATH="\$LEAP_THIRD_PARTY_DIR/Jacinle/bin:\$PATH"
export PYTHONPATH="\$LEAP_THIRD_PARTY_DIR/Jacinle:\$PYTHONPATH"

# Concepts
export PATH="\$LEAP_THIRD_PARTY_DIR/Concepts/bin:\$PATH"
export PYTHONPATH="\$LEAP_THIRD_PARTY_DIR/Concepts:\$PYTHONPATH"

# Disable tokenizers parallelism warning
export TOKENIZERS_PARALLELISM=false

echo "🔧 LEAP environment variables loaded"
EOF

# Create deactivation script
cat > $DEACTIVATE_DIR/leap_env.sh << EOF
#!/bin/bash
# Clean up LEAP environment variables
unset LEAP_THIRD_PARTY_DIR
echo "🧹 LEAP environment variables unloaded"
EOF

# Make scripts executable
chmod +x $ACTIVATE_DIR/leap_env.sh
chmod +x $DEACTIVATE_DIR/leap_env.sh

# Go back to project directory
cd - > /dev/null

# Set up API keys configuration
print_status "Setting up API keys configuration..."
if [ ! -f "config/api_keys.json" ]; then
    if [ ! -d "config" ]; then
        mkdir config
    fi
    
    if [ -f "config/api_keys.json.example" ]; then
        cp config/api_keys.json.example config/api_keys.json
        print_warning "Please edit config/api_keys.json with your actual API keys"
    else
        cat > config/api_keys.json << EOF
{
    "OpenAI_API_Key": "your-openai-api-key-here",
    "Deepseek_API_Key": "your-deepseek-api-key-here"
}
EOF
        print_warning "Created config/api_keys.json template. Please add your actual API keys."
    fi
else
    print_success "API keys configuration already exists"
fi

print_success "🎉 Setup completed successfully!"
echo
echo "To use the LEAP agent environment:"
echo "1. Activate the environment: conda activate $ENV_NAME"
echo "2. Edit config/api_keys.json with your API keys"
echo "3. Run the main script: cd src && python main_VH.py"
echo
print_warning "Note: Make sure to add your actual API keys to config/api_keys.json before running the agent!"
