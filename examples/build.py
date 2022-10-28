"""
This example shows how to build a Docker image using Image.build method.

See also `use_docker_py.py` and `use_python_on_whales.py` for other ways to build an image.
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
    image.build(['-t', 'hello:latest', '.'])
