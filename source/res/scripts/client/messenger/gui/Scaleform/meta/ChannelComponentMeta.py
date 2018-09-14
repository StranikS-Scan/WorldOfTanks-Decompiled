# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/messenger/gui/Scaleform/meta/ChannelComponentMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class ChannelComponentMeta(BaseDAAPIComponent):
    """
    DO NOT MODIFY!
    Generated with yaml.
    __author__ = 'yaml_processor'
    @extends BaseDAAPIComponent
    null
    """

    def isJoined(self):
        """
        :return Boolean:
        """
        self._printOverrideError('isJoined')

    def sendMessage(self, message):
        """
        :param message:
        :return Boolean:
        """
        self._printOverrideError('sendMessage')

    def getHistory(self):
        """
        :return String:
        """
        self._printOverrideError('getHistory')

    def getMessageMaxLength(self):
        """
        :return int:
        """
        self._printOverrideError('getMessageMaxLength')

    def onLinkClick(self, linkCode):
        """
        :param linkCode:
        :return :
        """
        self._printOverrideError('onLinkClick')

    def getLastUnsentMessage(self):
        """
        :return String:
        """
        self._printOverrideError('getLastUnsentMessage')

    def setLastUnsentMessage(self, message):
        """
        :param message:
        :return :
        """
        self._printOverrideError('setLastUnsentMessage')

    def as_setJoinedS(self, flag):
        """
        :param flag:
        :return :
        """
        return self.flashObject.as_setJoined(flag) if self._isDAAPIInited() else None

    def as_addMessageS(self, message):
        """
        :param message:
        :return :
        """
        return self.flashObject.as_addMessage(message) if self._isDAAPIInited() else None
