"""
The examples shows how to build and serve static website using hugo static site generator.

Hugo:
    https://gohugo.io/
Theme:
    https://themes.gohugo.io/themes/beautifulhugo/
Sample project:
    https://github.com/gohugoio/hugoBasicExample

Usage:

    python3 examples/hugo.py | docker buildx build --tag=hugo-demo:latest -
    docker run -p 8080:80 hugo-demo:latest
    Open http://localhost:8080/ in the browser.

"""

import docked as d


HUGO_VERSION = '0.104.3'
HUGO_DEB_URL = f'https://github.com/gohugoio/hugo/releases/download/v{HUGO_VERSION}/hugo_{HUGO_VERSION}_linux-amd64.deb'  # noqa
WEBSITE_REPO = 'https://github.com/gohugoio/hugoBasicExample.git'
THEME_REPO = 'https://github.com/halogenica/beautifulhugo.git'

generate_stage = d.Stage(
    base=d.BaseImage('debian', tag='bookworm-slim'),
    name='generate',
    build=[
        d.CLONE(WEBSITE_REPO, '/source'),
        d.CLONE(THEME_REPO, '/source/themes/theme'),
        d.DOWNLOAD(HUGO_DEB_URL, '/root/hugo.deb'),
        d.WORKDIR('/source'),
        d.RUN(
            'dpkg -i /root/hugo.deb',
            'hugo -t theme --baseURL /',
        ),
    ]
)

serve_stage = d.Stage(
    base=d.BaseImage('nginx', tag='stable-alpine'),
    name='serve',
    build=[
        d.COPY(
            '/source/public',
            '/usr/share/nginx/html',
            from_stage=generate_stage,
        ),
    ],
)

image = d.Image(
    generate_stage, serve_stage,
    syntax_channel='docker/dockerfile-upstream',
    syntax_version='master-labs',
)

if __name__ == '__main__':
    image.lint()
    print(image)
