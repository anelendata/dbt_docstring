#!/usr/bin/env python
from setuptools import setup

VERSION = "0.1.3"

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="dbt_docstring",
    version=VERSION,
    description="Docstring dbt test & documentation in SQL file",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Daigo Tanaka, Anelen Co., LLC",
    url="https://github.com/anelendata/dbt_docstring",

    classifiers=[
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: Apache Software License",

        "Operating System :: MacOS :: MacOS X",
        "Operating System :: POSIX :: Linux",

        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],

    install_requires=[
        "setuptools>=40.3.0",
        "pyyaml>=5.1",
    ],
    entry_points="""
    [console_scripts]
    dbtdocstr=dbt_docstring:main
    """,
    packages=["dbt_docstring"],
    package_data={
        # Use MANIFEST.ini
    },
    include_package_data=True
)
