#!/usr/bin/env python3
"""
Interactive CLI for Airis

Provides a REPL-style interface for multi-turn conversations with Airis.
"""

import sys
from airis.orchestrator import Orchestrator
from airis.interactive_mode import InteractiveOrchestrator
from airis.config import config
from airis.system_context import get_capability_info


def print_welcome():
    """Print welcome message."""
    print("=" * 70)
    print("  Airis - Interactive Mode")
    print("  対話型AIアシスタント")
    print("=" * 70)
    print("\n💬 対話モード: 常に有効")
    print("   - リクエストを入力すると自動的に要件確認が始まります")
    print("   - 'quick <リクエスト>' で即座実行（要件確認なし）")
    print("\nコマンド:")
    print("  リクエストを直接入力 - 対話モードで要件を詰める")
    print("  'quick <リクエスト>' - 即座に実行（要件確認なし）")
    print("  'project create <名前>' - プロジェクトを作成")
    print("  'project use <名前>' - プロジェクトを切り替え")
    print("  'ai engine info' - AI設定を確認")
    print("  'help' - ヘルプを表示")
    print("  'exit' / 'quit' - 終了")
    print("\n現在のプロジェクト:", config.get("current_project") or "未選択")
    print("=" * 70)


def print_help():
    """Print help message."""
    print("\n" + "=" * 70)
    print("Airis ヘルプ")
    print("=" * 70)
    print("\n【対話モード（デフォルト）】")
    print("  リクエストを直接入力")
    print("    例: 計算プログラムを作って")
    print("    → Airisが要件を確認する質問をします")
    print("    → 質問に答えて要件を詰めていきます")
    print("    → 要件確定後、自動的に実装開始")
    print("\n  対話モードは永続的です：")
    print("    - 一度開始すると、完了またはキャンセルまで継続")
    print("    - 複数ターンの会話で要件を明確化")
    print("    - 'execute' で実装開始")
    print("    - 'cancel' で対話を中止")
    print("\n【クイック実行モード】")
    print("  quick <リクエスト>")
    print("    例: quick web search: Docker best practices")
    print("    → 即座に実行（要件確認なし）")
    print("    → 単純なタスクや既知の操作に最適")
    print("\n【プロジェクト管理】")
    print("  project create <名前> - 新規プロジェクト作成")
    print("  project use <名前> - プロジェクト切り替え")
    print("  project list - プロジェクト一覧")
    print("\n【AI設定】")
    print("  ai engine info - AI設定を表示")
    print("  ai engine set default <engine> - デフォルトAIを変更")
    print("\n【その他】")
    print("  clear - 画面をクリア")
    print("  history - コマンド履歴")
    print("  exit / quit - 終了")
    print("=" * 70 + "\n")


