# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/NotificationsListMeta.py
from gui.Scaleform.daapi.view.lobby.popover.SmartPopOverView import SmartPopOverView

class NotificationsListMeta(SmartPopOverView):

    def onClickAction(self, typeID, entityID, action):
        self._printOverrideError('onClickAction')

    def getMessageActualTime(self, msTime):
        self._printOverrideError('getMessageActualTime')

    def as_setInitDataS(self, value):
        if self._isDAAPIInited():
            return self.flashObject.as_setInitData(value)

    def as_setMessagesListS(self, value):
        if self._isDAAPIInited():
            return self.flashObject.as_setMessagesList(value)

    def as_appendMessageS(self, messageData):
        if self._isDAAPIInited():
            return self.flashObject.as_appendMessage(messageData)

    def as_updateMessageS(self, messageData):
        if self._isDAAPIInited():
            return self.flashObject.as_updateMessage(messageData)
