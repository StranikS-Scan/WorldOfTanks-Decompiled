# Embedded file name: scripts/client/messenger/gui/Scaleform/view/LobbyChannelWindow.py
from gui.Scaleform.managers.windows_stored_data import DATA_TYPE, TARGET_ID
from gui.Scaleform.managers.windows_stored_data import stored_window
from messenger.gui.Scaleform.data.MembersDataProvider import MembersDataProvider
from messenger.gui.Scaleform.meta.LobbyChannelWindowMeta import LobbyChannelWindowMeta

@stored_window(DATA_TYPE.CHANNEL_WINDOW, TARGET_ID.CHANNEL_CAROUSEL)

class LobbyChannelWindow(LobbyChannelWindowMeta):

    def _populate(self):
        super(LobbyChannelWindow, self)._populate()
        channel = self._controller.getChannel()
        if channel.haveMembers():
            membersDP = MembersDataProvider()
            membersDP.setFlashObject(self.as_getMembersDPS())
            self._controller.setMembersDP(membersDP)
        else:
            self.as_hideMembersListS()

    def _dispose(self):
        if self._controller is not None:
            self._controller.removeMembersDP()
        super(LobbyChannelWindow, self)._dispose()
        return
