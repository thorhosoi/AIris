# Airis 機能ガイド

## バージョン情報

| 項目 | 内容 |
|------|------|
| 作成日 | 2025-10-13 |
| バージョン | 2.1.0 |
| 対象 | Airis 全機能 |
| 作成者 | AIris Development Team |

---

## 1. 概要

Airisは、複数のAIエンジンを統合した自律的なAIワークフォースプラットフォームです。ユーザーの高レベルなタスクを分析し、適切なAIエージェントに委譲して実行します。

---

## 2. 基本使用方法

### 2.1 起動方法
```bash
# Docker環境での起動
cd /path/to/AIris
echo y | docker-compose run -T --rm airis python3 -m airis.main "コマンド"
```

### 2.2 基本コマンド形式
```bash
python3 -m airis.main "タスクの説明"
```

---

## 3. AIエンジン選択システム

### 3.1 概要
ユーザーがAIエンジンを自由に選択・設定できる柔軟なシステムです。コンプライアンス要件やコスト最適化に対応します。

### 3.2 利用可能なエンジン
- **Claude (Anthropic)**: 高品質なコード生成とドキュメント作成
- **Gemini (Google)**: コード分析とドキュメント改善
- **Cursor**: 専門的なコード生成（AIアシスタント付き）
- **Web Search**: リアルタイム情報検索
- **Web Browser**: URLからのコンテンツ取得・要約
- **Local**: シェルコマンドとGit操作

### 3.3 基本設定コマンド

#### デフォルトエンジン設定
```bash
# デフォルトエンジンをGeminiに設定
echo y | docker-compose run -T --rm airis python3 -m airis.main "ai engine set default gemini"

# デフォルトエンジンをClaudeに設定
echo y | docker-compose run -T --rm airis python3 -m airis.main "ai engine set default claude"
```

#### タスク別エンジン設定
```bash
# コード生成をCursorに設定
echo y | docker-compose run -T --rm airis python3 -m airis.main "ai engine set task code_generation cursor"

# ドキュメント生成をClaudeに設定
echo y | docker-compose run -T --rm airis python3 -m airis.main "ai engine set task document_generation claude"

# コード分析をGeminiに設定
echo y | docker-compose run -T --rm airis python3 -m airis.main "ai engine set task code_analysis gemini"
```

#### 設定確認
```bash
# 現在の設定を表示
echo y | docker-compose run -T --rm airis python3 -m airis.main "ai engine info"
```

### 3.4 コンプライアンスモード

#### 有効化
```bash
# GeminiとLocalのみを許可
echo y | docker-compose run -T --rm airis python3 -m airis.main "ai engine enable compliance gemini local"

# ClaudeとGeminiのみを許可
echo y | docker-compose run -T --rm airis python3 -m airis.main "ai engine enable compliance claude gemini"
```

#### 無効化
```bash
echo y | docker-compose run -T --rm airis python3 -m airis.main "ai engine disable compliance"
```

### 3.5 コスト最適化モード

#### 有効化
```bash
echo y | docker-compose run -T --rm airis python3 -m airis.main "ai engine enable cost optimization"
```

#### 動作
- **高複雑度タスク**: Claude（高品質）
- **中複雑度タスク**: Gemini（中品質・中コスト）
- **低複雑度タスク**: Web検索（低コスト）
- **無料タスク**: Local（無料）

### 3.6 設定管理

#### 設定保存
```bash
echo y | docker-compose run -T --rm airis python3 -m airis.main "ai engine save"
```

#### 設定リセット
```bash
echo y | docker-compose run -T --rm airis python3 -m airis.main "ai engine reset"
```

---

## 4. コード生成機能

### 4.1 基本コード生成
```bash
# フィボナッチ関数の生成
echo y | docker-compose run -T --rm airis python3 -m airis.main "code generate fibonacci function"

# 計算機の生成
echo y | docker-compose run -T --rm airis python3 -m airis.main "code generate calculator"

# Webスクレイパーの生成
echo y | docker-compose run -T --rm airis python3 -m airis.main "code generate web scraper"
```

