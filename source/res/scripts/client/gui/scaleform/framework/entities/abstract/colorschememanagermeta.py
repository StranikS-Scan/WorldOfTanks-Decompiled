# Embedded file name: scripts/client/gui/Scaleform/framework/entities/abstract/ColorSchemeManagerMeta.py
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule

class ColorSchemeManagerMeta(DAAPIModule):

    def getColorScheme(self, schemeName):
        self._printOverrideError('getColorScheme')

    def as_updateS(self):
        if self._isDAAPIInited():
            return self.flashObject.as_update()
