# Airis

**Airis: 自己進化するAIワーカーフォース**

`Airis`は、自律的なAIエージェントが協力して複雑な知的タスクを解決する次世代AIワーカーフォースプラットフォームです。会話型インターフェースを通じて自然言語の指示を解釈し、安全なサンドボックス環境でシェルコマンドの実行やPythonコードの生成・実行を行います。

このMVP（最小実行可能製品）では、自然言語の指示を解釈してシェルコマンドを実行し、安全なサンドボックス環境でPythonコードを生成・実行する中核機能を実証しています。

---

## ✨ 機能

- **会話型CLI:** シンプルで直感的なコマンドラインインターフェースでAirisと対話
- **タスク分類:** AI駆動の`Orchestrator`が指示を分析し、必要なタスクタイプを決定
- **エージェントベース実行:**
    - **シェルエージェント:** 自然言語をシェルコマンドに翻訳（例：「すべてのファイルをリスト表示」）して安全に実行
    - **コードエージェント:** 要件に基づいてPythonコードを生成・実行（例：「フィボナッチ関数を書いて」）
- **サンドボックス環境:** すべてのコードとコマンドは一時的なDockerコンテナ内で実行され、ホストマシンの安全性を確保

## 📋 要件

- **Docker** と **Docker Compose**

## 🚀 クイックスタート

以下の手順に従ってAirisを起動してください。

### 1. 設定

まず、設定ファイルをセットアップする必要があります。

**a. `config.yaml`を作成**

サンプル設定ファイルをコピーします：

```bash
cp config.yaml.example config.yaml
```

このファイルを編集してAIエンジン、LLM設定、その他のオプションを設定できます。設定には以下が含まれます：

- **AIエンジン選択**: 異なるタスクにどのAIエンジンを使用するかを選択
- **タスクルーティング**: 特定のタスクタイプでデフォルトエンジンを上書き
- **コンプライアンスモード**: 承認されたエンジンのみに制限
- **コスト最適化**: 簡単なタスクにはより安いエンジンを自動選択

**b. `.env`ファイルを作成**

プロジェクトルートに`.env`という名前のファイルを作成し、LLM APIキーを追加します。アプリケーションはこのファイルを読み込んでLLMプロバイダーに認証します。

例：

```
# Anthropic Claude用
ANTHROPIC_API_KEY=sk-ant-xxxxxxxx

# OpenAI用
# OPENAI_API_KEY=sk-xxxxxxxx

# Google Gemini用
GEMINI_API_KEY=your-gemini-api-key
```

### 2. Dockerイメージをビルド

Docker Composeを使用してアプリケーションイメージをビルドします。これにより、必要な依存関係がすべてインストールされます。

```bash
docker-compose build
```

### 3. アプリケーションを実行

メインアプリケーションコンテナをバックグラウンドで起動します。

```bash
docker-compose up -d
```

### 4. セッションを開始

実行中のコンテナに接続して、Airisとの対話セッションを開始します。

```bash
docker-compose exec airis python -m airis.main
```

Airisプロンプト（`> `）が表示されます。指示を開始してください！

**使用例:**
- `現在のディレクトリのすべてのファイル（隠しファイルを含む）をリスト表示してください。`
- `最初の20個の素数を出力するPythonスクリプトを書いてください。`

セッションを終了するには、`exit`または`quit`と入力してください。

## ⚙️ AIエンジン設定

### クイックセットアップ例

**すべてのタスクでClaudeを使用:**
```yaml
ai_engines:
  default_engine: claude
  task_routing: {}  # 空の場合、すべてのタスクでデフォルトを使用
```

**コード生成のみCursorを使用:**
```yaml
ai_engines:
  default_engine: claude
  task_routing:
    code_generation: cursor
```

**コスト効率のためすべてGeminiを使用:**
```yaml
ai_engines:
  default_engine: gemini
  task_routing: {}  # 空の場合、すべてのタスクでデフォルトを使用
```

**企業コンプライアンスモード:**
```yaml
ai_engines:
  compliance_mode: true
  allowed_engines: [gemini, local]
  default_engine: gemini
```

