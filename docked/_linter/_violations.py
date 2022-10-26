
from logging import ERROR, INFO, WARNING
from ._violation import Violation

DOCKER_GUIDE = 'https://docs.docker.com/develop/develop-images/dockerfile_best-practices/'

WORKDIR_01 = Violation(
    code=201,
    severity=WARNING,
    summary='WORKDIR path should be absolute',
    url=f'{DOCKER_GUIDE}#workdir'
)

RUN_01 = Violation(
    code=301,
    severity=INFO,
    summary='Do not RUN {bin}',
)
RUN_02 = Violation(
    code=302,
    severity=WARNING,
    summary='Do not use sudo',
    url=f'{DOCKER_GUIDE}#user',
)


# TODO
Violation(
    code=3002,
    severity=WARNING,
    summary='Last USER should not be root',
    url=f'{DOCKER_GUIDE}#user'
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
