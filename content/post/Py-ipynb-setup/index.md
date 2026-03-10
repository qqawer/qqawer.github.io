---
title: macOS Python Virtual Environment + Jupyter/ipynb Configuration Guide
description: A comprehensive guide for macOS users to set up a Python virtual environment and Jupyter/ipynb in VS Code from scratch.
date: 2026-03-10
slug: macos-python-jupyter-setup-en
categories:
    - Documentation
tags:
    - macOS
    - Python
    - Jupyter
    - VS Code
    - venv
toc: true
---

# macOS Python Virtual Environment + Jupyter/ipynb Complete Setup Guide

## Document Overview
This document is designed for macOS users. It provides a step-by-step guide to setting up a Python virtual environment, installing Jupyter dependencies, and running `.ipynb` files in VS Code. The guide focuses on "environment isolation" and is "beginner-friendly," with all commands ready for copy-pasting.

## Key Highlights
- **Environment Isolation**: Uses `venv` to ensure project dependencies do not interfere with the system environment.
- **Direct Configuration**: Deeply optimized for macOS and VS Code, addressing common pain points like kernel detection.
- **Package Management**: Includes best practices for environment migration and `requirements.txt`.

## Final Objectives
Create an independent virtual environment in a specific directory (e.g., a machine learning project directory) to achieve:
- Complete isolation from the system global Python environment.
- Usage of virtual environment dependencies for `.ipynb` files in VS Code.
- Normal Jupyter kernel startup without version compatibility warnings.

## I. Prerequisites
### 1.1 Check System Environment
Ensure the macOS terminal is accessible (default Terminal or iTerm2 is recommended). No need to pre-install Python (a compatible version will be installed in the next step).

### 1.2 Target Path Description
Example virtual environment path used in this guide:
```
/Users/outsider/Downloads/NUS-ISS/SA61-ClassDocument+Exam/SA4110 Machine Learning Application Development/Myenv/
```
You can replace this with your own project path. Note that paths with spaces should be enclosed in quotes.

## II. Step 1: Install Python 3.10 (Stable for Jupyter)
Since the default macOS Python might be outdated, we recommend installing Python 3.10 (an LTS version officially supported by Jupyter) via Homebrew.

### 2.1 Install Homebrew (If not installed)
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```
After installation, verify Homebrew:
```bash
brew --version
```

### 2.2 Install Python 3.10
```bash
brew install python@3.10
```

### 2.3 Verify Python Installation
```bash
/opt/homebrew/bin/python3.10 --version
```
✅ Expected output: `Python 3.10.19` (small version differences are normal).

## III. Step 2: Create a Dedicated Virtual Environment
### 3.1 Navigate to the Target Directory
```bash
cd "/Users/outsider/Downloads/Myenv"
```

### 3.2 Create the Virtual Environment (Named `env`)
```bash
/opt/homebrew/bin/python3.10 -m venv env
```
This will generate an `env` folder in the `Myenv` directory.

```bash
# Rename old environment (Optional but recommended) - rename 'env' to 'env_old'
mv env env_old
```

### 3.3 Activate the Virtual Environment
```bash
source env/bin/activate
```
✅ Activation verification: The `(env)` prefix should appear in your terminal prompt.

## IV. Step 3: Install Jupyter/ipynb Core Dependencies
**Perform all actions while the virtual environment is activated (`(env)` prompt visible).**

### 4.1 Upgrade pip (To avoid installation errors)
```bash
pip install --upgrade pip
```
⚠️ If `pip: command not found` occurs, use the internal pip:
```bash
/Users/outsider/Downloads/NUS-ISS/SA61-ClassDocument+Exam/SA4110 Machine Learning Application Development/Myenv/env/bin/python -m pip install --upgrade pip
```

### 4.2 Install Jupyter Core Dependencies
```bash
pip install jupyter ipykernel
```

### 4.3 (Optional) Install Common ML Packages / Restore Packages
Install based on your project needs:
```bash
pip install pandas numpy scikit-learn matplotlib tensorflow
```

```bash
# Export all packages from the old environment to requirements.txt (use backslashes for spaces)
/Users/outsider/Downloads/NUS-ISS/SA61-ClassDocument+Exam/SA4110\ Machine\ Learning\ Application\ Development/Myenv/myenv_old/bin/python -m pip freeze > requirements.txt

