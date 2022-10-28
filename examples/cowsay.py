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
    base=d.BaseImage('python', tag='3.11-alpine'),
    build=[
        d.RUN(
            d.cmd.pip_install('cowsay'),
        ),
    ],
    run=[
        d.CMD(['cowsay', 'hello world!'])
    ],
)
image = d.Image(stage)

if __name__ == '__main__':
    print(image)
