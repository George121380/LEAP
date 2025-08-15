# LEAP: Learning Enhanced Agent Planning

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

A comprehensive framework for evaluating LLM-based embodied agents in virtual home environments. The framework supports various agent configurations including planning-based and policy-based approaches, with integrated behavior libraries and human guidance systems.

## 🏗 System Architecture

### LEAP Framework Overview
![LEAP System Architecture](assets/leap_system_overview.png)

The LEAP framework consists of four main components:
- **(a) System Input**: Task instructions and environmental observations from VirtualHome
- **(b) Preprocessing**: Task decomposition and abstract state representation  
- **(c) CDL Generation**: Formal planning with CROW planner and behavior library integration
- **(d) Execution and Self-evaluation**: Plan execution with human guidance and iterative refinement

### Learning and Guidance Mechanisms
![Learning and Guidance](assets/leap_learning_guidance.png)

The system incorporates three key learning mechanisms:
- **(a) Trial-and-error in environment**: Learning from interaction and execution failures
- **(b) Building a CDL library**: Continual learning through successful behavior memorization
- **(c) Human-provided guidance**: Expert knowledge integration for complex scenarios

## 🌟 Features

- **🤖 Multiple Agent Types**: Support for planning-based, policy-based, and pure LLM agents
- **📚 Behavior Library**: Reusable behavior patterns with RAG-based retrieval
- **🧭 Human Guidance**: LLM-based and manual guidance systems
- **🏠 VirtualHome Integration**: Comprehensive evaluation across different household scenarios
- **📊 Detailed Evaluation**: Task completion, efficiency, and generalization metrics
- **🔧 Easy Setup**: Automated installation with one-click setup script

## 🚀 Quick Start

### Automated Installation (Recommended)

```bash
git clone https://github.com/George121380/LEAP.git
cd LEAP
./setup.sh
conda activate leap-agent
```

### Verification

```bash
python verify_installation.py
```

### Run Your First Evaluation

```bash
cd src
python main_VH.py --config OursWG --mode single --scene 0 --task_path ../VirtualHome-HG/dataset/Cook_some_food/g1.txt
```

## 📋 Requirements

- **Python**: 3.9+
- **OS**: Linux, macOS, Windows
- **Memory**: 8GB+ RAM (16GB+ recommended)
- **Storage**: 5GB+ available space
- **API Keys**: OpenAI and/or DeepSeek (for LLM-based components)

## 🛠 Installation Options

### Option 1: Conda Environment (Recommended)

```bash
git clone https://github.com/George121380/LEAP.git
cd LEAP
conda env create -f environment.yml
conda activate leap-agent
```

### Option 2: pip Installation

```bash
git clone https://github.com/George121380/LEAP.git
cd LEAP
pip install -r requirements.txt
# Manual setup of third-party libraries required (see below)
```

### Third-Party Dependencies

The project requires two external libraries:

```bash
# Create directory for third-party libraries
mkdir -p ~/leap_third_party
cd ~/leap_third_party

# Install Jacinle (Python toolkit for researchers)
git clone https://github.com/vacancy/Jacinle --recursive

# Install Concepts (Concept learning framework)
git clone https://github.com/vacancy/Concepts --recursive

# Set environment variables
export PATH="~/leap_third_party/Jacinle/bin:$PATH"
export PYTHONPATH="~/leap_third_party/Jacinle:$PYTHONPATH"
export PATH="~/leap_third_party/Concepts/bin:$PATH"
export PYTHONPATH="~/leap_third_party/Concepts:$PYTHONPATH"
```

> **Note**: The automated setup script handles these dependencies automatically.

## ⚙️ Configuration

### API Keys Setup

1. Copy the example configuration:
   ```bash
   cp config/api_keys.json.example config/api_keys.json
   ```

2. Edit `config/api_keys.json` with your actual API keys:
   ```json
   {
     "OpenAI_API_Key": "sk-your-actual-openai-key",
     "Deepseek_API_Key": "your-actual-deepseek-key"
   }
   ```

### Agent Configurations

| Configuration | Description |
|---------------|-------------|
| **OursWG** | Full system with guidance (recommended) |
| **OursWOG** | Full system without guidance |
| **LLMWG** | LLM baseline with guidance |
| **LLMWOG** | LLM baseline without guidance |
| **LLMPlusPWG** | LLM with planning, with guidance |
| **CAPWG** | CAP baseline with guidance |

### Ablation Study Configurations

