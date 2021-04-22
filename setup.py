from setuptools import find_packages

import setuptools
import os
from io import open as io_open

src_dir = os.path.abspath(os.path.dirname(__file__))

with open("README.md", "r") as fh:
    long_description = fh.read()

requirements = os.path.join(src_dir, 'requirements.txt')
with io_open(requirements, mode='r') as fd:
    install_requires = [i.strip().split('#', 1)[0].strip()
                        for i in fd.read().strip().split('\n')]

setuptools.setup(
    name='jill',
    version='0.9.1',
    author="Johnny Chen",
    author_email="johnnychen94@hotmail.com",
    description="JILL -- Julia Installer for Linux (MacOS, Windows and FreeBSD) -- Light",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/johnnychen94/jill.py",
    packages=['jill'] + ['jill.' + i for i in find_packages('jill')],
    provides=['jill'],
    install_requires=install_requires,
    python_requires=">=3.6",
    entry_points={'console_scripts': ['jill=jill.__main__:main'], },
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
