# Build

Since Python is powerful and ecosystem is vast, there are multiple options availabe to you on how you can build images described by Docked, each having its own benefits.

## Piping

This is the way that requires a bit of shell piping but gives you the best control over how build happens.

1. In you code, simply print the image, and it will produce the Dockerfile: .
1. Run the script and pipe its output into Docker CLI.

## Writing Dockerfile

You can also produce the intermediate Dockerfile and then do operations with it. Having this intermediate step is benefitial when you want to build the image  later, in an environment without Python installed. For example, on CI usng kaniko.

## Image.build

The library provide Image.build methodthat will generate the dockerfile for you and pass it into Docker CLI. This is useful when you want the script to automaticall build itself but don't want to bring any third-party dependencies.

## python-on-whales

The python-on-whales library is a type-safe wrapper around Docker CLI. This is the best solution if you're going to do a lot of different operations with Docker and want to automate it.

## docker.py

There is also an official Python library for docker. It might be not as nice and friendly as python-on-hwales, but it is official, and so should be more stable.
