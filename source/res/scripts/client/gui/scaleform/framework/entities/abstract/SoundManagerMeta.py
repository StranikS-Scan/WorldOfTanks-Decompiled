# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/framework/entities/abstract/SoundManagerMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class SoundManagerMeta(BaseDAAPIComponent):

    def soundEventHandler(self, group, state, type, id):
        self._printOverrideError('soundEventHandler')
