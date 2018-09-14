# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/messenger/gui/Scaleform/meta/ChannelsManagementWindowMeta.py
from gui.Scaleform.framework.entities.abstract.AbstractWindowView import AbstractWindowView

class ChannelsManagementWindowMeta(AbstractWindowView):
    """
    DO NOT MODIFY!
    Generated with yaml.
    __author__ = 'yaml_processor'
    @extends AbstractWindowView
    null
    """

    def getSearchLimitLabel(self):
        """
        :return String:
        """
        self._printOverrideError('getSearchLimitLabel')

    def searchToken(self, token):
        """
        :param token:
        :return :
        """
        self._printOverrideError('searchToken')

    def joinToChannel(self, index):
        """
        :param index:
        :return :
        """
        self._printOverrideError('joinToChannel')

    def createChannel(self, name, usePassword, password, retype):
        """
        :param name:
        :param usePassword:
        :param password:
        :param retype:
        :return :
        """
        self._printOverrideError('createChannel')

    def as_freezSearchButtonS(self, isEnable):
        """
        :param isEnable:
        :return :
        """
        return self.flashObject.as_freezSearchButton(isEnable) if self._isDAAPIInited() else None

    def as_getDataProviderS(self):
        """
        :return Object:
        """
        return self.flashObject.as_getDataProvider() if self._isDAAPIInited() else None
