# Airis

**Airis: Your self-evolving AI workforce.**

`Airis` is a next-generation AI workforce platform where autonomous AI agents collaborate to solve complex intellectual tasks given through a conversational interface.

This MVP (Minimum Viable Product) demonstrates the core functionality: interpreting natural language instructions to execute shell commands and generate/run Python code in a secure, sandboxed environment.

---

## ✨ Features

- **Conversational CLI:** Interact with Airis through a simple, intuitive command-line interface.
- **Task Classification:** An AI-powered `Orchestrator` analyzes your instructions to determine the required task type.
- **Agent-based Execution:**
    - **Shell Agent:** Translates natural language into shell commands (e.g., "list all files") and executes them safely.
    - **Code Agent:** Generates and executes Python code based on your requirements (e.g., "write a fibonacci function").
- **Sandboxed Environment:** All code and commands are executed inside temporary Docker containers, ensuring the safety of your host machine.

## 📋 Requirements

- **Docker** and **Docker Compose**

## 🚀 Quick Start

Follow these steps to get Airis up and running.

### 1. Configuration

First, you need to set up your configuration files.

**a. Create `config.yaml`**

Copy the example configuration file:

```bash
cp config.yaml.example config.yaml
```

You can edit this file to configure AI engines, LLM settings, and other options. The configuration includes:

- **AI Engine Selection**: Choose which AI engine to use for different tasks
- **Task Routing**: Override default engine for specific task types
- **Compliance Mode**: Restrict to approved engines only
- **Cost Optimization**: Automatically select cheaper engines for simple tasks

**b. Create `.env` file**

Create a file named `.env` in the project root and add your LLM API key. The application will load this file to authenticate with the LLM provider.

For example:

```
# For Anthropic Claude
ANTHROPIC_API_KEY=sk-ant-xxxxxxxx

# For OpenAI
# OPENAI_API_KEY=sk-xxxxxxxx
```

### 2. Build the Docker Image

Use Docker Compose to build the application image. This will install all necessary dependencies.

```bash
docker-compose build
```

### 3. Run the Application

Start the main application container in the background.

```bash
docker-compose up -d
```

### 4. Start a Session

Connect to the running container to start your interactive session with Airis.

```bash
docker-compose exec airis python -m airis.main
```

You will be greeted with the Airis prompt (`> `). Start giving it instructions!

**Example Instructions:**
- `List all files in the current directory, including hidden ones.`
- `Write a Python script to print the first 20 prime numbers.`

To end the session, type `exit` or `quit`.

## ⚙️ AI Engine Configuration

### Quick Setup Examples

**All tasks use Claude:**
```yaml
ai_engines:
  default_engine: claude
  task_routing: {}  # Empty means all tasks use default
```

**Code generation only with Cursor:**
```yaml
ai_engines:
  default_engine: claude
  task_routing:
    code_generation: cursor
```

**All Gemini for cost efficiency:**
```yaml
ai_engines:
  default_engine: gemini
  task_routing: {}  # Empty means all tasks use default
```

**Enterprise compliance mode:**
```yaml
ai_engines:
  compliance_mode: true
  allowed_engines: [gemini, local]
  default_engine: gemini
```

**Cost optimization enabled:**
```yaml
ai_engines:
  cost_optimization: true
  default_engine: claude
  # System will automatically choose cheaper engines for simple tasks
```

## 🛠️ For Developers

### Project Structure

- **`airis/`**: Main application source code.
    - **`main.py`**: The CLI entrypoint (using Typer).
    - **`orchestrator.py`**: The central "brain" that interprets instructions and delegates to agents.
    - **`llm.py`**: The client for interacting with Large Language Models.
    - **`sandbox.py`**: Manages the secure execution of code/commands in Docker.
    - **`config.py`**: Handles loading of `config.yaml`.
- **`agents/`**: Contains the specialist agents.
    - **`base.py`**: Abstract base class for all agents.
    - **`shell_agent.py`**: Agent for handling shell commands.
    - **`code_agent.py`**: Agent for handling Python code generation/execution.
- **`doc/`**: Project documentation (proposal, requirements, design).
- **`Dockerfile` & `docker-compose.yml`**: Defines the containerized development environment.

### Adding a New Agent

1.  Create a new agent class in the `agents/` directory, inheriting from `BaseAgent`.
2.  Implement the `execute` method.
3.  Import and instantiate your new agent in `airis/orchestrator.py`.
4.  Update the `Orchestrator`'s classification logic and `run` method to delegate tasks to your new agent.
