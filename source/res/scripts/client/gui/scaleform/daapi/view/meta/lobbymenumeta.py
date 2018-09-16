# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/LobbyMenuMeta.py
"""
This file was generated using the wgpygen.
Please, don't edit this file manually.
"""
from gui.Scaleform.framework.entities.View import View

class LobbyMenuMeta(View):

    def settingsClick(self):
        self._printOverrideError('settingsClick')

    def cancelClick(self):
        self._printOverrideError('cancelClick')

    def refuseTraining(self):
        self._printOverrideError('refuseTraining')

    def logoffClick(self):
        self._printOverrideError('logoffClick')

    def quitClick(self):
        self._printOverrideError('quitClick')

    def versionInfoClick(self):
        self._printOverrideError('versionInfoClick')

    def onCounterNeedUpdate(self):
        self._printOverrideError('onCounterNeedUpdate')

    def bootcampClick(self):
        self._printOverrideError('bootcampClick')

    def onEscapePress(self):
        self._printOverrideError('onEscapePress')

    def as_setVersionMessageS(self, data):
        """
        :param data: Represented by VersionMessageVO (AS)
        """
        return self.flashObject.as_setVersionMessage(data) if self._isDAAPIInited() else None

    def as_setCounterS(self, counters):
        """
        :param counters: Represented by Vector.<CountersVo> (AS)
        """
        return self.flashObject.as_setCounter(counters) if self._isDAAPIInited() else None

    def as_removeCounterS(self, counters):
        """
        :param counters: Represented by Vector.<String> (AS)
        """
        return self.flashObject.as_removeCounter(counters) if self._isDAAPIInited() else None

    def as_setBootcampButtonLabelS(self, label, icon):
        return self.flashObject.as_setBootcampButtonLabel(label, icon) if self._isDAAPIInited() else None

    def as_showBootcampButtonS(self, value):
        return self.flashObject.as_showBootcampButton(value) if self._isDAAPIInited() else None

    def as_setMenuStateS(self, state):
        return self.flashObject.as_setMenuState(state) if self._isDAAPIInited() else None
