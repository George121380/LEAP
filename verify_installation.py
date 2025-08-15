#!/usr/bin/env python3
"""
LEAP Agent Installation Verification Script

This script checks if all dependencies and configurations are properly set up.
Run this after installation to ensure everything is working correctly.
"""

import sys
import os
import json
from pathlib import Path

def print_status(message, status="INFO"):
    """Print colored status messages"""
    colors = {
        "INFO": "\033[94m[INFO]\033[0m",
        "SUCCESS": "\033[92m[SUCCESS]\033[0m", 
        "WARNING": "\033[93m[WARNING]\033[0m",
        "ERROR": "\033[91m[ERROR]\033[0m"
    }
    print(f"{colors.get(status, '[INFO]')} {message}")

def check_python_version():
    """Check Python version"""
    version = sys.version_info
    if version.major == 3 and version.minor >= 9:
        print_status(f"Python {version.major}.{version.minor}.{version.micro}", "SUCCESS")
        return True
    else:
        print_status(f"Python {version.major}.{version.minor}.{version.micro} - requires Python 3.9+", "ERROR")
        return False

def check_core_dependencies():
    """Check if core dependencies are installed"""
    dependencies = [
        ("numpy", "numpy"),
        ("torch", "PyTorch"),
        ("transformers", "Transformers"),
        ("sentence_transformers", "Sentence Transformers"),
        ("faiss", "FAISS"),
        ("pandas", "Pandas"),
        ("matplotlib", "Matplotlib"),
        ("yaml", "PyYAML"),
        ("tqdm", "tqdm")
    ]
    
    success = True
    for module, name in dependencies:
        try:
            __import__(module)
            print_status(f"{name} installed", "SUCCESS")
        except ImportError:
            print_status(f"{name} not found", "ERROR")
            success = False
    
    return success

def check_third_party_libraries():
    """Check third-party libraries (Jacinle, Concepts)"""
    success = True
    
    # Check Jacinle
    try:
        import jacinle
        print_status("Jacinle library accessible", "SUCCESS")
    except ImportError:
        print_status("Jacinle library not found in PYTHONPATH", "WARNING")
        print_status("Make sure Jacinle is installed and PYTHONPATH is set correctly", "INFO")
        success = False
    
    # Check Concepts
    try:
        import concepts
        print_status("Concepts library accessible", "SUCCESS")
    except ImportError:
        print_status("Concepts library not found in PYTHONPATH", "WARNING")
        print_status("Make sure Concepts is installed and PYTHONPATH is set correctly", "INFO")
        success = False
    
    return success

def check_api_configuration():
    """Check API keys configuration"""
    config_path = Path("config/api_keys.json")
    
    if not config_path.exists():
        print_status("API keys configuration file not found", "ERROR")
        print_status("Create config/api_keys.json with your API keys", "INFO")
        return False
    
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        required_keys = ["OpenAI_API_Key", "Deepseek_API_Key"]
        missing_keys = []
        placeholder_keys = []
        
        for key in required_keys:
            if key not in config:
                missing_keys.append(key)
            elif config[key] in ["your-openai-api-key-here", "your-deepseek-api-key-here", ""]:
                placeholder_keys.append(key)
        
        if missing_keys:
            print_status(f"Missing API keys: {', '.join(missing_keys)}", "ERROR")
            return False
        
        if placeholder_keys:
            print_status(f"Placeholder values found for: {', '.join(placeholder_keys)}", "WARNING")
            print_status("Please replace with actual API keys", "INFO")
            return False
        
        print_status("API keys configuration looks good", "SUCCESS")
        return True
        
    except json.JSONDecodeError:
        print_status("Invalid JSON in API keys configuration", "ERROR")
        return False
    except Exception as e:
        print_status(f"Error reading API configuration: {e}", "ERROR")
        return False

def check_environment_variables():
    """Check important environment variables"""
    env_vars = {
        "PYTHONPATH": "Python path for third-party libraries",
        "TOKENIZERS_PARALLELISM": "Tokenizers parallelism setting"
    }
    
    success = True
    for var, description in env_vars.items():
        value = os.environ.get(var)
        if value:
            print_status(f"{var} = {value[:50]}{'...' if len(value) > 50 else ''}", "SUCCESS")
        else:
            if var == "TOKENIZERS_PARALLELISM":
                print_status(f"{var} not set - may see warnings", "WARNING")
            else:
                print_status(f"{var} not set", "WARNING")
                success = False
    
    return success

def check_project_structure():
    """Check if project structure is correct"""
    required_dirs = [
        "src",
        "VirtualHome-HG",
        "config"
    ]
    
    required_files = [
        "src/main_VH.py",
        "src/agent/leap.py", 
        "src/configs.py",
        "environment.yml",
        "requirements.txt"
    ]
    
    success = True
    
    for dir_name in required_dirs:
        if Path(dir_name).is_dir():
            print_status(f"Directory '{dir_name}' found", "SUCCESS")
        else:
            print_status(f"Directory '{dir_name}' missing", "ERROR")
            success = False
    
    for file_name in required_files:
        if Path(file_name).is_file():
            print_status(f"File '{file_name}' found", "SUCCESS")
        else:
            print_status(f"File '{file_name}' missing", "ERROR")
            success = False
    
    return success

def main():
    """Main verification function"""
    print("🔍 LEAP Agent Installation Verification")
    print("=" * 50)
    
    checks = [
        ("Python Version", check_python_version),
        ("Core Dependencies", check_core_dependencies), 
        ("Third-party Libraries", check_third_party_libraries),
        ("API Configuration", check_api_configuration),
        ("Environment Variables", check_environment_variables),
        ("Project Structure", check_project_structure)
    ]
    
    results = []
    
    for check_name, check_func in checks:
        print(f"\n📋 Checking {check_name}...")
        try:
            result = check_func()
            results.append((check_name, result))
        except Exception as e:
            print_status(f"Error during {check_name} check: {e}", "ERROR")
            results.append((check_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Verification Summary:")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for check_name, result in results:
        status = "✅" if result else "❌"
        print(f"{status} {check_name}")
    
    print(f"\nPassed: {passed}/{total} checks")
    
    if passed == total:
        print_status("🎉 All checks passed! Your installation is ready.", "SUCCESS")
        print_status("You can now run: cd src && python main_VH.py", "INFO")
        return True
    else:
        print_status("❌ Some checks failed. Please review the issues above.", "ERROR")
        print_status("Refer to SETUP_GUIDE.md for troubleshooting help.", "INFO")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
