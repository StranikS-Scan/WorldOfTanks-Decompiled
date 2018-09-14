# Embedded file name: scripts/common/Lib/plat-mac/Carbon/__init__.py
import warnings
warnings.filterwarnings('ignore', '', FutureWarning, '.*Controls')
warnings.filterwarnings('ignore', '', FutureWarning, '.*MacTextEditor')
from warnings import warnpy3k
warnpy3k('In 3.x, the Carbon package is removed.', stacklevel=2)
