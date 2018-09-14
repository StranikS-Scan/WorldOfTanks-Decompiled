# Embedded file name: scripts/client/gui/Scaleform/framework/entities/abstract/ColorSchemeManagerMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIModule import BaseDAAPIModule

class ColorSchemeManagerMeta(BaseDAAPIModule):

    def getColorScheme(self, schemeName):
        self._printOverrideError('getColorScheme')

    def as_updateS(self):
        if self._isDAAPIInited():
            return self.flashObject.as_update()
