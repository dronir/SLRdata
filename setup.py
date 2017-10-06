#!/usr/bin/env python

import os
import sys
import my_package 

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

requires = ["requests >= 1.0.0"]

setup(
    name='SLRdata',
    version = my_package.__version__,
    description='SLR file format parsers',
    long_description=open('README.rst').read(),
    author='Olli Wilkman',
    author_email='olli.wilkman@iki.fi',
    packages=['SLRdata'],
    install_requires=requires,
    license=open('LICENSE').read(),
    zip_safe=False,
    entry_points = {
        # the script will be called runit
        'console_scripts': ['runit = my_package.myfile:main',]
        },
)
