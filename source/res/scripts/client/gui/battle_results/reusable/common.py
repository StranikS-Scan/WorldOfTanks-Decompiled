# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_results/reusable/common.py
from collections import defaultdict, namedtuple
import logging
import typing
import ArenaType
from gui.battle_results.reusable.players import PlayerInfo
from gui.battle_results.battle_results_helper import getCommanderID, getCommanderInfo
from constants import ARENA_GUI_TYPE, ARENA_BONUS_TYPE, FINISH_REASON
from gui.battle_control import arena_visitor
from gui.battle_results.reusable import shared
from helpers import dependency
from helpers.bots import preprocessBotName
from shared_utils import first
from skeletons.gui.shared import IItemsCache
from soft_exception import SoftException
_logger = logging.getLogger(__name__)
SupplyInfo = namedtuple('SupplyInfo', 'supplyID intCD')

class CommonInfo(shared.UnpackedInfo):
    __slots__ = ('__arenaTypeID', '__winnerTeam', '__finishReason', '__arenaVisitor', '__bots', '__numDefended', '__supplies', '__suppliesIDtoCD')
    __itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, arenaTypeID=0, guiType=ARENA_GUI_TYPE.UNKNOWN, bonusType=ARENA_BONUS_TYPE.UNKNOWN, winnerTeam=0, finishReason=FINISH_REASON.UNKNOWN, bots=None, **kwargs):
        super(CommonInfo, self).__init__()
        self.__arenaTypeID = arenaTypeID
        self.__winnerTeam = winnerTeam
        self.__finishReason = finishReason
        self.__bots = defaultdict()
        self.__numDefended = kwargs.get('commonNumDefended', 0)
        if bots is not None:
            allActiveVehicles = kwargs.get('vehicles', {})
            additionalInfo = self._getAdditionalInfo(**kwargs)
            for info in bots.iteritems():
                if len(info) <= 1:
                    _logger.error('Bot information can not be unpacked: not enough data')
                    break
                vehicleID = info[0]
                if vehicleID in allActiveVehicles:
                    self.__bots[vehicleID] = self._processBot(info, additionalInfo)

        self.__suppliesIDtoCD = {}
        self.__supplies = self.__getSupplies(bots, kwargs.get('vehicles', {}))
        arenaType = ArenaType.g_cache[self.__arenaTypeID] if self.__arenaTypeID and self.__arenaTypeID in ArenaType.g_cache else None
        self.__arenaVisitor = arena_visitor.createSkeleton(arenaType=arenaType, guiType=guiType, bonusType=bonusType)
        return

    @property
    def arenaVisitor(self):
        return self.__arenaVisitor

    @property
    def arenaTypeID(self):
        return self.__arenaTypeID

    @property
    def arenaGuiType(self):
        return self.__arenaVisitor.getArenaGuiType()

    @property
    def arenaBonusType(self):
        return self.__arenaVisitor.getArenaBonusType()

    @property
    def arenaSubTypeName(self):
        return self.__arenaVisitor.type.getGamePlayName()

    @property
    def arenaType(self):
        return self.__arenaVisitor.type

    @property
    def winnerTeam(self):
        return self.__winnerTeam

    @property
    def finishReason(self):
        return self.__finishReason

    @property
    def isMultiTeamMode(self):
        return self.__arenaVisitor.gui.isMultiTeam()

    @property
    def numDefended(self):
        return self.__numDefended

    def isSquadSupported(self):
        return self.__arenaVisitor.bonus.isSquadSupported()

    def canTakeSquadXP(self):
        return self.__arenaVisitor.bonus.canTakeSquadXP()

    def canTakeSquadCredits(self):
        return self.__arenaVisitor.bonus.canTakeSquadCredits()

    def canTakeAnySquadBonus(self):
        return self.__arenaVisitor.bonus.canTakeAnySquadBonus()

    def getArenaIcon(self, iconKey):
        return self.__arenaVisitor.getArenaIcon(iconKey)

    def getBotInfo(self, vehicleID):
        return self.__bots[vehicleID] if vehicleID in self.__bots else None

    def getBots(self):
        return self.__bots

    def getAllSupplies(self):
        return set([ supplyInfo.supplyID for supplies in self.__supplies.values() for supplyInfo in supplies ])

    def getSupplyCD(self, supplyID):
        return self.__suppliesIDtoCD.get(supplyID)

    def getTeamSupplies(self, team):
        return self.__supplies.get(team, [])

    def _getAdditionalInfo(self, **kwargs):
        pass

    def _processBot(self, info, commanderInfo=None):
        team, name = info[1][:2]
        botPlayerInfo = PlayerInfo(team=team, realName=preprocessBotName(name))
        return botPlayerInfo

    def __getSupplies(self, bots, vehicles):
        if bots is None:
            return {}
        else:
            supplies = defaultdict(list)
            getItem = self.__itemsCache.items.getItemByCD
            for itemID in bots:
                if itemID not in vehicles:
                    continue
                itemInfo = first(vehicles[itemID])
                if itemInfo is None:
                    continue
                intCD = itemInfo.get('typeCompDescr', 0)
                item = getItem(intCD)
                if item.isSupply:
                    team = itemInfo['team']
                    supplies[team].append(SupplyInfo(itemID, intCD))
                    self.__suppliesIDtoCD[itemID] = intCD

            return supplies


class RTSCommonInfo(CommonInfo):
    __slots__ = ('__commanderTeam', '__commanderID')

    def __init__(self, arenaTypeID=0, guiType=ARENA_GUI_TYPE.UNKNOWN, bonusType=ARENA_BONUS_TYPE.UNKNOWN, winnerTeam=0, finishReason=FINISH_REASON.UNKNOWN, bots=None, **kwargs):
        self.__commanderTeam = 0
        self.__commanderID = 0
        self.__fillCommanderInfo(**kwargs)
        super(RTSCommonInfo, self).__init__(arenaTypeID, guiType, bonusType, winnerTeam, finishReason, bots, **kwargs)

    @property
    def commanderTeam(self):
        return self.__commanderTeam

    @property
    def commanderID(self):
        return self.__commanderID

    def _getAdditionalInfo(self, **kwargs):
        players = kwargs.get('players', {})
        return players.get(self.__commanderID)

    def _processBot(self, info, additionalInfo=None):
        botTeam, botName = info[1][:2]
        return PlayerInfo(dbID=self.__commanderID, **additionalInfo) if botTeam == self.__commanderTeam else PlayerInfo(team=botTeam, realName=preprocessBotName(botName))

    def __fillCommanderInfo(self, **kwargs):
        playerAvatar = kwargs.get('personalAvatar')
        players = kwargs.get('players')
        if playerAvatar is None or players is None:
            raise SoftException('Secondary data to extract bots info is None')
        commanderInfo = getCommanderInfo(playerAvatar, players)
        if commanderInfo:
            self.__commanderTeam = commanderInfo['team']
            self.__commanderID = getCommanderID(players, self.__commanderTeam)
        return
