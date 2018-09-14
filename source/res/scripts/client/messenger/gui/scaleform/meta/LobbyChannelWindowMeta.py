# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/messenger/gui/Scaleform/meta/LobbyChannelWindowMeta.py
from messenger.gui.Scaleform.view.lobby.SimpleChannelWindow import SimpleChannelWindow

class LobbyChannelWindowMeta(SimpleChannelWindow):
    """
    DO NOT MODIFY!
    Generated with yaml.
    __author__ = 'yaml_processor'
    @extends SimpleChannelWindow
    null
    """

    def as_getMembersDPS(self):
        """
        :return Object:
        """
        return self.flashObject.as_getMembersDP() if self._isDAAPIInited() else None

    def as_hideMembersListS(self):
        """
        :return :
        """
        return self.flashObject.as_hideMembersList() if self._isDAAPIInited() else None
