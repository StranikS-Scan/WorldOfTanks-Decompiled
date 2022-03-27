# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_results/reusable/__init__.py
import weakref
from collections import namedtuple
import typing
from account_helpers import getAccountDatabaseID
from constants import ARENA_BONUS_TYPE
from debug_utils import LOG_WARNING
from gui.Scaleform.daapi.view.lobby.server_events.events_helpers import BattlePassProgress
from gui.battle_control.arena_info import squad_finder
from gui.battle_results.reusable import sort_keys
from gui.battle_results.reusable.avatars import AvatarsInfo
from gui.battle_results.reusable.common import CommonInfo, RTSCommonInfo
from gui.battle_results.reusable.personal import PersonalInfo, RTSPersonalInfo
from gui.battle_results.reusable.players import PlayersInfo
from gui.battle_results.reusable.shared import VehicleDetailedInfo, TeamBasesInfo, SummarizeTeamBasesInfo, VehicleSummarizeInfo, SupplySummarizeInfo
from gui.battle_results.reusable.vehicles import VehiclesInfo
from gui.battle_results.settings import BATTLE_RESULTS_RECORD as _RECORD, PLAYER_TEAM_RESULT as _TEAM_RESULT, PREMIUM_STATE
from helpers import dependency
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
if typing.TYPE_CHECKING:
    from typing import Dict, Iterator, Optional, Tuple
_Reusables = namedtuple('_Reusables', ('common', 'personal', 'players', 'vehicles', 'avatars'))
_ReusableTypes = {ARENA_BONUS_TYPE.REGULAR: _Reusables(CommonInfo, PersonalInfo, PlayersInfo, VehiclesInfo, AvatarsInfo),
 ARENA_BONUS_TYPE.RTS: _Reusables(RTSCommonInfo, RTSPersonalInfo, PlayersInfo, VehiclesInfo, AvatarsInfo),
 ARENA_BONUS_TYPE.RTS_1x1: _Reusables(RTSCommonInfo, RTSPersonalInfo, PlayersInfo, VehiclesInfo, AvatarsInfo),
 ARENA_BONUS_TYPE.RTS_BOOTCAMP: _Reusables(RTSCommonInfo, RTSPersonalInfo, PlayersInfo, VehiclesInfo, AvatarsInfo)}

def _fetchRecord(results, recordName):
    if recordName in results:
        record = results[recordName]
        if record is None:
            LOG_WARNING('Record is not valid in the results. Perhaps, client and server versions of battle_results.g_config are different.', recordName)
        return record
    else:
        LOG_WARNING('Record is not found in the results', recordName, results.keys())
        return
        return


def _allies(allies, sortKey):
    for ally in sorted(allies, key=sortKey):
        yield ally


def _enemies(enemies, sortKey):
    for enemy in sorted(enemies, key=sortKey):
        yield enemy


def createReusableInfo(results):
    if _RECORD.ARENA_UNIQUE_ID in results:
        arenaUniqueID = results[_RECORD.ARENA_UNIQUE_ID]
    else:
        LOG_WARNING('Battle results must be contain key {}'.format(_RECORD.ARENA_UNIQUE_ID), results.keys())
        return
    unpackedRecords = []

    def _checkInfo(info, recordName):
        if info.hasUnpackedItems():
            unpackedRecords.append(recordName)
        return info

    record = _fetchRecord(results, _RECORD.COMMON)
    if record is not None:
        bonusType = record['bonusType']
        reusableTypes = _ReusableTypes.get(bonusType, _ReusableTypes[ARENA_BONUS_TYPE.REGULAR])
        commonInfo = _checkInfo(reusableTypes.common(vehicles=results[_RECORD.VEHICLES], personalAvatar=results.get(_RECORD.PERSONAL, {}).get(_RECORD.PERSONAL_AVATAR), players=results.get(_RECORD.PLAYERS), **record), _RECORD.COMMON)
    else:
        return
    record = _fetchRecord(results, _RECORD.PERSONAL)
    if record is not None:
        personalInfo = _checkInfo(reusableTypes.personal(record), _RECORD.PERSONAL)
    else:
        return
    record = _fetchRecord(results, _RECORD.PLAYERS)
    if record is not None:
        playersInfo = _checkInfo(reusableTypes.players(record), _RECORD.PLAYERS)
    else:
        return
    record = _fetchRecord(results, _RECORD.VEHICLES)
    if record is not None:
        vehiclesInfo = _checkInfo(reusableTypes.vehicles(record), _RECORD.VEHICLES)
    else:
        return
    record = _fetchRecord(results, _RECORD.AVATARS)
    if record is not None:
        avatarsInfo = _checkInfo(reusableTypes.avatars(record), _RECORD.AVATARS)
    else:
        return
    if not unpackedRecords:
        return _ReusableInfo(arenaUniqueID, commonInfo, personalInfo, playersInfo, vehiclesInfo, avatarsInfo)
    else:
        LOG_WARNING('Records are not valid in the results. Perhaps, client and server versions of battle_results.g_config are different.', *[ (record, results[record]) for record in unpackedRecords ])
        return


