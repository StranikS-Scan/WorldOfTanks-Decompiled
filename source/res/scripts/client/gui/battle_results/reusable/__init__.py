# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_results/reusable/__init__.py
import weakref
from account_helpers import getAccountDatabaseID
from constants import ARENA_BONUS_TYPE
from debug_utils import LOG_WARNING
from gui.battle_control.arena_info import squad_finder
from gui.battle_results.reusable import sort_keys
from gui.battle_results.reusable.avatars import AvatarsInfo
from gui.battle_results.reusable.common import CommonInfo
from gui.battle_results.reusable.personal import PersonalInfo
from gui.battle_results.reusable.players import PlayersInfo
from gui.battle_results.reusable.shared import VehicleDetailedInfo, TeamBasesInfo
from gui.battle_results.reusable.shared import VehicleSummarizeInfo
from gui.battle_results.reusable.vehicles import VehiclesInfo
from gui.battle_results.settings import BATTLE_RESULTS_RECORD as _RECORD, PREMIUM_STATE
from gui.battle_results.settings import PLAYER_TEAM_RESULT as _TEAM_RESULT
from gui.shared import g_itemsCache
from gui.LobbyContext import g_lobbyContext

def _fetchRecord(results, recordName):
    if recordName in results:
        record = results[recordName]
        if record is None:
            LOG_WARNING('Record is not valid in the results. Perhaps, client and server versions of file battle_results_shared.py are different.', recordName)
        return record
    else:
        LOG_WARNING('Record is not found in the results', recordName, results.keys())
        return
        return


def createReusableInfo(results):
    """Fetches reusable information form dictionary containing battle_results.
    Routine returns None if some value equals None by top level key. It means that
    client and server versions of file battle_results_shared are different.
    :param results: dictionary containing battle_results.
    :return: instance of _ReusableInfo
    """
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
        commonInfo = _checkInfo(CommonInfo(**record), _RECORD.COMMON)
    else:
        return
    record = _fetchRecord(results, _RECORD.PERSONAL)
    if record is not None:
        personalInfo = _checkInfo(PersonalInfo(record), _RECORD.PERSONAL)
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
        return _ReusableInfo(arenaUniqueID, commonInfo, personalInfo, playersInfo, vehiclesInfo, avatarsInfo)
    else:
        LOG_WARNING('Records are not valid in the results. Perhaps, client and server versions of file battle_results_shared.py are different.', *[ (record, results[record]) for record in unpackedRecords ])
        return
        return


