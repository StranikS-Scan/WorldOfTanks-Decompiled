# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/SessionStatsPopoverMeta.py
from gui.Scaleform.daapi.view.lobby.popover.SmartPopOverView import SmartPopOverView

class SessionStatsPopoverMeta(SmartPopOverView):

    def onClickMoreBtn(self):
        self._printOverrideError('onClickMoreBtn')

    def onClickResetBtn(self):
        self._printOverrideError('onClickResetBtn')

    def onExpanded(self, value):
        self._printOverrideError('onExpanded')

    def onTabSelected(self, alias):
        self._printOverrideError('onTabSelected')

    def onCounterUpdated(self):
        self._printOverrideError('onCounterUpdated')

    def as_setDataS(self, data):
        return self.flashObject.as_setData(data) if self._isDAAPIInited() else None

    def as_setButtonsStateS(self, states):
        return self.flashObject.as_setButtonsState(states) if self._isDAAPIInited() else None
