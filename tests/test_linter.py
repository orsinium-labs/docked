from io import StringIO
import pytest
import docked as d


@pytest.mark.parametrize('given, expected', [
    # FROM
    (
        [d.LABEL('a', 'b'), d.FROM('c', 'd')],
        'E0101: Only ARG can go before FROM but found LABEL',
    ),
    (
        [d.FROM('ubuntu')],
        'W0102: Specify base image tag',
    ),
    (
        [d.FROM('ubuntu', 'latest')],
        'W0103: Base image tag should not be `latest`',
    ),

    # WORKDIR
    (
        [d.WORKDIR('hello')],
        'W0201: WORKDIR path should be absolute',
    ),

    # RUN
    (
        [d.RUN('vim ./hi.txt')],
        'I0301: Do not RUN vim',
    ),
    (
        [d.RUN('sudo echo 1')],
        'W0302: Do not use sudo',
    ),
    (
        [d.RUN('sudo')],
        'W0302: Do not use sudo',
    ),

])
def test_linter(given: list, expected: str) -> None:
    image = d.Image(d.Stage(*given))
    stdout = StringIO()
    code = image.lint(exit_on_failure=False, stdout=stdout)
    assert code == 1
    stdout.seek(0)
    actual = stdout.read().rstrip()
    assert actual == expected
