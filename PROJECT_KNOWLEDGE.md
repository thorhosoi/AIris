# Project Airis Knowledge Base

This document summarizes the current state and understanding of the "Airis" project as of 2025-10-13. It serves as a comprehensive knowledge repository for maintaining context and tracking project evolution.

**Note:** This is a living document that will be continuously updated as new information about the project becomes available or as its state changes. It also records important environmental and procedural notes to avoid repeating troubleshooting steps.

## 1. Project Overview

- **Project Name:** `Airis`
- **Concept:** A self-evolving AI workforce platform. It receives complex, high-level tasks from a user via a conversational CLI and breaks them down for a team of autonomous AI agents to solve collaboratively.
- **Primary Goal:** To dramatically improve the productivity of developers and SREs by automating complex intellectual tasks, allowing humans to focus on more creative work.
- **Initial Target:** Automating SRE/DevOps tasks, suchs as provisioning cloud infrastructure via IaC.

## 2. Core Architecture & Concepts

- **IACT (Interactive Agents Call Tree):** This is the core architecture. A main orchestrator decomposes a user's request into a hierarchical tree of tasks. Each node in the tree is assigned to a specialized AI agent. Agents can communicate and collaborate to complete the task.
- **Dynamic Agent Generation:** The system can dynamically spin up necessary agents (e.g., for coding, shell execution, web searching) based on the task's requirements.
- **Self-Extension:** A key long-term feature. Airis can identify the need for a new tool, write the code for it, test it, and integrate it into its own capabilities.
- **Sandbox Environment:** All code and shell commands are executed within a secure, isolated Docker container to protect the host system. This is a critical safety feature.
- **User-in-the-loop:** For safety and control, the system will ask for user approval before executing potentially destructive or irreversible actions (like running shell commands or overwriting files).

## 3. MVP (Minimum Viable Product) Scope

The goal of the MVP is to validate the core user experience: a user gives an instruction, and Airis safely executes code/commands to produce a file-based artifact.

- **Interface:** A command-line interface (CLI).
- **Core Agents:**
    - `Code Agent`: To write and execute Python code.
    - `Shell Agent`: To execute shell commands.
- **Key Workflow:**
    1. User provides an instruction (e.g., "Write a Python function for Fibonacci").
    2. The `Orchestrator` plans the task.
    3. The `Code Agent` writes the Python code.
    4. The `Orchestrator` asks the user for approval to save the file, **suggesting a filename based on the task and generated code.**
    5. The file is saved to the local filesystem **in a dedicated output directory (e.g., `generated_scripts/`) upon user approval.**
- **Out of MVP Scope:** Self-extension, web browsing, multi-modal capabilities, GUI.

## 4. Technology Stack

- **Language:** Python 3.11+
- **CLI Framework:** Typer
- **AI/Agent Framework:** LangChain (This is a key library for implementing the orchestrator and agents).
- **Sandbox:** Docker (managed via the Docker SDK for Python).
- **Configuration:** PyYAML (`config.yaml`).
- **Environment Variables:** `python-dotenv` (for loading `.env` files).
- **Testing:** `pytest` (for unit and integration tests).

## 5. Project File Structure & Key Components

- **`airis/main.py`**: The CLI entry point built with Typer. It captures user input and passes it to the orchestrator.
- **`airis/orchestrator.py`**: The "brain" of the application. It will house the main IACT logic, interpret user requests, and coordinate the agents.
- **`airis/llm.py`**: A client to abstract communications with various Large Language Models (LLMs) like Claude, GPT, etc., likely using LangChain's wrappers.
- **`airis/sandbox.py`**: Manages the lifecycle of the Docker sandbox. It's responsible for creating a container, executing a command inside it, and then tearing it down.
- **`agents/`**: A directory for specialized agents.
    - `base.py`: An abstract base class for all agents.
    - `code_agent.py`: Agent responsible for writing and running code.
    - `shell_agent.py`: Agent responsible for executing shell commands.
- **`Dockerfile` / `docker-compose.yml`**: Defines the development and execution environment.
- **`config.yaml.example`**: An example configuration file where users can define the LLM model, API keys, etc.
- **`requirements.txt`**: Lists Python dependencies.
- **`tests/`**: Directory for unit and integration tests.
    - `test_orchestrator.py`: Unit tests for the Orchestrator's delegation logic.

