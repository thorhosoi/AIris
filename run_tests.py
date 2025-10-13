#!/usr/bin/env python3
"""
Airis 総合テスト実行スクリプト

このスクリプトは、Airis v2.1.0の全機能を自動的にテストします。
"""

import subprocess
import time
import json
import os
from datetime import datetime
from typing import Dict, List, Tuple

class AirisTester:
    def __init__(self):
        self.results = []
        self.start_time = datetime.now()
        self.docker_cmd = "echo y | docker-compose run -T --rm airis python3 -m airis.main"
        
    def run_test(self, test_id: str, test_name: str, command: str, expected_keywords: List[str] = None) -> Dict:
        """単一テストを実行"""
        print(f"\n{'='*60}")
        print(f"テスト実行: {test_id} - {test_name}")
        print(f"コマンド: {command}")
        print(f"{'='*60}")
        
        start_time = time.time()
        
        try:
            # Dockerコマンドを実行
            full_command = f"{self.docker_cmd} \"{command}\""
            result = subprocess.run(
                full_command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=60  # 60秒でタイムアウト
            )
            
            execution_time = time.time() - start_time
            success = result.returncode == 0
            
            # 期待されるキーワードのチェック
            if expected_keywords and success:
                output_text = result.stdout.lower()
                for keyword in expected_keywords:
                    if keyword.lower() not in output_text:
                        success = False
                        break
            
            test_result = {
                "test_id": test_id,
                "test_name": test_name,
                "command": command,
                "success": success,
                "execution_time": execution_time,
                "return_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "timestamp": datetime.now().isoformat()
            }
            
            status = "✅ PASS" if success else "❌ FAIL"
            print(f"結果: {status} ({execution_time:.2f}秒)")
            
            if not success:
                print(f"エラー出力: {result.stderr}")
            
            return test_result
            
        except subprocess.TimeoutExpired:
            execution_time = time.time() - start_time
            test_result = {
                "test_id": test_id,
                "test_name": test_name,
                "command": command,
                "success": False,
                "execution_time": execution_time,
                "return_code": -1,
                "stdout": "",
                "stderr": "Timeout after 60 seconds",
                "timestamp": datetime.now().isoformat()
            }
            
            print(f"結果: ⏰ TIMEOUT ({execution_time:.2f}秒)")
            return test_result
            
        except Exception as e:
            execution_time = time.time() - start_time
            test_result = {
                "test_id": test_id,
                "test_name": test_name,
                "command": command,
                "success": False,
                "execution_time": execution_time,
                "return_code": -1,
                "stdout": "",
                "stderr": str(e),
                "timestamp": datetime.now().isoformat()
            }
            
            print(f"結果: 💥 ERROR ({execution_time:.2f}秒) - {str(e)}")
            return test_result
    
    def run_ai_engine_tests(self):
        """AIエンジン選択システムのテスト"""
        print("\n🤖 AIエンジン選択システムテスト開始")
        
        tests = [
            ("AI-001", "デフォルトエンジン設定", "ai engine set default gemini", ["default engine set to: gemini"]),
            ("AI-002", "タスク別エンジン設定", "ai engine set task code_generation cursor", ["task", "cursor"]),
            ("AI-003", "エンジン情報表示", "ai engine info", ["ai engine information", "default engine"]),
            ("AI-004", "設定保存", "ai engine save", ["configuration saved"]),
            ("AI-006", "コンプライアンスモード有効化", "ai engine enable compliance gemini local", ["compliance mode enabled"]),
            ("AI-007", "コンプライアンスモード無効化", "ai engine disable compliance", ["compliance mode disabled"]),
            ("AI-009", "コスト最適化モード有効化", "ai engine enable cost optimization", ["cost optimization enabled"]),
        ]
        
        for test_id, test_name, command, expected_keywords in tests:
            result = self.run_test(test_id, test_name, command, expected_keywords)
            self.results.append(result)
    
    def run_agent_tests(self):
        """各エージェントのテスト"""
        print("\n🔧 エージェント機能テスト開始")
        
        tests = [
            # コード生成テスト
            ("CODE-001", "基本コード生成", "code generate fibonacci function", ["fibonacci", "function"]),
            ("CODE-002", "複雑なコード生成", "code generate web scraper", ["scraper", "requests"]),
            
            # Cursorエージェントテスト
            ("CURSOR-001", "Cursorコード生成", "code generate calculator", ["cursor", "calculator"]),
            ("CURSOR-003", "Cursorバージョン確認", "cursor version", ["cursor", "version"]),
            
            # Geminiエージェントテスト
            ("GEMINI-001", "Geminiコード分析", "gemini analyze code", ["gemini", "analyze"]),
            
            # Web検索テスト
            ("WEB-001", "基本Web検索", "search Python best practices", ["search", "python"]),
            ("WEB-002", "日本語Web検索", "search 機械学習 最新技術", ["search", "機械学習"]),
            
            # Webブラウジングテスト
            ("BROWSE-001", "URL取得", "browse https://github.com", ["github", "browse"]),
            
            # Gitエージェントテスト
            ("GIT-001", "Git状態確認", "git status", ["git", "status"]),
            ("GIT-002", "Git自動ワークフロー", "git auto", ["git", "auto"]),
            
            # シェルエージェントテスト
            ("SHELL-001", "基本シェルコマンド", "shell ls -la", ["ls", "total"]),
        ]
        
        for test_id, test_name, command, expected_keywords in tests:
            result = self.run_test(test_id, test_name, command, expected_keywords)
            self.results.append(result)
    
    def run_project_tests(self):
        """プロジェクト管理機能のテスト"""
        print("\n📁 プロジェクト管理機能テスト開始")
        
        tests = [
            ("PROJ-001", "プロジェクト作成", "create project test_project", ["project", "created"]),
            ("PROJ-002", "プロジェクト切り替え", "switch project test_project", ["project", "switched"]),
            ("PROJ-003", "プロジェクト一覧", "list projects", ["projects", "list"]),
        ]
        
        for test_id, test_name, command, expected_keywords in tests:
            result = self.run_test(test_id, test_name, command, expected_keywords)
            self.results.append(result)
    
    def run_document_tests(self):
        """ドキュメント生成機能のテスト"""
        print("\n📄 ドキュメント生成機能テスト開始")
        
        tests = [
            ("DOC-001", "要件定義書生成", "generate requirements", ["requirements", "要件"]),
            ("DOC-002", "設計書生成", "generate design", ["design", "設計"]),
            ("DOC-003", "README生成", "generate readme", ["readme", "readme"]),
        ]
        
        for test_id, test_name, command, expected_keywords in tests:
            result = self.run_test(test_id, test_name, command, expected_keywords)
            self.results.append(result)
    
    def run_integration_tests(self):
        """統合テスト"""
        print("\n🔗 統合テスト開始")
        
        tests = [
            ("E2E-001", "完全な開発サイクル", "create project integration_test && code generate hello world && generate requirements", ["project", "hello", "requirements"]),
            ("E2E-002", "複数エージェント連携", "search Python tutorial && code generate example", ["search", "python", "code"]),
        ]
        
        for test_id, test_name, command, expected_keywords in tests:
            result = self.run_test(test_id, test_name, command, expected_keywords)
            self.results.append(result)
    
    def generate_report(self):
        """テスト結果レポートを生成"""
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if r["success"])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        total_time = (datetime.now() - self.start_time).total_seconds()
        
        print(f"\n{'='*80}")
        print("📊 テスト結果サマリー")
        print(f"{'='*80}")
        print(f"総テスト数: {total_tests}")
        print(f"成功: {passed_tests} ✅")
        print(f"失敗: {failed_tests} ❌")
        print(f"成功率: {success_rate:.1f}%")
        print(f"総実行時間: {total_time:.2f}秒")
        
        # 失敗したテストの詳細
        if failed_tests > 0:
            print(f"\n❌ 失敗したテスト:")
            for result in self.results:
                if not result["success"]:
                    print(f"  - {result['test_id']}: {result['test_name']}")
                    if result["stderr"]:
                        print(f"    エラー: {result['stderr'][:100]}...")
        
        # 結果をJSONファイルに保存
        report_data = {
            "summary": {
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "failed_tests": failed_tests,
                "success_rate": success_rate,
                "total_time": total_time,
                "start_time": self.start_time.isoformat(),
                "end_time": datetime.now().isoformat()
            },
            "results": self.results
        }
        
        report_file = f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2)
        
        print(f"\n📄 詳細レポート: {report_file}")
        
        return success_rate >= 80  # 80%以上の成功率で合格
    
    def run_all_tests(self):
        """全テストを実行"""
        print("🚀 Airis 総合テスト開始")
        print(f"開始時刻: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        try:
            # 各テストカテゴリを実行
            self.run_ai_engine_tests()
            self.run_agent_tests()
            self.run_project_tests()
            self.run_document_tests()
            self.run_integration_tests()
            
            # レポート生成
            success = self.generate_report()
            
            if success:
                print("\n🎉 テスト完了: 合格")
                return 0
            else:
                print("\n⚠️ テスト完了: 不合格")
                return 1
                
        except KeyboardInterrupt:
            print("\n⏹️ テスト中断")
            return 1
        except Exception as e:
            print(f"\n💥 テストエラー: {str(e)}")
            return 1

def main():
    """メイン関数"""
    tester = AirisTester()
    exit_code = tester.run_all_tests()
    exit(exit_code)

if __name__ == "__main__":
    main()
