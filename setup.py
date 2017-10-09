#!/usr/bin/env python

import os
import sys
import SLRdata 

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


setup(
    name='SLRdata',
    version = SLRdata.__version__,
    description='SLR file format parsers',
    long_description=open('README.rst').read(),
    author='Olli Wilkman',
    author_email='olli.wilkman@iki.fi',
    packages=['SLRdata'],
    license=open('LICENSE').read(),
    zip_safe=False
)
