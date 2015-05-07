# -*- coding: utf-8 -*-
"""Durant. Simple git deployment tool.

Usage examples:
- Deploy project to stage    
  $ durant deploy [-n] <stage>

Please run 'durant --help' to see full help"""

__title__ = 'durant'
__version__ = '0.2.3'
__author__ = 'Marius Bărbulescu'
__license__ = 'Apache 2.0'
__copyright__ = 'Copyright 2015 Marius Bărbulescu'

import commands

from .config import Config
from .deployer import Deployer
