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
    url="https://github.com/hoijui/rdfx",
    license=LICENSE,
    packages=PACKAGES,
    platforms=["any"],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
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
    python_requires='>=3.7',
    # NOTE While this is the same info as in 'requirements.txt',
    #      we should still maintain them separately,
    #      see <https://stackoverflow.com/questions/14399534/reference-requirements-txt-for-the-install-requires-kwarg-in-setuptools-setup-py>.
    #      While we should maintain the minimum requried versions here,
    #      we might want to promote more recent versions in 'requirements.txt'.
    install_requires=[
        'boto3>=1.20,<2',
        'botocore>=1.24,<2',
        'httpx>=0.23,<1',
        'rdflib>=6.0.2,<8'
        ],
    tests_require=[
        'pytest>=6.2.5,<8',
        'moto>=2.2.9,<3',
        'pytest-asyncio>=0.16,<1',
        'twine>=4.0.1,<5'
        ],
    test_suite="tests",
)
