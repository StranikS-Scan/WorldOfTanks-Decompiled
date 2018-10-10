# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/NotificationPopUpViewerMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class NotificationPopUpViewerMeta(BaseDAAPIComponent):

    def setListClear(self):
        self._printOverrideError('setListClear')

    def onMessageHidden(self, byTimeout, wasNotified, typeID, entityID):
        self._printOverrideError('onMessageHidden')

    def onClickAction(self, typeID, entityID, action):
        self._printOverrideError('onClickAction')

    def getMessageActualTime(self, msTime):
        self._printOverrideError('getMessageActualTime')

    def as_hasPopUpIndexS(self, typeID, entityID):
        return self.flashObject.as_hasPopUpIndex(typeID, entityID) if self._isDAAPIInited() else None

    def as_appendMessageS(self, data):
        return self.flashObject.as_appendMessage(data) if self._isDAAPIInited() else None

    def as_updateMessageS(self, data):
        return self.flashObject.as_updateMessage(data) if self._isDAAPIInited() else None

    def as_removeMessageS(self, typeID, entityID):
        return self.flashObject.as_removeMessage(typeID, entityID) if self._isDAAPIInited() else None

    def as_removeAllMessagesS(self):
        return self.flashObject.as_removeAllMessages() if self._isDAAPIInited() else None

    def as_initInfoS(self, maxMessagessCount, padding):
        return self.flashObject.as_initInfo(maxMessagessCount, padding) if self._isDAAPIInited() else None