## 6. Development Environment Notes

- **Container User:** To simplify development and avoid Docker socket permission issues, the main container currently runs as the `root` user. This is not ideal for security and should be revisited in the future to implement a more secure solution (e.g., GID matching).
- **Git State Discrepancy:** A persistent issue was encountered where the AI's execution environment saw a different `git status` than the user's environment. Standard commands like `git add .` and `git add -A` failed to stage new files for the AI, even though the files existed. The root cause appears to be a synchronization problem between the AI's tool environment and the user's filesystem state.
- **Resolution:** The user had to manually stage the files. In the future, if `git` commands produce unexpected results, assume this state discrepancy is occurring and defer to the user for `git` operations, or attempt a `rm .git/index` to force a full rescan by Git.
- **Curses TUI Instability:** An attempt was made to replace the simple CLI with a more advanced Text-based User Interface (TUI) using Python's `curses` library. This repeatedly failed with `cbreak() returned ERR` and `nocbreak() returned ERR` errors across various implementation strategies (using `curses.wrapper`, manual setup, etc.). The root cause is suspected to be an incompatibility between the `curses` library and the terminal environment provided by the AI's `run_shell_command` tool, which may not be a fully-featured TTY.
- **Decision:** Development of the `curses` TUI is postponed indefinitely. The project will continue with the existing CLI, focusing on core feature enhancements as outlined in the MVP requirements.
- **HOST_PROJECT_DIR for Sandbox:** When running `Airis` within a Docker container, the `airis/sandbox.py` module needs to create nested Docker containers. To correctly mount the host's project directory into these child sandbox containers, the `HOST_PROJECT_DIR` environment variable (set in `docker-compose.yml` to `${PWD}`) is utilized. This ensures that the `sandbox` can correctly reference the host's absolute path for bind mounts.
- **Docker Interactive Mode Instability:** An attempt was made to enable interactive sessions with `Airis` running inside a Docker container using `docker attach`. This repeatedly failed with `the input device is not a TTY` errors, even with `tty: true` and `stdin_open: true` in `docker-compose.yml`. This indicates that the `run_shell_command` environment cannot fully emulate an interactive TTY session required for `docker attach` to function correctly.
- **Decision:** Interactive mode for `Airis` within a Docker container is postponed indefinitely. The project will continue with the single-command execution model for `Airis` running in Docker.

## 7. Current Implemented Features

### Core Features
- **CLI Interface:** User interaction via command-line prompts with conversational AI
- **Multi-Agent Architecture:** Specialized agents for different task types
- **AI Engine Selection System:** Dynamic selection of AI engines based on task requirements
- **Project Management:** Complete project lifecycle management with automatic document generation
- **Docker Sandbox:** Secure execution environment for all code and commands
- **Git Integration:** Automatic version control with intelligent commit messages

### Specialized Agents
- **Code Agent:** Generates and executes Python code in a Docker sandbox
- **Shell Agent:** Generates and executes shell commands in a Docker sandbox
- **Web Search Agent:** Performs web searches using DuckDuckGo API
- **Web Browser Agent:** Fetches and summarizes content from URLs
- **Cursor Agent:** Integrates with Cursor editor for advanced code generation
- **Gemini Agent:** Utilizes Google Gemini API for code analysis and document improvement
- **Git Agent:** Handles all git operations (add, commit, push, status)
- **Document Completion Agent:** Automatically checks and completes incomplete documents

### Advanced Capabilities
- **Multi-Language Support:** Japanese and English documentation generation
- **Intelligent Task Routing:** AI-powered task classification and agent selection
- **Compliance Mode:** Corporate policy compliance with restricted AI engine usage
- **Cost Optimization:** Task complexity-based engine selection for cost efficiency
- **Document Quality Assurance:** Automatic completeness checking and completion
- **Cross-Platform Compatibility:** Works on Windows, macOS, and Linux
- **Comprehensive Testing:** Automated and manual testing frameworks

## 8. Recent Troubleshooting and Resolutions (2025-10-13)

This section details issues encountered and their resolutions during the development session on 2025-10-13.

### 8.1. `SyntaxError: unterminated string literal` in `airis/orchestrator.py`

