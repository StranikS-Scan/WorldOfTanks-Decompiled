# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/shared/helper.py
from gui.Scaleform.genConsts.CROSSHAIR_CASSETTE_TYPES import CROSSHAIR_CASSETTE_TYPES

def getClipType(gunSettings):
    clipType = CROSSHAIR_CASSETTE_TYPES.NO_CASSETTE
    if gunSettings.isCassetteClip():
        if gunSettings.hasAutoReload():
            clipType = CROSSHAIR_CASSETTE_TYPES.AUTOLOADER
            if gunSettings.isMultiGun():
                clipType = CROSSHAIR_CASSETTE_TYPES.MULTIPLE_BARREL_AUTOLOADER
        else:
            clipType = CROSSHAIR_CASSETTE_TYPES.CASSETTE
            if gunSettings.isMultiGun():
                clipType = CROSSHAIR_CASSETTE_TYPES.MULTIPLE_BARREL_CASSETTE
    return clipType
