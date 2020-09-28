# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/WTEventPlayerLivesMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class WTEventPlayerLivesMeta(BaseDAAPIComponent):

    def as_setCountLivesS(self, count, dead):
        return self.flashObject.as_setCountLives(count, dead) if self._isDAAPIInited() else None
