# AIエンジン設定ガイド

## バージョン情報

| 項目 | 内容 |
|------|------|
| 作成日 | 2025-10-17 |
| バージョン | 2.4.0 |
| 機能名 | Unified AI Engine Management |

---

## 1. 概要

Airisのすべての AI 使用は `config.yaml` で一元管理されています。

### 1.1 なぜ一元管理が必要か

**従来の問題**:
- AI エンジンがコードにハードコード されていた
- Claude のクレジットが切れたら動作しなくなる
- エンジンを変更するにはコード修正が必要

**一元管理の解決策**:
- すべての AI 使用を `config.yaml` で制御
- エンジンの切り替えが設定ファイルの変更のみで可能
- タスクごとに最適な AI を選択可能

---

## 2. 設定方法

### 2.1 基本設定

`config.yaml` の `ai_engines` セクション:

```yaml
ai_engines:
  # デフォルトエンジン
  default_engine: gemini
  
  # タスクごとのエンジン指定
  task_routing:
    code_generation: cursor      # コード生成
    document_generation: gemini  # ドキュメント生成
    code_analysis: gemini        # コード分析
    orchestration: gemini        # タスク振り分け
    interactive_mode: gemini     # 対話モード
    validation: gemini           # 出力検証
    project_memory: gemini       # プロジェクト記憶
    web_search: web_search       # Web検索
    web_browsing: web_browser    # Webブラウジング
    git_operations: local        # Git操作
    shell_operations: local      # シェル操作
```

### 2.2 各タスクの説明

| タスクタイプ | 説明 | 推奨エンジン |
|-------------|------|------------|
| `code_generation` | Python/JavaScriptなどのコード生成 | `cursor` |
| `document_generation` | README、要件定義書などの生成 | `gemini` / `claude` |
| `code_analysis` | コードの分析や説明 | `gemini` / `claude` |
| `orchestration` | タスクの振り分けと判断 | `gemini` / `claude` |
| `interactive_mode` | 対話型の要件確認 | `gemini` / `claude` |
| `validation` | 出力の品質検証 | `gemini` / `claude` |
| `project_memory` | プロジェクト記憶の分析 | `gemini` / `claude` |
| `web_search` | インターネット検索 | `web_search` (固定) |
| `web_browsing` | URL の内容取得 | `web_browser` (固定) |
| `git_operations` | Git コマンド実行 | `local` (固定) |
| `shell_operations` | シェルコマンド実行 | `local` (固定) |

---

## 3. 設定例

### 3.1 すべて Gemini を使う（推奨）

Claude のクレジットが不足している場合:

```yaml
ai_engines:
  default_engine: gemini
  task_routing:
    code_generation: cursor      # コード生成のみ Cursor
    orchestration: gemini
    interactive_mode: gemini
    validation: gemini
    project_memory: gemini
```

### 3.2 すべて Claude を使う

Claude のクレジットが十分にある場合:

```yaml
ai_engines:
  default_engine: claude
  task_routing:
    code_generation: cursor      # コード生成のみ Cursor
    orchestration: claude
    interactive_mode: claude
    validation: claude
    project_memory: claude
```

### 3.3 コスト最適化

```yaml
ai_engines:
  default_engine: gemini          # 低コストの Gemini をデフォルトに
  cost_optimization: true
  task_routing:
    code_generation: cursor       # コード生成は Cursor
    document_generation: gemini   # ドキュメントは Gemini
    code_analysis: claude         # 高度な分析のみ Claude
```

### 3.4 コンプライアンスモード

社内規定で使用可能なAIが制限されている場合:

```yaml
ai_engines:
  compliance_mode: true
  allowed_engines:
    - gemini      # Gemini のみ使用可能
    - local       # ローカル操作は許可
  default_engine: gemini
```

---

## 4. エンジン別の設定

### 4.1 Gemini 設定

```yaml
gemini:
  max_tokens: 4000
  temperature: 0.1
  model_name: gemini-2.5-pro
```

**必要な環境変数**:
```bash
GEMINI_API_KEY=your_api_key_here
```

### 4.2 Claude 設定

```yaml
claude:
  max_tokens: 4000
  temperature: 0.1
  model_name: claude-sonnet-4-5-20250929
```

**必要な環境変数**:
```bash
ANTHROPIC_API_KEY=your_api_key_here
```

**注意**: クレジット不足の場合は Gemini に切り替えてください。

### 4.3 Cursor 設定

```yaml
cursor:
  api_url: http://localhost:5000
  code_generation: true
  max_tokens: 4000
  path: cursor
  temperature: 0.1
```

---

## 5. トラブルシューティング

### 5.1 Claude のクレジットエラー

**エラーメッセージ**:
```
Error code: 400 - Your credit balance is too low to access the Anthropic API
```

**解決方法**:

#### 方法1: Gemini に切り替え

`config.yaml` を編集:

```yaml
ai_engines:
  default_engine: gemini  # claude → gemini に変更
  task_routing:
    orchestration: gemini
    interactive_mode: gemini
    validation: gemini
```

#### 方法2: コマンドで切り替え

```bash
Airis> ai engine set default gemini
```

