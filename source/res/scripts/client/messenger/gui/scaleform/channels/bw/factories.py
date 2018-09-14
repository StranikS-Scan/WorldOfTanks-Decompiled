# Embedded file name: scripts/client/messenger/gui/Scaleform/channels/bw/factories.py
from messenger.gui.Scaleform.channels.bw import lobby_controllers
from messenger.gui.interfaces import IControllerFactory
from messenger.m_constants import LAZY_CHANNEL
from messenger.proto.bw import find_criteria
from messenger.storage import storage_getter

class LobbyControllersFactory(IControllerFactory):

    def __init__(self):
        super(LobbyControllersFactory, self).__init__()

    @storage_getter('channels')
    def channelsStorage(self):
        return None

    def init(self):
        controllers = []
        channels = self.channelsStorage.getChannelsByCriteria(find_criteria.BWLobbyChannelFindCriteria())
        for channel in channels:
            controller = self.factory(channel)
            if controller is not None:
                controllers.append(controller)

        return controllers

    def factory(self, channel):
        controller = None
        if channel.getName() in LAZY_CHANNEL.ALL:
            if channel.getName() == LAZY_CHANNEL.SPECIAL_BATTLES:
                controller = lobby_controllers.BSLazyChannelController(channel)
            else:
                controller = lobby_controllers.LazyChannelController(channel)
        elif not channel.isBattle():
            controller = lobby_controllers.LobbyChannelController(channel)
        return controller
