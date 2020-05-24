# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/offers/__init__.py
import typing
from constants import GF_RES_PROTOCOL
from gui.shared.utils.functions import getAbsoluteUrl

def getGfImagePath(imgPath):
    if imgPath is None:
        return
    else:
        newPath = getAbsoluteUrl(imgPath)
        if not newPath.startswith(GF_RES_PROTOCOL.IMG):
            newPath = ''.join([GF_RES_PROTOCOL.IMG, newPath])
        return newPath
