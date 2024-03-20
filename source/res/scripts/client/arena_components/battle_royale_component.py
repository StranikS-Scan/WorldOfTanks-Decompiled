# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/arena_components/battle_royale_component.py
import BigWorld
from arena_component_system.client_arena_component_system import ClientArenaComponent
from constants import ARENA_BONUS_TYPE
import Event
from helpers import dependency
from skeletons.gui.game_control import IBattleRoyaleController
from skeletons.gui.battle_session import IBattleSessionProvider
from debug_utils import LOG_DEBUG_DEV

class BattleRoyaleComponent(ClientArenaComponent):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)
    __battleRoyaleController = dependency.descriptor(IBattleRoyaleController)

    def __init__(self, componentSystem):
        ClientArenaComponent.__init__(self, componentSystem)
        self.__place = None
        self.__defeatedTeams = []
        self.onBattleRoyalePlaceUpdated = Event.Event(self._eventManager)
        self.onBattleRoyaleDefeatedTeamsUpdate = Event.Event(self._eventManager)
        return

    def setBattleRoyalePlace(self, place):
        LOG_DEBUG_DEV('setBattleRoyalePlace', place)
        self.__place = place
        self.onBattleRoyalePlaceUpdated(place)

    def setDefeatedTeams(self, defeatedTeams):
        LOG_DEBUG_DEV('setDefeatedTeams', defeatedTeams)
        self.__defeatedTeams = defeatedTeams
        self.onBattleRoyaleDefeatedTeamsUpdate(defeatedTeams)

    @property
    def place(self):
        return self.__place

    @property
    def defeatedTeams(self):
        return self.__defeatedTeams

    @property
    def stpDailyBonusFactor(self):
        defaultFactor = 1
        vehicle = BigWorld.entity(BigWorld.player().playerVehicleID)
        stPatrickComp = vehicle.dynamicComponents.get('vehicleBRStPatrickComponent')
        if not stPatrickComp or not stPatrickComp.isDailyBonusAvailable:
            return defaultFactor
        stpDailyBonusConf = self.__battleRoyaleController.getModeSettings().dailyBonusSTP
        arenaBonusType = self.__sessionProvider.arenaVisitor.getArenaBonusType()
        topPlaceKey = 'squadTopPlaces' if arenaBonusType in ARENA_BONUS_TYPE.BATTLE_ROYALE_SQUAD_RANGE else 'soloTopPlaces'
        topPlace = stpDailyBonusConf.get(topPlaceKey, 0)
        return stpDailyBonusConf['bonusFactor'] if self.place <= topPlace else defaultFactor
