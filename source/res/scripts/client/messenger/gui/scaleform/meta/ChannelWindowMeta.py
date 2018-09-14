# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/messenger/gui/Scaleform/meta/ChannelWindowMeta.py
from gui.Scaleform.framework.entities.abstract.AbstractWindowView import AbstractWindowView

class ChannelWindowMeta(AbstractWindowView):
    """
    DO NOT MODIFY!
    Generated with yaml.
    __author__ = 'yaml_processor'
    @extends AbstractWindowView
    null
    """

    def showFAQWindow(self):
        """
        :return :
        """
        self._printOverrideError('showFAQWindow')

    def getClientID(self):
        """
        :return Number:
        """
        self._printOverrideError('getClientID')

    def as_setTitleS(self, title):
        """
        :param title:
        :return :
        """
        return self.flashObject.as_setTitle(title) if self._isDAAPIInited() else None

    def as_setCloseEnabledS(self, enabled):
        """
        :param enabled:
        :return :
        """
        return self.flashObject.as_setCloseEnabled(enabled) if self._isDAAPIInited() else None
