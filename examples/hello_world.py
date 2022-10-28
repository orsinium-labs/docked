"""
This example shows generation of the most simple Dockerfile.

Generate a Dockerfile:

    python3 ./examples/hello_world.py > Dockerfile

Directly build and run Docker image without saving a file:

    python3 ./examples/hello_world.py | docker buildx build --tag=hello:latest -
    docker run hello:latest

"""
import docked as d


stage = d.Stage(
    base=d.BaseImage('busybox'),
    run=[
        d.CMD(['echo', 'hello world!'])
    ],
)
image = d.Image(stage)

if __name__ == '__main__':
    print(image)
