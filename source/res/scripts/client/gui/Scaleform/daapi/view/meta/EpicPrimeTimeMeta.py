# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/EpicPrimeTimeMeta.py
from gui.Scaleform.daapi.view.lobby.prime_time_view_base import PrimeTimeViewBase

class EpicPrimeTimeMeta(PrimeTimeViewBase):

    def as_setDataS(self, data):
        return self.flashObject.as_setData(data) if self._isDAAPIInited() else None
