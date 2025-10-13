# Airis 技術仕様書

## バージョン情報

| 項目 | 内容 |
|------|------|
| 更新日 | 2025-10-13 |
| バージョン | 2.0 |
| 対象システム | Airis AI Development Assistant |

---

## 1. システム概要

### 1.1 システム名
Airis - 自己進化型AI開発アシスタント

### 1.2 システムの目的
複雑な知的タスクを自動化し、開発者とSREの生産性を大幅に向上させる自己進化型AIワークフォースプラットフォーム

### 1.3 主要機能
- コード生成・実行
- ドキュメント生成・管理
- Web検索・ブラウジング
- Git自動管理
- プロジェクト管理

## 2. アーキテクチャ仕様

### 2.1 システム構成

```
┌─────────────────────────────────────────────┐
│                Orchestrator                 │
│  (Keyword-based routing & task delegation)  │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│              Agent System                   │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐   │
│  │   Code   │ │  Shell   │ │  Cursor  │   │
│  └──────────┘ └──────────┘ └──────────┘   │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐   │
│  │WebSearch │ │WebBrowser│ │DocComp.  │   │
│  └──────────┘ └──────────┘ └──────────┘   │
│  ┌──────────┐                             │
│  │   Git    │                             │
│  └──────────┘                             │
└─────────────────────────────────────────────┘
```

### 2.2 コンポーネント仕様

#### 2.2.1 Orchestrator
- **責任**: タスクの分析と適切なエージェントへの委譲
- **実装**: `airis/orchestrator.py`
- **機能**:
  - キーワードベースルーティング
  - 開発サイクル管理
  - エージェント間の調整

#### 2.2.2 Agent System
各エージェントは`BaseAgent`を継承し、`execute`メソッドを実装

**Code Agent**:
- **ファイル**: `agents/code_agent.py`
- **機能**: Pythonコード生成・実行
- **技術**: Base64エンコーディング、Dockerサンドボックス

**Shell Agent**:
- **ファイル**: `agents/shell_agent.py`
- **機能**: シェルコマンド実行
- **技術**: Dockerサンドボックス

**Web Search Agent**:
- **ファイル**: `agents/web_search_agent.py`
- **機能**: Web検索・結果要約
- **技術**: DuckDuckGo API、LLM要約

**Web Browser Agent**:
- **ファイル**: `agents/web_browser_agent.py`
- **機能**: URL取得・コンテンツ要約
- **技術**: requests、BeautifulSoup、LLM要約

**Document Completion Agent**:
- **ファイル**: `agents/document_completion_agent.py`
- **機能**: ドキュメント完成度チェック・自動完成
- **技術**: パターンマッチング、LLM補完

**Git Agent**:
- **ファイル**: `agents/git_agent.py`
- **機能**: Git操作（add, commit, push）
- **技術**: subprocess、git config自動設定

## 3. データ仕様

### 3.1 設定ファイル

**config.yaml**:
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

### 3.2 プロジェクト構造

```
projects/
├── project_name/
│   ├── doc/
│   │   ├── 01_requirements.md
│   │   ├── 02_design.md
│   │   └── README.md
│   ├── src/
│   │   └── generated_code.py
│   ├── tests/
│   └── README.md
```

### 3.3 ドキュメント仕様

**要件定義書** (01_requirements.md):
- プロジェクト概要
- 機能要件
- 非機能要件
- 制約事項
- 受け入れ基準

**システム設計書** (02_design.md):
- システム概要
- アーキテクチャ設計
- コンポーネント設計
- データ設計
- インターフェース設計
- セキュリティ設計

**README.md**:
- プロジェクト概要
- 機能
- インストール方法
- 使用方法
- ファイル構成
- ライセンス
- 貢献方法

## 4. インターフェース仕様

### 4.1 CLI インターフェース

**基本コマンド**:
```bash
# コード生成
python3 -m airis.main "write a Python function to calculate fibonacci"

# 開発サイクル
python3 -m airis.main "develop: create a web scraper"

# Web検索
python3 -m airis.main "search for Python best practices"

# Webブラウジング
python3 -m airis.main "browse https://www.python.org"

# ドキュメント完成
python3 -m airis.main "complete doc project_name"

# Git管理
python3 -m airis.main "git auto"
```

### 4.2 エージェント間通信

**BaseAgent インターフェース**:
```python
class BaseAgent:
    def execute(self, instruction: str, context: str | None = None, **kwargs) -> str:
        pass
```

