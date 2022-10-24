from io import StringIO
import pytest
import docked as d


@pytest.mark.parametrize('given, expected', [
    (
        [d.LABEL('a', 'b'), d.FROM('c', 'd')],
        'E101: Only ARG can go before FROM but found LABEL',
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
