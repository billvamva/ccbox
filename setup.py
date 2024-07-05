from setuptools import setup, find_packages

setup(
    name='ccbox',
    version='1.0',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'ccbox=ccbox.cli:main',
        ],
    },
    install_requires=[
        'requests',
    ],
)