### 5.2 Gemini API エラー

**エラーメッセージ**:
```
404 models/gemini-2.5-pro is not found
```

**解決方法**:

`config.yaml` のモデル名を確認:

```yaml
gemini:
  model_name: gemini-2.5-pro  # 正しいモデル名を指定
```

### 5.3 API キーが見つからない

**エラーメッセージ**:
```
GEMINI_API_KEY not found
```

**解決方法**:

`.env` ファイルを作成:

```bash
# .env
GEMINI_API_KEY=your_gemini_key_here
ANTHROPIC_API_KEY=your_claude_key_here  # 使う場合のみ
```

---

## 6. 実際の使用例

### 6.1 プロジェクト作成（Gemini 使用）

```bash
Airis> project create my_calculator

# 内部的に:
# - orchestration: gemini （タスク振り分け）
# - interactive_mode: gemini （要件確認）
# - code_generation: cursor （コード生成）
# - validation: gemini （出力検証）
```

### 6.2 ドキュメント生成（Gemini 使用）

```bash
Airis> README を生成して

# 内部的に:
# - orchestration: gemini
# - document_generation: gemini
# - validation: gemini
```

### 6.3 エンジンの確認

```bash
Airis> ai engine info

現在のAI設定:
デフォルトエンジン: gemini

タスク別設定:
  orchestration: gemini
  interactive_mode: gemini
  validation: gemini
  code_generation: cursor
```

---

## 7. 高度な設定

### 7.1 タスクの複雑度に応じた自動選択

```yaml
ai_engines:
  cost_optimization: true
  cost_preferences:
    free: local
    low_cost: web_search
    medium_cost: gemini
    high_cost: claude
```

システムが自動的にタスクの複雑度を判断し、適切なエンジンを選択します。

### 7.2 複数プロファイルの切り替え

**開発環境** (`config.yaml`):
```yaml
ai_engines:
  default_engine: gemini  # 低コスト
```

**本番環境** (`config.production.yaml`):
```yaml
ai_engines:
  default_engine: claude  # 高品質
```

---

## 8. ベストプラクティス

### 8.1 コスト管理

✅ **推奨**:
- デフォルトは Gemini（低コスト）
- 高度なタスクのみ Claude
- コード生成は Cursor（サブスクリプション）

```yaml
ai_engines:
  default_engine: gemini
  task_routing:
    code_generation: cursor
    code_analysis: claude  # 高度な分析のみ
```

### 8.2 品質重視

✅ **推奨**:
- すべて Claude（クレジットが十分な場合）
- 検証は常に有効

```yaml
ai_engines:
  default_engine: claude
enable_output_validation: true
```

### 8.3 オフライン環境

✅ **推奨**:
- Cursor のみ使用
- Web 検索は無効化

```yaml
ai_engines:
  compliance_mode: true
  allowed_engines: [cursor, local]
  default_engine: cursor
```

---

## 9. まとめ

### 9.1 一元管理の利点

1. **柔軟性**: エンジンの切り替えが簡単
2. **コスト管理**: タスクごとに最適なエンジンを選択
3. **可用性**: あるエンジンが使えなくても切り替え可能
4. **透明性**: どのタスクで何を使っているか明確

### 9.2 現在の推奨設定

```yaml
ai_engines:
  default_engine: gemini          # Gemini をデフォルトに
  task_routing:
    code_generation: cursor       # コード生成は Cursor
    orchestration: gemini         # オーケストレーションは Gemini
    interactive_mode: gemini      # 対話モードは Gemini
    validation: gemini            # 検証は Gemini
    project_memory: gemini        # プロジェクト記憶は Gemini

# Gemini 設定
gemini:
  max_tokens: 4000
  temperature: 0.1
  model_name: gemini-2.5-pro

# 検証を有効化
enable_output_validation: true
```

---

## 付録A: 全タスクタイプ一覧

| タスクタイプ | 使用箇所 | デフォルトエンジン |
|-------------|---------|------------------|
| `orchestration` | `Orchestrator` | `gemini` |
| `interactive_mode` | `InteractiveSession` | `gemini` |
| `validation` | `ValidatorAgent` | `gemini` |
| `code_generation` | `CodeAgent` | `cursor` |
| `document_generation` | `DocumentCompletionAgent` | `gemini` |
| `code_analysis` | `GeminiAgent` | `gemini` |
| `web_search` | `WebSearchAgent` | `web_search` |
| `web_browsing` | `WebBrowserAgent` | `web_browser` |
| `git_operations` | `GitAgent` | `local` |
| `shell_operations` | `ShellAgent` | `local` |
| `project_memory` | `ProjectMemory` | `gemini` |

---

## 付録B: 設定変更チェックリスト

### Claude → Gemini への移行

- [ ] `config.yaml` の `default_engine` を `gemini` に変更
- [ ] `task_routing` の各タスクを `gemini` に変更
- [ ] `.env` に `GEMINI_API_KEY` を設定
- [ ] Docker コンテナを再起動
- [ ] `ai engine info` で設定を確認
- [ ] テストプロジェクトで動作確認

### 完了！

すべての AI 使用が `config.yaml` で制御されています。