| Configuration | Purpose |
|---------------|---------|
| **WOLibrary** | Without behavior library |
| **ActionLibrary** | Action-based vs behavior-based library |
| **WORefinement** | Without goal refinement |
| **WOSplit** | Without task decomposition |
| **PvP** | Policy vs Planning comparison |

## 📖 Usage

### Interactive Mode

```bash
cd src
python main_VH.py
```

Follow the prompts to:
1. Select agent configuration
2. Choose evaluation mode (single task or batch)
3. Specify scenes and parameters

### Command Line Interface

```bash
# Single task evaluation
python main_VH.py --config OursWG --mode single --scene 0 \
  --task_path ../VirtualHome-HG/dataset/Cook_some_food/g1.txt

# Batch evaluation
python main_VH.py --config OursWG --mode all --run_mode test --scene all

# Cooking-specific tasks
python main_cooking.py
```

### Available Command Line Options

```
--config CONFIG         Agent configuration (e.g., OursWG, LLMWG)
--mode {single,all}     Evaluation mode
--scene SCENE           Scene ID or 'all' for all scenes
--task_path TASK_PATH   Path to specific task file (single mode)
--run_mode {debug,test} Running mode for batch evaluation
--checkpoint PATH       Resume from checkpoint
--verbo                 Verbose output
```

## 🏗 Project Structure

```
LEAP/
├── 📁 src/                     # Source code
│   ├── 🤖 agent/               # Agent implementations
│   │   ├── base.py             # Base agent class
│   │   ├── leap.py             # LEAP agent (main)
│   │   └── llm_based.py        # LLM-only agent
│   ├── 📊 evaluation.py        # Task evaluation logic
│   ├── 🏠 env.py               # VirtualHome environment wrapper
│   ├── 🧠 planning.py          # Planning pipeline
│   ├── 📚 library.py           # Behavior library
│   ├── 👤 human.py             # Human guidance interface
│   ├── ⚙️ configs.py           # Configuration classes
│   ├── 📁 prompts/             # LLM prompts and templates
│   ├── 📁 simulator/           # VirtualHome simulator components
│   └── 📁 utils/               # Utility functions and models
├── 📁 VirtualHome-HG/          # Dataset and scenes
│   ├── 📁 dataset/             # Task definitions
│   └── 📁 scenes/              # Environment scenes
├── 📁 config/                  # Configuration files
├── 🐍 environment.yml          # Conda environment
├── 📦 requirements.txt         # Python dependencies
├── 🔧 setup.sh                 # Automated setup script
└── ✅ verify_installation.py   # Installation verification
```

## 🧪 Key Components

### Agent Architecture

- **🧠 Planning Agent**: Uses formal planning with CDL goal representations
- **🎯 Policy Agent**: Direct action selection based on current state  
- **💭 LLM Agent**: Pure language model-based decision making

### Behavior Library

The system maintains a library of successful behaviors:
- **Behavior-based storage**: Formal CDL representations
- **Action-based storage**: Sequential action patterns
- **RAG retrieval**: Semantic similarity-based behavior matching

### Human Guidance

- **🤖 LLM Guidance**: Automated assistance using language models
- **👤 Manual Guidance**: Interactive human input during execution
- **🔄 Loop Feedback**: Iterative refinement based on execution results

## 📊 Evaluation Metrics

The framework provides comprehensive evaluation across multiple dimensions:

- **Task Completion Rate**: Percentage of successfully completed tasks
- **Action Efficiency**: Number of actions required vs optimal
- **Library Usage**: Effectiveness of behavior reuse
- **Guidance Dependency**: Reliance on human assistance
- **Cross-scene Generalization**: Performance across different environments
- **Error Analysis**: Detailed failure mode categorization

Results are automatically logged in CSV format for analysis.

## 📚 Citation

If you use this work in your research, please cite:

```bibtex
@inproceedings{leap2024,
  title={LEAP: Learning Enhanced Agent Planning for Embodied AI},
  author={Your Name and Collaborators},
  booktitle={Proceedings of ICLR 2024},
  year={2024}
}
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **VirtualHome**: Built upon the VirtualHome simulator for household environments
- **Jacinle & Concepts**: Utilizes frameworks by Jiayuan Mao for reasoning and planning
- **Community**: Thanks to all contributors and researchers in embodied AI

---

**⭐ Star this repository if you find it helpful!**

For questions and discussions, please open an issue or reach out to the maintainers.