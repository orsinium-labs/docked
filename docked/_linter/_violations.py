
from logging import ERROR, INFO, WARNING
from ._violation import Violation

FROM_01 = Violation(
    code=101,
    severity=ERROR,
    summary='Only ARG can go before FROM but found {step}',
)
FROM_02 = Violation(
    code=102,
    severity=WARNING,
    summary='Specify base image tag',
)
FROM_03 = Violation(
    code=103,
    severity=WARNING,
    summary='Base image tag should not be `latest`',
)
FROM_04 = Violation(
    code=104,
    severity=ERROR,
    summary='Base image name must not be empty',
)

V3000 = Violation(
    code=3000,
    severity=ERROR,
    summary='Use absolute WORKDIR',
)
V3001 = Violation(
    code=3001,
    severity=INFO,
    summary='Do not RUN {bin} in Docker',
)
V3002 = Violation(
    code=3002,
    severity=WARNING,
    summary='Last USER should not be root',
)
