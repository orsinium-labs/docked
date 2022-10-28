"""
The examples shows how to create a nice image for a CLI tool.

HTTPie:
    https://httpie.io/

Usage:

    python3 examples/httpie.py | docker buildx build --tag=httpie:latest -
    docker run httpie:latest GET https://httpbin.org/get

"""

import docked as d


HTTPIE_VERSION = '3.2.1'

stage = d.Stage(
    base=d.BaseImage('python', '3.10-alpine'),
    build=[
        d.RUN(
            d.cmd.pip_install(f'httpie=={HTTPIE_VERSION}')
        ),
    ],
    run=[
        d.ENTRYPOINT('http --print hb'),
        d.CMD('--help'),
    ],
)
image = d.Image(stage)

if __name__ == '__main__':
    print(image)
