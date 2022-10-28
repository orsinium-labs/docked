from datetime import timedelta
from pathlib import PosixPath
from signal import SIGKILL

import pytest

import docked as d


@pytest.mark.parametrize('given, expected', [
    # ---
    (d.ARG('user'), 'ARG user'),
    (d.ARG('user', 'root'), 'ARG user=root'),
    (d.ARG('user', 'gram orsinium'), 'ARG user=gram orsinium'),  # is that right?

    # ---
    (d.RUN('apt-get update'), 'RUN apt-get update'),
    (d.RUN('echo 1', 'echo 2'), 'RUN echo 1 && \\\n    echo 2'),
    (d.RUN('apt-get update', shell=False), 'RUN ["apt-get", "update"]'),
    (d.RUN(['apt-get', 'update']), 'RUN apt-get update'),
    (d.RUN('echo 1', mount=d.SecretMount()), 'RUN --mount=type=secret echo 1'),
    (d.RUN('echo 1', network='none'), 'RUN --network=none echo 1'),
    (d.RUN('echo 1', security='insecure'), 'RUN --security=insecure echo 1'),

    # ---
    (d.CMD('echo 1', shell=True), 'CMD echo 1'),
    (d.CMD(['echo', '1'], shell=True), 'CMD echo 1'),
    (d.CMD('echo 1'), 'CMD ["echo", "1"]'),
    (d.CMD(['echo', '1']), 'CMD ["echo", "1"]'),

    # ---
    (d.EXPOSE(80), 'EXPOSE 80/tcp'),
    (d.EXPOSE(8125, 'udp'), 'EXPOSE 8125/udp'),

    # ---
    (d.ENV('user', 'root'), 'ENV user=root'),
    (d.ENV('user', 'gram orsinium'), 'ENV user="gram orsinium"'),

    # ---
    (
        d.DOWNLOAD(
            'https://a.b/c.gz', '/',
            checksum=d.Checksum('244'),
        ), 'ADD --checksum=sha256:244 https://a.b/c.gz /'),
    (
        d.DOWNLOAD('https://a.b/c.gz', '/', checksum=d.Checksum('244', algorithm='sha512')),
        'ADD --checksum=sha512:244 https://a.b/c.gz /',
    ),
    (
        d.CLONE('https://github.com/moby/buildkit.git#v0.10.1', '/buildkit', keep_git_dir=True),
        'ADD --keep-git-dir=true https://github.com/moby/buildkit.git#v0.10.1 /buildkit',
    ),
    (d.EXTRACT('a/b/c.gz', '/'), 'ADD a/b/c.gz /'),
    (d.EXTRACT('a/b/c.gz', '/', chown='gram'), 'ADD --chown=gram a/b/c.gz /'),

    # ---
    (d.COPY('hom*', '/mydir/'), 'COPY hom* /mydir/'),
    (d.COPY('test.txt', 'relativeDir/'), 'COPY test.txt relativeDir/'),
    (d.COPY('test.txt', PosixPath('hello', 'world')), 'COPY test.txt hello/world'),
    (d.COPY('win path', '/'), 'COPY ["win path", "/"]'),
    (d.COPY('src', 'win path'), 'COPY ["src", "win path"]'),
    (d.COPY(['src1', 'src2'], '/'), 'COPY src1 src2 /'),
    (d.COPY('files', '/somedir/', chown='gram'), 'COPY --chown=gram files /somedir/'),
    (d.COPY('files', '/somedir/', chown='gram:docker'), 'COPY --chown=gram:docker files /somedir/'),
    (d.COPY('files', '/somedir/', chown=1), 'COPY --chown=1 files /somedir/'),
    (d.COPY('files/', '/', link=True), 'COPY --link files/ /'),
    (d.COPY('files/', '/', from_stage=d.BaseImage('build')), 'COPY --from=build files/ /'),

    # ---
    (d.ENTRYPOINT('nginx'), 'ENTRYPOINT ["nginx"]'),
    (d.ENTRYPOINT('cowsay hello'), 'ENTRYPOINT ["cowsay", "hello"]'),
    (d.ENTRYPOINT(['nginx']), 'ENTRYPOINT ["nginx"]'),
    (d.ENTRYPOINT(['cowsay', 'hello']), 'ENTRYPOINT ["cowsay", "hello"]'),
    (d.ENTRYPOINT(['top', '-b']), 'ENTRYPOINT ["top", "-b"]'),
    (d.ENTRYPOINT(['nginx'], shell=True), 'ENTRYPOINT nginx'),
    (d.ENTRYPOINT(['cowsay', 'hello'], shell=True), 'ENTRYPOINT cowsay hello'),
    (d.ENTRYPOINT(['top', '-b'], shell=True), 'ENTRYPOINT top -b'),

    # ---
    (d.VOLUME('/myvol'), 'VOLUME /myvol'),
    (d.VOLUME('/var/log/'), 'VOLUME /var/log/'),
    (d.VOLUME('/var/log', '/var/db'), 'VOLUME /var/log /var/db'),
    (d.VOLUME('win path'), 'VOLUME ["win path"]'),

    # ---
    (d.USER('gram'), 'USER gram'),
    (d.USER('gram', 'docker'), 'USER gram:docker'),
    (d.USER(1, 100), 'USER 1:100'),

    # ---
    (d.WORKDIR('/home/'), 'WORKDIR /home/'),
    (d.WORKDIR('home/'), 'WORKDIR home/'),
    (d.WORKDIR('win path'), 'WORKDIR win path'),  # is that right?

    # ---
    (d.ONBUILD(d.COPY('.', '/app/src')), 'ONBUILD COPY . /app/src'),
    (d.ONBUILD(d.RUN('echo hello')), 'ONBUILD RUN echo hello'),

    # ---
    (d.STOPSIGNAL('SIGKILL'), 'STOPSIGNAL SIGKILL'),
    (d.STOPSIGNAL(SIGKILL), 'STOPSIGNAL 9'),
    (d.STOPSIGNAL(9), 'STOPSIGNAL 9'),

    # ---
    (d.HEALTHCHECK(None), 'HEALTHCHECK NONE'),
    (d.HEALTHCHECK('curl -f localhost'), 'HEALTHCHECK CMD ["curl", "-f", "localhost"]'),
    (d.HEALTHCHECK('curl -f localhost', shell=True), 'HEALTHCHECK CMD curl -f localhost'),
    (d.HEALTHCHECK('echo 1', interval='5m'), 'HEALTHCHECK --interval=5m CMD ["echo", "1"]'),
    (d.HEALTHCHECK('echo 1', interval=timedelta(seconds=34)), 'HEALTHCHECK --interval=34s CMD ["echo", "1"]'),
    (d.HEALTHCHECK('echo 1', timeout='5m'), 'HEALTHCHECK --timeout=5m CMD ["echo", "1"]'),
    (d.HEALTHCHECK('echo 1', timeout=timedelta(seconds=34)), 'HEALTHCHECK --timeout=34s CMD ["echo", "1"]'),
    (d.HEALTHCHECK('echo 1', start_period='5m'), 'HEALTHCHECK --start-period=5m CMD ["echo", "1"]'),
    (d.HEALTHCHECK('echo 1', retries=9), 'HEALTHCHECK --retries=9 CMD ["echo", "1"]'),

    # ---
    (d.SHELL(['bash', '-c']), 'SHELL ["bash", "-c"]'),
    (d.SHELL('bash -c'), 'SHELL ["bash", "-c"]'),
])
def test_as_str(given: d.Step, expected: str) -> None:
    assert given.as_str() == expected
    assert str(given) == expected