### 4.2 複雑なコード生成
```bash
# データベース接続クラス
echo y | docker-compose run -T --rm airis python3 -m airis.main "code generate database connection class"

# REST API エンドポイント
echo y | docker-compose run -T --rm airis python3 -m airis.main "code generate REST API endpoints"

# 機械学習モデル
echo y | docker-compose run -T --rm airis python3 -m airis.main "code generate machine learning model"
```

### 4.3 コード生成の特徴
- **自動ファイル保存**: 生成されたコードは自動的にファイルに保存
- **エラーハンドリング**: 適切なエラーハンドリングを含む
- **型ヒント**: Pythonの型ヒントを適切に使用
- **ドキュメント**: コメントとdocstringを含む

---

## 5. Cursor統合機能

### 5.1 ファイル操作
```bash
# ファイルをCursorで開く
echo y | docker-compose run -T --rm airis python3 -m airis.main "cursor open filename.py"

# Cursorバージョン確認
echo y | docker-compose run -T --rm airis python3 -m airis.main "cursor version"
```

### 5.2 コード生成（Cursor）
```bash
# Cursorでコード生成
echo y | docker-compose run -T --rm airis python3 -m airis.main "code generate hello world"
```

### 5.3 Cursorの特徴
- **AIアシスタント**: CursorのAI機能を活用
- **リアルタイム編集**: 生成されたコードを即座に編集可能
- **コンテキスト理解**: プロジェクト全体のコンテキストを理解

---

## 6. Gemini統合機能

### 6.1 コード分析
```bash
# コードの分析
echo y | docker-compose run -T --rm airis python3 -m airis.main "gemini analyze code"

# 特定のファイルの分析
echo y | docker-compose run -T --rm airis python3 -m airis.main "gemini analyze file.py"
```

### 6.2 ドキュメント改善
```bash
# ドキュメントの改善提案
echo y | docker-compose run -T --rm airis python3 -m airis.main "gemini improve document"

# コードの改善提案
echo y | docker-compose run -T --rm airis python3 -m airis.main "gemini improve code"
```

---

## 7. Web検索機能

### 7.1 基本検索
```bash
# Pythonのベストプラクティスを検索
echo y | docker-compose run -T --rm airis python3 -m airis.main "search Python best practices"

# Dockerの最新情報を検索
echo y | docker-compose run -T --rm airis python3 -m airis.main "search Docker latest features 2024"
```

### 7.2 日本語検索
```bash
# 日本語での検索
echo y | docker-compose run -T --rm airis python3 -m airis.main "search 機械学習 最新技術"

# 日本の技術情報を検索
echo y | docker-compose run -T --rm airis python3 -m airis.main "search 日本 AI 開発"
```

### 7.3 検索の特徴
- **リアルタイム情報**: 最新の情報を取得
- **要約機能**: 検索結果を自動要約
- **多言語対応**: 日本語と英語の検索に対応

---

## 8. Webブラウジング機能

### 8.1 URL取得
```bash
# GitHubの内容を取得
echo y | docker-compose run -T --rm airis python3 -m airis.main "browse https://github.com"

# 技術ブログの内容を取得
echo y | docker-compose run -T --rm airis python3 -m airis.main "browse https://example.com/blog"
```

### 8.2 コンテンツ要約
```bash
# 長い記事の要約
echo y | docker-compose run -T --rm airis python3 -m airis.main "browse https://long-article.com"
```

### 8.3 ブラウジングの特徴
- **HTML解析**: BeautifulSoupを使用した高精度な解析
- **自動要約**: 取得したコンテンツを自動要約
- **エラーハンドリング**: ネットワークエラーやタイムアウトに対応

---

## 9. Git管理機能

### 9.1 基本Git操作
```bash
# Git状態確認
echo y | docker-compose run -T --rm airis python3 -m airis.main "git status"

# ファイル追加
echo y | docker-compose run -T --rm airis python3 -m airis.main "git add filename.py"

# コミット
echo y | docker-compose run -T --rm airis python3 -m airis.main "git commit 'Add new feature'"

# プッシュ
echo y | docker-compose run -T --rm airis python3 -m airis.main "git push"
```

