# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/framework/entities/abstract/ColorSchemeManagerMeta.py
"""
This file was generated using the wgpygen.
Please, don't edit this file manually.
"""
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class ColorSchemeManagerMeta(BaseDAAPIComponent):

    def getColorScheme(self, schemeName):
        self._printOverrideError('getColorScheme')

    def getIsColorBlind(self):
        self._printOverrideError('getIsColorBlind')

    def as_updateS(self):
        return self.flashObject.as_update() if self._isDAAPIInited() else None
