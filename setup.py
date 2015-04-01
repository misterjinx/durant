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
    author='',
    author_email='',
    license='Apache 2.0',
    packages=['durant'],
    entry_points = {
        'console_scripts': ['durant=durant.main:main'],
    },
    zip_safe=False
)
