import docker
from docker.types import Mount
import os

class Sandbox:
    def __init__(self, image="python:3.11-slim"):
        self.docker_client = docker.from_env()
        self.image = image
        self.host_project_dir = os.environ.get("HOST_PROJECT_DIR")
        if not self.host_project_dir:
            raise ValueError("HOST_PROJECT_DIR environment variable is not set. This is required for sandbox to function correctly.")

    def run_command(self, command: str, working_dir: str) -> tuple[str, str, int]:
        """
        Runs a command in a new Docker container and returns the output.

        Args:
            command: The command to execute.
            working_dir: The absolute path on the host to mount as the working directory.

        Returns:
            A tuple containing (stdout, stderr, exit_code).
        """
        container = None
        try:
            # The source for the mount must be a path on the host machine
            # We assume that the working_dir passed is relative to the project root
            # and HOST_PROJECT_DIR is the absolute path of the project root on the host.
            mount_source = os.path.join(self.host_project_dir, working_dir.replace("/app", "").lstrip('/'))
            mount = Mount(target="/app", source=mount_source, type="bind")
            container = self.docker_client.containers.create(
                self.image,
                command=["/bin/sh", "-c", command],
                mounts=[mount],
                working_dir="/app",
                detach=True,
            )
            container.start()
            result = container.wait()
            
            stdout = container.logs(stdout=True, stderr=False).decode('utf-8').strip()
            stderr = container.logs(stdout=False, stderr=True).decode('utf-8').strip()
            exit_code = result["StatusCode"]

            return stdout, stderr, exit_code
        finally:
            if container:
                container.remove(force=True)