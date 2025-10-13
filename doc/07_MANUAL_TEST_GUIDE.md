# Airis 手動動作試験手順書

## バージョン情報

| 項目 | 内容 |
|------|------|
| 作成日 | 2025-10-13 |
| バージョン | 2.1.0 |
| 試験対象 | Airis 全機能 |
| 作成者 | AIris Development Team |

---

## 1. 試験概要

### 1.1 目的
Airis v2.1.0の全機能を手動で網羅的に試験し、実際の使用環境での動作を確認する。

### 1.2 試験範囲
- AIエンジン選択システム
- 各エージェントの基本機能
- プロジェクト管理機能
- ドキュメント生成機能
- Git管理機能
- Web検索・ブラウジング機能
- 統合機能

### 1.3 前提条件
- Docker環境が正常に動作している
- 必要なAPIキーが設定されている
- インターネット接続が利用可能

---

## 2. 試験環境準備

### 2.1 事前確認
```bash
# Docker環境確認
docker --version
docker-compose --version

# プロジェクトディレクトリに移動
cd /path/to/AIris

# 環境変数確認
cat .env
```

### 2.2 初期状態確認
```bash
# 現在の設定確認
echo y | docker-compose run -T --rm airis python3 -m airis.main "ai engine info"
```

---

## 3. 試験手順

### 3.1 AIエンジン選択システム試験

#### 3.1.1 基本設定試験

**試験項目**: デフォルトエンジン設定
```bash
# 1. 現在のデフォルトエンジンを確認
echo y | docker-compose run -T --rm airis python3 -m airis.main "ai engine info"

# 2. デフォルトエンジンをGeminiに変更
echo y | docker-compose run -T --rm airis python3 -m airis.main "ai engine set default gemini"

# 3. 変更を確認
echo y | docker-compose run -T --rm airis python3 -m airis.main "ai engine info"

# 期待結果: Default Engine: gemini と表示される
```

**試験項目**: タスク別エンジン設定
```bash
# 1. コード生成タスクをCursorに設定
echo y | docker-compose run -T --rm airis python3 -m airis.main "ai engine set task code_generation cursor"

# 2. ドキュメント生成タスクをClaudeに設定
echo y | docker-compose run -T --rm airis python3 -m airis.main "ai engine set task document_generation claude"

# 3. 設定を確認
echo y | docker-compose run -T --rm airis python3 -m airis.main "ai engine info"

# 期待結果: Task Routing に設定が反映される
```

**試験項目**: 設定保存
```bash
# 1. 設定を保存
echo y | docker-compose run -T --rm airis python3 -m airis.main "ai engine save"

# 期待結果: "Configuration saved to config.yaml" と表示される
```

#### 3.1.2 コンプライアンスモード試験

**試験項目**: コンプライアンスモード有効化
```bash
# 1. コンプライアンスモードを有効化（GeminiとLocalのみ許可）
echo y | docker-compose run -T --rm airis python3 -m airis.main "ai engine enable compliance gemini local"

# 2. 設定を確認
echo y | docker-compose run -T --rm airis python3 -m airis.main "ai engine info"

# 期待結果: Compliance Mode: True, Allowed Engines: gemini, local と表示される
```

**試験項目**: 制限されたエンジンでのタスク実行
```bash
# 1. Claudeタスクを実行（Geminiにフォールバックされるはず）
echo y | docker-compose run -T --rm airis python3 -m airis.main "code generate hello world"

# 期待結果: Geminiエージェントが選択される
```

**試験項目**: コンプライアンスモード無効化
```bash
# 1. コンプライアンスモードを無効化
echo y | docker-compose run -T --rm airis python3 -m airis.main "ai engine disable compliance"

# 2. 設定を確認
echo y | docker-compose run -T --rm airis python3 -m airis.main "ai engine info"

# 期待結果: Compliance Mode: False と表示される
```

#### 3.1.3 コスト最適化モード試験

