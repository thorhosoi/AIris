#!/bin/bash
# Airis起動スクリプト - gRPC警告を抑制

# 環境変数を設定
export GRPC_VERBOSITY=ERROR
export GRPC_TRACE=""

# gRPC警告メッセージを除外してAirisを起動
python3 -m airis.main 2>&1 | grep -v "WARNING: All log messages before absl::InitializeLog()" | grep -v "ALTS creds ignored" | grep -v "Unknown tracer" | grep -v "alts_credentials.cc" | grep -v "trace.cc" | grep -v "E0000 00:00"

