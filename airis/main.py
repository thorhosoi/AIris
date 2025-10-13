import typer
from airis.orchestrator import Orchestrator
import os
from airis.config import config

def create_project_structure(project_name: str):
    projects_root = config.get("projects_root_dir", "projects")
    project_path = os.path.join(projects_root, project_name)

    if os.path.exists(project_path):
        typer.echo(f"Project directory '{project_path}' already exists. Aborting project creation.")
        return

    os.makedirs(os.path.join(project_path, "doc"), exist_ok=True)
    os.makedirs(os.path.join(project_path, "src"), exist_ok=True)
    os.makedirs(os.path.join(project_path, "tests"), exist_ok=True)

    # Create template files
    with open(os.path.join(project_path, "README.md"), "w") as f:
        f.write(f"# {project_name} Project\n\nThis is the README for the {project_name} project.")
    
    with open(os.path.join(project_path, "doc", "01_requirements.md"), "w") as f:
        f.write(f"# {project_name} - Requirements Definition\n\n## 1. Introduction\n\n## 2. Functional Requirements\n\n## 3. Non-Functional Requirements")

    with open(os.path.join(project_path, "doc", "02_design.md"), "w") as f:
        f.write(f"# {project_name} - System Design\n\n## 1. Architecture\n\n## 2. Component Design")

    typer.echo(f"Project '{project_name}' created successfully at '{project_path}'.")

def main(prompt: str):
    """
    Airis: Your personal AI assistant.
    """
    print(f"Received task: {prompt}")

    # Check for project creation intent
    if prompt.lower().startswith("create new project"):
        project_name = prompt.lower().replace("create new project", "").strip()
        if not project_name:
            typer.echo("Please provide a project name. Example: 'create new project my_awesome_app'")
            return
        create_project_structure(project_name)
        return

    # Check for project selection intent
    if prompt.lower().startswith("use project"):
        project_name = prompt.lower().replace("use project", "").strip()
        if not project_name:
            typer.echo("Please provide a project name. Example: 'use project my_awesome_app'")
            return
        
        projects_root = config.get("projects_root_dir", "projects")
        project_path = os.path.join(projects_root, project_name)
        if not os.path.exists(project_path):
            typer.echo(f"Project '{project_name}' not found at '{project_path}'. Please create it first.")
            return
        
        config.set("current_project", project_name)
        typer.echo(f"Switched to project '{project_name}'.")
        return

    orchestrator = Orchestrator()
    display_result, generated_code = orchestrator.delegate_task(prompt)
    print("--- RESULT ---")
    print(display_result)

    # User approval step for file saving
    if generated_code and "Suggested filename:" in display_result:
        filename_line = [line for line in display_result.split('\n') if "Suggested filename:" in line][0]
        suggested_filename = filename_line.split(':', 1)[1].strip()
        
        response = typer.confirm(f"Airis suggests saving the generated code to {suggested_filename}. Do you approve?")
        if response:
            current_project = config.get("current_project")
            if current_project:
                projects_root = config.get("projects_root_dir", "projects")
                output_dir = os.path.join(projects_root, current_project, "src")
            else:
                output_dir = config.get("script_output_dir", "generated_scripts")
            
            os.makedirs(output_dir, exist_ok=True)
            file_path = os.path.join(output_dir, suggested_filename)
            try:
                with open(file_path, "w") as f:
                    f.write(generated_code)
                print(f"Code saved to {file_path}.")
            except Exception as e:
                print(f"Error saving file: {e}")
        else:
            print("Denied. Code will not be saved.")

if __name__ == "__main__":
    typer.run(main)