class _ReusableInfo(object):
    """Class contains reusable information that is fetched from dictionary
    containing results of battle."""
    __slots__ = ('__arenaUniqueID', '__clientIndex', '__premiumState', '__common', '__personal', '__players', '__vehicles', '__avatars', '__squadFinder')

    def __init__(self, arenaUniqueID, common, personal, players, vehicles, avatars):
        super(_ReusableInfo, self).__init__()
        self.__arenaUniqueID = arenaUniqueID
        self.__clientIndex = 0
        self.__premiumState = PREMIUM_STATE.NONE
        self.__common = common
        self.__personal = personal
        self.__players = players
        self.__vehicles = vehicles
        self.__avatars = avatars
        self.__squadFinder = squad_finder.createSquadFinder(self.__common.arenaVisitor)
        self.__findSquads()

    @property
    def arenaUniqueID(self):
        """Gets unique ID of arena."""
        return self.__arenaUniqueID

    @property
    def clientIndex(self):
        """Gets client index of arena, because of view can downgrade arenaUniqueID
        when player tries to buy premium from battle results window."""
        return self.__clientIndex

    @clientIndex.setter
    def clientIndex(self, index):
        self.__clientIndex = index

    @property
    def premiumState(self):
        """Gets premium state of account corresponding to given battle results.
        :return: bitmask containing values from PREMIUM_STATE."""
        return self.__premiumState

    @premiumState.setter
    def premiumState(self, state):
        """Sets premium state of account corresponding to given battle results.
        :param state:
        :return:
        """
        self.__premiumState = state

    @property
    def isPremiumBought(self):
        """Is premium bought in current client session?"""
        return self.__premiumState & PREMIUM_STATE.BOUGHT > 0

    @property
    def isPostBattlePremium(self):
        """Is premium bought in current client session or
        player has premium before the battle?"""
        return self.__personal.isPremium or self.isPremiumBought

    @property
    def canUpgradeToPremium(self):
        """Can player buy premium by given battle result?"""
        return self.__premiumState & PREMIUM_STATE.BUY_ENABLED > 0 and self.__premiumState & PREMIUM_STATE.HAS_ALREADY == 0 and not self.isPostBattlePremium and self.__common.arenaBonusType == ARENA_BONUS_TYPE.REGULAR and self.__personal.getXPDiff() > 0 and self.__personal.getCreditsDiff() > 0

    @property
    def canResourceBeFaded(self):
        """Can resource be faded if value equals zero.
        Resource can not be faded if penalties are applied. @see WOTD-76976."""
        return not self.__personal.avatar.hasPenalties()

    @property
    def isSquadSupported(self):
        """Can some squad take part in the specified battle."""
        return self.__common.isSquadSupported()

    @property
    def isStunEnabled(self):
        """Is stun info should be visible."""
        return g_lobbyContext.getServerSettings().spgRedesignFeatures.isStunEnabled()

    @property
    def common(self):
        """Gets common reusable information"""
        return self.__common

    @property
    def personal(self):
        """Gets personal reusable information"""
        return self.__personal

    @property
    def players(self):
        """Gets reusable information about players who took part in the battle."""
        return self.__players

    @property
    def vehicles(self):
        """Gets reusable information about vehicles that took part in the battle."""
        return self.__vehicles

    @property
    def avatars(self):
        """Gets reusable information about avatar who took part in the battle."""
        return self.__avatars

    def getAvatarInfo(self, dbID=0):
        """ Get information about avatar by specified account's database ID or
        use personal account's database ID
        :param dbID:
        :return: instance of AvatarInfo.
        """
        if not dbID:
            dbID = self.__personal.avatar.accountDBID
        return self.__avatars.getAvatarInfo(dbID)

    def isPersonalTeamWin(self):
        """Does personal team win?"""
        return self.__common.winnerTeam == self.__personal.avatar.team

    def getPersonalTeam(self):
        """Gets number of personal team."""
        return self.__personal.avatar.team

    def getPersonalTeamResult(self):
        """Gets personal team result (win, defeat or draw).
        :return: string containing one of PLAYER_TEAM_RESULT.*.
        """
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
        """Gets information about desired player.
        :param dbID: long containing account database ID or 0.
        :return: instance of PlayerInfo.
        """
        if not dbID:
            dbID = self.__personal.avatar.accountDBID
        return self.__players.getPlayerInfo(dbID)

    def getPlayerInfoByVehicleID(self, vehicleID):
        """Gets information about desired player by vehicle ID and include bots to search.
        :param vehicleID: long containing vehicle entity ID.
        :return: instance of PlayerInfo.
        """
        accountDBID = self.__vehicles.getAccountDBID(vehicleID)
        if accountDBID:
            playerInfo = self.__players.getPlayerInfo(accountDBID)
        else:
            botInfo = self.__common.getBotInfo(vehicleID)
            playerInfo = self.__players.makePlayerInfo(0, botInfo.name)
        return playerInfo

    def wasInBattle(self, dbID=0):
        """Was player in the battle?
        :param dbID: long containing account database ID or 0.
        :return: True if player was in the battle, otherwise - False.
        """
        if not dbID:
            dbID = getAccountDatabaseID()
        return self.__players.getPlayerInfo(dbID).wasInBattle

    def getPersonalDetailsIterator(self, result):
        """Gets generator to iterate details for each personal vehicle.
        Note: the last item is containing summarize information.
        :param result: dict containing results['personal'].
        :return: generator.
        """
        totalSortable = {}
        totalBases = []
        playerTeam = self.__personal.avatar.team
        playerDBID = self.__personal.avatar.accountDBID
        getVehicleInfo = self.__vehicles.getVehicleInfo
        getBotInfo = self.__common.getBotInfo
        getPlayerInfo = self.__players.getPlayerInfo
        makePlayerInfo = self.__players.makePlayerInfo
        getItemByCD = g_itemsCache.items.getItemByCD
        for _, vData in self.__personal.getVehicleCDsIterator(result):
            details = vData.get('details', {})
            enemies = []
            for (vehicleID, _), data in details.iteritems():
                vehicleInfo = getVehicleInfo(vehicleID)
                if not vehicleInfo.intCD:
                    intCD = getBotInfo(vehicleID).intCD
                else:
                    intCD = vehicleInfo.intCD
                if vehicleInfo.accountDBID == playerDBID or vehicleInfo.team == playerTeam:
                    continue
                if vehicleInfo.accountDBID:
                    playerInfo = weakref.proxy(getPlayerInfo(vehicleInfo.accountDBID))
                else:
                    playerInfo = makePlayerInfo(name=getBotInfo(vehicleID).name)
                sortable = VehicleDetailedInfo.makeForEnemy(vehicleID, getItemByCD(intCD), playerInfo, data, vehicleInfo.deathReason)
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

    def getPersonalVehiclesInfo(self, result):
        """Gets summarize information about all personal vehicles.
        :param result: dict containing results['personal'].
        :return: instance of VehicleSummarizeInfo.
        """
        player = weakref.proxy(self.getPlayerInfo())
        info = VehicleSummarizeInfo(0, player)
        getItemByCD = g_itemsCache.items.getItemByCD
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

    def getBiDirectionTeamsIterator(self, result):
        """Gets two generators to iterate details for each vehicle.
        :param result: dict containing results['vehicles'].
        :return: tuple containing generator of allied vehicles and generator of enemy vehicles.
        """
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

        def __allies():
            for ally in sorted(allies, key=sort_keys.TeamItemSortKey):
                yield ally

        def __enemies():
            for enemy in sorted(enemies, key=sort_keys.TeamItemSortKey):
                yield enemy

        return (__allies(), __enemies())

    def getPersonalSquadFlags(self):
        """Gets flags to shown bonuses and penalties for personal squad.
        :return: tuple(<are squad labels shown>, <has squad bonus>)
        """
        playerInfo = self.getPlayerInfo()
        showSquadLabels = playerInfo.squadIndex and self.__common.canTakeSquadXP()
        squadHasBonus = False
        if showSquadLabels:
            showSquadLabels, squadHasBonus = self.__personal.avatar.getPersonalSquadFlags(self.__vehicles)
        return (showSquadLabels, squadHasBonus)

    def __findSquads(self):
        getVehicleID = self.__vehicles.getVehicleID
        getAccountID = self.__vehicles.getAccountDBID
        for dbID, info in self.__players.getPlayerInfoIterator():
            prebattleID = info.prebattleID
            vehicleID = getVehicleID(info.dbID)
            team = info.team
            if prebattleID and vehicleID:
                self.__squadFinder.addVehicleInfo(team, prebattleID, vehicleID)

        setter = self.__players.setSquadIndex
        for vehicleID, squadIndex in self.__squadFinder.findSquads():
            setter(getAccountID(vehicleID), squadIndex)
