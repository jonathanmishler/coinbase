from setuptools import setup, find_packages
import pathlib

here = pathlib.Path(__file__).parent.resolve()

long_description = (here / 'README.md').read_text(encoding='utf-8')

setup(
    name='coinbase',  # Required
    version='0.0.1',  # Required
    description='A Python Coinbase API library',  # Optional
    long_description=long_description,  # Optional
    long_description_content_type='text/markdown',  # Optional
    # url='https://github.com/pypa/sampleproject',  # Optional
    author='Jonathan Mishler',  # Optional
    author_email='jonathan.mishler@gmail.com',  # Optional
    # keywords='sample, setuptools, development',  # Optional
    package_dir={'': 'src'},  # Optional
    packages=find_packages(where='src'),  # Required
    python_requires='>=3.9, <4',

    # This field lists other packages that your project depends on to run.
    # Any package you put here will be installed by pip when your project is
    # installed, so they must be valid existing projects.
    #
    # For an analysis of "install_requires" vs pip's requirements files see:
    # https://packaging.python.org/discussions/install-requires-vs-requirements/
    install_requires=['httpx', 'websockets'],  # Optional

    # List additional groups of dependencies here (e.g. development
    # dependencies). Users will be able to install these using the "extras"
    # syntax, for example:
    #
    #   $ pip install sampleproject[dev]
    #
    # Similar to `install_requires` above, these must be valid existing
    # projects.
    extras_require={  # Optional
        'dev': ['check-manifest'],
        'test': ['coverage'],
    }
)
