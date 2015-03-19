import os, sys
from setuptools import setup
from setuptools.command.test import test as TestCommand

class PyTest(TestCommand):
    # Taken from py.test setuptools integration page
    # http://pytest.org/latest/goodpractices.html

    user_options = [('pytest-args=', 'a', 'Arguments to pass to py.test')]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.pytest_args = []

    def finialize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import pytest
        errno = pytest.main(self.pytest_args)
        sys.exit(errno)

tests_require = ['py', 'pytest'] 

if __name__ == "__main__":

    setup(
        name="pynads",
        version="0.0.1",
        author="Alec Nikolas Reiter",
        description="Bad monads for Python",
        license="MIT",
        packages=["pynads"],
        url="https://github.com/justanr/pynads",
        keywords="monad functor applicative",
        test_suite='tests',
        tests_require=tests_require,
        cmdclass = {'test' : PyTest}
        )
