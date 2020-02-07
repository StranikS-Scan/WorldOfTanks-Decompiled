# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/SessionStatsSettingsMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class SessionStatsSettingsMeta(BaseDAAPIComponent):

    def onClickApplyBtn(self):
        self._printOverrideError('onClickApplyBtn')

    def onClickBackBtn(self):
        self._printOverrideError('onClickBackBtn')

    def onClickResetBtn(self):
        self._printOverrideError('onClickResetBtn')

    def onSettingsInputChanged(self, identifier, value):
        self._printOverrideError('onSettingsInputChanged')

    def as_setDataS(self, data):
        return self.flashObject.as_setData(data) if self._isDAAPIInited() else None

    def as_setControlsStateS(self, data):
        return self.flashObject.as_setControlsState(data) if self._isDAAPIInited() else None

    def as_setBattleSettingsStatusS(self, value, showWarning):
        return self.flashObject.as_setBattleSettingsStatus(value, showWarning) if self._isDAAPIInited() else None
