"""Package installation logic"""

from pathlib import Path

from setuptools import setup, find_packages

VERSION = 'developemnt'


def get_requirements():
    """Return a list of package dependencies"""

    requirements_path = Path(__file__).parent / 'requirements.txt'
    with requirements_path.open() as req_file:
        return req_file.read().splitlines()


setup(
    name='crc-wrappers',
    description='Command-line applications for interacting with HPC clusters at the Pitt CRC.',
    version=VERSION,
    packages=find_packages(),
    python_requires='>=3.7',
    entry_points="""
        [console_scripts]
        usage-monitor=node_nanny.cli:CLIParser.execute
    """,
    install_requires=get_requirements(),
    author="Pitt Center for Research Computing",
    keyword='Pitt, CRC, HPC, wrappers',
    long_description_content_type='text/markdown',
    classifiers=[
        'Programming Language :: Python :: 3',
    ]
)
