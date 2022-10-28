# Differences from Dockerfile

The project started as one-to-one mapping of Dockerfile instructions to Python, and then we evolved some  components to provide a more friendly and safe API. If you're familiar with Dockerfile and looking for a quick start with docked, there are some differences that you should know:

1. There is no FROM. Instead, pass arguments (base, name, and platform) into Stage.
1. There is no MAINTAINER. Use labels instead.
1. There is no LABEL. Pass `labels` argument into Stage instead.
1. There is no ADD. Instead, use COPY, EXTRACT, CLONE, or DOWNLOAD.
1. There is no way to declare ARG before FROM. If you need to parametrize the base image, do it on the Python level.
1. If shell will be used to run the command or not depends not on if you pass a list or a string but on `shell` argument. The argument is True by default for RUN and False for everything else (HEALTHCHECK, CMD, ENTRYPOINT).
1. We call instructions steps for bravity.
1. There is a clear separation between commans that affect build and the ones that take effect in runtime. That means, there is no way to put VOLUME somewhere before, let's say, RUN.
