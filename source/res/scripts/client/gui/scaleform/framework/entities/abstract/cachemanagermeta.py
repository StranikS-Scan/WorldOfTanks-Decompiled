# Embedded file name: scripts/client/gui/Scaleform/framework/entities/abstract/CacheManagerMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIModule import BaseDAAPIModule

class CacheManagerMeta(BaseDAAPIModule):

    def getSettings(self):
        self._printOverrideError('getSettings')