- **Issue:** The `airis/orchestrator.py` file contained a `SyntaxError` on line 26 due to an extra double quote and backslash in a string literal, preventing the application from starting correctly.
- **Resolution:** Removed the extraneous characters from the string literal in `airis/orchestrator.py`.

### 8.2. `AssertionError` in `tests/test_orchestrator.py`

- **Issue:** After fixing the `SyntaxError` in `orchestrator.py`, two unit tests (`test_orchestrator_delegates_to_code_agent` and `test_orchestrator_defaults_to_code_agent`) failed with `AssertionError`. This was because the `orchestrator.delegate_task` method was modified to return a tuple `(display_result, generated_code)`, but the tests were still asserting against the entire `result` tuple instead of its first element (`result[0]`).
- **Resolution:** Updated the failing assertions in `tests/test_orchestrator.py` to correctly check `result[0]` for the expected strings.

### 8.3. `SyntaxError` during CodeAgent execution (Markdown Delimiters)

- **Issue:** When running the `develop` command, the `CodeAgent` failed with `SyntaxError: invalid syntax` because the LLM's output included markdown code block delimiters (e.g., ```python) which were not being correctly stripped, leading to them being written into the executable Python file.
- **Resolution:** Modified `agents/code_agent.py` to use a more robust, direct string manipulation approach to strip ```python` and ``` ` delimiters from the beginning and end of the generated code.

### 8.4. `SyntaxError` / `IndentationError` during CodeAgent execution (Malformed LLM Output)

- **Issue:** Even after fixing the markdown delimiter stripping, the `CodeAgent` sometimes encountered `SyntaxError: unterminated triple-quoted string literal` or `IndentationError: expected an indented block` because the LLM was generating incomplete or malformed Python code (e.g., unclosed docstrings, missing function bodies).
- **Resolution:**
    1.  Refined the LLM prompt in `agents/code_agent.py` to explicitly request "complete and syntactically correct Python script" and to "Ensure all function definitions and control flow statements are followed by an indented block."
    2.  Implemented a Python syntax check in `agents/code_agent.py` using `compile(code, '<string>', 'exec')` before writing and executing the generated code. This prevents execution of invalid code and provides immediate feedback about syntax issues.

### 8.5. Successful `develop` command execution

- **Outcome:** After applying all the above fixes, the `develop` command successfully executed, generating the requirements document, design document, and a syntactically valid and executable Python script for calculating Fibonacci numbers.

## 9. Project Conventions and Preferences

This section outlines established conventions and user preferences for the Airis project.

### 9.1. Project Naming Convention

- **Convention:** `[YYYYMMDD]-[project-purpose-in-kebab-case]`
- **Description:** When creating new projects using Airis, the project name should follow this format. It starts with the creation date (YYYYMMDD) followed by a descriptive purpose in kebab-case (lowercase, hyphen-separated words). This ensures consistency, clarity, and machine-friendliness.
- **Example:** `20251013-fibonacci-calculator`

### 9.2. Documentation Language

- **Preference:** 日本語 (Japanese)
- **Description:** All documentation generated by Airis, including requirements, design documents, and any other textual output intended for human consumption, should be in Japanese.

- **CLI Interface:** User interaction via command-line prompts.
- **Code Agent:** Generates and executes Python code in a Docker sandbox.
- **Shell Agent:** Generates and executes shell commands in a Docker sandbox.
- **Orchestrator:** Dispatches tasks to appropriate agents based on keywords.
- **LLM Client:** Abstracts communication with LLMs (e.g., Anthropic Claude), loading API keys from `config.yaml` or `.env` files.
- **Docker Sandbox:** Secure execution environment for generated code/commands.
- **Filename Suggestion:** LLM suggests an appropriate filename for generated code.
- **User Approval:** Prompts user for approval before saving generated code to a file.
- **Dedicated Output Directory:** Saves generated scripts to a configurable directory (default: `generated_scripts/`).
- **Docker Integration:** `Airis` itself runs within a Docker container, simplifying setup and ensuring portability.
- **Unit Tests:** `pytest` based unit tests for the Orchestrator's core logic.
- **Project Management:** Allows creation of new project directories (`projects/[project_name]/`) with predefined subdirectories (`doc/`, `src/`, `tests/`) and template files. Users can also switch between active projects, and generated code is saved to the active project's `src/` directory.
- **Document Generation:** Generates requirements, design, or README documents for the active project's `doc/` directory based on LLM output.

