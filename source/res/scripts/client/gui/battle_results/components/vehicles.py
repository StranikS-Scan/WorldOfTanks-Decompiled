# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_results/components/vehicles.py
"""
Module contains components that are included in information about vehicles: list of enemy vehicles,
list of ally vehicles, detailed information about each vehicle.
"""
from constants import DEATH_REASON_ALIVE
from gui.Scaleform.locale.BATTLE_RESULTS import BATTLE_RESULTS
from gui.Scaleform.locale.RANKED_BATTLES import RANKED_BATTLES
from gui.Scaleform.genConsts.RANKEDBATTLES_ALIASES import RANKEDBATTLES_ALIASES
from gui.battle_results.components import base, personal, shared, style, common
from gui.battle_results.reusable import sort_keys
from gui.shared.gui_items.Vehicle import getSmallIconPath, getIconPath
from gui.shared.formatters import text_styles
from helpers import dependency, i18n
from skeletons.gui.lobby_context import ILobbyContext
_STAT_VALUES_VO_REPLACER = {'damageAssisted': 'damageAssistedSelf',
 'damageAssistedStun': 'damageAssistedStunSelf'}
_STAT_STUN_FIELD_NAMES = ('damageAssistedStun', 'stunNum')

class TeamPlayerNameBlock(shared.PlayerNameBlock):
    __slots__ = ('igrType',)

    def setPlayerInfo(self, playerInfo):
        super(TeamPlayerNameBlock, self).setPlayerInfo(playerInfo)
        self.igrType = playerInfo.igrType

    def setRecord(self, result, reusable):
        self.setPlayerInfo(result)


class RegularVehicleStatsBlock(base.StatsBlock):
    """Block contains vehicle information to show in team list."""
    __slots__ = ('_isObserver', 'achievements', 'achievementsCount', 'vehicleState', 'vehicleStatePrefix', 'vehicleStateSuffix', 'killerID', 'deathReason', 'isPrematureLeave', 'vehicleName', 'vehicleShortName', 'vehicleIcon', 'vehicleSort', 'isPersonal', 'kills', 'tkills', 'realKills', 'xp', 'damageDealt', 'vehicles', 'playerID', 'player', 'statValues', 'fortResource', 'squadIndex', 'isPersonalSquad', 'xpSort', 'intCD', 'rank', 'rankIcon', 'badge', 'badgeIcon')

    def __init__(self, meta=None, field='', *path):
        super(RegularVehicleStatsBlock, self).__init__(meta, field, *path)
        self._isObserver = False
        self.isPersonal = None
        self.isPersonalSquad = None
        self.vehicleSort = None
        self.badge = 0
        self.badgeIcon = None
        return

    def setRecord(self, result, reusable):
        """Sets record of battle results to fetch required data.
        :param result: instance of VehicleDetailedInfo or VehicleSummarizeInfo
        :param reusable: instance of _ReusableInfo.
        """
        player = result.player
        avatar = reusable.avatars.getAvatarInfo(player.dbID)
        noPenalties = not avatar.hasPenalties()
        self.badge = avatar.badge
        if self.badge > 0:
            self.badgeIcon = style.makeBadgeIcon(self.badge)
        else:
            self.badgeIcon = None
        self._setVehicleInfo(result.vehicle)
        self._setPlayerInfo(player)
        self._setTotalStats(result, noPenalties)
        self._setVehiclesStats(result)
        if not self.isPersonal or noPenalties:
            self._setAchievements(result)
        if not self._isObserver:
            self._setVehicleState(result, reusable)
        return

    def _setVehicleInfo(self, vehicle):
        if vehicle is not None:
            self._isObserver = vehicle.isObserver
            self.intCD = vehicle.intCD
            self.vehicleName = vehicle.userName
            self.vehicleShortName = vehicle.shortUserName
            self.vehicleIcon = getSmallIconPath(vehicle.name)
            self.vehicles = [{'icon': getIconPath(vehicle.name)}]
        return

    def _setPlayerInfo(self, player):
        self.playerID = player.dbID
        self.player = player
        self.squadIndex = player.squadIndex

    def _setTotalStats(self, result, noPenalties):
        self.kills = kills = result.kills
        self.tkills = teamKills = result.tkills
        self.realKills = kills - teamKills
        self.damageDealt = result.damageDealt
        if noPenalties:
            self.xp = result.xp
            self.xpSort = result.xp
        else:
            self.xp = 0
            self.xpSort = 0

    def _setVehiclesStats(self, result):
        self.statValues = (self.isPersonal, result.getVehiclesIterator())

    def _setAchievements(self, result):
        achievements = result.getAchievements()
        self.achievementsCount = len(achievements)
        self.achievements = achievements

    def _setVehicleState(self, result, reusable):
        if self._isObserver:
            return
        self.killerID = result.killerID
        self.deathReason = result.deathReason
        if self.isPersonal and reusable.personal.avatar.isPrematureLeave:
            state = i18n.makeString(BATTLE_RESULTS.COMMON_VEHICLESTATE_PREMATURELEAVE)
            self.vehicleState = state
            self.vehicleStatePrefix = state
        elif self.deathReason > DEATH_REASON_ALIVE:
            if self.killerID:
                reason = style.makeI18nDeathReason(self.deathReason)
                self.vehicleState = reason.i18nString
                self.vehicleStatePrefix = reason.prefix
                self.vehicleStateSuffix = reason.suffix
                block = personal.KillerPlayerNameBlock()
                block.setPlayerInfo(reusable.getPlayerInfoByVehicleID(self.killerID))
                self.addComponent(self.getNextComponentIndex(), block)
        else:
            self.vehicleState = i18n.makeString(BATTLE_RESULTS.COMMON_VEHICLESTATE_ALIVE)


