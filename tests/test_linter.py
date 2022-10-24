from io import StringIO
import pytest
import docked as d


@pytest.mark.parametrize('given, expected', [
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
    (
        [d.FROM('', 'hi')],
        'E0104: Base image name must not be empty',
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
