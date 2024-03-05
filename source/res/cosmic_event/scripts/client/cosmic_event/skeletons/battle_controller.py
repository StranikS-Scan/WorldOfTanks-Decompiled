# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: cosmic_event/scripts/client/cosmic_event/skeletons/battle_controller.py
from typing import TYPE_CHECKING
from skeletons.gui.game_control import IGameController, ISeasonProvider
if TYPE_CHECKING:
    from Event import Event
    from cosmic_event.settings import CosmicEventConfig
    from cosmic_event.gui.impl.gen.view_models.views.lobby.cosmic_lobby_view.cosmic_lobby_view_model import LobbyRouteEnum

class ICosmicEventBattleController(IGameController, ISeasonProvider):
    onPrimeTimeStatusUpdated = None
    onCosmicConfigChanged = None
    onStatusTick = None
    onLobbyRouteChange = None

    @property
    def isEnabled(self):
        raise NotImplementedError

    def getEventVehicle(self):
        raise NotImplementedError

    def isAvailable(self):
        raise NotImplementedError

    def isBattleAvailable(self):
        raise NotImplementedError

    def isFrozen(self):
        raise NotImplementedError

    def switchPrb(self):
        raise NotImplementedError

    def onPrbEnter(self):
        raise NotImplementedError

    def onPrbLeave(self):
        raise NotImplementedError

    def getModeSettings(self):
        raise NotImplementedError

    def openQueueView(self):
        raise NotImplementedError

    def openEventLobby(self):
        raise NotImplementedError

    def getTokenProgressionID(self):
        raise NotImplementedError

    def getProgressionQuestPrefix(self):
        raise NotImplementedError

    def getVehicleRentQuestID(self):
        raise NotImplementedError

    def getProgressionFinishedToken(self):
        raise NotImplementedError

    def isCosmicMode(self):
        raise NotImplementedError

    def getLobbyRoute(self):
        raise NotImplementedError

    def setLobbyRoute(self, route, notify=False):
        raise NotImplementedError

    def isVehicleRentQuest(self, questID):
        raise NotImplementedError

    def closeRewardScreen(self):
        raise NotImplementedError

    def closePostBattleScreen(self):
        raise NotImplementedError
