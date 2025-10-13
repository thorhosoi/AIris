#!/bin/bash

# Airis 手動試験実行スクリプト
# このスクリプトは手動試験の手順を自動化し、結果を記録します

set -e

# 色付き出力の定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# ログファイルの設定
LOG_DIR="manual_test_logs"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
LOG_FILE="${LOG_DIR}/manual_test_${TIMESTAMP}.log"
RESULT_FILE="${LOG_DIR}/manual_test_results_${TIMESTAMP}.json"

# ログディレクトリの作成
mkdir -p "$LOG_DIR"

# ログ関数
log() {
    echo -e "$1" | tee -a "$LOG_FILE"
}

# テスト実行関数
run_test() {
    local test_id="$1"
    local test_name="$2"
    local command="$3"
    local expected_keywords="$4"
    
    log "\n${BLUE}============================================================${NC}"
    log "${BLUE}テスト実行: $test_id - $test_name${NC}"
    log "${BLUE}コマンド: $command${NC}"
    log "${BLUE}============================================================${NC}"
    
    local start_time=$(date +%s)
    local result="FAIL"
    local error_message=""
    
    # コマンド実行
    if output=$(echo y | docker-compose run -T --rm airis python3 -m airis.main "$command" 2>&1); then
        # 期待されるキーワードのチェック
        if [ -n "$expected_keywords" ]; then
            local keyword_found=true
            IFS=',' read -ra keywords <<< "$expected_keywords"
            for keyword in "${keywords[@]}"; do
                if ! echo "$output" | grep -qi "$keyword"; then
                    keyword_found=false
                    break
                fi
            done
            
            if [ "$keyword_found" = true ]; then
                result="PASS"
            fi
        else
            result="PASS"
        fi
    else
        error_message="$output"
    fi
    
    local end_time=$(date +%s)
    local execution_time=$((end_time - start_time))
    
    # 結果表示
    if [ "$result" = "PASS" ]; then
        log "${GREEN}結果: ✅ PASS (${execution_time}秒)${NC}"
    else
        log "${RED}結果: ❌ FAIL (${execution_time}秒)${NC}"
        if [ -n "$error_message" ]; then
            log "${RED}エラー: $error_message${NC}"
        fi
    fi
    
    # JSON結果に追加
    echo "  {
    \"test_id\": \"$test_id\",
    \"test_name\": \"$test_name\",
    \"command\": \"$command\",
    \"result\": \"$result\",
    \"execution_time\": $execution_time,
    \"error_message\": \"$error_message\",
    \"timestamp\": \"$(date -Iseconds)\"
  }," >> "$RESULT_FILE.tmp"
}

