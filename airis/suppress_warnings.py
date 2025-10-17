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
            self.buffer = ""
            StderrFilter._initialized = True
        
    def write(self, message):
        # Accumulate message in buffer
        self.buffer += message
        
        # Check if we have complete lines
        if '\n' in self.buffer:
            lines = self.buffer.split('\n')
            # Keep incomplete line in buffer
            self.buffer = lines[-1]
            
            # Process complete lines
            for line in lines[:-1]:
                # Filter out specific warning messages
                if not any(pattern in line for pattern in self.suppressed_patterns):
                    self.original_stderr.write(line + '\n')
                    self.original_stderr.flush()
        
    def flush(self):
        # Flush any remaining buffered content
        if self.buffer:
            if not any(pattern in self.buffer for pattern in self.suppressed_patterns):
                self.original_stderr.write(self.buffer)
            self.buffer = ""
        self.original_stderr.flush()
    
    def isatty(self):
        """Check if underlying stderr is a TTY."""
        return self.original_stderr.isatty()
    
    def fileno(self):
        """Return file descriptor."""
        return self.original_stderr.fileno()


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

