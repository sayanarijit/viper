# -*- coding: utf-8 -*-
from os import path
from setuptools import find_packages
from setuptools import setup
from viper import __author__
from viper import __description__
from viper import __email__
from viper import __homepage__
from viper import __license__
from viper import __version__

import typing as t

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, "README.rst"), encoding="utf-8") as f:
    long_description = f.read()

install_requires: t.List[str] = []
autocomplete_requires = ["argcomplete==1.10.3"]
testing_requires = autocomplete_requires + [
    "pytest>=4.4.1",
    "pytest-cov>=2.7.1",
    "black>=19.3b0",
    "isort>=4.3.21",
    "mypy>=0.710",
    "lxml>=4.3.4",
    "pre-commit>=1.20.0",
    "pre-commit-hooks>=2.4.0",
]
dev_requires = testing_requires + ["tox>=3.12.1", "twine>=3.1.1", "sphinx>=2.2.1"]

setup(
    name="viper-infra-commander",
    version=__version__,
    description=__description__,
    long_description=long_description,
    url=__homepage__,
    author=__author__,
    author_email=__email__,
    license=__license__,
    py_modules=["viper"],
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "Intended Audience :: System Administrators ",
        "Intended Audience :: Other Audience",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
    platforms=["Any"],
    zip_safe=False,
    keywords="viper infrastructure commander",
    packages=find_packages(exclude=["contrib", "docs", "tests", "examples"]),
    install_requires=install_requires,
    extras_require={
        "autocomplete": autocomplete_requires,
        "testing": testing_requires,
        "dev": dev_requires,
    },
    entry_points={"console_scripts": ["viper = viper.main:main"]},
)
