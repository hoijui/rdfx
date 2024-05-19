from setuptools import setup
from os import path
import re


def find_version(filename):
    """ Find the embedded version string in the package source. """
    _version_re = re.compile(r"__VERSION__ *= *'(.*)'", re.IGNORECASE)
    for line in open(filename):
        version_match = _version_re.match(line)
        if version_match:
            return version_match.group(1)


NAME = 'rdfx'
HERE = path.abspath(path.dirname(__file__))
VERSION = find_version(path.join(HERE, ('%s/__init__.py' % NAME)))
PACKAGES = [NAME]
LICENSE = "BSD"

setup(
    name=NAME,
    version=VERSION,
    description="Tools for converting, merging, persisting and reading RDF data in different formats.",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="Dr. Nicholas Car",
    author_email="nicholas.car@surroundaustralia.com",
    maintainer="David Habgood",
    maintainer_email="david.habgood@surroundaustralia.com",
    url="https://github.com/surroundaustralia/rdfx",
    license=LICENSE,
    packages=PACKAGES,
    platforms=["any"],
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "License :: OSI Approved :: %s License" % LICENSE,
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Operating System :: OS Independent",
        "Natural Language :: English",
    ],
    tests_require=["pytest"],
    test_suite="tests",
)
