"""
Suppress gRPC/ALTS Warnings

This module must be imported before any google modules.
It filters stderr to remove gRPC/ALTS warning messages.
"""

import sys
import os


class StderrFilter:
    """Filter stderr to remove gRPC/ALTS warnings."""
    
    _instance = None
    _initialized = False
    
    def __new__(cls, original_stderr):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self, original_stderr):
        if not StderrFilter._initialized:
            self.original_stderr = original_stderr
            self.suppressed_patterns = [
                "WARNING: All log messages before absl::InitializeLog()",
                "ALTS creds ignored",
                "Unknown tracer",
                "alts_credentials.cc",
                "trace.cc",
                "E0000 00:00:",  # Generic gRPC error prefix
            ]
            StderrFilter._initialized = True
        
    def write(self, message):
        # Filter out specific warning messages
        if any(pattern in message for pattern in self.suppressed_patterns):
            return  # Suppress these messages
        self.original_stderr.write(message)
        
    def flush(self):
        self.original_stderr.flush()


def install_stderr_filter():
    """Install stderr filter to suppress gRPC warnings."""
    if not isinstance(sys.stderr, StderrFilter):
        sys.stderr = StderrFilter(sys.stderr)


def setup_environment():
    """Setup environment variables to suppress warnings."""
    # Set BEFORE any google/grpc imports
    os.environ['GRPC_VERBOSITY'] = 'ERROR'
    os.environ['GRPC_TRACE'] = ''
    os.environ['GRPC_ENABLE_FORK_SUPPORT'] = '1'
    os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'


# Auto-setup when this module is imported
setup_environment()
install_stderr_filter()

