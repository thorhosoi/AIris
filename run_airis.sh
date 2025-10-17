#!/bin/bash
# Airis起動スクリプト - gRPC警告を抑制

# gRPC警告メッセージを除外してAirisを起動
python3 -m airis.main 2>&1 | grep -v "WARNING: All log messages before absl::InitializeLog()" | grep -v "ALTS creds ignored" | grep -v "Unknown tracer"

