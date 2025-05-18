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

import random
from typing import Optional
import dagger
from dagger import dag, function, object_type


@object_type
class HelloWorld:
    async def build_dev(self, source: dagger.Directory) -> dagger.Container:
        """Build a ready-to-use development environment"""
        return (
            dag.container()
            # start from a base Python container
            .from_("python:3.12-slim")
            # add the source code at /src
            .with_directory("/src", source)
            # change the working directory to /src
            .with_workdir("/src")
            # mount pip cache
            .with_mounted_cache("/root/.cache/pip", dag.cache_volume("pip-cache"))
            # install development dependencies
            .with_exec(
                ["pip", "install", "--no-cache-dir", "-r", "requirements-dev.lock"]
            )
        )

    def build(self, source: dagger.Directory) -> dagger.Container:
        """Build a production image with only requirements.lock and app directory"""
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
        container = await self.build_dev(source)
        # Now you can call .with_exec() on the container

        return await container.with_exec(["pytest", "--capture=no"]).stdout()

    @function
    async def publish(self, source: dagger.Directory) -> str:
        """
        Publish the application container after building and testing it on-the-fly

        dagger call publish --source=.
        """
        self.test(source)
        image_full_name = f"ttl.sh/fastapi-app-{random.randrange(10 ** 8)}:latest"
        return await self.build(source).publish(image_full_name)

    @function
    async def kustomize(
        self,
        directory_arg: dagger.Directory,
        image_name: str,
        image_tag: str,
        # env: str | None = "base",
    ) -> dagger.Directory:
        """
        Update the kustomization.yaml file with the new image URL

        dagger call kustomize --directory_arg=. --image_name=image_name --image_tag=v0.0.1 export --path .
        """

        return (
            dag.container()
            .from_("registry.k8s.io/kustomize/kustomize:v5.0.0")
            .with_mounted_directory("/mnt", directory_arg)
            .with_workdir("/mnt")
            # .with_workdir(f"/mnt/k8s/base/{env}")
            .with_exec(
                [
                    "kustomize",
                    "edit",
                    "set",
                    "image",
                    f"fastapi-app:latest={image_name}:{image_tag}",
                ]
            )
            .directory("/mnt")
        )

    @function
    async def build_and_promote(
        self, directory_arg: dagger.Directory, env: str | None = "nonprod"
    ) -> dagger.Directory:
        """
        Update the kustomization.yaml file with the new image URL

        dagger call build-and-promote --directory_arg=. export --path k8s/
        """

        # Publish the new image
        image_full_name = await self.publish(directory_arg)

        # Extract the image name and tag
        image_name, image_tag = image_full_name.split("@")[0].split(":")

        # Update the kustomization.yaml file with the new image URL
        return await self.kustomize(directory_arg, image_name, image_tag, env)

    async def build_release_container(
        self, source: dagger.Directory
    ) -> dagger.Container:
        """Build a container for running release-please commands"""
        return (
            dag.container()
            .from_("node:20-slim")
            .with_workdir("/app")
            .with_directory(
                "/app",
                source,
                include=[
                    "release-please-config.json",
                    ".release-please-manifest.json",
                    "apps/*",
                ],
            )
            .with_exec(["npm", "install", "-g", "release-please"])
        )

    @function
    async def create_release_pr(
        self,
        source: dagger.Directory,
        github_token: str,
        repo_url: str = "https://github.com/pmpaulino/homelab",
        dry_run: bool = False,
        snapshot: bool = False,
        release_as: Optional[str] = None,
    ) -> str:
        """Create a release PR using Release Please.

        Args:
            source: Source directory containing the repository
            github_token: GitHub token for authentication
            repo_url: GitHub repository URL
            dry_run: If True, only show what would be done
            snapshot: If True, create a snapshot release
            release_as: Override the version to release as
        """
        container = await self.build_release_container(source)

        # Build the release-please command
        cmd = [
            "release-please",
            "release-pr",
            f"--repo-url={repo_url}",
            f"--token={github_token}",
        ]

        if dry_run:
            cmd.append("--dry-run")
        if snapshot:
            cmd.append("--snapshot")
        if release_as:
            cmd.append(f"--release-as={release_as}")

        # Run release-please
        return await container.with_exec(cmd).stdout()

    @function
    async def create_github_release(
        self,
        source: dagger.Directory,
        github_token: str,
        repo_url: str = "https://github.com/pmpaulino/homelab",
        release_as: Optional[str] = None,
    ) -> str:
        """Create a GitHub release using Release Please.

        Args:
            source: Source directory containing the repository
            github_token: GitHub token for authentication
            repo_url: GitHub repository URL
            release_as: Override the version to release as
        """
        container = await self.build_release_container(source)

        cmd = [
            "release-please",
            "github-release",
            f"--repo-url={repo_url}",
            f"--token={github_token}",
        ]
        if release_as:
            cmd.append(f"--release-as={release_as}")

        return await container.with_exec(cmd).stdout()

    @function
    async def build_and_push(
        self,
        source: dagger.Directory,
        github_token: str,
        registry: str = "ghcr.io",
        image_name: str = "pmpaulino/hello-world",
        tag: Optional[str] = None,
    ) -> str:
        """Build and push the container to GitHub Container Registry.
        
        Args:
            source: Source directory containing the repository
            github_token: GitHub Personal Access Token with write:packages scope
            registry: Container registry URL (defaults to ghcr.io)
            image_name: Name of the image to push (defaults to pmpaulino/hello-world)
            tag: Optional tag for the image. If not provided, uses version from manifest
        """
        # Build the container
        container = self.build(source)

        # Get version from manifest if tag not provided
        if not tag:
            manifest = await source.file(".release-please-manifest.json").contents()
            import json
            manifest_data = json.loads(manifest)
            tag = manifest_data.get("apps/hello-world", "latest")

        # For GitHub Container Registry, username is the same as the image name owner
        username = image_name.split("/")[0]

        # Create a secret from the token
        token_secret = dag.set_secret("github-token", github_token)

        # Push to registry with authentication
        return await container.with_registry_auth(registry, username, token_secret).publish(
            f"{registry}/{image_name}:{tag}"
        )