## 9. Project Conventions

- **File Naming:** Use snake_case for Python files, kebab-case for project directories
- **Documentation:** All documentation should be in Japanese for better accessibility
- **Code Style:** Follow PEP 8 guidelines
- **Testing:** Include unit tests for all new functionality
- **Knowledge Base:** This file serves as the central knowledge repository for the project
- **Git Management:** All code changes are automatically committed to git
- **Document Quality:** All generated documents are checked for completeness and auto-completed if needed

## 10. Recent Updates (2025-10-13)

### New Features Added
- **Document Completion Agent:** Automatically checks and completes incomplete documents
- **Git Management Agent:** Handles git operations (add, commit, push) automatically
- **Web Search Agent:** Performs web searches using DuckDuckGo
- **Web Browser Agent:** Fetches and summarizes content from URLs
- **Cursor Agent:** Advanced code generation with Cursor editor integration
- **Gemini Agent:** Google Gemini API integration for code analysis
- **Japanese Documentation:** All generated documents are now in Japanese
- **Auto Git Commit:** Code changes are automatically committed to git
- **AI Engine Selection System:** Dynamic AI engine selection based on task requirements
- **Compliance Mode:** Corporate policy compliance with restricted AI engine usage
- **Cost Optimization:** Task complexity-based engine selection for cost efficiency

### Technical Decisions
- **Max Tokens:** Reduced to 4000 to avoid API rate limits
- **Document Quality:** Implemented completion checking to ensure full documents
- **Git Integration:** Automatic git operations for all code changes
- **Error Handling:** Improved error handling for git operations and document generation
- **AI Engine Selection:** Implemented flexible AI engine selection system
- **Cursor Integration:** Code generation delegated to Cursor for better quality
- **Compliance Mode:** Added corporate policy compliance features
- **Cost Optimization:** Implemented task complexity-based engine selection
- **File Organization:** Cleaned up project structure and organized test files
- **Privacy Protection:** Removed all personal information from git history
- **Cross-Platform Support:** Eliminated absolute paths for better portability

### Architecture Updates
- **Agent System:** Added 6 new agents (DocumentCompletion, Git, WebSearch, WebBrowser, Cursor, Gemini)
- **Orchestrator:** Enhanced with intelligent task routing and AI engine selection
- **Document Generation:** Improved prompts for Japanese documentation
- **Code Execution:** Fixed temp_code.py issues with base64 encoding approach
- **AI Engine Manager:** Added intelligent engine selection system
- **Cursor Agent:** Enhanced with code generation capabilities
- **Configuration System:** YAML-based flexible configuration management
- **Project Structure:** Organized test files and cleaned up unnecessary files
- **Documentation:** Added comprehensive Japanese README and feature guides

## 11. AI Engine Selection System

### Overview
The AI Engine Selection System allows users to dynamically choose which AI engine to use for different tasks, providing flexibility for compliance, cost optimization, and quality requirements.

### Available Engines
- **Claude (Anthropic)**: High-quality code generation and document creation
- **Gemini (Google)**: Code analysis and document improvement
- **Cursor**: Specialized code generation with AI assistance
- **Web Search**: Real-time information retrieval
- **Web Browser**: URL content fetching and summarization
- **Local**: Shell commands and git operations

### Configuration Modes

#### Default Mode
```yaml
ai_engines:
  default_engine: claude
  task_routing:
    code_generation: cursor
    document_generation: claude
    code_analysis: gemini
    web_search: web_search
    web_browsing: web_browser
    git_operations: local
    shell_operations: local
```

#### Compliance Mode
```yaml
ai_engines:
  compliance_mode: true
  allowed_engines:
    - gemini
    - local
```

#### Cost Optimization Mode
```yaml
ai_engines:
  cost_optimization: true
  cost_preferences:
    high_cost: claude
    medium_cost: gemini
    low_cost: web_search
    free: local
```

