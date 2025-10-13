# Airis 機能一覧

## 🚀 基本機能

### AIエンジン選択システム
- **デフォルトエンジン設定**: `ai engine set default <engine>`
- **タスク別エンジン設定**: `ai engine set task <task_type> <engine>`
- **コンプライアンスモード**: `ai engine enable compliance <engines>`
- **コスト最適化モード**: `ai engine enable cost optimization`
- **設定管理**: `ai engine info`, `ai engine save`, `ai engine reset`

### 利用可能なAIエンジン
- **Claude (Anthropic)**: 高品質コード生成・ドキュメント作成
- **Gemini (Google)**: コード分析・ドキュメント改善
- **Cursor**: 専門的コード生成（AIアシスタント付き）
- **Web Search**: リアルタイム情報検索
- **Web Browser**: URLコンテンツ取得・要約
- **Local**: シェルコマンド・Git操作

## 🔧 エージェント機能

### コード生成
```bash
# 基本コード生成
code generate fibonacci function
code generate calculator
code generate web scraper

# 複雑なコード生成
code generate database connection class
code generate REST API endpoints
code generate machine learning model
```

### Cursor統合
```bash
# ファイル操作
cursor open filename.py
cursor version

# コード生成（Cursor）
code generate hello world
```

### Gemini統合
```bash
# コード分析
gemini analyze code
gemini analyze file.py

# ドキュメント改善
gemini improve document
gemini improve code
```

### Web検索
```bash
# 基本検索
search Python best practices
search Docker latest features 2024

# 日本語検索
search 機械学習 最新技術
search 日本 AI 開発
```

### Webブラウジング
```bash
# URL取得・要約
browse https://github.com
browse https://example.com/blog
```

### Git管理
```bash
# 基本操作
git status
git add filename.py
git commit "Add new feature"
git push

# 自動ワークフロー
git auto
```

### シェルコマンド
```bash
# 基本コマンド
shell ls -la
shell find . -name "*.py"
shell uname -a

# 複雑なコマンド
shell ps aux | grep python
shell tar -czf backup.tar.gz project/
```

## 📁 プロジェクト管理

### プロジェクト操作
```bash
# プロジェクト作成・管理
create project my_new_project
switch project my_new_project
list projects
```

### ドキュメント生成
```bash
# ドキュメント生成
generate requirements
generate design
generate readme
```

## 🔗 統合機能

### 完全な開発サイクル
```bash
# プロジェクト作成からドキュメント生成まで
create project full_cycle && code generate hello world && generate requirements
```

### 複数エージェント連携
```bash
# Web検索→コード生成
search Python tutorial && code generate example
```

### 自動Git管理
```bash
# コード生成後に自動でGit管理
code generate feature && git auto
```

## ⚙️ 設定

### 基本設定
```yaml
# config.yaml
ai_engines:
  default_engine: gemini
  compliance_mode: false
  cost_optimization: true
  task_routing:
    code_generation: cursor
    document_generation: claude
    code_analysis: gemini
```

### 環境変数
```bash
# .env
ANTHROPIC_API_KEY=your_key
GEMINI_API_KEY=your_key
CURSOR_API_KEY=your_key
```

## 📊 使用例

### 基本的な使用例
```bash
# 1. プロジェクト作成
create project my_app

# 2. コード生成
code generate web application

# 3. ドキュメント生成
generate requirements

# 4. Git管理
git auto
```

### 高度な使用例
```bash
# 1. 技術調査
search React best practices 2024

# 2. コード分析
gemini analyze code

# 3. 複雑なコード生成
code generate microservices architecture

# 4. ドキュメント改善
gemini improve document
```

### コンプライアンス対応
```bash
# 1. コンプライアンスモード有効化
ai engine enable compliance gemini local

# 2. 制限された環境での開発
code generate secure application
```

## 🛠️ トラブルシューティング

### よくある問題
- **Dockerエラー**: `docker-compose down && docker-compose up -d`
- **APIキーエラー**: `.env`ファイルの確認
- **パスエラー**: 現在のディレクトリ確認

### ログ確認
```bash
# 設定確認
ai engine info
```

## 📈 ベストプラクティス

### 効率的な使用方法
1. **プロジェクト単位での管理**: 関連タスクは同じプロジェクトで実行
2. **適切なエンジン選択**: タスクに応じて最適なエンジンを選択
3. **定期的なGit管理**: 変更は定期的にコミット・プッシュ

### コスト最適化
1. **コスト最適化モードの活用**: 簡単なタスクは低コストエンジンを使用
2. **バッチ処理**: 複数のタスクをまとめて実行

### セキュリティ
1. **APIキーの管理**: 環境変数で安全に管理
2. **コンプライアンスモード**: 企業ポリシーに準拠した設定
3. **サンドボックス環境**: Dockerコンテナ内での安全な実行

---

**バージョン**: 2.1.0  
**最終更新**: 2025-10-13
