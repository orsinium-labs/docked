
from logging import ERROR, INFO, WARNING
from ._violation import Violation

FROM_01 = Violation(
    code=101,
    severity=ERROR,
    summary='Only ARG can go before FROM but found {step}',
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
