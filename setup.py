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
    name='my_package',
    version = my_package.__version__,
    description='Python MODULE DESCRIPTION',
    long_description=open('README.rst').read(),
    author='Your Name Sir',
    author_email='name@exampele.com',
    url='http://proj.example.com/',
    packages=['my_package'],
    install_requires=requires,
    license=open('LICENSE').read(),
    zip_safe=False,
    entry_points = {
        # the script will be called runit
        'console_scripts': ['runit = my_package.myfile:main',]
        },
)
