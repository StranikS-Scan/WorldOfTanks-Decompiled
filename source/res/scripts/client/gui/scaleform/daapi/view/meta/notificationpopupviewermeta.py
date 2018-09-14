# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/NotificationPopUpViewerMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class NotificationPopUpViewerMeta(BaseDAAPIComponent):

    def setListClear(self):
        self._printOverrideError('setListClear')

    def onMessageHided(self, byTimeout, wasNotified):
        self._printOverrideError('onMessageHided')

    def onClickAction(self, typeID, entityID, action):
        self._printOverrideError('onClickAction')

    def getMessageActualTime(self, msTime):
        self._printOverrideError('getMessageActualTime')

    def as_getPopUpIndexS(self, typeID, entityID):
        if self._isDAAPIInited():
            return self.flashObject.as_getPopUpIndex(typeID, entityID)

    def as_appendMessageS(self, messageData):
        if self._isDAAPIInited():
            return self.flashObject.as_appendMessage(messageData)

    def as_updateMessageS(self, messageData):
        if self._isDAAPIInited():
            return self.flashObject.as_updateMessage(messageData)

    def as_removeMessageS(self, typeID, entityID):
        if self._isDAAPIInited():
            return self.flashObject.as_removeMessage(typeID, entityID)

    def as_removeAllMessagesS(self):
        if self._isDAAPIInited():
            return self.flashObject.as_removeAllMessages()

    def as_layoutInfoS(self, data):
        if self._isDAAPIInited():
            return self.flashObject.as_layoutInfo(data)

    def as_initInfoS(self, maxMessagessCount, padding):
        if self._isDAAPIInited():
            return self.flashObject.as_initInfo(maxMessagessCount, padding)
