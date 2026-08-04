from setuptools import setup
# read the contents of your README file
from pathlib import Path
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(name='ldsc',
      version='3.0.2',
      description='LD Score Regression (LDSC)',
      long_description=long_description,
      long_description_content_type='text/markdown',
      url='http://github.com/bulik/ldsc',
      author='Brendan Bulik-Sullivan and Hilary Finucane',
      author_email='',
      license='GPLv3',
      packages=['ldscore'],
      scripts=['ldsc.py', 'munge_sumstats.py', 'make_annot.py'],
      py_modules=['ldscore.ldsc_utils'],  # Add this line to include ldsc_utils.py
      install_requires = [
            # bitarray removed -- ldscore.py no longer depends on it (see numpy-based rewrite)
            # pybedtools removed -- make_annot.py no longer depends on it (see numpy-based rewrite)
            # nose removed -- test-only, not needed to run ldsc, and not in the fixed environment
            'numpy==1.26.4',
            'pandas==2.2.3',
            'scipy==1.7.3',
            'pysam==0.19.1',            # TODO: confirm actually needed -- not in the fixed environment
            'python-dateutil==2.9.0.post0',
            'pytz==2025.2',
            'six==1.17.0'
      ]
)
