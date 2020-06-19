# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/Event10YCPrimeTimeMeta.py
from gui.Scaleform.daapi.view.lobby.prime_time_view_base import PrimeTimeViewBase

class Event10YCPrimeTimeMeta(PrimeTimeViewBase):

    def as_setTitleS(self, value):
        return self.flashObject.as_setTitle(value) if self._isDAAPIInited() else None

    def as_setBgS(self, value):
        return self.flashObject.as_setBg(value) if self._isDAAPIInited() else None
