"""
This example shows how to build an image with the official Docker SDK.

https://github.com/docker/docker-py
"""
import docked as d
import docker

stage = d.Stage(
    d.FROM('busybox', tag='latest'),
    d.CMD(['echo', 'hello world!'])
)
image = d.Image(stage)

if __name__ == '__main__':
    client = docker.from_env()
    client.images.build(
        path='.',
        dockerfile=image.save(),
        tag='hello:latest',
    )
    stdout = client.containers.run('hello:latest')
    print(stdout.decode())