class RankedBattlesVehicleStatsBlock(RegularVehicleStatsBlock):
    __slots__ = ('rank', 'rankIcon')

    def setRecord(self, result, reusable):
        super(RankedBattlesVehicleStatsBlock, self).setRecord(result, reusable)
        player = result.player
        avatar = reusable.avatars.getAvatarInfo(player.dbID)
        prevRank = avatar.prevAccRank
        self.rankIcon = style.makeRankIcon(prevRank)
        self.rank = prevRank


class RegularVehicleStatValuesBlock(base.StatsBlock):
    """Block contains detailed statistics of vehicle that are shown in separate view
    when player click to some vehicle in team list."""
    __slots__ = ('_isPersonal', 'shots', 'hits', 'explosionHits', 'damageDealt', 'sniperDamageDealt', 'directHitsReceived', 'piercingsReceived', 'noDamageDirectHitsReceived', 'explosionHitsReceived', 'damageBlockedByArmor', 'teamHitsDamage', 'spotted', 'damagedKilled', 'damageAssisted', 'damageAssistedStun', 'stunNum', 'capturePoints', 'mileage', '__rawDamageAssistedStun', '__rawStunNum')
    lobbyContext = dependency.descriptor(ILobbyContext)

    def setPersonal(self, flag):
        self._isPersonal = flag

    def setRecord(self, result, reusable):
        """Sets record of battle results to fetch required data.
        :param result: instance of VehicleDetailedInfo or VehicleSummarizeInfo
        :param reusable: instance of _ReusableInfo.
        """
        self.__rawDamageAssistedStun = result.damageAssistedStun
        self.__rawStunNum = result.stunNum
        self.shots = style.getIntegralFormatIfNoEmpty(result.shots)
        self.hits = (result.directHits, result.piercings)
        self.explosionHits = style.getIntegralFormatIfNoEmpty(result.explosionHits)
        self.damageDealt = style.getIntegralFormatIfNoEmpty(result.damageDealt)
        self.sniperDamageDealt = style.getIntegralFormatIfNoEmpty(result.sniperDamageDealt)
        self.directHitsReceived = style.getIntegralFormatIfNoEmpty(result.directHitsReceived)
        self.piercingsReceived = style.getIntegralFormatIfNoEmpty(result.piercingsReceived)
        self.noDamageDirectHitsReceived = style.getIntegralFormatIfNoEmpty(result.noDamageDirectHitsReceived)
        self.explosionHitsReceived = style.getIntegralFormatIfNoEmpty(result.explosionHitsReceived)
        self.damageBlockedByArmor = style.getIntegralFormatIfNoEmpty(result.damageBlockedByArmor)
        self.teamHitsDamage = (result.tkills, result.tdamageDealt)
        self.spotted = style.getIntegralFormatIfNoEmpty(result.spotted)
        self.damagedKilled = (result.damaged, result.kills)
        self.damageAssisted = style.getIntegralFormatIfNoEmpty(result.damageAssisted)
        self.damageAssistedStun = style.getIntegralFormatIfNoEmpty(result.damageAssistedStun)
        self.stunNum = style.getIntegralFormatIfNoEmpty(result.stunNum)
        self.capturePoints = (result.capturePoints, result.droppedCapturePoints)
        self.mileage = result.mileage

    def getVO(self):
        vo = []
        isStunEnabled = self.lobbyContext.getServerSettings().spgRedesignFeatures.isStunEnabled()
        for component in self._components:
            field = component.getField()
            showStunNum = False
            if isStunEnabled:
                showStunNum = self.__rawStunNum > 0
            if showStunNum and field == 'stunNum' or showStunNum and field == 'damageAssistedStun' or field not in _STAT_STUN_FIELD_NAMES:
                value = component.getVO()
                if self._isPersonal and field in _STAT_VALUES_VO_REPLACER:
                    field = _STAT_VALUES_VO_REPLACER[field]
                vo.append(style.makeStatValue(field, value))

        return vo


