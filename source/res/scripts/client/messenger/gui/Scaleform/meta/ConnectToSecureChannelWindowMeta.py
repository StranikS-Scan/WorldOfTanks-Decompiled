# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/messenger/gui/Scaleform/meta/ConnectToSecureChannelWindowMeta.py
from gui.Scaleform.framework.entities.abstract.AbstractWindowView import AbstractWindowView

class ConnectToSecureChannelWindowMeta(AbstractWindowView):
    """
    DO NOT MODIFY!
    Generated with yaml.
    __author__ = 'yaml_processor'
    @extends AbstractWindowView
    """

    def sendPassword(self, value):
        self._printOverrideError('sendPassword')

    def cancelPassword(self):
        self._printOverrideError('cancelPassword')

    def as_infoMessageS(self, value):
        return self.flashObject.as_infoMessage(value) if self._isDAAPIInited() else None
