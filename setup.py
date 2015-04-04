# -*- coding: utf-8 -*-

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

def readme():
    with open('README.rst') as f:
        return f.read()

setup(
    name='durant',
    version='0.1',
    description='Simple git deployment tool',
    long_description=readme(),
    url='',
    author='Marius Bărbulescu',
    author_email='',
    platforms='linux',
    license='Apache 2.0',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4'
    ],
    packages=['durant'],
    entry_points = {
        'console_scripts': [
            'durant = durant.main:main'
        ],
    },
    zip_safe=False
)
