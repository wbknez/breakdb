#!/usr/bin/env python
# -*- encoding: utf-8 -*-
import io
import re
from glob import glob
from os.path import basename
from os.path import dirname
from os.path import join
from os.path import splitext

from setuptools import find_packages
from setuptools import setup


def read(*names, **kwargs):
    return io.open(
        join(dirname(__file__), *names),
        encoding=kwargs.get('encoding', 'utf8')
    ).read()


setup(
    name='breakdb',
    version='0.1.0',
    license='Apache 2.0 License',
    description='Utility for collating fracture X-ray images into a database.',
    long_description='%s\n%s' % (
        re.compile('^.. start-badges.*^.. end-badges', re.M | re.S).sub('', read('Readme.md')),
        re.sub(':[a-z]+:`~?(.*?)`', r'``\1``', read('Changelog.md'))
    ),
    author='Will Knez',
    author_email='wibknez@salud.unm.edu',
    url='https://github.com/wbknez/breakdb',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    py_modules=[splitext(basename(path))[0] for path in glob('src/*.py')],
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Operating System :: Unix',
        'Operating System :: POSIX',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Database',
        'Topic :: Scientific/Engineering :: Medical Science Apps',
        'Topic :: Utilities'
    ],
    keywords=[
        'radiography', 'databases', 'dicom'
    ],
    install_requires=[
        'pandas',
        'pydicom',
        'pytest'
    ],
    extras_require={
    },
    entry_points={
        'console_scripts': [
        ]
    },
)
