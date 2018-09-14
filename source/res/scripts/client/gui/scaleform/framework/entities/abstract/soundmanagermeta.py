# Embedded file name: scripts/client/gui/Scaleform/framework/entities/abstract/SoundManagerMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIModule import BaseDAAPIModule

class SoundManagerMeta(BaseDAAPIModule):

    def soundEventHandler(self, group, state, type, id):
        self._printOverrideError('soundEventHandler')
