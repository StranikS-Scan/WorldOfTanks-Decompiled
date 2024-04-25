# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/server_events/battle_royale_formatters.py
import logging
from collections import namedtuple
from constants import ARENA_BONUS_TYPE
from gui.Scaleform.locale.BATTLE_ROYALE import BATTLE_ROYALE
from gui.battle_control.arena_info import vos_collections
from gui.battle_control.battle_constants import PERSONAL_EFFICIENCY_TYPE as _ETYPE
from helpers import dependency
from skeletons.gui.lobby_context import ILobbyContext
_logger = logging.getLogger(__name__)
_logger.addHandler(logging.NullHandler())
_StatsItemValues = namedtuple('_StatsItemValues', ('value', 'maxValue'))
_NO_MAX_VALUE = -1

class StatsItemType(object):
    PLACE = 'place'
    KILLS_SOLO = 'kills'
    KILLS_SQUAD = 'squadKills'
    DAMAGE_DEAL = 'damageDealt'
    DAMAGE_BLOCK = 'damageBlockedByArmor'


SOLO_ITEMS_ORDER = [StatsItemType.PLACE,
 StatsItemType.KILLS_SOLO,
 StatsItemType.DAMAGE_DEAL,
 StatsItemType.DAMAGE_BLOCK]
SQUAD_ITEMS_ORDER = [StatsItemType.PLACE,
 StatsItemType.KILLS_SOLO,
 StatsItemType.KILLS_SQUAD,
 StatsItemType.DAMAGE_DEAL,
 StatsItemType.DAMAGE_BLOCK]

class BRSections(object):
    FINISH_REASON = 'finishReason'
    COMMON = 'common'
    PERSONAL = 'personal'
    STATS = 'stats'
    PROGRESS = 'eventProgression'
    LEADERBOARD = 'leaderboard'
    IN_BATTLE = 'inBattle'
    FINANCE = 'financialBalance'
    FINANCE_PREM = 'financialBalancePrem'
    REWARDS = 'rewards'
    ACHIEVEMENTS = 'achievements'
    BONUSES = 'bonuses'
    BATTLE_PASS = 'battlePass'
    BR_AWARD_TOKENS = 'brAwardTokens'


class IngameBattleRoyaleResultsViewDataFormatter(object):
    __lobbyContext = dependency.descriptor(ILobbyContext)

    def __init__(self, sessionProvider, bonusQuestById):
        self.__sessionProvider = sessionProvider
        self.__arenaDP = sessionProvider.getArenaDP()
        self.__playerVehicleID = self.__arenaDP.getPlayerVehicleID()
        self.__efficiencyCtrl = sessionProvider.shared.personalEfficiencyCtrl

    @property
    def isInSquad(self):
        bonusType = self.__sessionProvider.arenaVisitor.getArenaBonusType()
        return bonusType in ARENA_BONUS_TYPE.BATTLE_ROYALE_SQUAD_RANGE

    @property
    def playersCount(self):
        return vos_collections.ActiveVehiclesItemsCollection().count(self.__arenaDP)

    def getSummaryStats(self):
        return [self.__getPlace(),
         self.__getDamageDealt(),
         self.__getKilled(),
         self.__getBlockedDamage()]

    def __getPlace(self):
        place = self.__sessionProvider.arenaVisitor.getComponentSystem().battleRoyaleComponent.place
        return self.__createStatItem('{}/{}'.format(place, self.__maxPlaceValue()), BATTLE_ROYALE.PLAYERSTATS_PLACESTAT_NAME, StatsItemType.PLACE)

    def __maxPlaceValue(self):
        if self.isInSquad:
            vehicles = self.__arenaDP.getVehiclesItemsGenerator()
            return len({vinfo.team for vinfo, _ in vehicles if vinfo.isPlayer()})
        return self.playersCount

    def __getKilled(self):
        return self.__createStatItem(self.__arenaDP.getVehicleStats().frags, BATTLE_ROYALE.PLAYERSTATS_KILLSSTAT_NAME, StatsItemType.KILLS_SOLO)

    def __getBlockedDamage(self):
        return self.__createStatItem(self.__efficiencyCtrl.getTotalEfficiency(_ETYPE.BLOCKED_DAMAGE), BATTLE_ROYALE.PLAYERSTATS_DAMAGEBLOCKEDBYARMORSTAT_NAME, StatsItemType.DAMAGE_BLOCK)

    def __getDamageDealt(self):
        return self.__createStatItem(self.__efficiencyCtrl.getTotalEfficiency(_ETYPE.DAMAGE), BATTLE_ROYALE.PLAYERSTATS_DAMAGEDEALTSTAT_NAME, StatsItemType.DAMAGE_DEAL)

    @staticmethod
    def __createStatItem(value, descr, imgID):
        return {'value': str(value),
         'description': descr,
         'imageID': imgID}
