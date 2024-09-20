import dagger
import random
from dagger import dag, function, object_type


@object_type
class HelloDaggerFastapiRye:
    @function
    async def build_env(self, source: dagger.Directory) -> dagger.Container:
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

    @function
    async def test(self, source: dagger.Directory) -> str:
        """Return the result of running unit tests"""
        # Await the build_env function to get the container
        container = await self.build_env(source)
        # Now you can call .with_exec() on the container
        return await container.with_exec(["pytest"]).stdout()

    @function
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
    async def publish(self, source: dagger.Directory) -> str:
        """Publish the application container after building and testing it on-the-fly"""
        # Call Dagger Function to run unit tests
        await self.test(source)
        # Call Dagger Function to build the application image
        # Publish the image to ttl.sh
        return await self.build(source).publish(
            f"ttl.sh/myapp-{random.randrange(10 ** 8)}"
        )
