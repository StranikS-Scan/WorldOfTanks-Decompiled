# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/PveEventPointCurrentMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class PveEventPointCurrentMeta(BaseDAAPIComponent):

    def as_updateCountS(self, count):
        return self.flashObject.as_updateCount(count) if self._isDAAPIInited() else None

    def as_showEventPointCurrentS(self, show):
        return self.flashObject.as_showEventPointCurrent(show) if self._isDAAPIInited() else None

    def as_setNicknameS(self, name):
        return self.flashObject.as_setNickname(name) if self._isDAAPIInited() else None
