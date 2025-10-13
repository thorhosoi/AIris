# Airis Project

Airis is a self-evolving AI workforce platform designed to automate complex intellectual tasks. It receives high-level instructions from a user via a conversational CLI and leverages autonomous AI agents to collaboratively solve them.

## Features

*   **Code Generation & Execution:** Generates and executes Python code in a secure Docker sandbox.
*   **Shell Command Execution:** Generates and executes shell commands in a secure Docker sandbox.
*   **Intelligent Orchestration:** Dispatches tasks to specialized AI agents.
*   **Filename Suggestion & User Approval:** Suggests appropriate filenames for generated code and seeks user approval before saving.
*   **Project Management:** Create and manage isolated project directories with predefined structures (`doc/`, `src/`, `tests/`).
*   **Document Generation:** Automatically generates requirements, design, and README documents for active projects.
*   **Docker Integration:** Runs entirely within Docker containers for easy setup and portability.

## Getting Started

### Prerequisites

*   **Docker:** Ensure Docker is installed and running on your system.
*   **Git:** For cloning the repository.

### Setup

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/thorhosoi/AIris.git
    cd AIris
    ```

2.  **Prepare `.env` file:**
    Create a `.env` file in the project root with your LLM API key (e.g., Anthropic):
    ```
    ANTHROPIC_API_KEY="YOUR_ANTHROPIC_API_KEY"
    ```
    Replace `YOUR_ANTHROPIC_API_KEY` with your actual API key.

3.  **Build the Docker image:**
    ```bash
    docker-compose build airis
    ```

## Usage

Airis is executed via `docker-compose run`. Here are some common commands:

*   **Run a task (e.g., generate a Python function):**
    ```bash
    echo y | docker-compose run -T --rm airis python3 -m airis.main "フィボナッチ数を計算するPython関数を書いて"
    ```

*   **Create a new project:**
    ```bash
    docker-compose run -T --rm airis python3 -m airis.main "create new project my_awesome_project"
    ```

*   **Switch to an active project:**
    ```bash
    docker-compose run -T --rm airis python3 -m airis.main "use project my_awesome_project"
    ```

*   **Generate a requirements document for the active project:**
    ```bash
    echo y | docker-compose run -T --rm airis python3 -m airis.main "generate docs requirements for my_awesome_project"
    ```

*   **Run unit tests:**
    ```bash
    docker-compose run --rm airis pytest
    ```

## Contributing

See [CONTRIBUTING.md](doc/CONTRIBUTING.md) for guidelines on how to contribute to Airis.
