# Python bytecode 2.6 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/sre.py
# Compiled at: 2010-05-25 20:46:16
"""This file is only retained for backwards compatibility.
It will be removed in the future.  sre was moved to re in version 2.5.
"""
import warnings
warnings.warn('The sre module is deprecated, please import re.', DeprecationWarning, 2)
from re import *
from re import __all__
from re import _compile