def run_interactive_cli():
    """Run the interactive CLI."""
    print_welcome()
    
    orchestrator = Orchestrator()
    interactive_orch = InteractiveOrchestrator(orchestrator)
    command_history = []
    
    while True:
        try:
            # Check if in interactive session
            if interactive_orch.has_active_session():
                prompt_prefix = "Airis> (対話中) "
            else:
                current_project = config.get("current_project")
                if current_project:
                    prompt_prefix = f"Airis [{current_project}]> "
                else:
                    prompt_prefix = "Airis> "
            
            # Get user input
            user_input = input(prompt_prefix).strip()
            
            if not user_input:
                continue
            
            # Add to history
            command_history.append(user_input)
            
            # Handle commands
            lower_input = user_input.lower()
            
            # Exit commands
            if lower_input in ["exit", "quit", "終了"]:
                print("\nAirisを終了します。ありがとうございました！")
                break
            
            # Help command
            elif lower_input in ["help", "h", "ヘルプ"]:
                print_help()
                continue
            
            # About/Capabilities command
            elif lower_input in ["about", "info", "自己紹介", "機能", "capabilities"]:
                print("\n" + get_capability_info())
                print("詳細: 'help'コマンドでヘルプを表示\n")
                continue
            
            # Clear screen
            elif lower_input in ["clear", "cls"]:
                print("\033[2J\033[H")  # ANSI escape code to clear screen
                continue
            
            # Command history
            elif lower_input in ["history", "履歴"]:
                print("\n=== コマンド履歴 ===")
                for i, cmd in enumerate(command_history[-10:], 1):
                    print(f"{i}. {cmd}")
                print()
                continue
            
            # Check if user wants to start a new interactive session explicitly
            # (This is now the default behavior, but kept for backwards compatibility)
            elif user_input.startswith("interactive ") or user_input.startswith("対話 "):
                request = user_input.split(maxsplit=1)[1] if " " in user_input else ""
                if not request:
                    print("エラー: リクエストを指定してください")
                    print("例: 計算プログラムを作って（'interactive'は不要です）")
                    continue
                
                # Start interactive mode
                print("\n" + "=" * 70)
                print("💬 要件確認を開始します...")
                print("=" * 70 + "\n")
                
                response = interactive_orch.start_interactive_mode(request)
                print(response)
                print("\n" + "-" * 70)
                print("💡 質問に回答してください。")
                print("   'execute' または '実行': 要件確定後に実装開始")
                print("   'cancel' または 'キャンセル': 対話を中止")
                print("-" * 70 + "\n")
                continue
            
            # Quick execution mode
            elif user_input.startswith("quick ") or user_input.startswith("即実行 "):
                request = user_input.split(maxsplit=1)[1] if " " in user_input else ""
                if not request:
                    print("エラー: リクエストを指定してください")
                    continue
                
                print("\n" + "=" * 70)
                print("クイック実行モード...")
                print("=" * 70 + "\n")
                
                result, code = orchestrator.delegate_task(request)
                print("--- RESULT ---")
                print(result)
                if code:
                    print("\n--- GENERATED CODE ---")
                    print(code[:500] + "..." if len(code) > 500 else code)
                print("\n" + "=" * 70 + "\n")
                continue
            
            # Project management
            elif user_input.startswith("project ") or user_input.startswith("プロジェクト "):
                parts = user_input.split()
                if len(parts) < 2:
                    print("エラー: サブコマンドを指定してください")
                    print("使用例: project create my_app")
                    continue
                
                subcommand = parts[1].lower()
                
                if subcommand in ["create", "作成"] and len(parts) >= 3:
                    project_name = parts[2]
                    result, _ = orchestrator.delegate_task(f"create new project {project_name}")
                    print(result)
                
                elif subcommand in ["use", "切り替え", "switch"] and len(parts) >= 3:
                    project_name = parts[2]
                    result, _ = orchestrator.delegate_task(f"use project {project_name}")
                    print(result)
                
                elif subcommand in ["list", "一覧", "ls"]:
                    import os
                    projects_root = config.get("projects_root_dir", "projects")
                    if os.path.exists(projects_root):
                        projects = [d for d in os.listdir(projects_root) 
                                  if os.path.isdir(os.path.join(projects_root, d))]
                        print("\n=== プロジェクト一覧 ===")
                        for proj in projects:
                            marker = " (active)" if proj == config.get("current_project") else ""
                            print(f"  - {proj}{marker}")
                        print()
                    else:
                        print("プロジェクトディレクトリが見つかりません")
                
                else:
                    print("エラー: 不明なサブコマンド")
                    print("使用可能: create, use, list")
                
                continue
            
            # In interactive session
            elif interactive_orch.has_active_session():
                is_complete, response, execution_result = interactive_orch.process_user_input(user_input)
                
                print("\n" + response)
                
                if execution_result:
                    print("\n" + "=" * 70)
                    print("実行結果:")
                    print("=" * 70)
                    print(execution_result)
                
                if is_complete and not execution_result:
                    print("\n" + "=" * 70 + "\n")
                
                continue
            
            # Direct command execution (AI engine, etc.)
            elif user_input.startswith("ai engine"):
                result, _ = orchestrator.delegate_task(user_input)
                print("\n" + result + "\n")
                continue
            
            # Default: automatically start interactive mode
            else:
                # Start interactive mode automatically
                print("\n" + "=" * 70)
                print("💬 要件確認を開始します...")
                print("=" * 70 + "\n")
                
                response = interactive_orch.start_interactive_mode(user_input)
                print(response)
                print("\n" + "-" * 70)
                print("💡 質問に回答してください。")
                print("   'execute' または '実行': 要件確定後に実装開始")
                print("   'cancel' または 'キャンセル': 対話を中止")
                print("   ヒント: 即座に実行したい場合は 'quick <リクエスト>' を使用")
                print("-" * 70 + "\n")
                continue
        
        except KeyboardInterrupt:
            print("\n\n中断されました。'exit'で終了できます。\n")
            continue
        
        except EOFError:
            print("\n\nAirisを終了します。")
            break
        
        except Exception as e:
            print(f"\nエラーが発生しました: {str(e)}\n")
            continue


if __name__ == "__main__":
    run_interactive_cli()