**試験項目**: コスト最適化モード有効化
```bash
# 1. コスト最適化モードを有効化
echo y | docker-compose run -T --rm airis python3 -m airis.main "ai engine enable cost optimization"

# 2. 設定を確認
echo y | docker-compose run -T --rm airis python3 -m airis.main "ai engine info"

# 期待結果: Cost Optimization: True と表示される
```

**試験項目**: 複雑度別エンジン選択
```bash
# 1. 高複雑度タスク（Claudeが選択されるはず）
echo y | docker-compose run -T --rm airis python3 -m airis.main "code generate complex enterprise system"

# 2. 中複雑度タスク（Geminiが選択されるはず）
echo y | docker-compose run -T --rm airis python3 -m airis.main "analyze code structure"

# 3. 低複雑度タスク（Web検索が選択されるはず）
echo y | docker-compose run -T --rm airis python3 -m airis.main "simple hello world function"
```

### 3.2 エージェント機能試験

#### 3.2.1 コード生成エージェント試験

**試験項目**: 基本コード生成
```bash
# 1. フィボナッチ関数の生成
echo y | docker-compose run -T --rm airis python3 -m airis.main "code generate fibonacci function"

# 期待結果: フィボナッチ関数のコードが生成される
```

**試験項目**: 複雑なコード生成
```bash
# 1. Webスクレイパーの生成
echo y | docker-compose run -T --rm airis python3 -m airis.main "code generate web scraper"

# 期待結果: Webスクレイパーのコードが生成される
```

**試験項目**: エラーハンドリング
```bash
# 1. 無効なコード生成要求
echo y | docker-compose run -T --rm airis python3 -m airis.main "code generate invalid syntax"

# 期待結果: 適切なエラーメッセージが表示される
```

#### 3.2.2 Cursorエージェント試験

**試験項目**: Cursorバージョン確認
```bash
# 1. Cursorバージョンを確認
echo y | docker-compose run -T --rm airis python3 -m airis.main "cursor version"

# 期待結果: Cursorのバージョン情報が表示される
```

**試験項目**: ファイル開封
```bash
# 1. テストファイルを作成
echo "print('Hello World')" > test_file.py

# 2. Cursorでファイルを開く
echo y | docker-compose run -T --rm airis python3 -m airis.main "cursor open test_file.py"

# 期待結果: ファイルがCursorで開かれる（または開くための指示が表示される）
```

**試験項目**: コード生成
```bash
# 1. Cursorでコード生成
echo y | docker-compose run -T --rm airis python3 -m airis.main "code generate calculator"

# 期待結果: Cursorでコード生成が開始される（またはファイルが作成される）
```

#### 3.2.3 Geminiエージェント試験

**試験項目**: コード分析
```bash
# 1. コード分析を実行
echo y | docker-compose run -T --rm airis python3 -m airis.main "gemini analyze code"

# 期待結果: コード分析結果が表示される
```

**試験項目**: ドキュメント改善
```bash
# 1. ドキュメント改善を実行
echo y | docker-compose run -T --rm airis python3 -m airis.main "gemini improve document"

# 期待結果: ドキュメント改善提案が表示される
```

#### 3.2.4 Web検索エージェント試験

**試験項目**: 基本Web検索
```bash
# 1. Pythonのベストプラクティスを検索
echo y | docker-compose run -T --rm airis python3 -m airis.main "search Python best practices"

# 期待結果: 検索結果が要約されて表示される
```

**試験項目**: 日本語Web検索
```bash
# 1. 日本語で機械学習について検索
echo y | docker-compose run -T --rm airis python3 -m airis.main "search 機械学習 最新技術"

# 期待結果: 日本語の検索結果が要約されて表示される
```

**試験項目**: エラーハンドリング
```bash
# 1. 無効な検索クエリ
echo y | docker-compose run -T --rm airis python3 -m airis.main "search"

# 期待結果: 適切なエラーメッセージが表示される
```

#### 3.2.5 Webブラウジングエージェント試験

