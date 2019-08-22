# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/BattleRoyaleMainPageMeta.py
from gui.Scaleform.framework.entities.View import View

class BattleRoyaleMainPageMeta(View):

    def onClose(self):
        self._printOverrideError('onClose')

    def onPageChanged(self, viewId):
        self._printOverrideError('onPageChanged')

    def as_setDataS(self, data):
        return self.flashObject.as_setData(data) if self._isDAAPIInited() else None

    def as_setHeaderDataS(self, data):
        return self.flashObject.as_setHeaderData(data) if self._isDAAPIInited() else None

    def as_setCountersS(self, countersData):
        return self.flashObject.as_setCounters(countersData) if self._isDAAPIInited() else None
