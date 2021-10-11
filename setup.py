#!/usr/bin/env python

from distutils.core import setup

__version__ = "1.0.0"

setup(
    name="yaml-merger",
    version=__version__,
    install_requires=[
        "PyYAML==5.4.1",
        "click==8.0.1",
        "deepmerge==0.3.0",
    ],
    keywords=["yaml", "merger", "merging"],
    description="""
          Utility function that merges YAML files into a single one applying 
          the strategic merge patch strategy used in kustomize, for example.
        """,
    author="JohnW",
    author_email="joao.wojcikiewicz@protonmail.com",
    license="MIT",
    packages=["yamlmerger"],
    entry_points={
        "console_scripts": [
            "yaml-merge = yamlmerger.cli:cli",
        ],
    },
)
