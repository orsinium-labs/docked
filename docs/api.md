# API

## Basics

```{eval-rst}
.. autoclass:: docked.Image
    :members:

.. autoclass:: docked.Stage
    :members:

```

## Build steps

```{eval-rst}
.. autoclass:: docked.BuildStep
.. autoclass:: docked.ARG
.. autoclass:: docked.CLONE
.. autoclass:: docked.COPY
.. autoclass:: docked.DOWNLOAD
.. autoclass:: docked.ENV
.. autoclass:: docked.EXTRACT
.. autoclass:: docked.ONBUILD
.. autoclass:: docked.RUN
.. autoclass:: docked.SHELL
.. autoclass:: docked.USER
.. autoclass:: docked.WORKDIR
```

## Run steps

```{eval-rst}
.. autoclass:: docked.RunStep
.. autoclass:: docked.CMD
.. autoclass:: docked.ENTRYPOINT
.. autoclass:: docked.EXPOSE
.. autoclass:: docked.HEALTHCHECK
.. autoclass:: docked.STOPSIGNAL
.. autoclass:: docked.VOLUME
```

## Other types

```{eval-rst}
.. autoclass:: docked.BaseImage
.. autoclass:: docked.BindMount
.. autoclass:: docked.CacheMount
.. autoclass:: docked.Checksum
.. autoclass:: docked.Mount
.. autoclass:: docked.SecretMount
.. autoclass:: docked.SSHMount
```

## Helpers

```{eval-rst}
.. automodule:: docked.cmd
    :members:
```