**コスト最適化を有効化:**
```yaml
ai_engines:
  cost_optimization: true
  default_engine: claude
  # システムが簡単なタスクにはより安いエンジンを自動選択
```

## 🛠️ 開発者向け

### プロジェクト構造

- **`airis/`**: メインアプリケーションのソースコード
    - **`main.py`**: CLIエントリーポイント（Typer使用）
    - **`orchestrator.py`**: 指示を解釈してエージェントに委譲する中央の「脳」
    - **`llm.py`**: 大規模言語モデルとの対話用クライアント
    - **`sandbox.py`**: Dockerでのコード/コマンドの安全な実行を管理
    - **`config.py`**: `config.yaml`の読み込みを処理
- **`agents/`**: 専門エージェントを含む
    - **`base.py`**: すべてのエージェントの抽象基底クラス
    - **`shell_agent.py`**: シェルコマンドを処理するエージェント
    - **`code_agent.py`**: Pythonコードの生成/実行を処理するエージェント
    - **`web_search_agent.py`**: ウェブ検索を実行するエージェント
    - **`web_browser_agent.py`**: ウェブページの内容を取得・要約するエージェント
    - **`cursor_agent.py`**: Cursorエディタとの連携を行うエージェント
    - **`gemini_agent.py`**: Google Gemini APIとの連携を行うエージェント
    - **`git_agent.py`**: Git操作を実行するエージェント
- **`doc/`**: プロジェクトドキュメント（提案書、要件定義、設計書）
- **`test_files/`**: テスト用ファイルとスクリプト
- **`Dockerfile` & `docker-compose.yml`**: コンテナ化された開発環境を定義

### 新規エージェントの追加

1. `agents/`ディレクトリに新しいエージェントクラスを作成し、`BaseAgent`を継承
2. `execute`メソッドを実装
3. `airis/orchestrator.py`で新しいエージェントをインポートしてインスタンス化
4. `Orchestrator`の分類ロジックと`run`メソッドを更新して、新しいエージェントにタスクを委譲

## 🔧 高度な機能

### AIエンジン選択システム

Airisは複数のAIエンジンから選択できる柔軟なシステムを提供します：

- **Claude (Anthropic)**: 高品質なコード生成と分析
- **Gemini (Google)**: コスト効率の良い処理
- **Cursor**: コード生成とエディタ連携
- **Web Search**: リアルタイム情報検索
- **Web Browser**: ウェブページの内容取得

### プロジェクト管理

- プロジェクトの作成、切り替え、管理
- 自動ドキュメント生成（要件定義書、設計書、README）
- 日本語でのドキュメント生成対応

### 自動Git管理

- コード生成後の自動コミット
- プロジェクト変更の自動追跡
- バージョン管理の自動化

## 📚 ドキュメント

詳細なドキュメントは`doc/`ディレクトリにあります：

- **`00_PROJECT_PROPOSAL.md`**: プロジェクト提案書
- **`01_REQUIREMENTS_DEFINITION.md`**: 要件定義書
- **`02_SYSTEM_DESIGN.md`**: システム設計書
- **`03_ARCHITECTURE_UPDATE.md`**: アーキテクチャ更新履歴
- **`04_TECHNICAL_SPECIFICATIONS.md`**: 技術仕様書
- **`05_CHANGELOG.md`**: 変更履歴
- **`06_TEST_PLAN.md`**: テスト計画書
- **`07_MANUAL_TEST_GUIDE.md`**: 手動テストガイド
- **`08_MANUAL_TEST_CHECKLIST.md`**: 手動テストチェックリスト
- **`09_FEATURE_GUIDE.md`**: 機能ガイド

## 🤝 貢献

プロジェクトへの貢献を歓迎します。詳細は`doc/CONTRIBUTING.md`を参照してください。

## 📄 ライセンス

このプロジェクトはMITライセンスの下で公開されています。

---

**Airis** - 未来のAIワーカーフォースを今日から始めましょう。
