"""
The example shows how to provide a CLI for your build scripts.


The script accepts one argument -- the Python version to use.

IPython:
    https://github.com/ipython/ipython

Usage:

    python3 examples/ipython.py 3.11 | docker buildx build --tag=ipython:latest -
    docker run -it ipython:latest

"""

from argparse import ArgumentParser

import docked as d


def get_image(python_version: str = '3.11') -> d.Image:
    stage = d.Stage(
        base=d.BaseImage('python', f'{python_version}-alpine'),
        build=[
            d.RUN(
                d.cmd.pip_install('ipython')
            ),
        ],
        run=[
            d.CMD('ipython'),
        ],
    )
    return d.Image(stage)


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('python', help='Python version to use')
    args = parser.parse_args()
    print(get_image(args.python))
