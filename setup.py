#! /usr/local/bin/python3
import os
from setuptools import setup
from simplewave import __version__


def _read_description():
    description_file_path = os.path.join(os.path.dirname(__file__), 'document/description.md')
    with open(description_file_path, 'rt', encoding='utf-8') as description_file:
        description_text = description_file.read()
    return description_text


setup(
    name='simplewave',
    version=__version__,
    author='lotcarnage',
    author_email='lotcarnage@gmail.com',
    url='https://github.com/lotcarnage/simplewave',
    packages=['simplewave'],
    license='MIT',
    install_requires=['numpy'],
    python_requires='>=3.8',
    description='Simple Wave file read and write module',
    long_description_content_type='text/markdown',
    long_description=_read_description(),
    entry_points={
        "console_scripts": [
            "fetchwave=simplewave:cli_entry",
        ]
    },
)
