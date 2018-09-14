# Embedded file name: scripts/client/gui/Scaleform/framework/entities/abstract/TextManagerMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIModule import BaseDAAPIModule

class TextManagerMeta(BaseDAAPIModule):

    def getTextStyle(self, style):
        self._printOverrideError('getTextStyle')
