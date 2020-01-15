from setuptools import find_packages

import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='jill',
    version='0.0.1',
    author="Johnny Chen",
    author_email="johnnychen94@hotmail.com",
    description="Julia Installer 4 Linux(and MacOS) - Light",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/johnnychen94/jill.py",
    packages=['jill'] + ['jill.' + i for i in find_packages('jill')],
    provides=['jill'],
    python_requires=">=3.5",
    entry_points={'console_scripts': ['jill=jill.__main__:main'], },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
