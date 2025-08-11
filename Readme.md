# Virtual Home Embodied Agent Evaluation

A comprehensive evaluation framework for Large Language Models (LLMs) in embodied decision making tasks within virtual home environments.

## Overview

This project provides a systematic evaluation pipeline for assessing LLM-based agents in virtual home environments. It supports various agent configurations, task types, and evaluation metrics to understand the capabilities and limitations of language models in embodied AI scenarios.

### Key Features

- **Multi-Agent Configurations**: Support for various agent types including LLM-based agents, human-guided agents, and baseline methods
- **Comprehensive Task Dataset**: Diverse household tasks across different difficulty levels (easy, medium, hard)
- **Fine-grained Evaluation**: Detailed metrics beyond simple success rates, including action efficiency, planning quality, and error analysis
- **Flexible Scene Support**: Multiple virtual home scenes with different layouts and object configurations
- **Library System**: Reusable behavior library for improved agent performance

## Project Structure

```
├── src/                                  # Main source code
│   ├── main_VH.py                        # Main evaluation entry point
│   ├── configs.py                        # Agent configurations
│   ├── agent.py                          # Agent implementations
│   ├── env.py                            # Virtual environment
│   ├── evaluation.py                     # Evaluation framework
│   ├── metrics_new.py                    # Evaluation metrics
│   ├── prompts/                          # LLM prompts and templates
│   └── utils/                            # Utility functions and models
├── VirtualHome-HG/                       # Task dataset (migrated from cdl_dataset)
│   ├── dataset/                          # Household task definitions
│   ├── cooking/                          # Cooking-specific tasks
│   ├── scenes/                           # Virtual scene configurations
│   └── scripts/                          # Dataset processing utilities
├── docs/                                 # Documentation
│   ├── INSTALLATION.md                   # Installation guide
│   ├── USAGE.md                          # Usage instructions
│   └── CONTRIBUTING.md                   # Contribution guidelines
├── run_evaluation.py                     # Simple command-line interface
├── requirements.txt                      # Python dependencies
└── README.md                            # This file
```

## Quick Start

### Prerequisites

- Python 3.8+
- Required Python packages (see `requirements.txt`)

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd 06-virtual-home
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

### Basic Usage

1. **Run a single task evaluation**:
```bash
conda run -n eagent python src/main_VH.py --config OursWG --mode single --scene 0 --task_path VirtualHome-HG/dataset/Put_groceries_in_Fridge/g1.txt
```

2. **Run comprehensive evaluation**:
```bash
conda run -n eagent python src/main_VH.py --config OursWG --mode all --run_mode test
```

3. **Continue from checkpoint**:
```bash
python run_evaluation.py --config OursWG --mode all --checkpoint log/20241201_120000_OursWG
```

For more detailed usage instructions, see [docs/USAGE.md](docs/USAGE.md).

## Agent Configurations

The system supports multiple agent configurations:

### Baseline Methods
- **OursWG**: Our method with guidance
- **OursWOG**: Our method without guidance  
- **LLMWG/LLMWOG**: Pure LLM methods with/without guidance
- **LLMPlusPWG/LLMPlusPWOG**: LLM with planning, with/without guidance
- **CAPWG/CAPWOG**: CAP baseline with/without guidance

### Ablation Studies
- **WOLibrary**: Without behavior library
- **ActionLibrary**: Action-based library (vs behavior-based)
- **WORefinement**: Without plan refinement
- **WOSplit**: Without task splitting
- **PvP**: Plan vs Plan comparison

## Task Dataset

The dataset includes household tasks categorized by:

- **Difficulty Levels**: Easy, Medium, Hard
- **Task Types**: 
  - Cooking tasks (boiling, frying, preparing meals)
  - Cleaning tasks (bathroom, dishes, windows)
  - Organization tasks (groceries, clothes)
  - Entertainment tasks (TV, music, reading)
  - And more...

### Scene Environments

Three different virtual home scenes with varying:
- Room layouts
- Object placements  
- Available items and appliances

## Evaluation Metrics

The framework provides comprehensive evaluation including:

- **Success Rate**: Task completion percentage
- **Action Efficiency**: Number of actions required
- **Planning Quality**: Subgoal decomposition effectiveness
- **Error Analysis**: Categorization of failure types
- **Time Performance**: Execution time analysis

## Results and Logging

All experiment results are automatically logged with:
- Detailed action sequences
- Performance metrics
- Error analysis
- Timing information
- Configuration parameters

Results are saved in timestamped directories under `log/`.

## Documentation

Comprehensive documentation is available in the `docs/` directory:

- **[Installation Guide](docs/INSTALLATION.md)**: Step-by-step setup instructions
- **[Usage Guide](docs/USAGE.md)**: Detailed usage examples and configuration options
- **[Contributing Guide](docs/CONTRIBUTING.md)**: Guidelines for contributing to the project

## Contributing

We welcome contributions! Please see our [Contributing Guide](docs/CONTRIBUTING.md) for details on:

- Setting up the development environment
- Code style guidelines
- Pull request process
- Issue reporting

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Citation

If you use this work in your research, please cite:

```bibtex
@article{Li2024EmbodiedAI,
  title={Embodied Agent Interface: Benchmarking LLMs for Embodied Decision Making},
  author={Manling Li and Shiyu Zhao and Qineng Wang and Kangrui Wang and Yu Zhou and Sanjana Srivastava and Cem Gokmen and Tony Lee and Erran Li and Ruohan Zhang and Weiyu Liu and Jiayuan Mao and Percy Liang and Fei-Fei Li and Jiajun Wu},
  year={2024}
}
```

## Acknowledgments

This project builds upon the VirtualHome environment and incorporates various LLM evaluation methodologies for embodied AI research.
