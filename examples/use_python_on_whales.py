"""
This example shows how to build an image with python-on-whales.

The python-on-whales is a type-safe Python wrapper around Docker CLI.

https://github.com/gabrieldemarmiesse/python-on-whales
"""
from python_on_whales import docker

import docked as d


stage = d.Stage(
    base=d.BaseImage('busybox'),
    run=[
        d.CMD(['echo', 'hello world!'])
    ],
)
image = d.Image(stage)

if __name__ == '__main__':
    docker.build(
        context_path='.',
        file=image.save(),
        tags='hello:latest',
    )
    print(docker.run('hello:latest'))
