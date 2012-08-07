
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

SCRIPTS = [
    'scripts/bed2probeMap.py',
    'scripts/bedMap.py',
    'scripts/compileCancerData.py',
    'scripts/compileCancerORM.py',
    'scripts/compileScan.py',
    'scripts/dataNetwork.py',
    'scripts/editMetainfo.py',
    'scripts/extractClinical.py',
    'scripts/extractClinicalFeatures.py',
    'scripts/extractGenomic.py',
    'scripts/extractProbes.py',
    'scripts/extractSamples.py',
    'scripts/getMatrixList.py',
    'scripts/getRefGene_hg18.sh',
    'scripts/setupRepo.py',
    'scripts/tcga2cgdata.py',
    'scripts/tcgaAliquotFetch.py',
    'scripts/tcgaAliquotSampleMap.sh',
]

__version__="undefined"

class test_cgData(Command):
    tests = None
    user_options = [('tests=', 't', 'comma separated list of tests to run')]

    def initialize_options(self):
        pass
        
    def finalize_options(self):
        pass


    def run(self):
        os.chdir("tests")
        sys.path.insert(0, '')
        import runTests
        runTests.main([] if self.tests == None else self.tests.split(','))



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
    ext_modules=EXTENSIONS,
    scripts=SCRIPTS
)