### 9.2 自動ワークフロー
```bash
# 自動でadd, commit, pushを実行
echo y | docker-compose run -T --rm airis python3 -m airis.main "git auto"
```

### 9.3 Git機能の特徴
- **自動設定**: 初回実行時にgit設定を自動化
- **メッセージエスケープ**: 特殊文字を含むコミットメッセージに対応
- **エラーハンドリング**: Git操作のエラーを適切に処理

---

## 10. シェルコマンド機能

### 10.1 基本コマンド
```bash
# ディレクトリ一覧
echo y | docker-compose run -T --rm airis python3 -m airis.main "shell ls -la"

# ファイル検索
echo y | docker-compose run -T --rm airis python3 -m airis.main "shell find . -name '*.py'"

# システム情報
echo y | docker-compose run -T --rm airis python3 -m airis.main "shell uname -a"
```

### 10.2 複雑なコマンド
```bash
# パイプラインコマンド
echo y | docker-compose run -T --rm airis python3 -m airis.main "shell ps aux | grep python"

# ファイル操作
echo y | docker-compose run -T --rm airis python3 -m airis.main "shell tar -czf backup.tar.gz project/"
```

---

## 11. プロジェクト管理機能

### 11.1 プロジェクト作成・管理
```bash
# 新しいプロジェクトを作成
echo y | docker-compose run -T --rm airis python3 -m airis.main "create project my_new_project"

# プロジェクトを切り替え
echo y | docker-compose run -T --rm airis python3 -m airis.main "switch project my_new_project"

# プロジェクト一覧を表示
echo y | docker-compose run -T --rm airis python3 -m airis.main "list projects"
```

### 11.2 プロジェクト構造
```
projects/
├── my_new_project/
│   ├── doc/
│   │   ├── 01_requirements.md
│   │   ├── 02_design.md
│   │   └── README.md
│   └── src/
│       └── [生成されたコード]
```

---

## 12. ドキュメント生成機能

### 12.1 要件定義書生成
```bash
# 要件定義書を生成
echo y | docker-compose run -T --rm airis python3 -m airis.main "generate requirements"
```

### 12.2 設計書生成
```bash
# 設計書を生成
echo y | docker-compose run -T --rm airis python3 -m airis.main "generate design"
```

### 12.3 README生成
```bash
# READMEを生成
echo y | docker-compose run -T --rm airis python3 -m airis.main "generate readme"
```

### 12.4 ドキュメントの特徴
- **日本語生成**: 全てのドキュメントが日本語で生成
- **標準化された構造**: 一貫したフォーマット
- **自動完成**: 不完全なドキュメントを自動完成
- **プロジェクト連動**: 現在のプロジェクトに基づいて生成

---

## 13. 統合機能

### 13.1 完全な開発サイクル
```bash
# プロジェクト作成からドキュメント生成まで
echo y | docker-compose run -T --rm airis python3 -m airis.main "create project full_cycle && code generate hello world && generate requirements"
```

### 13.2 複数エージェント連携
```bash
# Web検索→コード生成の連携
echo y | docker-compose run -T --rm airis python3 -m airis.main "search Python tutorial && code generate example"
```

### 13.3 自動Git管理
```bash
# コード生成後に自動でGit管理
echo y | docker-compose run -T --rm airis python3 -m airis.main "code generate feature && git auto"
```

---

## 14. 設定ファイル

