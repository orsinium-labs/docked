
from logging import ERROR, INFO, WARNING

from ._violation import Violation


DOCKER_GUIDE = 'https://docs.docker.com/develop/develop-images/dockerfile_best-practices/'

# ARG           01
# CLONE         02
# CMD           03

CMD_01 = Violation(
    code=301,
    severity=WARNING,
    summary='There should be only one CMD',
)
CMD_02 = Violation(
    code=302,
    severity=INFO,
    summary='Using `shell=True` for CMD is a bad idea.',
    url=f'{DOCKER_GUIDE}#cmd',
)

# COPY          04
# DOWNLOAD      05
# ENTRYPOINT    06
# ENV           07
# EXPOSE        08

EXPOSE_01 = Violation(
    code=801,
    severity=ERROR,
    summary='The port must be in 0-65535 range',
)

# EXTRACT       09
# HEALTHCHECK   10
# ONBUILD       11
# RUN           12

RUN_01 = Violation(
    code=1201,
    severity=INFO,
    summary='Do not RUN `{bin}`',
)
RUN_02 = Violation(
    code=1202,
    severity=WARNING,
    summary='Do not use `sudo`',
    url=f'{DOCKER_GUIDE}#user',
)
RUN_03 = Violation(
    code=1203,
    severity=INFO,
    summary='Avoid running `apt-get {subcmd}`',
)
RUN_04 = Violation(
    code=1204,
    severity=WARNING,
    summary='Combine `apt-get update` with `apt-get install` in a single RUN',
)

# SHELL         13
# STOPSIGNAL    14
# USER          15

USER_01 = Violation(
    code=1501,
    severity=WARNING,
    summary='Last USER should not be root',
    url=f'{DOCKER_GUIDE}#user'
)

# VOLUME        16
# WORKDIR       17

WORKDIR_01 = Violation(
    code=1701,
    severity=WARNING,
    summary='WORKDIR path should be absolute',
    url=f'{DOCKER_GUIDE}#workdir'
)


Violation(
    code=101,
    severity=ERROR,
    summary='Only ARG can go before FROM but found {step}',
)
Violation(
    code=102,
    severity=WARNING,
    summary='Specify base image tag',
)
Violation(
    code=103,
    severity=WARNING,
    summary='Base image tag should not be `latest`',
)
