# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/LobbyMenuMeta.py
from gui.Scaleform.framework.entities.abstract.AbstractWindowView import AbstractWindowView

class LobbyMenuMeta(AbstractWindowView):
    """
    DO NOT MODIFY!
    Generated with yaml.
    __author__ = 'yaml_processor'
    @extends AbstractWindowView
    null
    """

    def settingsClick(self):
        """
        :return :
        """
        self._printOverrideError('settingsClick')

    def cancelClick(self):
        """
        :return :
        """
        self._printOverrideError('cancelClick')

    def refuseTraining(self):
        """
        :return :
        """
        self._printOverrideError('refuseTraining')

    def logoffClick(self):
        """
        :return :
        """
        self._printOverrideError('logoffClick')

    def quitClick(self):
        """
        :return :
        """
        self._printOverrideError('quitClick')

    def versionInfoClick(self):
        """
        :return :
        """
        self._printOverrideError('versionInfoClick')

    def as_setVersionMessageS(self, data):
        """
        :param data:
        :return :
        """
        return self.flashObject.as_setVersionMessage(data) if self._isDAAPIInited() else None
