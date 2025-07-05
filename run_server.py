#!/usr/bin/env python3
"""Direct runner for Yamcs MCP Server without uv."""

import sys
import os
import subprocess
from pathlib import Path

def check_python_version():
    """Ensure Python 3.12+ is being used."""
    if sys.version_info < (3, 12):
        print(f"Error: Python 3.12+ required, but {sys.version} found", file=sys.stderr)
        sys.exit(1)

def setup_environment():
    """Set up the Python environment."""
    venv_path = Path(".venv")
    
    if not venv_path.exists():
        print("Creating virtual environment...", file=sys.stderr)
        subprocess.run([sys.executable, "-m", "venv", ".venv"], check=True)
        
        # Install dependencies
        pip_path = venv_path / "bin" / "pip" if os.name != "nt" else venv_path / "Scripts" / "pip"
        print("Installing dependencies...", file=sys.stderr)
        subprocess.run([str(pip_path), "install", "-e", "."], check=True)

def run_server():
    """Run the MCP server."""
    # Add src to Python path
    src_path = Path(__file__).parent / "src"
    sys.path.insert(0, str(src_path))
    
    # Import and run the server
    try:
        from yamcs_mcp.server import main
        main()
    except ImportError as e:
        print(f"Error importing server: {e}", file=sys.stderr)
        print("Please ensure dependencies are installed:", file=sys.stderr)
        print("  pip install -e .", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    check_python_version()
    # setup_environment()  # Uncomment to auto-setup environment
    run_server()