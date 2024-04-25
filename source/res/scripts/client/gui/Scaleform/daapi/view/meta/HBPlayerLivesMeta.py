# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/HBPlayerLivesMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class HBPlayerLivesMeta(BaseDAAPIComponent):

    def as_setCountLivesS(self, count, dead, locked):
        return self.flashObject.as_setCountLives(count, dead, locked) if self._isDAAPIInited() else None
