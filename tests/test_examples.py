from importlib import import_module
from pathlib import Path

import pytest


TESTS_DIR = Path(__file__).parent


@pytest.mark.parametrize('name', [
    'cowsay',
    'hello_world',
    'httpie',
    'hugo',
    'ipython',
])
def test_example(name: str) -> None:
    module = import_module(f'examples.{name}')
    try:
        actual = str(module.image)
    except AttributeError:
        actual = str(module.get_image())
    expected_path = TESTS_DIR / 'expected' / f'{name}.txt'
    expected = expected_path.read_text()
    assert actual + '\n' == expected
