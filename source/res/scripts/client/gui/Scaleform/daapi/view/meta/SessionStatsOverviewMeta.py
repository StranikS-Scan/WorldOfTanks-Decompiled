# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/SessionStatsOverviewMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class SessionStatsOverviewMeta(BaseDAAPIComponent):

    def onClickMoreBtn(self):
        self._printOverrideError('onClickMoreBtn')

    def onClickResetBtn(self):
        self._printOverrideError('onClickResetBtn')

    def onClickSettingsBtn(self):
        self._printOverrideError('onClickSettingsBtn')

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

    def as_setHeaderTooltipS(self, value):
        return self.flashObject.as_setHeaderTooltip(value) if self._isDAAPIInited() else None
