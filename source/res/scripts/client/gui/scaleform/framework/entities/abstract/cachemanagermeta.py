# Embedded file name: scripts/client/gui/Scaleform/framework/entities/abstract/CacheManagerMeta.py
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule

class CacheManagerMeta(DAAPIModule):

    def getSettings(self):
        self._printOverrideError('getSettings')