# メイン関数
main() {
    log "${GREEN}🚀 Airis 手動試験開始${NC}"
    log "開始時刻: $(date)"
    log "ログファイル: $LOG_FILE"
    log "結果ファイル: $RESULT_FILE"
    
    # JSON結果ファイルの初期化
    echo "{
  \"test_session\": {
    \"start_time\": \"$(date -Iseconds)\",
    \"version\": \"2.1.0\",
    \"tester\": \"$(whoami)\"
  },
  \"results\": [" > "$RESULT_FILE.tmp"
    
    # 1. AIエンジン選択システム試験
    log "\n${YELLOW}🤖 AIエンジン選択システム試験開始${NC}"
    
    run_test "AI-001" "デフォルトエンジン設定" "ai engine set default gemini" "default engine set to: gemini"
    run_test "AI-002" "タスク別エンジン設定" "ai engine set task code_generation cursor" "task,cursor"
    run_test "AI-003" "エンジン情報表示" "ai engine info" "ai engine information,default engine"
    run_test "AI-004" "設定保存" "ai engine save" "configuration saved"
    run_test "AI-006" "コンプライアンスモード有効化" "ai engine enable compliance gemini local" "compliance mode enabled"
    run_test "AI-007" "制限されたエンジンでのタスク実行" "code generate hello world" "hello,world"
    run_test "AI-008" "コンプライアンスモード無効化" "ai engine disable compliance" "compliance mode disabled"
    run_test "AI-009" "コスト最適化モード有効化" "ai engine enable cost optimization" "cost optimization enabled"
    
    # 2. エージェント機能試験
    log "\n${YELLOW}🔧 エージェント機能試験開始${NC}"
    
    # コード生成エージェント
    run_test "CODE-001" "基本コード生成" "code generate fibonacci function" "fibonacci,function"
    run_test "CODE-002" "複雑なコード生成" "code generate web scraper" "scraper,requests"
    
    # Cursorエージェント
    run_test "CURSOR-001" "Cursorバージョン確認" "cursor version" "cursor,version"
    run_test "CURSOR-002" "Cursorコード生成" "code generate calculator" "calculator"
    
    # Geminiエージェント
    run_test "GEMINI-001" "Geminiコード分析" "gemini analyze code" "gemini,analyze"
    
    # Web検索エージェント
    run_test "WEB-001" "基本Web検索" "search Python best practices" "search,python"
    run_test "WEB-002" "日本語Web検索" "search 機械学習 最新技術" "search,機械学習"
    
    # Webブラウジングエージェント
    run_test "BROWSE-001" "URL取得" "browse https://github.com" "github,browse"
    
    # Gitエージェント
    run_test "GIT-001" "Git状態確認" "git status" "git,status"
    run_test "GIT-002" "Git自動ワークフロー" "git auto" "git,auto"
    
    # シェルエージェント
    run_test "SHELL-001" "基本シェルコマンド" "shell ls -la" "ls,total"
    
    # 3. プロジェクト管理機能試験
    log "\n${YELLOW}📁 プロジェクト管理機能試験開始${NC}"
    
    run_test "PROJ-001" "プロジェクト作成" "create project manual_test_$(date +%s)" "project,created"
    run_test "PROJ-002" "プロジェクト一覧" "list projects" "projects,list"
    
    # 4. ドキュメント生成機能試験
    log "\n${YELLOW}📄 ドキュメント生成機能試験開始${NC}"
    
    run_test "DOC-001" "要件定義書生成" "generate requirements" "requirements,要件"
    run_test "DOC-002" "設計書生成" "generate design" "design,設計"
    run_test "DOC-003" "README生成" "generate readme" "readme"
    
    # 5. 統合テスト
    log "\n${YELLOW}🔗 統合テスト開始${NC}"
    
    run_test "E2E-001" "完全な開発サイクル" "create project e2e_test_$(date +%s) && code generate hello world && generate requirements" "project,hello,requirements"
    run_test "E2E-002" "複数エージェント連携" "search Python tutorial && code generate example" "search,python,code"
    
    # JSON結果ファイルの完了
    # 最後のカンマを削除
    sed -i '$ s/,$//' "$RESULT_FILE.tmp"
    echo "  ],
  \"summary\": {
    \"total_tests\": $(grep -c "test_id" "$RESULT_FILE.tmp"),
    \"passed_tests\": $(grep -c "\"result\": \"PASS\"" "$RESULT_FILE.tmp"),
    \"failed_tests\": $(grep -c "\"result\": \"FAIL\"" "$RESULT_FILE.tmp"),
    \"end_time\": \"$(date -Iseconds)\"
  }
}" >> "$RESULT_FILE.tmp"
    
    # 一時ファイルを最終ファイルに移動
    mv "$RESULT_FILE.tmp" "$RESULT_FILE"
    
    # 結果サマリー
    local total_tests=$(grep -c "test_id" "$RESULT_FILE")
    local passed_tests=$(grep -c "\"result\": \"PASS\"" "$RESULT_FILE")
    local failed_tests=$(grep -c "\"result\": \"FAIL\"" "$RESULT_FILE")
    local success_rate=$((passed_tests * 100 / total_tests))
    
    log "\n${BLUE}================================================================================${NC}"
    log "${BLUE}📊 試験結果サマリー${NC}"
    log "${BLUE}================================================================================${NC}"
    log "総試験数: $total_tests"
    log "成功: $passed_tests ✅"
    log "失敗: $failed_tests ❌"
    log "成功率: $success_rate%"
    log "ログファイル: $LOG_FILE"
    log "結果ファイル: $RESULT_FILE"
    
    if [ $success_rate -ge 80 ]; then
        log "\n${GREEN}🎉 試験完了: 合格${NC}"
        exit 0
    else
        log "\n${RED}⚠️ 試験完了: 不合格${NC}"
        exit 1
    fi
}

# スクリプト実行
main "$@"
