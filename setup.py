#!/usr/bin/env python
from setuptools import setup, find_packages


def get_long_description():
    return """
    Usage:   crypto.py
"""


setup(
    name='cryptocompare-cli',
    version="0.0.1",
    author='TonyChG',
    author_email='antoine.chiny@inria.fr',
    long_description=get_long_description(),
    url='https://github.com/tonychg/cryptocompare-cli.git',
    packages=find_packages(),
    scripts=[
        "crypto.py"
    ],
    install_requires=[
        "cryptocompare"
    ],
    include_package_data=True,
    python_requires='>=3.6',
    classifiers=[
      "Development Status :: 5 - In developpment",
      "Topic :: Software Development :: Libraries :: Python Modules",
      "License :: Apache License Version 2.0",
      "Programming Language :: Python :: 3",
    ]
)

