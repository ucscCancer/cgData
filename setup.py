
import sys
import os

from distutils.core import setup
from distutils.core import Command
from distutils.command.install import install
from distutils.command.build_py import build_py
from distutils.command.build_ext import build_ext
from distutils.extension import Extension


PACKAGES = [
	'cgData'
]

EXTENSIONS = [
    Extension('cgData.segToMatrix',
              ['cgData/segToMatrix.cc']
              )
]

__version__="undefined"

setup(
    name='cgData',
    version=__version__,
    author='Kyle Ellrott',
    author_email='kellrott@soe.ucsc.edu',
    url='http://genome-cancer.ucsc.edu/',
    description='Tools for preparing Cancer Genome Browser Data.',
    download_url='http://genome-cancer.ucsc.edu/',
    #cmdclass={
    #    "install" : install_biopython,
    #    "build_py" : build_py_biopython,
    #    "build_ext" : build_ext_biopython,
    #    "test" : test_biopython,
    #    },
    packages=PACKAGES,
    ext_modules=EXTENSIONS
)

