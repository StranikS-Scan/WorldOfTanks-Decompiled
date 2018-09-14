# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/NotificationPopUpViewerMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class NotificationPopUpViewerMeta(BaseDAAPIComponent):
    """
    DO NOT MODIFY!
    Generated with yaml.
    __author__ = 'yaml_processor'
    @extends BaseDAAPIComponent
    null
    """

    def setListClear(self):
        """
        :return :
        """
        self._printOverrideError('setListClear')

    def onMessageHided(self, byTimeout, wasNotified):
        """
        :param byTimeout:
        :param wasNotified:
        :return :
        """
        self._printOverrideError('onMessageHided')

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

    def as_hasPopUpIndexS(self, typeID, entityID):
        """
        :param typeID:
        :param entityID:
        :return Boolean:
        """
        return self.flashObject.as_hasPopUpIndex(typeID, entityID) if self._isDAAPIInited() else None

    def as_appendMessageS(self, data):
        """
        :param data:
        :return :
        """
        return self.flashObject.as_appendMessage(data) if self._isDAAPIInited() else None

    def as_updateMessageS(self, data):
        """
        :param data:
        :return :
        """
        return self.flashObject.as_updateMessage(data) if self._isDAAPIInited() else None

    def as_removeMessageS(self, typeID, entityID):
        """
        :param typeID:
        :param entityID:
        :return :
        """
        return self.flashObject.as_removeMessage(typeID, entityID) if self._isDAAPIInited() else None

    def as_removeAllMessagesS(self):
        """
        :return :
        """
        return self.flashObject.as_removeAllMessages() if self._isDAAPIInited() else None

    def as_layoutInfoS(self, data):
        """
        :param data:
        :return :
        """
        return self.flashObject.as_layoutInfo(data) if self._isDAAPIInited() else None

    def as_initInfoS(self, maxMessagessCount, padding):
        """
        :param maxMessagessCount:
        :param padding:
        :return :
        """
        return self.flashObject.as_initInfo(maxMessagessCount, padding) if self._isDAAPIInited() else None
