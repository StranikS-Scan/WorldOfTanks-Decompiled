# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/NotificationsListMeta.py
from gui.Scaleform.daapi.view.lobby.popover.SmartPopOverView import SmartPopOverView

class NotificationsListMeta(SmartPopOverView):

    def onClickAction(self, typeID, entityID, action):
        self._printOverrideError('onClickAction')

    def getMessageActualTime(self, msTime):
        self._printOverrideError('getMessageActualTime')

    def onGroupChange(self, groupIdx):
        self._printOverrideError('onGroupChange')

    def as_setInitDataS(self, value):
        """
        :param value: Represented by NotificationViewInitVO (AS)
        """
        return self.flashObject.as_setInitData(value) if self._isDAAPIInited() else None

    def as_setMessagesListS(self, value):
        """
        :param value: Represented by NotificationMessagesListVO (AS)
        """
        return self.flashObject.as_setMessagesList(value) if self._isDAAPIInited() else None

    def as_appendMessageS(self, messageData):
        """
        :param messageData: Represented by NotificationInfoVO (AS)
        """
        return self.flashObject.as_appendMessage(messageData) if self._isDAAPIInited() else None

    def as_updateMessageS(self, messageData):
        """
        :param messageData: Represented by NotificationInfoVO (AS)
        """
        return self.flashObject.as_updateMessage(messageData) if self._isDAAPIInited() else None

    def as_updateCountersS(self, counts):
        """
        :param counts: Represented by Array (AS)
        """
        return self.flashObject.as_updateCounters(counts) if self._isDAAPIInited() else None
