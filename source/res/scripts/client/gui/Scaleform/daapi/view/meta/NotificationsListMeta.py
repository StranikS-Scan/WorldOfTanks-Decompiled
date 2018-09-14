# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/NotificationsListMeta.py
from gui.Scaleform.daapi.view.lobby.popover.SmartPopOverView import SmartPopOverView

class NotificationsListMeta(SmartPopOverView):
    """
    DO NOT MODIFY!
    Generated with yaml.
    __author__ = 'yaml_processor'
    @extends SmartPopOverView
    null
    """

    def onClickAction(self, typeID, entityID, action):
        """
        :param typeID:
        :param entityID:
        :param action:
        :return :
        """
        self._printOverrideError('onClickAction')

    def getMessageActualTime(self, msTime):
        """
        :param msTime:
        :return String:
        """
        self._printOverrideError('getMessageActualTime')

    def as_setInitDataS(self, value):
        """
        :param value:
        :return :
        """
        return self.flashObject.as_setInitData(value) if self._isDAAPIInited() else None

    def as_setMessagesListS(self, value):
        """
        :param value:
        :return :
        """
        return self.flashObject.as_setMessagesList(value) if self._isDAAPIInited() else None

    def as_appendMessageS(self, messageData):
        """
        :param messageData:
        :return :
        """
        return self.flashObject.as_appendMessage(messageData) if self._isDAAPIInited() else None

    def as_updateMessageS(self, messageData):
        """
        :param messageData:
        :return :
        """
        return self.flashObject.as_updateMessage(messageData) if self._isDAAPIInited() else None
