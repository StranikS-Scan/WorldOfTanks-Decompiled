# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/IngameMenuMeta.py
from gui.Scaleform.framework.entities.abstract.AbstractWindowView import AbstractWindowView

class IngameMenuMeta(AbstractWindowView):

    def quitBattleClick(self):
        self._printOverrideError('quitBattleClick')

    def settingsClick(self):
        self._printOverrideError('settingsClick')

    def helpClick(self):
        self._printOverrideError('helpClick')

    def cancelClick(self):
        self._printOverrideError('cancelClick')

    def onCounterNeedUpdate(self):
        self._printOverrideError('onCounterNeedUpdate')

    def bootcampClick(self):
        self._printOverrideError('bootcampClick')

    def as_setServerSettingS(self, serverName, tooltipFullData, serverState):
        return self.flashObject.as_setServerSetting(serverName, tooltipFullData, serverState) if self._isDAAPIInited() else None

    def as_setServerStatsS(self, stats, tooltipType):
        return self.flashObject.as_setServerStats(stats, tooltipType) if self._isDAAPIInited() else None

    def as_setCounterS(self, counters):
        return self.flashObject.as_setCounter(counters) if self._isDAAPIInited() else None

    def as_removeCounterS(self, counters):
        return self.flashObject.as_removeCounter(counters) if self._isDAAPIInited() else None

    def as_setMenuButtonsLabelsS(self, helpLabel, settingsLabel, cancelLabel, quitLabel, bootcampLabel, bootcampIcon):
        return self.flashObject.as_setMenuButtonsLabels(helpLabel, settingsLabel, cancelLabel, quitLabel, bootcampLabel, bootcampIcon) if self._isDAAPIInited() else None

    def as_showQuitButtonS(self, value):
        return self.flashObject.as_showQuitButton(value) if self._isDAAPIInited() else None

    def as_showBootcampButtonS(self, value):
        return self.flashObject.as_showBootcampButton(value) if self._isDAAPIInited() else None
