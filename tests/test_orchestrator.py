import pytest
from unittest.mock import MagicMock, patch
from airis.orchestrator import Orchestrator
from agents.code_agent import CodeAgent
from agents.shell_agent import ShellAgent

@pytest.fixture
def orchestrator(mock_code_agent, mock_shell_agent, mock_git_agent):
    return Orchestrator()

@pytest.fixture
def mock_llm_client():
    with patch('airis.orchestrator.llm_client') as mock:
        yield mock

@pytest.fixture
def mock_code_agent():
    with patch('airis.orchestrator.CodeAgent') as mock:
        mock_instance = mock.return_value
        mock_instance.execute.return_value = ("Code executed successfully.", "def test_func(): pass")
        yield mock_instance

@pytest.fixture
def mock_git_agent():
    with patch('airis.orchestrator.GitAgent') as mock:
        mock_instance = mock.return_value
        mock_instance._check_git_repo.return_value = True
        mock_instance.execute.return_value = "✅ Git operations completed"
        yield mock_instance

@pytest.fixture
def mock_shell_agent():
    with patch('airis.orchestrator.ShellAgent') as mock:
        mock_instance = mock.return_value
        mock_instance.execute.return_value = "Command executed successfully."
        yield mock_instance

def test_orchestrator_delegates_to_code_agent(orchestrator, mock_code_agent, mock_llm_client, mock_git_agent):
    mock_llm_client.invoke.return_value.content = "test_file.py"
    result = orchestrator.delegate_task("write python code")
    mock_code_agent.execute.assert_called_once_with("write python code")
    assert "Code executed successfully." in result[0]
    assert "Code saved to:" in result[0]
    assert "test_file.py" in result[0]

def test_orchestrator_delegates_to_shell_agent(orchestrator, mock_shell_agent):
    result = orchestrator.delegate_task("run shell command")
    mock_shell_agent.execute.assert_called_once_with("run shell command")
    assert "Command executed successfully." in result

def test_orchestrator_defaults_to_code_agent(orchestrator, mock_code_agent, mock_llm_client, mock_git_agent):
    mock_llm_client.invoke.return_value.content = "default.py"
    result = orchestrator.delegate_task("just a task")
    mock_code_agent.execute.assert_called_once_with("just a task")
    assert "Code executed successfully." in result[0]
    assert "Code saved to:" in result[0]
    assert "default.py" in result[0]
