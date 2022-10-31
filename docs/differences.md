# Differences from Dockerfile

The project started as one-to-one mapping of Dockerfile instructions to Python, and then we evolved some  components to provide a more friendly and safe API. If you're familiar with Dockerfile and looking for a quick start with docked, there are some differences that you should know:

1. There is no [FROM](https://docs.docker.com/engine/reference/builder/#from). Instead, pass arguments (`base`, `name`, and `platform`) into {py:class}`docked.Stage`.
1. There is no [MAINTAINER](https://docs.docker.com/engine/reference/builder/#maintainer-deprecated). Use `labels` instead.
1. There is no [LABEL](https://docs.docker.com/engine/reference/builder/#label). Pass `labels` argument into {py:class}`docked.Stage` instead.
1. There is no [ADD](https://docs.docker.com/engine/reference/builder/#add). Instead, use {py:class}`docked.COPY`, {py:class}`docked.EXTRACT`, {py:class}`docked.CLONE`, or {py:class}`docked.DOWNLOAD`.
1. There is no way to declare ARG before FROM. If you need to parametrize the base image, do it on the Python level.
1. If shell will be used to run the command or not depends not on if you pass a list or a string but on `shell` argument. The argument is True by default for {py:class}`docked.RUN` and False for everything else ({py:class}`docked.HEALTHCHECK`, {py:class}`docked.CMD`, {py:class}`docked.ENTRYPOINT`).
1. We call instructions steps ({py:class}`docked.Step`) for bravity.
1. There is a clear separation between commans that affect build and the ones that take effect in runtime. That means, there is no way to put {py:class}`docked.VOLUME` somewhere before, let's say, {py:class}`docked.RUN`.
