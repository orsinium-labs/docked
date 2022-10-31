# docked

A human-friendly alternative to Dockerfile. It's a Python library for generating Docker images, with API designed to be safe, secure, and easy-to-use correctly.

**Features:**

+ **Just a Python library**. No custom syntax, no monkey-patching, no magic. Get the full power of Python.
+ **100% type-safe**. The code base is fully type annotated and type checked, and we put a lot of effort to make the best API that makes invalid or insecure usage impossible.
+ **Supports all versions** of Dockerfile and Containerfile standards and syntax.
+ Automatically picks the most **compatible syntax** version based on the features you use.
+ **Built-in linter** to help you to make safe and effective containers.
+ **API is very close to that of Dockerfile**.
+ Our top priority is to provide a **friendly and simple** way of making Docker images. We carefully designed our API to avoid the most common mistakes of Docker newcomers.
+ Generates a **human-readable** and valid Dockerfile, so you can use it together with any other tools without any vendor-lock.

## Why

The Dockerfile already exists, and yet we made this project. THere are many good reasons for that:

+ Python is powerful. You get loops, conditions, environment variables, command-line tools, and a lot of other cool stuff that Dockerfile will never get.
+ Python has a great tooling. You get linters, type-checker, autoformatters, debugger, autoomplete, syntax highlighting, and so on to make your code easy to write, read, and maintain.
+ Python has a great ecosystem. You can use docker.py to go beyond of just building containers, boto3 to access S3 secrets at build-time, slack SDK to send notifications about build status, toml to read config files, dotenv to support .env files, and anything else you can ever imagine.
+ Python has a consistent and expressive syntax designed by smart people over many years.

Our goal was to provide the best possible IDE assistance to the users. All API is concise, precise, explicit, well-documented, and 100% type anntated. Docked will give your team greater learning experience than Docker can ever dream of.

## Installation

```bash
python3 -m pip install docked
```

## Usage

No more words, it's time for code!

```python
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
    image.lint()
    print(image)
```

What's happening:

1. `d.Image` is equivalent of a single Dockerfile file. It wraps one or more stages. YOu can have many stage in per image in [multi-stage builds](https://docs.docker.com/build/building/multi-stage/).
1. `d.Stage` is a single "stage". You can have multiple s
1. `base=d.BaseImage(...)` is the image on which the stage is based. It can be anything available on [Docker Hub](https://hub.docker.com/).
1. `build=[...]` is a list of steps to perform when building the image. Most of the steps correspond to a [Docker instruction](https://docs.docker.com/engine/reference/builder/) with the same name.
1. `d.RUN(...)` is the same as [RUN](https://docs.docker.com/engine/reference/builder/#run) in Docker. It tells to run a list of the given shell-commands when building the image.
1. `d.cmd.pip_install` is a convenience function that will produce a command for `pip` to install the given packages. It's better than just passing `pip install cowsay` because it will produce a command that follows the best practice of installing Python packages in Docker images. Docked provides a few most useful convenience functions but not many, we don't want it to be too verbose.
1. `run=[...]` is a list of Docker instruction describing not how the image should be build but how it will behave when it is run. A good example is [VOLUME](https://docs.docker.com/engine/reference/builder/#volume) which cannot mount volumes when building an image, and so it can be passed in `run=[...]` but not in `build=[...]`
1. `image.lint()` runs built-in linter that will make sure we follow the best practice of building Docker images.
1. `print(image)` generates a Dockerfile and prints it into stdout.

Now, pipe it into docker and run the image:

```bash
python3 examples/cowsay.py | docker buildx build --tag=hello:latest -
docker run hello:latest
```

And you should see Mr. Cow:

```text
  ____________
| hello world! |
  ============
            \
             \
               ^__^
               (oo)\_______
               (__)\       )\/\
                   ||----w |
                   ||     ||

```

## Learn more

1. [docked.orsinium.dev](https://docked.orsinium.dev/) hosts documentation.
1. [examples](./examples/) directory has, you guessed it, examples. All are real and runnable.
1. You should be able to just install docked and start using it. It has quite good type annotations and docstrings, so let your IDE guide you.
