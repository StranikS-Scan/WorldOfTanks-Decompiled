# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/messenger/gui/Scaleform/meta/ChannelComponentMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class ChannelComponentMeta(BaseDAAPIComponent):

    def isJoined(self):
        self._printOverrideError('isJoined')

    def sendMessage(self, message):
        self._printOverrideError('sendMessage')

    def getHistory(self):
        self._printOverrideError('getHistory')

    def getMessageMaxLength(self):
        self._printOverrideError('getMessageMaxLength')

    def onLinkClick(self, linkCode):
        self._printOverrideError('onLinkClick')

    def as_notifyInfoChangedS(self):
        return self.flashObject.as_notifyInfoChanged() if self._isDAAPIInited() else None

    def as_setJoinedS(self, flag):
        return self.flashObject.as_setJoined(flag) if self._isDAAPIInited() else None

    def as_addMessageS(self, message):
        return self.flashObject.as_addMessage(message) if self._isDAAPIInited() else None

    def as_getLastUnsentMessageS(self):
        return self.flashObject.as_getLastUnsentMessage() if self._isDAAPIInited() else None

    def as_setLastUnsentMessageS(self, message):
        return self.flashObject.as_setLastUnsentMessage(message) if self._isDAAPIInited() else None
