import pathlib
import re

import setuptools

ROOT = pathlib.Path(__file__).parent

README = (ROOT / 'README.md').read_text()
INIT = (ROOT / 'editabletuple.py').read_text()
match = re.search(r"__version__\s*=\s*'(?P<version>.*?)'", INIT)
VERSION = match.group('version')

setuptools.setup(
    name='editabletuple',
    version=VERSION,
    author='Mark Summerfield',
    author_email='mark@qtrac.eu',
    description='Provides the editabletuple function for creating classes \
with a fixed sequence of fields, similar to a namedtuple, except editable',
    long_description=README,
    long_description_content_type='text/markdown',
    url='https://github.com/mark-summerfield/editabletuple',
    license='GPLv3',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Topic :: Software Development :: Libraries'],
    package_dir={'': '.'},
    py_modules=['editabletuple'],
    python_requires='>=3.8')
