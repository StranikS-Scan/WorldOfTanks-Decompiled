# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/LobbyMenuMeta.py
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

    def postClick(self):
        self._printOverrideError('postClick')

    def onCounterNeedUpdate(self):
        self._printOverrideError('onCounterNeedUpdate')

    def onEscapePress(self):
        self._printOverrideError('onEscapePress')

    def manualClick(self):
        self._printOverrideError('manualClick')

    def showLegal(self):
        self._printOverrideError('showLegal')

    def as_setVersionMessageS(self, message):
        return self.flashObject.as_setVersionMessage(message) if self._isDAAPIInited() else None

    def as_setCounterS(self, counters):
        return self.flashObject.as_setCounter(counters) if self._isDAAPIInited() else None

    def as_removeCounterS(self, counters):
        return self.flashObject.as_removeCounter(counters) if self._isDAAPIInited() else None

    def as_setPostButtonIconsS(self, iconClose, iconOpen):
        return self.flashObject.as_setPostButtonIcons(iconClose, iconOpen) if self._isDAAPIInited() else None

    def as_setPostButtonVisibleS(self, isVisible):
        return self.flashObject.as_setPostButtonVisible(isVisible) if self._isDAAPIInited() else None

    def as_showManualButtonS(self, value):
        return self.flashObject.as_showManualButton(value) if self._isDAAPIInited() else None

    def as_setManualButtonIconS(self, icon):
        return self.flashObject.as_setManualButtonIcon(icon) if self._isDAAPIInited() else None

    def as_setMenuStateS(self, state):
        return self.flashObject.as_setMenuState(state) if self._isDAAPIInited() else None

    def as_setCopyrightS(self, copyrightVal, legalInfo):
        return self.flashObject.as_setCopyright(copyrightVal, legalInfo) if self._isDAAPIInited() else None

    def as_showVersionS(self, value):
        return self.flashObject.as_showVersion(value) if self._isDAAPIInited() else None
