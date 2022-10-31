# Build

Since Python is powerful and the ecosystem is vast, there are multiple options available to you on how you can build images described by Docked, each having its own benefits.

## Piping

This is the way that requires a bit of shell piping but gives you the best control over how the build happens.

1. In your code, simply print the image, and it will produce the Dockerfile:

    ```python
    if __name__ == '__main__':
        print(image)
    ```

1. Run the script and pipe its output into Docker CLI:

    ```bash
    python3 ./examples/hello_world.py | docker buildx build --tag=hello:latest -
    ```

## Writing Dockerfile

You can also produce the intermediate Dockerfile and then do operations with it. Having this intermediate step is beneficial when you want to build the image later, in an environment without Python installed. For example, on CI using [kaniko](https://github.com/GoogleContainerTools/kaniko).

```bash
python3 ./examples/hello_world.py > Dockerfile
```

## Image.build

The library provides the {py:class}`docked.Image`.build method that will generate the Dockerfile for you and pass it into Docker CLI. This is useful when you want the script to automatically build itself but don't want to bring any third-party dependencies.

```python
if __name__ == '__main__':
    image.build(['-t', 'hello:latest', '.'])
```

## python-on-whales

The [python-on-whales](https://github.com/gabrieldemarmiesse/python-on-whales) library is a type-safe wrapper around Docker CLI. This is the best solution if you're going to do a lot of different operations with Docker and want to automate it.

```python
from python_on_whales import docker

...

if __name__ == '__main__':
    docker.build(
        context_path='.',
        file=image.save(),
        tags='hello:latest',
    )
    print(docker.run('hello:latest'))
```

## docker.py

There is also an [official Python library](https://github.com/docker/docker-py) for Docker. It might be not as nice and friendly as python-on-hwales, but it is official, and so should be more stable.

```python
import docker

...

if __name__ == '__main__':
    client = docker.from_env()
    client.images.build(
        path='.',
        dockerfile=image.save(),
        tag='hello:latest',
    )
    stdout = client.containers.run('hello:latest')
    print(stdout.decode())
```
