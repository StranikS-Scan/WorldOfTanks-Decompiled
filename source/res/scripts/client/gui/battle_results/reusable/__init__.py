# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_results/reusable/__init__.py
import weakref
import typing
from account_helpers import getAccountDatabaseID
from debug_utils import LOG_WARNING
from gui.Scaleform.daapi.view.lobby.server_events.events_helpers import BattlePassProgress
from gui.battle_control.arena_info import squad_finder
from gui.battle_results.reusable import sort_keys
from gui.battle_results.reusable.avatars import AvatarsInfo
from gui.battle_results.reusable.common import CommonInfo
from gui.battle_results.reusable.personal import PersonalInfo
from gui.battle_results.reusable.players import PlayersInfo
from gui.battle_results.reusable.economics import EconomicsInfo
from gui.battle_results.reusable.progress import ProgressInfo
from gui.battle_results.reusable.shared import VehicleDetailedInfo, TeamBasesInfo, VehicleSummarizeInfo
from gui.battle_results.reusable.vehicles import VehiclesInfo
from gui.battle_results.br_constants import BattleResultsRecord as _RECORD, PlayerTeamResult as _TEAM_RESULT
from helpers import dependency
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
if typing.TYPE_CHECKING:
    from typing import Dict, Iterator, Optional, Tuple

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
        commonInfo = _checkInfo(CommonInfo(vehicles=results[_RECORD.VEHICLES], **record), _RECORD.COMMON)
    else:
        return
    record = _fetchRecord(results, _RECORD.PERSONAL)
    if record is not None:
        personalInfo = _checkInfo(PersonalInfo(record), _RECORD.PERSONAL)
        economicsInfo = _checkInfo(EconomicsInfo(record), _RECORD.PERSONAL)
        progressInfo = _checkInfo(ProgressInfo(record), _RECORD.PERSONAL)
    else:
        return
    record = _fetchRecord(results, _RECORD.PLAYERS)
    if record is not None:
        playersInfo = _checkInfo(PlayersInfo(record), _RECORD.PLAYERS)
    else:
        return
    record = _fetchRecord(results, _RECORD.VEHICLES)
    if record is not None:
        vehiclesInfo = _checkInfo(VehiclesInfo(record), _RECORD.VEHICLES)
    else:
        return
    record = _fetchRecord(results, _RECORD.AVATARS)
    if record is not None:
        avatarsInfo = _checkInfo(AvatarsInfo(record), _RECORD.AVATARS)
    else:
        return
    if not unpackedRecords:
        return ReusableInfo(arenaUniqueID, commonInfo, personalInfo, playersInfo, vehiclesInfo, avatarsInfo, economicsInfo, progressInfo)
    else:
        LOG_WARNING('Records are not valid in the results. Perhaps, client and server versions of battle_results.g_config are different.', *[ (record, results[record]) for record in unpackedRecords ])
        return


class ReusableInfo(object):
    __slots__ = ('__arenaUniqueID', '__clientIndex', '__squadFinder', '__economics', '__common', '__personal', '__players', '__vehicles', '__avatars', '__progress', '__battlePassProgress')
    itemsCache = dependency.descriptor(IItemsCache)
    lobbyContext = dependency.descriptor(ILobbyContext)

    def __init__(self, arenaUniqueID, common, personal, players, vehicles, avatars, econimics, progress):
        super(ReusableInfo, self).__init__()
        self.__arenaUniqueID = arenaUniqueID
        self.__clientIndex = 0
        self.__common = common
        self.__personal = personal
        self.__players = players
        self.__vehicles = vehicles
        self.__avatars = avatars
        self.__economics = econimics
        self.__progress = progress
        self.__squadFinder = squad_finder.createSquadFinder(self.__common.arenaVisitor)
        self.__findSquads()
        self.__battlePassProgress = BattlePassProgress(self.__common.arenaBonusType, **self.__personal.avatar.extensionInfo)

    @property
    def arenaUniqueID(self):
        return self.__arenaUniqueID

    @property
    def clientIndex(self):
        return self.__clientIndex

    @clientIndex.setter
    def clientIndex(self, index):
        self.__clientIndex = index

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
    def economics(self):
        return self.__economics

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
    def progress(self):
        return self.__progress

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

    def getPersonalDetailsIterator(self, result):
        totalSortable = {}
        totalBases = []
        playerTeam = self.__personal.avatar.team
        playerDBID = self.__personal.avatar.accountDBID
        getVehicleInfo = self.__vehicles.getVehicleInfo
        getBotInfo = self.__common.getBotInfo
        getPlayerInfo = self.__players.getPlayerInfo
        makePlayerInfo = self.__players.makePlayerInfo
        getItemByCD = self.itemsCache.items.getItemByCD
        for _, vData in self.__personal.getVehicleCDsIterator(result):
            details = vData.get('details', {})
            enemies = []
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
                vehicle = getItemByCD(intCD) if intCD else None
                sortable = VehicleDetailedInfo.makeForEnemy(vehicleID, vehicle, playerInfo, data, vehicleInfo.deathReason, vehicleInfo.isTeamKiller)
                if not sortable.haveInteractionDetails():
                    continue
                if (vehicleID, intCD) not in totalSortable:
                    totalSortable[vehicleID, intCD] = VehicleSummarizeInfo(vehicleID, playerInfo)
                totalSortable[vehicleID, intCD].addVehicleInfo(sortable)
                enemies.append(sortable)

            bases = TeamBasesInfo(vData.get('capturePoints', 0), vData.get('droppedCapturePoints', 0))
            totalBases.append(bases)
            yield ((bases,), sorted(enemies, key=sort_keys.VehicleInfoSortKey))

        yield (totalBases, sorted(totalSortable.itervalues(), key=sort_keys.VehicleInfoSortKey))
        return

    def getPersonalVehiclesInfo(self, result):
        player = weakref.proxy(self.getPlayerInfo())
        info = VehicleSummarizeInfo(0, player)
        getItemByCD = self.itemsCache.items.getItemByCD
        for intCD, records in self.__personal.getVehicleCDsIterator(result):
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
            info = self.__vehicles.getAIBotVehicleSummarizeInfo(bot[0], bot[1], result)
            if playerTeam == bot[1].team:
                allies.append(info)
            enemies.append(info)

        def __allies():
            for ally in sorted(allies, key=sortKey):
                yield ally

        def __enemies():
            for enemy in sorted(enemies, key=sortKey):
                yield enemy

        return (__allies(), __enemies())

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
