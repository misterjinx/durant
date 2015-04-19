# -*- coding: utf-8 -*-

import re

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


def readme():
    with open('README.rst') as f:
        return f.read()


def history():
    with open('HISTORY.rst') as f:
        return f.read()


def version():
    version = None
    with open('durant/__init__.py') as f:
        version = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]',
                            f.read(), re.MULTILINE).group(1)
    if version:
        return version

    raise RuntimeError('Package version not defined')


setup(
    name='durant',
    version=version(),
    description='Simple git deployment tool',
    long_description=readme() + history(),
    url='https://github.com/misterjinx/durant',
    author='Marius Bărbulescu',
    author_email='marius@freshcolors.ro',
    platforms='linux',
    license='Apache 2.0',
    classifiers=[
        'Development Status :: 4 - Beta', 'Environment :: Console',
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
    install_requires=[
        'argparse',
    ],
    entry_points={
        'console_scripts': [
            'durant = durant.main:main'
        ], 
    },
    zip_safe=False
)
