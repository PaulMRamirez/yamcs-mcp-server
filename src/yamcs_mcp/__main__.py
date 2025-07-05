"""Allow yamcs_mcp to be run as a module with python -m yamcs_mcp."""

from .server import main

if __name__ == "__main__":
    main()
