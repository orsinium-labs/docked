from io import StringIO
import pytest
import docked as d


@pytest.mark.parametrize('given, expected', [
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
    image = d.Image(d.Stage(base=d.BaseImage('alpine'), build=given))
    stdout = StringIO()
    code = image.lint(exit_on_failure=False, stdout=stdout)
    assert code == 1
    stdout.seek(0)
    actual = stdout.read().rstrip()
    assert actual == expected
