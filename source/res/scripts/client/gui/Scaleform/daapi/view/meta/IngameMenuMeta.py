# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/IngameMenuMeta.py
from gui.Scaleform.framework.entities.abstract.AbstractWindowView import AbstractWindowView

class IngameMenuMeta(AbstractWindowView):
    """
    DO NOT MODIFY!
    Generated with yaml.
    __author__ = 'yaml_processor'
    @extends AbstractWindowView
    """

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

    def as_setServerSettingS(self, serverName, tooltipFullData, serverState):
        return self.flashObject.as_setServerSetting(serverName, tooltipFullData, serverState) if self._isDAAPIInited() else None

    def as_setServerStatsS(self, stats, tooltipType):
        return self.flashObject.as_setServerStats(stats, tooltipType) if self._isDAAPIInited() else None

    def as_setSettingsBtnCounterS(self, value):
        return self.flashObject.as_setSettingsBtnCounter(value) if self._isDAAPIInited() else None