**戻り値仕様**:
- 成功時: 実行結果の文字列
- 失敗時: エラーメッセージの文字列

## 5. セキュリティ仕様

### 5.1 サンドボックス環境

**Dockerコンテナ**:
- ベースイメージ: `python:3.11-slim`
- 実行環境: 完全に分離されたコンテナ
- リソース制限: メモリ、CPU制限設定可能

**セキュリティ対策**:
- ホストシステムへの直接アクセス禁止
- ネットワークアクセス制限
- ファイルシステムアクセス制限

### 5.2 認証・認可

**API認証**:
- Anthropic API: 環境変数または設定ファイル
- その他API: 同様の方式

**Git認証**:
- SSH鍵またはHTTPS認証
- 自動設定機能（ローカル開発用）

## 6. パフォーマンス仕様

### 6.1 レスポンス時間

| 操作 | 目標時間 | 備考 |
|------|----------|------|
| コード生成 | < 30秒 | LLM応答時間依存 |
| Web検索 | < 15秒 | ネットワーク依存 |
| ドキュメント生成 | < 45秒 | ドキュメント長依存 |
| Git操作 | < 10秒 | リポジトリサイズ依存 |

### 6.2 スループット

- **同時実行**: 1リクエスト（シーケンシャル処理）
- **レート制限**: API制限に準拠（4,000トークン/分）

### 6.3 リソース使用量

**メモリ**:
- ベース: 512MB
- 最大: 2GB（LLM処理時）

**CPU**:
- ベース: 0.5コア
- 最大: 2コア（並列処理時）

**ストレージ**:
- ベース: 1GB
- プロジェクト: 100MB/プロジェクト

## 7. エラーハンドリング仕様

### 7.1 エラー分類

**Level 1 (警告)**:
- 非致命的なエラー
- 処理継続可能
- ユーザーに通知

**Level 2 (エラー)**:
- 処理中断
- ユーザーにエラーメッセージ表示
- ログ記録

**Level 3 (致命的)**:
- システム停止
- 緊急対応必要
- 詳細ログ記録

### 7.2 エラーメッセージ仕様

**形式**: `[エラータイプ]: エラー内容`

**例**:
- `[API Error]: Rate limit exceeded`
- `[File Error]: Project directory not found`
- `[Git Error]: Authentication failed`

## 8. ログ仕様

### 8.1 ログレベル

- **DEBUG**: 詳細なデバッグ情報
- **INFO**: 一般的な情報
- **WARNING**: 警告メッセージ
- **ERROR**: エラーメッセージ
- **CRITICAL**: 致命的エラー

### 8.2 ログ形式

```
[YYYY-MM-DD HH:MM:SS] [LEVEL] [COMPONENT] MESSAGE
```

**例**:
```
[2025-10-13 16:30:45] [INFO] [Orchestrator] Task delegated to CodeAgent
[2025-10-13 16:30:46] [ERROR] [GitAgent] Failed to push changes
```

## 9. テスト仕様

### 9.1 単体テスト

**対象**:
- 各エージェントの`execute`メソッド
- オーケストレーターのルーティング機能
- ユーティリティ関数

**ツール**: pytest

**カバレッジ目標**: 80%以上

### 9.2 統合テスト

**対象**:
- エージェント間の連携
- エンドツーエンドのワークフロー
- エラーハンドリング

### 9.3 パフォーマンステスト

**対象**:
- レスポンス時間
- メモリ使用量
- 同時実行性能

## 10. 運用仕様

### 10.1 デプロイメント

**Docker Compose**:
```yaml
version: '3.8'
services:
  airis:
    build: .
    environment:
      - HOST_PROJECT_DIR=${PWD}
    volumes:
      - .:/app
```

### 10.2 監視

**メトリクス**:
- リクエスト数
- レスポンス時間
- エラー率
- リソース使用量

**アラート**:
- エラー率 > 5%
- レスポンス時間 > 60秒
- メモリ使用量 > 90%

### 10.3 バックアップ

**対象**:
- プロジェクトファイル
- 設定ファイル
- ログファイル

**頻度**: 日次

**保持期間**: 30日

---

**文書承認**

本技術仕様書は、プロジェクト関係者の合意のもとで作成されました。

- プロジェクトマネージャー: Airis Development Team
- 技術リード: AIris Architecture Team
- 品質保証担当: AIris QA Team

**文書終了**
