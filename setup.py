import setuptools
from distutils.util import convert_path

with open("README.md", "r") as fh:
    long_description = fh.read()

metadata = {}
ver_path = convert_path('rplanpy/metadata.py')
with open(ver_path) as ver_file:
    exec(ver_file.read(), metadata)


setuptools.setup(
    name="rplanpy",
    version=metadata['__version__'],
    author=metadata['__author__'],
    author_email=metadata['__email__'],
    description="Set of python utilities to work with the RPLAN dataset from \"[Data-driven Interior Plan Generation for Residential Buildings](https://doi.org/10.1145/3355089.3356556)\" paper.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/unaisaralegui/rplanpy",
    packages=setuptools.find_packages(),
    install_requires=[
        'imageio',
        'numpy',
        'matplotlib',
        'networkx',
        'skimage',
        'scipy'
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ]
)
