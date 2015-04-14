# -*- coding: utf-8 -*-
"""Durant. Simple git deployment tool.

Usage:
durant [OPTIONS] deploy <stage>

Options:
-n, --dry-run   Perform a trial run, without actually deploying
-v, --version   Show version number
-h, --help      Show this screen"""

__title__ = 'durant'
__version__ = '0.1.0'
__author__ = 'Marius Bărbulescu'
__license__ = 'Apache 2.0'
__copyright__ = 'Copyright 2015 Marius Bărbulescu'

from deployer import Deployer
