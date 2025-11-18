# Installation Guide

This guide covers installing Python 3, pip3, and all prerequisites for DevFoam on both macOS and Windows.

## Prerequisites

- Python 3.7 or higher
- pip3 (Python package manager)
- tkinter (usually included with Python)

## macOS Installation

### Method 1: Using Homebrew (Recommended)

1. **Install Homebrew** (if not already installed):
   ```bash
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   ```

2. **Install Python 3**:
   ```bash
   brew install python3
   ```

3. **Verify Installation**:
   ```bash
   python3 --version
   # Should show: Python 3.x.x
   
   pip3 --version
   # Should show: pip x.x.x from ...
   ```

### Method 2: Using Official Python Installer

1. **Download Python**:
   - Visit [python.org/downloads](https://www.python.org/downloads/)
   - Download the latest Python 3.x for macOS
   - Choose the appropriate installer for your Mac (Intel or Apple Silicon)

2. **Run the Installer**:
   - Double-click the downloaded `.pkg` file
   - Follow the installation wizard
   - **Important**: Check "Add Python to PATH" if available

3. **Verify Installation**:
   ```bash
   python3 --version
   pip3 --version
   ```

### Install tkinter (if needed)

On macOS, tkinter is usually included with Python. If you get an error about tkinter:

```bash
# For Homebrew Python
brew install python-tk

# Or reinstall Python with tkinter support
brew reinstall python3
```

## Windows Installation

### Method 1: Using Official Python Installer (Recommended)

1. **Download Python**:
   - Visit [python.org/downloads](https://www.python.org/downloads/)
   - Download the latest Python 3.x for Windows
   - Choose the appropriate installer (32-bit or 64-bit)

2. **Run the Installer**:
   - Double-click the downloaded `.exe` file
   - **Important**: Check "Add Python to PATH" at the bottom of the installer
   - Choose "Install Now" or "Customize installation"
   - If customizing, ensure "tcl/tk and IDLE" is selected (includes tkinter)

3. **Verify Installation**:
   - Open Command Prompt (cmd) or PowerShell
   ```cmd
   python --version
   # Should show: Python 3.x.x
   
   pip --version
   # Should show: pip x.x.x from ...
   ```

   **Note**: On Windows, you may use `python` instead of `python3`, and `pip` instead of `pip3`.

### Method 2: Using Microsoft Store

1. **Open Microsoft Store**:
   - Search for "Python 3.x"
   - Click "Get" or "Install"

2. **Verify Installation**:
   ```cmd
   python --version
   pip --version
   ```

### Install tkinter (if needed)

If tkinter is not available:

1. **Reinstall Python** with tkinter:
   - Run the Python installer again
   - Choose "Modify"
   - Ensure "tcl/tk and IDLE" is checked
   - Click "Install"

2. **Or install separately** (advanced):
   - Download tkinter from Python's official site
   - Or use: `pip install tk`

## Upgrading pip

After installing Python, upgrade pip to the latest version:

**macOS/Linux**:
```bash
python3 -m pip install --upgrade pip
```

**Windows**:
```cmd
python -m pip install --upgrade pip
```

## Installing DevFoam Dependencies

Once Python and pip are installed, install the required packages:

**macOS/Linux**:
```bash
# Navigate to the project directory
cd /path/to/devfoam

# Install dependencies
pip3 install -r requirements.txt
```

**Windows**:
```cmd
# Navigate to the project directory
cd C:\path\to\devfoam

# Install dependencies
pip install -r requirements.txt
```

### Required Packages

The installation will install:
- `ezdxf` - For DXF file support
- `svg.path` - For SVG file support (optional)
- `fontTools` - For font rendering (optional)
- `pytest` - For testing (development)

## Verifying Installation

Test that everything is installed correctly:

**macOS/Linux**:
```bash
python3 -c "import tkinter; print('tkinter: OK')"
python3 -c "import ezdxf; print('ezdxf: OK')"
```

**Windows**:
```cmd
python -c "import tkinter; print('tkinter: OK')"
python -c "import ezdxf; print('ezdxf: OK')"
```

## Troubleshooting

### "python3: command not found" (macOS/Linux)

- Ensure Python 3 is installed: `brew install python3` or download from python.org
- Check your PATH: `echo $PATH`
- Try using `python` instead of `python3` (some systems alias it)

### "python is not recognized" (Windows)

- Python was not added to PATH during installation
- Reinstall Python and check "Add Python to PATH"
- Or manually add Python to PATH:
  1. Find Python installation (usually `C:\Python3x\` or `C:\Users\YourName\AppData\Local\Programs\Python\Python3x\`)
  2. Add to System PATH via Control Panel → System → Advanced → Environment Variables

### "pip3: command not found" (macOS/Linux)

- pip3 should come with Python 3
- Try: `python3 -m pip --version`
- If that works, use `python3 -m pip install` instead of `pip3 install`

### "No module named 'tkinter'"

**macOS**:
```bash
brew install python-tk
# Or reinstall Python: brew reinstall python3
```

**Windows**:
- Reinstall Python and ensure "tcl/tk and IDLE" is selected
- Or try: `pip install tk`

**Linux**:
```bash
sudo apt-get install python3-tk  # Debian/Ubuntu
sudo yum install python3-tkinter  # RedHat/CentOS
```

### Permission Errors During pip Install

**macOS/Linux**:
- Use `--user` flag: `pip3 install --user -r requirements.txt`
- Or use a virtual environment (recommended)

**Windows**:
- Run Command Prompt as Administrator
- Or use `--user` flag: `pip install --user -r requirements.txt`

## Using Virtual Environments (Recommended)

Virtual environments isolate project dependencies. This is recommended for all users:

**macOS/Linux**:
```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate

# Install dependencies
pip3 install -r requirements.txt

# Deactivate when done
deactivate
```

**Windows**:
```cmd
# Create virtual environment
python -m venv venv

# Activate it
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Deactivate when done
deactivate
```

## Next Steps

After installation, see the main [README.md](../README.md) for usage instructions.

