# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/NotificationsListMeta.py
from gui.Scaleform.daapi.view.lobby.popover.SmartPopOverView import SmartPopOverView

class NotificationsListMeta(SmartPopOverView):
    """
    DO NOT MODIFY!
    Generated with yaml.
    __author__ = 'yaml_processor'
    @extends SmartPopOverView
    """

    def onClickAction(self, typeID, entityID, action):
        self._printOverrideError('onClickAction')

    def getMessageActualTime(self, msTime):
        self._printOverrideError('getMessageActualTime')

    def onGroupChange(self, groupIdx):
        self._printOverrideError('onGroupChange')

    def as_setInitDataS(self, data):
        """
        :param data: Represented by NotificationViewInitVO (AS)
        """
        return self.flashObject.as_setInitData(data) if self._isDAAPIInited() else None

    def as_setMessagesListS(self, data):
        """
        :param data: Represented by NotificationMessagesListVO (AS)
        """
        return self.flashObject.as_setMessagesList(data) if self._isDAAPIInited() else None

    def as_appendMessageS(self, data):
        """
        :param data: Represented by NotificationInfoVO (AS)
        """
        return self.flashObject.as_appendMessage(data) if self._isDAAPIInited() else None

    def as_updateMessageS(self, data):
        """
        :param data: Represented by NotificationInfoVO (AS)
        """
        return self.flashObject.as_updateMessage(data) if self._isDAAPIInited() else None

    def as_updateCountersS(self, counts):
        return self.flashObject.as_updateCounters(counts) if self._isDAAPIInited() else None
