
import sys
import os

from distutils.core import setup
from distutils.core import Command
from distutils.command.install import install
from distutils.command.build_py import build_py
from distutils.command.build_ext import build_ext
from distutils.extension import Extension


PACKAGES = [
	'CGData'
]

EXTENSIONS = [
    Extension('CGData.CsegToMatrix',
              ['CGData/CsegToMatrix.cc']
              )
]

__version__="undefined"

class test_cgData(Command):
    user_options = []

    def initialize_options(self):
        pass
        
    def finalize_options(self):
        pass


    def run(self):
        os.chdir("tests")
        sys.path.insert(0, '')
        import runTests 
        runTests.main([])



setup(
    name='CGData',
    version=__version__,
    author='Kyle Ellrott',
    author_email='kellrott@soe.ucsc.edu',
    url='http://genome-cancer.ucsc.edu/',
    description='Tools for preparing Cancer Genome Browser Data.',
    download_url='http://genome-cancer.ucsc.edu/',
    cmdclass={
            "test" : test_cgData
    },
    packages=PACKAGES,
    ext_modules=EXTENSIONS
)

