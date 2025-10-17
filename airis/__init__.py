"""
Airis Package

Suppress warnings before any other imports.
"""

# CRITICAL: Import suppress_warnings FIRST
from airis.suppress_warnings import setup_environment, install_stderr_filter

# Setup environment and install filter
setup_environment()
install_stderr_filter()

