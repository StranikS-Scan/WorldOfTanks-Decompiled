# Embedded file name: scripts/client/gui/Scaleform/framework/entities/abstract/TextManagerMeta.py
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule

class TextManagerMeta(DAAPIModule):

    def getTextStyle(self, style):
        self._printOverrideError('getTextStyle')
