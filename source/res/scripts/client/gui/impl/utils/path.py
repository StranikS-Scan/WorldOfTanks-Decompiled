# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/utils/path.py
from __future__ import absolute_import
import logging
import typing
from past.builtins import basestring
from constants import GF_RES_PROTOCOL
from gui.shared.utils.functions import getAbsoluteUrl
if typing.TYPE_CHECKING:
    from typing import Optional
_logger = logging.getLogger(__name__)

def normalizeGfImagePath(imgPath):
    if not isinstance(imgPath, basestring) or not imgPath:
        _logger.warning('Wrong image path: %s.', imgPath)
        return None
    else:
        newPath = getAbsoluteUrl(str(imgPath))
        newPath = newPath.replace('\\', '/')
        if not newPath.startswith(GF_RES_PROTOCOL.IMG):
            newPath = ''.join((GF_RES_PROTOCOL.IMG, newPath))
        return newPath