**試験項目**: URL取得
```bash
# 1. GitHubの内容を取得
echo y | docker-compose run -T --rm airis python3 -m airis.main "browse https://github.com"

# 期待結果: GitHubの内容が要約されて表示される
```

**試験項目**: 無効なURL
```bash
# 1. 存在しないURL
echo y | docker-compose run -T --rm airis python3 -m airis.main "browse https://invalid-url-12345.com"

# 期待結果: 適切なエラーメッセージが表示される
```

#### 3.2.6 Gitエージェント試験

**試験項目**: Git状態確認
```bash
# 1. Git状態を確認
echo y | docker-compose run -T --rm airis python3 -m airis.main "git status"

# 期待結果: Gitの状態が表示される
```

**試験項目**: ファイル追加
```bash
# 1. テストファイルを作成
echo "print('Test')" > git_test.py

# 2. ファイルをGitに追加
echo y | docker-compose run -T --rm airis python3 -m airis.main "git add git_test.py"

# 期待結果: ファイルがステージングされる
```

**試験項目**: コミット
```bash
# 1. 変更をコミット
echo y | docker-compose run -T --rm airis python3 -m airis.main "git commit 'Add test file'"

# 期待結果: コミットが作成される
```

**試験項目**: 自動ワークフロー
```bash
# 1. 自動ワークフローを実行
echo y | docker-compose run -T --rm airis python3 -m airis.main "git auto"

# 期待結果: add, commit, pushが自動実行される
```

#### 3.2.7 シェルエージェント試験

**試験項目**: 基本シェルコマンド
```bash
# 1. ディレクトリ一覧を表示
echo y | docker-compose run -T --rm airis python3 -m airis.main "shell ls -la"

# 期待結果: ディレクトリ一覧が表示される
```

**試験項目**: 複雑なシェルコマンド
```bash
# 1. Pythonファイルを検索
echo y | docker-compose run -T --rm airis python3 -m airis.main "shell find . -name '*.py'"

# 期待結果: Pythonファイルの一覧が表示される
```

**試験項目**: エラーハンドリング
```bash
# 1. 無効なコマンド
echo y | docker-compose run -T --rm airis python3 -m airis.main "shell invalid_command"

# 期待結果: 適切なエラーメッセージが表示される
```

### 3.3 プロジェクト管理機能試験

#### 3.3.1 プロジェクト作成・管理

**試験項目**: プロジェクト作成
```bash
# 1. 新しいプロジェクトを作成
echo y | docker-compose run -T --rm airis python3 -m airis.main "create project manual_test_project"

# 期待結果: プロジェクトが作成される
```

**試験項目**: プロジェクト切り替え
```bash
# 1. プロジェクトを切り替え
echo y | docker-compose run -T --rm airis python3 -m airis.main "switch project manual_test_project"

# 期待結果: プロジェクトが切り替わる
```

**試験項目**: プロジェクト一覧
```bash
# 1. プロジェクト一覧を表示
echo y | docker-compose run -T --rm airis python3 -m airis.main "list projects"

# 期待結果: プロジェクト一覧が表示される
```

#### 3.3.2 ドキュメント生成

**試験項目**: 要件定義書生成
```bash
# 1. 要件定義書を生成
echo y | docker-compose run -T --rm airis python3 -m airis.main "generate requirements"

# 期待結果: 要件定義書が日本語で生成される
```

**試験項目**: 設計書生成
```bash
# 1. 設計書を生成
echo y | docker-compose run -T --rm airis python3 -m airis.main "generate design"

# 期待結果: 設計書が日本語で生成される
```

**試験項目**: README生成
```bash
# 1. READMEを生成
echo y | docker-compose run -T --rm airis python3 -m airis.main "generate readme"

# 期待結果: READMEが日本語で生成される
```

### 3.4 統合機能試験

#### 3.4.1 エンドツーエンド試験