### 14.1 config.yaml
```yaml
current_project: final_test_project

# AI Engine Selection Configuration
ai_engines:
  allowed_engines:
  - gemini
  - local
  compliance_mode: false
  cost_optimization: true
  cost_preferences:
    free: local
    high_cost: claude
    low_cost: web_search
    medium_cost: gemini
  default_engine: gemini
  task_routing:
    code_analysis: gemini
    code_generation: cursor
    document_generation: claude
    git_operations: local
    shell_operations: local
    web_browsing: web_browser
    web_search: web_search

# Cursor configuration
cursor:
  api_url: http://localhost:5000
  code_generation: true
  max_tokens: 4000
  path: cursor  # macOS: /Applications/Cursor.app/Contents/Resources/app/bin/cursor
  temperature: 0.1

# Gemini configuration
gemini:
  max_tokens: 4000
  temperature: 0.1

# LLM configuration
llm:
  max_tokens: 4000
  model_name: claude-sonnet-4-5-20250929
  provider: anthropic
  temperature: 0.1

# Project configuration
projects_root_dir: projects
script_output_dir: generated_scripts
```

### 14.2 環境変数 (.env)
```bash
ANTHROPIC_API_KEY=your_anthropic_api_key
GEMINI_API_KEY=your_gemini_api_key
CURSOR_API_KEY=your_cursor_api_key
```

---

## 15. 使用例

### 15.1 基本的な使用例
```bash
# 1. プロジェクト作成
echo y | docker-compose run -T --rm airis python3 -m airis.main "create project my_app"

# 2. コード生成
echo y | docker-compose run -T --rm airis python3 -m airis.main "code generate web application"

# 3. ドキュメント生成
echo y | docker-compose run -T --rm airis python3 -m airis.main "generate requirements"

# 4. Git管理
echo y | docker-compose run -T --rm airis python3 -m airis.main "git auto"
```

### 15.2 高度な使用例
```bash
# 1. 技術調査
echo y | docker-compose run -T --rm airis python3 -m airis.main "search React best practices 2024"

# 2. コード分析
echo y | docker-compose run -T --rm airis python3 -m airis.main "gemini analyze code"

# 3. 複雑なコード生成
echo y | docker-compose run -T --rm airis python3 -m airis.main "code generate microservices architecture"

# 4. ドキュメント改善
echo y | docker-compose run -T --rm airis python3 -m airis.main "gemini improve document"
```

### 15.3 コンプライアンス対応例
```bash
# 1. コンプライアンスモード有効化
echo y | docker-compose run -T --rm airis python3 -m airis.main "ai engine enable compliance gemini local"

# 2. 制限された環境での開発
echo y | docker-compose run -T --rm airis python3 -m airis.main "code generate secure application"
```

---

## 16. トラブルシューティング

### 16.1 よくある問題

#### Dockerエラー
```bash
# Dockerコンテナの再起動
docker-compose down
docker-compose up -d
```

#### APIキーエラー
```bash
# 環境変数の確認
cat .env
```

#### パスエラー
```bash
# 現在のディレクトリ確認
pwd
```

### 16.2 ログ確認
```bash
# 詳細なログを確認
echo y | docker-compose run -T --rm airis python3 -m airis.main "ai engine info"
```

---

## 17. ベストプラクティス

### 17.1 効率的な使用方法
1. **プロジェクト単位での管理**: 関連するタスクは同じプロジェクトで実行
2. **適切なエンジン選択**: タスクに応じて最適なエンジンを選択
3. **定期的なGit管理**: 変更は定期的にコミット・プッシュ

### 17.2 コスト最適化
1. **コスト最適化モードの活用**: 簡単なタスクは低コストエンジンを使用
2. **キャッシュの活用**: 同じようなタスクは結果を再利用
3. **バッチ処理**: 複数のタスクをまとめて実行

### 17.3 セキュリティ
1. **APIキーの管理**: 環境変数で安全に管理
2. **コンプライアンスモード**: 企業ポリシーに準拠した設定
3. **サンドボックス環境**: Dockerコンテナ内での安全な実行

---

## 18. 更新履歴

### v2.1.0 (2025-10-13)
- AIエンジン選択システムの追加
- Cursor統合の強化
- コンプライアンスモードの追加
- コスト最適化モードの追加

### v2.0.0 (2025-10-13)
- Web検索・ブラウジング機能の追加
- ドキュメント生成機能の追加
- Git管理機能の追加
- 日本語対応の強化

---

**文書管理情報**
- 作成者: AIris Development Team
- 最終更新: 2025-10-13
- バージョン: 1.0
