# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/RankedBattlesIntroMeta.py
from gui.Scaleform.framework.entities.View import View

class RankedBattlesIntroMeta(View):

    def onClose(self):
        self._printOverrideError('onClose')

    def onAcceptClick(self):
        self._printOverrideError('onAcceptClick')

    def onDetailedClick(self):
        self._printOverrideError('onDetailedClick')

    def onPlayVideoClick(self):
        self._printOverrideError('onPlayVideoClick')

    def as_setDataS(self, data):
        return self.flashObject.as_setData(data) if self._isDAAPIInited() else None

    def as_setAlertMessageBlockDataS(self, data):
        return self.flashObject.as_setAlertMessageBlockData(data) if self._isDAAPIInited() else None

    def as_setBeforeSeasonBlockDataS(self, data):
        return self.flashObject.as_setBeforeSeasonBlockData(data) if self._isDAAPIInited() else None
