#!/bin/bash
# Airis起動スクリプト - gRPC警告を抑制

# 環境変数を設定
export GRPC_VERBOSITY=ERROR
export GRPC_TRACE=""

# STDERRを一時的にフィルタリング用のプロセス置換を使用
exec 2> >(grep --line-buffered -v -e "WARNING: All log messages before absl::InitializeLog()" -e "ALTS creds ignored" -e "Unknown tracer" -e "alts_credentials.cc" -e "trace.cc" -e "E0000 00:00" >&2)

# Airisを起動
exec python3 -m airis.main

