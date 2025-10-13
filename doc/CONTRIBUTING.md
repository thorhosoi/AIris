# Contributing to Airis

We welcome contributions to the Airis project! By following these guidelines, you can help us maintain a high-quality codebase and ensure a smooth collaboration process.

## 1. Getting Started

### 1.1. Prerequisites

Before you begin, ensure you have the following installed:

*   **Docker:** Airis runs within Docker containers. Follow the official Docker installation guide for your operating system.
*   **Git:** For version control.

### 1.2. Setup

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/thorhosoi/AIris.git
    cd AIris
    ```

2.  **Prepare `.env` file:**
    Create a `.env` file in the project root with your LLM API key:
    ```
    ANTHROPIC_API_KEY="YOUR_ANTHROPIC_API_KEY"
    ```
    Replace `YOUR_ANTHROPIC_API_KEY` with your actual API key.

3.  **Build the Docker image:**
    ```bash
    docker-compose build airis
    ```

## 2. Development Workflow

### 2.1. Running Airis

To run Airis with a specific task:

```bash
# Example: Generate a Fibonacci function and save it
echo y | docker-compose run -T --rm airis python3 -m airis.main "フィボナッチ数を計算するPython関数を書いて"
```

### 2.2. Creating and Managing Projects

*   **Create a new project:**
    ```bash
    docker-compose run -T --rm airis python3 -m airis.main "create new project my_awesome_project"
    ```
*   **Switch to an active project:**
    ```bash
    docker-compose run -T --rm airis python3 -m airis.main "use project my_awesome_project"
    ```
    *(Note: The `use project` command updates `config.yaml` on the host, which is then read by subsequent container runs.)*

### 2.3. Generating Documentation

```bash
# Example: Generate requirements document for the active project
echo y | docker-compose run -T --rm airis python3 -m airis.main "generate docs requirements for my_awesome_project"
```

### 2.4. Running Tests

To run the unit tests:

```bash
docker-compose run --rm airis pytest
```

## 3. Code Style and Quality

*   **Python:** Adhere to PEP 8 guidelines.
*   **Type Hinting:** Use type hints consistently.
*   **Docstrings:** Provide clear and concise docstrings for all functions and classes.

## 4. Submitting Changes

1.  **Create a new branch:**
    ```bash
    git checkout -b feature/your-feature-name
    ```
2.  **Make your changes.**
3.  **Run tests:** Ensure all existing tests pass and add new tests for your changes.
4.  **Update documentation:** If your changes affect functionality, update relevant documentation files (`.md` files in `doc/` and `GEMINI.md`).
5.  **Commit your changes:** Write clear, concise commit messages.
6.  **Push your branch:**
    ```bash
    git push origin feature/your-feature-name
    ```
7.  **Open a Pull Request:** Describe your changes and the problem they solve.