class AllRegularVehicleStatValuesBlock(base.StatsBlock):
    __slots__ = ()

    def setRecord(self, result, reusable):
        isPersonal, iterator = result
        add = self.addNextComponent
        for vehicle in iterator:
            block = RegularVehicleStatValuesBlock()
            block.setPersonal(isPersonal)
            block.setRecord(vehicle, reusable)
            add(block)


class PersonalVehiclesRegularStatsBlock(base.StatsBlock):
    __slots__ = ()

    def setRecord(self, result, reusable):
        info = reusable.getPersonalVehiclesInfo(result)
        add = self.addNextComponent
        for data in info.getVehiclesIterator():
            block = RegularVehicleStatValuesBlock()
            block.setPersonal(True)
            block.setRecord(data, reusable)
            add(block)


class TeamStatsBlock(base.StatsBlock):
    __slots__ = ('__class',)

    def __init__(self, class_, meta=None, field='', *path):
        super(TeamStatsBlock, self).__init__(meta, field, *path)
        self.__class = class_

    def setRecord(self, result, reusable):
        personalInfo = reusable.getPlayerInfo()
        personalDBID = personalInfo.dbID
        if personalInfo.squadIndex:
            personalPrebattleID = personalInfo.prebattleID
        else:
            personalPrebattleID = 0
        for idx, item in enumerate(result):
            if item.vehicle is not None and item.vehicle.isObserver:
                continue
            player = item.player
            isPersonal = player.dbID == personalDBID
            block = self.__class()
            block.vehicleSort = idx
            block.isPersonal = isPersonal
            block.isPersonalSquad = personalPrebattleID != 0 and personalPrebattleID == player.prebattleID
            block.setRecord(item, reusable)
            self.addComponent(self.getNextComponentIndex(), block)

        return


class RegularTeamStatsBlock(TeamStatsBlock):
    __slots__ = ()

    def __init__(self, meta=None, field='', *path):
        super(RegularTeamStatsBlock, self).__init__(RegularVehicleStatsBlock, meta, field, *path)


class RankedBattlesTeamStatsBlock(TeamStatsBlock):
    __slots__ = ()

    def __init__(self, meta=None, field='', *path):
        super(RankedBattlesTeamStatsBlock, self).__init__(RankedBattlesVehicleStatsBlock, meta, field, *path)


class TwoTeamsStatsBlock(shared.BiDiStatsBlock):
    __slots__ = ()

    def addComponent(self, index, component):
        super(TwoTeamsStatsBlock, self).addComponent(index, component)
        assert isinstance(component, TeamStatsBlock), 'Component must be extended class TeamStatsBlock'

    def setRecord(self, result, reusable):
        allies, enemies = reusable.getBiDirectionTeamsIterator(result)
        self.left.setRecord(allies, reusable)
        self.right.setRecord(enemies, reusable)