### Command Interface
```bash
# Basic configuration
ai engine set default <engine_name>
ai engine set task <task_type> <engine_name>

# Compliance mode
ai engine enable compliance [allowed_engines...]
ai engine disable compliance

# Cost optimization
ai engine enable cost optimization
ai engine disable cost optimization

# Engine management
ai engine set availability <engine_name> <true/false>
ai engine info
ai engine save
ai engine reset
```

### Task Complexity Assessment
The system automatically assesses task complexity based on keywords:
- **High Complexity**: "complex", "advanced", "sophisticated", "enterprise"
- **Medium Complexity**: "analysis", "optimize", "improve", "refactor"
- **Low Complexity**: "simple", "basic", "quick", "small"

### Use Cases
1. **All Gemini**: Set default to Gemini for all tasks
2. **Compliance**: Restrict to approved engines only
3. **Cost Optimization**: Use cheapest engine for simple tasks
4. **Code Generation Only Cursor**: Use Cursor only for code generation
5. **Hybrid Approach**: Different engines for different task types

## 12. Project Organization and Structure

### Current File Organization
```
AIris/
├── agents/                 # AIエージェント
│   ├── base.py            # 基底クラス
│   ├── code_agent.py      # コード生成エージェント
│   ├── shell_agent.py     # シェルコマンドエージェント
│   ├── web_search_agent.py # ウェブ検索エージェント
│   ├── web_browser_agent.py # ウェブブラウジングエージェント
│   ├── cursor_agent.py    # Cursorエディタ連携エージェント
│   ├── gemini_agent.py    # Gemini API連携エージェント
│   ├── git_agent.py       # Git操作エージェント
│   └── document_completion_agent.py # ドキュメント完成エージェント
├── airis/                  # メインアプリケーション
│   ├── main.py            # CLIエントリーポイント
│   ├── orchestrator.py    # タスクオーケストレーター
│   ├── llm.py             # LLMクライアント
│   ├── sandbox.py         # Dockerサンドボックス管理
│   ├── config.py          # 設定管理
│   ├── ai_engine_manager.py # AIエンジン選択管理
│   └── ai_engine_commands.py # AIエンジンコマンド処理
├── doc/                    # プロジェクトドキュメント
│   ├── 00_PROJECT_PROPOSAL.md
│   ├── 01_REQUIREMENTS_DEFINITION.md
│   ├── 02_SYSTEM_DESIGN.md
│   ├── 03_ARCHITECTURE_UPDATE.md
│   ├── 04_TECHNICAL_SPECIFICATIONS.md
│   ├── 05_CHANGELOG.md
│   ├── 06_TEST_PLAN.md
│   ├── 07_MANUAL_TEST_GUIDE.md
│   ├── 08_MANUAL_TEST_CHECKLIST.md
│   ├── 09_FEATURE_GUIDE.md
│   ├── CONTRIBUTING.md
│   ├── README.md
│   └── TASKS.md
├── test_files/            # テスト関連ファイル
│   ├── run_tests.py       # テスト実行スクリプト
│   ├── manual_test_runner.sh
│   └── test_projects/     # テスト用プロジェクト
├── tests/                 # ユニットテスト
│   ├── __init__.py
│   └── test_orchestrator.py
├── README.md              # 英語版README
├── README_JP.md           # 日本語版README
├── FEATURES.md            # 機能一覧
├── PROJECT_KNOWLEDGE.md   # プロジェクト知識ベース（英語）
├── PROJECT_KNOWLEDGE_JP.md # プロジェクト知識ベース（日本語）
├── config.yaml            # 設定ファイル
├── config.yaml.example    # 設定ファイルサンプル
├── requirements.txt       # Python依存関係
├── Dockerfile             # Dockerイメージ定義
├── docker-compose.yml     # Docker Compose設定
└── .gitignore             # Git除外設定
```

### Key Improvements Made
- **File Cleanup**: Removed unnecessary files (fibonacci.py, test_api_keys.py, test reports)
- **Test Organization**: Moved all test files to test_files/ directory
- **Project Structure**: Organized test projects under test_files/test_projects/
- **Documentation**: Added comprehensive Japanese README and feature guides
- **Privacy Protection**: Completely removed personal information from git history
- **Cross-Platform Support**: Eliminated absolute paths for better portability
- **Git Management**: Updated .gitignore for better test file management
