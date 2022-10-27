from io import StringIO
import pytest
import docked as d


@pytest.mark.parametrize('given, expected', [
    # ARG           01
    # CLONE         02
    # CMD           03
    # COPY          04
    # DOWNLOAD      05
    # ENTRYPOINT    06
    # ENV           07
    # EXPOSE        08
    # EXTRACT       09
    # HEALTHCHECK   10
    # ONBUILD       11
    # RUN           12
    (
        [d.RUN('vim ./hi.txt')],
        'I1201: Do not RUN vim',
    ),
    (
        [d.RUN('sudo echo 1')],
        'W1202: Do not use sudo',
    ),
    (
        [d.RUN('sudo')],
        'W1202: Do not use sudo',
    ),

    # SHELL         13
    # STOPSIGNAL    14
    # USER          15
    # VOLUME        16

    # WORKDIR       17
    (
        [d.WORKDIR('hello')],
        'W1701: WORKDIR path should be absolute',
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