**試験項目**: 完全な開発サイクル
```bash
# 1. プロジェクト作成
echo y | docker-compose run -T --rm airis python3 -m airis.main "create project e2e_test"

# 2. コード生成
echo y | docker-compose run -T --rm airis python3 -m airis.main "code generate hello world"

# 3. ドキュメント生成
echo y | docker-compose run -T --rm airis python3 -m airis.main "generate requirements"

# 4. Git管理
echo y | docker-compose run -T --rm airis python3 -m airis.main "git auto"

# 期待結果: 一連の流れが正常に実行される
```

**試験項目**: 複数エージェント連携
```bash
# 1. Web検索
echo y | docker-compose run -T --rm airis python3 -m airis.main "search Python tutorial"

# 2. コード生成
echo y | docker-compose run -T --rm airis python3 -m airis.main "code generate example"

# 期待結果: 検索結果を基にコードが生成される
```

### 3.5 エラーハンドリング試験

#### 3.5.1 ネットワークエラー

**試験項目**: オフライン環境
```bash
# 1. ネットワークを切断してWeb検索を実行
# （実際の環境ではネットワーク設定を変更）

# 期待結果: 適切なエラーメッセージが表示される
```

#### 3.5.2 APIエラー

**試験項目**: 無効なAPIキー
```bash
# 1. 環境変数を無効にしてAPI呼び出し
# （実際の環境では.envファイルを一時的に変更）

# 期待結果: 適切なエラーメッセージが表示される
```

---

## 4. 試験結果記録

### 4.1 試験結果テンプレート

```
試験項目: [項目名]
試験日時: [YYYY-MM-DD HH:MM:SS]
実行者: [実行者名]
結果: [PASS/FAIL/SKIP]
実行時間: [秒]
エラーメッセージ: [エラーがある場合]
備考: [その他の情報]
```

### 4.2 問題報告テンプレート

```
問題ID: [問題ID]
発見日時: [YYYY-MM-DD HH:MM:SS]
発見者: [発見者名]
重要度: [高/中/低]
問題の概要: [問題の簡潔な説明]
再現手順: [問題を再現する手順]
期待結果: [期待される結果]
実際の結果: [実際に発生した結果]
影響範囲: [影響を受ける機能]
```

---

## 5. 試験完了基準

### 5.1 必須条件
- 高優先度試験項目の100%成功
- 中優先度試験項目の90%以上成功
- 重大なエラー（システムクラッシュ等）の0件

### 5.2 品質基準
- レスポンス時間: 各エージェント5秒以内
- エラー率: 5%以下
- ユーザビリティ: 直感的な操作が可能

---

## 6. 試験スケジュール

| フェーズ | 期間 | 内容 |
|----------|------|------|
| 準備 | 0.5日 | 環境確認、事前準備 |
| AIエンジン試験 | 1日 | AIエンジン選択システム |
| エージェント試験 | 2日 | 各エージェントの個別試験 |
| プロジェクト管理試験 | 1日 | プロジェクト・ドキュメント管理 |
| 統合試験 | 1日 | エンドツーエンド試験 |
| エラーハンドリング試験 | 0.5日 | エラーケースの試験 |
| 結果まとめ | 0.5日 | 結果記録、問題整理 |

**合計期間**: 6日間

---

## 7. 注意事項

### 7.1 試験実行時の注意
- 各試験項目は順序立てて実行する
- エラーが発生した場合は詳細を記録する
- 試験環境は清潔に保つ
- 機密情報は含めない

### 7.2 トラブルシューティング
- Dockerエラー: `docker-compose down && docker-compose up -d`
- APIエラー: 環境変数の確認
- ネットワークエラー: 接続状況の確認

---

## 8. 承認・承認者

| 項目 | 承認者 | 承認日 | 署名 |
|------|--------|--------|------|
| 試験計画 | [承認者名] | [日付] | [署名] |
| 試験実行 | [承認者名] | [日付] | [署名] |
| 試験完了 | [承認者名] | [日付] | [署名] |

---

**文書管理情報**
- 作成者: AIris Development Team
- 承認者: [承認者名]
- 最終更新: 2025-10-13
- バージョン: 1.0
