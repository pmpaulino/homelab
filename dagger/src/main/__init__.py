"""A generated module for HelloDaggerFastapiRye functions

This module has been generated via dagger init and serves as a reference to
basic module structure as you get started with Dagger.

Two functions have been pre-created. You can modify, delete, or add to them,
as needed. They demonstrate usage of arguments and return types using simple
echo and grep commands. The functions can be called from the dagger CLI or
from one of the SDKs.

The first line in this comment block is a short description line and the
rest is a long description with more detail on the module's purpose or usage,
if appropriate. All modules should have a short description.
"""

# NOTE: it's recommended to move your code into other files in this package
# and keep __init__.py for imports only, according to Python's convention.
# The only requirement is that Dagger needs to be able to import a package
# called "main" (i.e., src/main/).
#
# For example, to import from src/main/main.py:
# >>> from .main import HelloDaggerFastapiRye as HelloDaggerFastapiRye

import dagger
from dagger import dag, function, object_type

import random


@object_type
class HelloDaggerFastapiRye:
    async def build_local_env(self, source: dagger.Directory) -> dagger.Container:
        """Build a ready-to-use development environment"""
        return (
            dag.container()
            # start from a base Python container
            .from_("python:3.12")
            # add the source code at /src
            .with_directory("/src", source)
            # change the working directory to /src
            .with_workdir("/src")
            # install development dependencies
            .with_exec(["pip", "install", "-r", "requirements-dev.lock"])
        )

    def build_env(self, source: dagger.Directory) -> dagger.Container:
        """
        Build a production image with only requirements.lock and app directory

        dagger call test --source=.
        """
        return (
            dag.container()
            .from_("python:3.12-slim")
            .with_workdir("/")
            .with_file("/requirements.lock", source.file("requirements.lock"))
            .with_env_variable("PYTHONDONTWRITEBYTECODE", "1")
            .with_exec(["pip", "install", "--no-cache-dir", "-r", "requirements.lock"])
            .with_directory("/app", source.directory("app"))
            .with_exposed_port(80)
            .with_entrypoint(
                ["fastapi", "run", "/app/main.py", "--proxy-headers", "--port", "80"]
            )
        )

    @function
    async def test(self, source: dagger.Directory) -> str:
        """
        Return the result of running unit tests

        dagger call test --source=.
        """
        # Await the build_env function to get the container
        container = await self.build_local_env(source)
        # Now you can call .with_exec() on the container
        return await container.with_exec(["pytest"]).stdout()


    @function
    async def publish(self, source: dagger.Directory) -> str:
        """
        Publish the application container after building and testing it on-the-fly

        dagger call publish --source=.
        """
        self.test(source)
        image_full_name = f"ttl.sh/fastapi-app-{random.randrange(10 ** 8)}:latest"
        return await self.build_env(source).publish(image_full_name)

    @function
    async def kustomize(
        self,
        directory_arg: dagger.Directory,
        image_name: str,
        image_tag: str,
        env: str | None = "nonprod",
    ) -> dagger.Directory:
        """Update the kustomization.yaml file with the new image URL"""

        return (
            dag.container()
            .from_("registry.k8s.io/kustomize/kustomize:v5.0.0")
            .with_mounted_directory("/mnt", directory_arg)
            .with_workdir(f"/mnt/k8s/overlays/{env}")
            .with_exec(
                [
                    "kustomize",
                    "edit",
                    "set",
                    "image",
                    f"fastapi-app:latest={image_name}:{image_tag}",
                ]
            )
            .with_workdir("/mnt/k8s")
            .with_exec(
                [
                    "kustomize",
                    "build",
                    f"overlays/{env}",
                    "-o",
                    f"manifests/{env}/manifests.yaml",
                ]
            )
            .directory("/mnt/k8s")
        )

    @function
    async def build_and_promote(
        self, directory_arg: dagger.Directory, env: str | None = "nonprod"
    ) -> dagger.Directory:
        """Update the kustomization.yaml file with the new image URL"""

        # Publish the new image
        image_full_name = await self.publish(directory_arg)

        # Extract the image name and tag
        image_name, image_tag = image_full_name.split("@")[0].split(":")

        # Update the kustomization.yaml file with the new image URL
        return await self.kustomize(directory_arg, image_name, image_tag, env)
