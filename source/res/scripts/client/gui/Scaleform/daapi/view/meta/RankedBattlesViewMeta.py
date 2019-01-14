# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/RankedBattlesViewMeta.py
from gui.Scaleform.daapi.view.meta.WrapperViewMeta import WrapperViewMeta

class RankedBattlesViewMeta(WrapperViewMeta):

    def onCloseBtnClick(self):
        self._printOverrideError('onCloseBtnClick')

    def onEscapePress(self):
        self._printOverrideError('onEscapePress')

    def onAwardClick(self, awardID):
        self._printOverrideError('onAwardClick')

    def as_setDataS(self, data):
        return self.flashObject.as_setData(data) if self._isDAAPIInited() else None

    def as_setLeagueDataS(self, awards):
        return self.flashObject.as_setLeagueData(awards) if self._isDAAPIInited() else None

    def as_setRankedDataS(self, calendarStatus, progressBlock):
        return self.flashObject.as_setRankedData(calendarStatus, progressBlock) if self._isDAAPIInited() else None