# Activate the new environment
source env/bin/activate
# Install all packages in the new environment
pip install -r requirements.txt
```

### 4.4 Verify Dependency Installation
```bash
pip list
```
✅ Expected output: The list should include `jupyter`, `ipykernel`, `pandas` (if installed), etc.

## V. Step 4: VS Code Configuration (Kernel Selection)
### 5.1 Install Required Extensions
Open VS Code → Extensions (`Cmd+Shift+X`), then search for and install:
- `Jupyter` (by Microsoft)
- `Python` (by Microsoft)

### 5.2 Select the Virtual Environment as ipynb Kernel
1. Open a `.ipynb` file (or create: `Cmd+Shift+P` → `Jupyter: Create New Notebook`).
2. Click "Select Kernel" in the top-right corner → "Select Another Kernel...".
3. Choose "Python Environments...".
4. Find your environment in the list: `env (Python 3.10.19) /Users/outsider/.../Myenv/env/bin/python`.
   ⚠️ If not listed, choose "Enter interpreter path..." → "Browse..." and manually locate:
   ```
   /Users/outsider/Downloads/NUS-ISS/SA61-ClassDocument+Exam/SA4110 Machine Learning Application Development/Myenv/env/bin/python
   ```
5. Once selected, VS Code will load the dependencies from that environment.

## VI. Step 5: Verify Configuration
Run the following code in a new code cell:
```python
# Verify Python interpreter path
import sys
print("Python path (Correct if it contains Myenv/env):", sys.executable)

# Verify Jupyter kernel
import ipykernel
print("ipykernel version:", ipykernel.__version__)

# Verify installed packages (e.g., numpy)
try:
    import numpy
    print("numpy version:", numpy.__version__)
    print("✅ Configuration successful! ipynb is using the virtual environment.")
except ImportError:
    print("❌ Package not loaded. Please check the installation steps.")
```

✅ Expected output example:
```
Python path (Correct if it contains Myenv/env): /Users/outsider/.../Myenv/env/bin/python
ipykernel version: 6.25.2
numpy version: 1.26.4
✅ Configuration successful! ipynb is using the virtual environment.
```

## VII. Troubleshooting (macOS Specific)
### 7.1 VS Code Cannot Find Virtual Environment
- Restart VS Code to trigger an environment scan.
- Switch the Python interpreter in the bottom-left status bar first, then re-select the kernel.
- Ensure `python`, `pip`, and `ipykernel` exist in the `env/bin/` directory.

### 7.2 ipynb Error: "Kernel failed to start"
Activate the environment and run:
```bash
source env/bin/activate
pip install --upgrade ipykernel
python -m ipykernel install --user --name=env  # Register the kernel to the system
```

### 7.3 Virtual Environment Inactive After Closing Terminal
You must reactivate it in every new terminal session:
```bash
cd "/Users/outsider/.../Myenv" && source env/bin/activate
```

## VIII. Summary of Key Operations
1. **Creation**: `python3.10 -m venv env` to create, `source env/bin/activate` to activate.
2. **Installation**: Install `jupyter ipykernel` within the active environment for isolation.
3. **VS Code**: Manually point to the virtual environment's `python` path to avoid using global settings.
4. **Verification**: Confirm the Python path in `.ipynb` includes `Myenv/env`.

## IX. Common Shortcuts & Commands
| Action | Command / Shortcut |
| :--- | :--- |
| Activate Env | `source env/bin/activate` |
| Deactivate Env | `deactivate` |
| Export Packages | `pip freeze > requirements.txt` |
| Install from List | `pip install -r requirements.txt` |
| Open ipynb via CLI | `code filename.ipynb` |
| Restart Kernel | VS Code: "Kernel" → "Restart Kernel" |