class _ReusableInfo(object):
    __slots__ = ('__arenaUniqueID', '__clientIndex', '__premiumState', '__common', '__personal', '__players', '__vehicles', '__avatars', '__squadFinder', '__premiumPlusState', '__isAddXPBonusApplied', '__battlePassProgress')
    itemsCache = dependency.descriptor(IItemsCache)
    lobbyContext = dependency.descriptor(ILobbyContext)

    def __init__(self, arenaUniqueID, common, personal, players, vehicles, avatars):
        super(_ReusableInfo, self).__init__()
        self.__arenaUniqueID = arenaUniqueID
        self.__clientIndex = 0
        self.__premiumState = PREMIUM_STATE.NONE
        self.__premiumPlusState = PREMIUM_STATE.NONE
        self.__isAddXPBonusApplied = False
        self.__common = common
        self.__personal = personal
        self.__players = players
        self.__vehicles = vehicles
        self.__avatars = avatars
        self.__squadFinder = squad_finder.createSquadFinder(self.__common.arenaVisitor)
        self.__findSquads()
        self.__battlePassProgress = BattlePassProgress(self.__common.arenaBonusType, **self.__personal.avatar.extensionInfo)

    @property
    def arenaUniqueID(self):
        return self.__arenaUniqueID

    @property
    def arenaBonusType(self):
        return self.__common.arenaBonusType

    @property
    def clientIndex(self):
        return self.__clientIndex

    @clientIndex.setter
    def clientIndex(self, index):
        self.__clientIndex = index

    @property
    def hasAnyPremiumInPostBattle(self):
        return self.__personal.hasAnyPremium

    @property
    def premiumState(self):
        return self.__premiumState

    @premiumState.setter
    def premiumState(self, state):
        self.__premiumState = state

    @property
    def premiumPlusState(self):
        return self.__premiumPlusState

    @premiumPlusState.setter
    def premiumPlusState(self, state):
        self.__premiumPlusState = state

    @property
    def isPremiumBought(self):
        return self.__premiumState & PREMIUM_STATE.BOUGHT > 0

    @property
    def isPremiumPlusBought(self):
        return self.__premiumPlusState & PREMIUM_STATE.BOUGHT > 0

    @property
    def isPostBattlePremium(self):
        return self.__personal.isPremium or self.isPremiumBought

    @property
    def isPostBattlePremiumPlus(self):
        return self.__personal.isPremiumPlus or self.isPremiumPlusBought

    @property
    def isAddXPBonusApplied(self):
        return self.__personal.isAddXPBonusApplied

    @isAddXPBonusApplied.setter
    def isAddXPBonusApplied(self, state):
        self.__personal.isAddXPBonusApplied = state

    @property
    def canUpgradeToPremium(self):
        return self.__premiumState & PREMIUM_STATE.BUY_ENABLED > 0 and self.__premiumState & PREMIUM_STATE.HAS_ALREADY == 0 and not self.isPostBattlePremium and self.__common.arenaBonusType in (ARENA_BONUS_TYPE.REGULAR, ARENA_BONUS_TYPE.EPIC_RANDOM, ARENA_BONUS_TYPE.EPIC_BATTLE)

    @property
    def canUpgradeToPremiumPlus(self):
        return self.__premiumPlusState & PREMIUM_STATE.BUY_ENABLED > 0 and self.__premiumPlusState & PREMIUM_STATE.HAS_ALREADY == 0 and not self.isPostBattlePremiumPlus and self.__common.arenaBonusType in (ARENA_BONUS_TYPE.REGULAR, ARENA_BONUS_TYPE.EPIC_RANDOM, ARENA_BONUS_TYPE.EPIC_BATTLE)

    @property
    def canResourceBeFaded(self):
        return not self.__personal.avatar.hasPenalties()

    @property
    def isSquadSupported(self):
        return self.__common.isSquadSupported()

    @property
    def isStunEnabled(self):
        return self.lobbyContext.getServerSettings().spgRedesignFeatures.isStunEnabled()

    @property
    def common(self):
        return self.__common

    @property
    def personal(self):
        return self.__personal

    @property
    def players(self):
        return self.__players

    @property
    def vehicles(self):
        return self.__vehicles

    @property
    def avatars(self):
        return self.__avatars

    @property
    def battlePassProgress(self):
        return self.__battlePassProgress

    def getAvatarInfo(self, dbID=0):
        if not dbID:
            dbID = self.__personal.avatar.accountDBID
        return self.__avatars.getAvatarInfo(dbID)

    def isPersonalTeamWin(self):
        return self.__common.winnerTeam == self.__personal.avatar.team

    def getPersonalTeam(self):
        return self.__personal.avatar.team

    def getPersonalTeamResult(self):
        winnerTeam = self.__common.winnerTeam
        playerTeam = self.__personal.avatar.team
        if not winnerTeam:
            teamResult = _TEAM_RESULT.DRAW
        elif winnerTeam == playerTeam:
            teamResult = _TEAM_RESULT.WIN
        else:
            teamResult = _TEAM_RESULT.DEFEAT
        return teamResult

    def getPlayerInfo(self, dbID=0):
        if not dbID:
            dbID = self.__personal.avatar.accountDBID
        return self.__players.getPlayerInfo(dbID)

    def getPlayerInfoByVehicleID(self, vehicleID):
        accountDBID = self.__vehicles.getAccountDBID(vehicleID)
        if accountDBID:
            playerInfo = self.__players.getPlayerInfo(accountDBID)
        else:
            botInfo = self.__common.getBotInfo(vehicleID)
            botName = botInfo.realName if botInfo else ''
            playerInfo = self.__players.makePlayerInfo(realName=botName, fakeName=botName)
        return playerInfo

    def wasInBattle(self, dbID=0):
        if not dbID:
            dbID = getAccountDatabaseID()
        return self.__players.getPlayerInfo(dbID).wasInBattle

    def getPersonalDetailsIterator(self, result, onlySummary=False):
        totalSortableVehicles = {}
        totalSortableSupplies = {}
        totalBases = SummarizeTeamBasesInfo(result)
        playerTeam = self.__personal.avatar.team
        playerDBID = self.__personal.avatar.accountDBID
        getVehicleInfo = self.__vehicles.getVehicleInfo
        getBotInfo = self.__common.getBotInfo
        getPlayerInfo = self.__players.getPlayerInfo
        makePlayerInfo = self.__players.makePlayerInfo
        getItemByCD = self.itemsCache.items.getItemByCD
        sortVehicleKey = sort_keys.VehicleInfoSortKey
        for _, vData in self.__personal.getVehicleCDsIterator(result):
            vehicles = []
            supplies = []
            details = vData.get('details', {})
            for (vehicleID, _), data in details.iteritems():
                vehicleInfo = getVehicleInfo(vehicleID)
                intCD = None
                if not vehicleInfo.intCD and not vehicleInfo.accountDBID:
                    if getBotInfo(vehicleID) is not None:
                        intCD = vehicleID
                else:
                    intCD = vehicleInfo.intCD
                if vehicleInfo.accountDBID == playerDBID or vehicleInfo.team == playerTeam:
                    continue
                if vehicleInfo.accountDBID:
                    playerInfo = weakref.proxy(getPlayerInfo(vehicleInfo.accountDBID))
                else:
                    botInfo = getBotInfo(vehicleID)
                    botName = botInfo.realName if botInfo else ''
                    playerInfo = makePlayerInfo(realName=botName, fakeName=botName)
                item = getItemByCD(intCD) if intCD else None
                sortable = VehicleDetailedInfo.makeForEnemy(vehicleID, item, playerInfo, data, vehicleInfo.deathReason, vehicleInfo.isTeamKiller)
                if not item or not sortable.haveInteractionDetails():
                    continue
                if item.isSupply:
                    supplies.append(sortable)
                    totalSortableItems, itemKey = totalSortableSupplies, intCD
                else:
                    vehicles.append(sortable)
                    totalSortableItems, itemKey = totalSortableVehicles, (vehicleID, intCD)
                if itemKey not in totalSortableItems:
                    totalSortableItems[itemKey] = VehicleSummarizeInfo(vehicleID, playerInfo)
                totalSortableItems[itemKey].addVehicleInfo(sortable)

            bases = TeamBasesInfo(vData.get('capturePoints', 0), vData.get('droppedCapturePoints', 0))
            totalBases.addBasesInfo(bases)
            if not onlySummary:
                yield ((bases,), sorted(vehicles, key=sortVehicleKey), sorted(supplies))

        yield ((totalBases,), sorted(totalSortableVehicles.itervalues(), key=sortVehicleKey), sorted(totalSortableSupplies.itervalues(), key=sortVehicleKey))
        return

    def getPersonalVehiclesInfo(self, result, reusable=None):
        player = weakref.proxy(self.getPlayerInfo())
        info = VehicleSummarizeInfo(0, player)
        getItemByCD = self.itemsCache.items.getItemByCD
        for intCD, records in self.__personal.getVehicleCDsIterator(result, reusable):
            critsRecords = []
            if 'details' in records:
                playerTeam = self.__personal.avatar.team
                playerDBID = self.__personal.avatar.accountDBID
                getVehicleInfo = self.__vehicles.getVehicleInfo
                details = records['details']
                for (vehicleID, _), data in details.iteritems():
                    vehicleInfo = getVehicleInfo(vehicleID)
                    if vehicleInfo.accountDBID != playerDBID and vehicleInfo.team != playerTeam:
                        critsRecords.append(data['crits'])

            info.addVehicleInfo(VehicleDetailedInfo.makeForVehicle(0, getItemByCD(intCD), player, records, critsRecords=critsRecords))

        info.addAvatarInfo(weakref.proxy(self.getAvatarInfo()))
        return info

    def getAllPlayersIterator(self, result, sortKey=sort_keys.TeamItemSortKey):
        allPlayers = []
        getAvatarInfo = self.__avatars.getAvatarInfo
        for dbID, player in self.__players.getPlayerInfoIterator():
            info = self.__vehicles.getVehicleSummarizeInfo(player, result)
            info.addAvatarInfo(weakref.proxy(getAvatarInfo(dbID)))
            allPlayers.append(info)

        bots = self.__common.getBots()
        for bot in bots.iteritems():
            info = self.__vehicles.getAIBotVehicleSummarizeInfo(bot[0], bot[1], result)
            allPlayers.append(info)

        def __allPlayers():
            for player in sorted(allPlayers, key=sortKey):
                yield player

        return __allPlayers()

    def getBiDirectionTeamsIterator(self, result, sortKey=sort_keys.TeamItemSortKey):
        allies = []
        enemies = []
        enemySupplies = {}
        allySupplies = {}
        playerTeam = self.__personal.avatar.team
        getAvatarInfo = self.__avatars.getAvatarInfo
        for dbID, player in self.__players.getPlayerInfoIterator():
            info = self.__vehicles.getVehicleSummarizeInfo(player, result)
            info.addAvatarInfo(weakref.proxy(getAvatarInfo(dbID)))
            if playerTeam == player.team:
                allies.append(info)
            enemies.append(info)

        bots = self.__common.getBots()
        for bot in bots.iteritems():
            botVehicleID, botPlayerInfo = bot[0], bot[1]
            isAlly = botPlayerInfo.team == playerTeam
            info = self.__vehicles.getAIBotVehicleSummarizeInfo(botVehicleID, botPlayerInfo, result)
            supplyCD = self.__common.getSupplyCD(botVehicleID)
            if supplyCD is not None:
                totalSortableItems = allySupplies if isAlly else enemySupplies
                if supplyCD not in totalSortableItems:
                    totalSortableItems[supplyCD] = SupplySummarizeInfo(botVehicleID, botPlayerInfo)
                totalSortableItems[supplyCD].addVehicleInfo(info)
            if isAlly:
                allies.append(info)
            enemies.append(info)

        allies.extend(allySupplies.values())
        enemies.extend(enemySupplies.values())
        return (_allies(allies, sortKey), _enemies(enemies, sortKey))

    def getPersonalSquadFlags(self):
        playerInfo = self.getPlayerInfo()
        showSquadLabels = playerInfo.squadIndex and self.__common.canTakeAnySquadBonus()
        squadHasBonus = False
        if showSquadLabels:
            showSquadLabels, squadHasBonus = self.__personal.avatar.getPersonalSquadFlags(self.__vehicles)
        return (showSquadLabels, squadHasBonus)

    def updateXPEarnings(self, additionalXPValues):
        self.__personal.updateXPEarnings(additionalXPValues)

    def __findSquads(self):
        getVehicleID = self.__vehicles.getVehicleID
        getAccountID = self.__vehicles.getAccountDBID
        for _, info in self.__players.getPlayerInfoIterator():
            prebattleID = info.prebattleID
            vehicleID = getVehicleID(info.dbID)
            team = info.team
            if prebattleID and vehicleID:
                self.__squadFinder.addVehicleInfo(team, prebattleID, vehicleID)

        setter = self.__players.setSquadIndex
        for vehicleID, squadIndex in self.__squadFinder.findSquads():
            setter(getAccountID(vehicleID), squadIndex)
