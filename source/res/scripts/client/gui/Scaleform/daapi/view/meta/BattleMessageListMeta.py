# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/BattleMessageListMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIModule import BaseDAAPIModule

class BattleMessageListMeta(BaseDAAPIModule):
    """
    DO NOT MODIFY!
    Generated with yaml.
    __author__ = 'yaml_processor'
    @extends BaseDAAPIModule
    null
    """

    def onRefreshComplete(self):
        """
        :return :
        """
        self._printOverrideError('onRefreshComplete')

    def as_setupListS(self, data):
        """
        :param data:
        :return :
        """
        return self.flashObject.as_setupList(data) if self._isDAAPIInited() else None

    def as_clearS(self):
        """
        :return :
        """
        return self.flashObject.as_clear() if self._isDAAPIInited() else None

    def as_refreshS(self):
        """
        :return :
        """
        return self.flashObject.as_refresh() if self._isDAAPIInited() else None

    def as_showYellowMessageS(self, key, text):
        """
        :param key:
        :param text:
        :return :
        """
        return self.flashObject.as_showYellowMessage(key, text) if self._isDAAPIInited() else None

    def as_showRedMessageS(self, key, text):
        """
        :param key:
        :param text:
        :return :
        """
        return self.flashObject.as_showRedMessage(key, text) if self._isDAAPIInited() else None

    def as_showPurpleMessageS(self, key, text):
        """
        :param key:
        :param text:
        :return :
        """
        return self.flashObject.as_showPurpleMessage(key, text) if self._isDAAPIInited() else None

    def as_showGreenMessageS(self, key, text):
        """
        :param key:
        :param text:
        :return :
        """
        return self.flashObject.as_showGreenMessage(key, text) if self._isDAAPIInited() else None

    def as_showGoldMessageS(self, key, text):
        """
        :param key:
        :param text:
        :return :
        """
        return self.flashObject.as_showGoldMessage(key, text) if self._isDAAPIInited() else None

    def as_showSelfMessageS(self, key, text):
        """
        :param key:
        :param text:
        :return :
        """
        return self.flashObject.as_showSelfMessage(key, text) if self._isDAAPIInited() else None