class RankedResultsTeamStatsBlock(shared.BiDiStatsBlock):
    """
    This block is used in external RankedBattlesBattleResults view. Not in the regular Battle results window
    """
    __slots__ = ()

    def setRecord(self, result, reusable):
        allies, enemies = reusable.getBiDirectionTeamsIterator(result, sort_keys.VehicleXpSortKey)
        self.left.setRecord(allies, reusable)
        self.right.setRecord(enemies, reusable)


class RankedResultsTeamDataStatsBlock(base.StatsBlock):
    """Block contains one Team data to show in team list for RankedBattlesBattleResults."""
    __slots__ = ('title', 'firstListData', 'secondListData', 'firstBackgroundType', 'secondBackgroundType', 'firstBackgroundBlink', 'secondBackgroundBlink', 'titleAlpha')
    _TEAM_MEMBERS_NUMBER = 15

    def setRecord(self, result, reusable):
        helper = common.RankInfoHelper(reusable)
        winTeam = reusable.common.winnerTeam
        teamId = None
        topBound = helper.getLoserTopBound()
        xpAtBorder = 0
        self.firstListData = []
        self.secondListData = []
        personalDBID = reusable.personal.avatar.accountDBID
        self.firstBackgroundBlink = False
        self.secondBackgroundBlink = False
        for idx, item in enumerate(result):
            if teamId is None:
                teamId = item.player.team
                topBound = helper.getTopBoundForTeam(teamId)
            if idx < topBound:
                dataList = self.firstListData
                standoff = False
                xpAtBorder = item.xp
                if not self.firstBackgroundBlink and item.player.dbID == personalDBID:
                    self.firstBackgroundBlink = True
            else:
                dataList = self.secondListData
                standoff = item.xp == xpAtBorder
                if not self.secondBackgroundBlink and item.player.dbID == personalDBID and not standoff:
                    self.secondBackgroundBlink = True
            listItem = RankedResultsListItemStatsBlock()
            listItem.setRecord((item, standoff), reusable)
            dataList.append(listItem.getVO())

        self.__fillIncompleteTeam(topBound)
        if winTeam == teamId:
            self.title = text_styles.highTitle(RANKED_BATTLES.BATTLERESULT_WINNERS)
            self.firstBackgroundType = RANKEDBATTLES_ALIASES.BACKGROUND_STATE_TOP12
            self.secondBackgroundType = RANKEDBATTLES_ALIASES.BACKGROUND_STATE_NOTEFFECTIVE
            self.titleAlpha = 1.0
        else:
            self.title = text_styles.highTitle(RANKED_BATTLES.BATTLERESULT_LOSERS)
            self.firstBackgroundType = RANKEDBATTLES_ALIASES.BACKGROUND_STATE_TOP3
            self.secondBackgroundType = RANKEDBATTLES_ALIASES.BACKGROUND_STATE_LOSE12
            self.titleAlpha = 0.6
        return

    def __fillIncompleteTeam(self, topBound):
        """
        This method is necessary for development needs.
        Both teams should be normally 15vs15, but in development case the number can be less.
        We should fill with empty data to show layout correctly.
        """
        membersNumber = len(self.firstListData) + len(self.secondListData)
        for idx in range(membersNumber, RankedResultsTeamDataStatsBlock._TEAM_MEMBERS_NUMBER):
            dataList = self.firstListData if idx < topBound else self.secondListData
            dataList.append(RankedResultsListItemStatsBlock().getVO())


class RankedResultsListItemStatsBlock(base.StatsBlock):
    """Block contains one Item data to show in 'firstListData' or 'secondListData'."""
    __slots__ = ('nickName', 'points', 'selected', 'standoff')

    def setRecord(self, result, reusable):
        item, standoff = result
        self.nickName = style.makeRankedNickNameValue(item.player.name)
        self.points = style.makeRankedPointValue(item.xp)
        self.selected = item.player.dbID == reusable.personal.avatar.accountDBID
        self.standoff = standoff
