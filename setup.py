import os
import sys
from setuptools import find_packages
from setuptools import setup
from setuptools.command.test import test as TestCommand


def get_install_requires():
    with open("requirements.txt", "r") as requirements_file:
        res = requirements_file.readlines()
        return [req.split(" ", maxsplit=1)[0] for req in res if req]


def get_version():
    with open(os.path.join("thoth", "glyph", "__init__.py")) as f:
        content = f.readlines()

    for line in content:
        if line.startswith("__version__ ="):
            return line.split(" = ")[1][1:-2]

    raise ValueError("No version identifier found")


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


class Test(TestCommand):
    """Introduce test command to run testsuite using pytest."""

    _IMPLICIT_PYTEST_ARGS = [
        "--timeout=60",
        "--mypy",
        "--capture=no",
        "--verbose",
        "-l",
        "-s",
        "-vv",
        "tests/",
    ]

    user_options = [("pytest-args=", "a", "Arguments to pass into py.test")]

    def initialize_options(self):
        super().initialize_options()
        self.pytest_args = None

    def finalize_options(self):
        super().finalize_options()
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import pytest

        passed_args = list(self._IMPLICIT_PYTEST_ARGS)

        if self.pytest_args:
            self.pytest_args = [arg for arg in self.pytest_args.split() if arg]
            passed_args.extend(self.pytest_args)

        sys.exit(pytest.main(passed_args))


VERSION = get_version()
setup(
    name="thoth-glyph",
    version=VERSION,
    description="Package and package stack adviser for the Thoth project",
    long_description=read("README.rst"),
    author="Tushar Sharma",
    author_email="tussharm@redhat.com",
    license="GPLv3+",
    packages=[
        "thoth.glyph",
    ],
    url="https://github.com/thoth-station/glyph",
    download_url="https://pypi.org/project/glyph",
    package_data={"thoth.glyph": ["py.typed"]},
    entry_points={"console_scripts": ["thoth-glyph=thoth.glyph.cli:cli"]},
    install_requires=get_install_requires(),
    cmdclass={"test": Test},
    long_description_content_type="text/x-rst",
)
