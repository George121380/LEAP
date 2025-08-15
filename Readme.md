# VirtualHome Embodied Agent Evaluation

This project provides a comprehensive framework for evaluating LLM-based embodied agents in virtual home environments. The framework supports various agent configurations including planning-based and policy-based approaches, with integrated behavior libraries and human guidance systems.

## Features

- **Multiple Agent Types**: Support for planning-based and policy-based agents
- **Behavior Library**: Reusable behavior patterns for common tasks
- **Human Guidance**: LLM-based and manual guidance systems
- **Task Evaluation**: Comprehensive evaluation across different scenarios
- **Cooking Tasks**: Specialized evaluation for cooking-related activities
- **Multi-scene Support**: Evaluation across different virtual environments

## Project Structure

```
src/
├── agent.py              # Main agent implementation
├── agent_base.py         # Base agent class
├── agent_LLM.py         # LLM-based agent implementation
├── configs.py           # Configuration classes for different experiments
├── env.py              # VirtualHome environment wrapper
├── main_VH.py          # Main evaluation script
├── main_cooking.py     # Cooking tasks evaluation
├── paths.py            # Path utilities
├── library.py          # Behavior library implementation
├── planning.py         # Planning pipeline
├── evaluation.py       # Task evaluation logic
├── human.py            # Human guidance interface
├── logger.py           # Logging utilities
├── domain/             # Domain knowledge files
├── prompts/            # LLM prompts and API interface
├── simulator/          # VirtualHome simulator (external)
└── utils/              # Utility functions and models

VirtualHome-HG/         # VirtualHome dataset and scenes
├── dataset/           # Task definitions
├── cooking/           # Cooking-specific tasks
└── scenes/           # Environment scenes
```

## Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd 06-virtual-home
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up API keys**
   
   Create a configuration file for API keys:
   ```bash
   mkdir config
   cp config/api_keys.json.example config/api_keys.json
   ```
   
   Edit `config/api_keys.json` with your actual API keys:
   ```json
   {
     "OpenAI_API_Key": "your-openai-api-key-here",
     "Deepseek_API_Key": "your-deepseek-api-key-here"
   }
   ```
   
   Alternatively, set environment variables:
   ```bash
   export OPENAI_API_KEY="your-openai-api-key"
   export DEEPSEEK_API_KEY="your-deepseek-api-key"
   ```

## Usage

### Basic Evaluation

Run the main evaluation script:

```bash
cd src
python main_VH.py
```

You'll be prompted to:
1. Select a configuration (agent type)
2. Choose evaluation mode (single task or all tasks)
3. Specify scenes and other parameters

### Command Line Interface

For automated runs, use command line arguments:

```bash
# Evaluate single task
python main_VH.py --config OursWG --mode single --scene 0 --task_path ../VirtualHome-HG/dataset/Cook_some_food/g1.txt

# Evaluate all tasks
python main_VH.py --config OursWG --mode all --run_mode test --scene all
```

### Cooking Tasks

For cooking-specific evaluation:

```bash
python main_cooking.py
```

## Configuration Options

The framework supports several agent configurations:

### Baseline Configurations
- **OursWG**: Full system with guidance
- **OursWOG**: Full system without guidance  
- **LLMWG**: LLM baseline with guidance
- **LLMWOG**: LLM baseline without guidance
- **LLMPlusPWG**: LLM with planning, with guidance
- **LLMPlusPWOG**: LLM with planning, without guidance
- **CAPWG**: CAP baseline with guidance
- **CAPWOG**: CAP baseline without guidance

### Ablation Studies
- **WOLibrary**: Without behavior library
- **ActionLibrary**: Using action-based library instead of behavior-based
- **WORefinement**: Without goal refinement
- **WOSplit**: Without task decomposition
- **PvP**: Policy vs Planning comparison

## Key Components

### Agent Types
- **Planning Agent**: Uses formal planning with goal representations
- **Policy Agent**: Direct action selection based on current state
- **LLM Agent**: Pure language model-based decision making

### Behavior Library
The system maintains a library of successful behaviors that can be reused across tasks:
- Behavior-based storage (formal representations)
- Action-based storage (action sequences)
- RAG-based retrieval for relevant behaviors

### Human Guidance
- **LLM Guidance**: Automated guidance using language models
- **Manual Guidance**: Interactive human input
- **No Guidance**: Pure autonomous operation

## Evaluation

The framework evaluates agents on:
- Task completion rate
- Action efficiency
- Library usage effectiveness
- Human guidance dependency
- Cross-scene generalization

Results are logged in CSV format with detailed metrics for analysis.

## Contributing

1. Follow the existing code style and structure
2. Add appropriate docstrings and comments
3. Test your changes across different configurations
4. Update documentation as needed

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

This project builds upon the VirtualHome simulator and incorporates various planning and learning techniques for embodied AI research.