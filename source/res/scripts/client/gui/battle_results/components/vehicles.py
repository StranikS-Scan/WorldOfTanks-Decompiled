# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_results/components/vehicles.py
import typing
from constants import DEATH_REASON_ALIVE
from epic_constants import EPIC_BATTLE_TEAM_ID
from gui.Scaleform.genConsts.RANKEDBATTLES_ALIASES import RANKEDBATTLES_ALIASES
from gui.Scaleform.locale.BATTLE_RESULTS import BATTLE_RESULTS
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.settings import ICONS_SIZES
from gui.battle_results.components import base, shared, style, ranked
from gui.battle_results.components.base import PropertyValue
from gui.battle_results.components.personal import fillKillerInfoBlock, NO_OWNER_DEATH_REASON_IDS
from gui.battle_results.reusable import sort_keys
from gui.battle_results.reusable.avatars import AvatarInfo
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.formatters import text_styles
from gui.shared.gui_items.Vehicle import getSmallIconPath, getIconPath
from helpers import dependency, i18n
from messenger.m_constants import USER_TAG
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.game_control import IRankedBattlesController
from skeletons.gui.lobby_context import ILobbyContext
from items import vehicles
from gui.battle_results.reusable.shared import VehicleSummarizeInfo
if typing.TYPE_CHECKING:
    from gui.battle_results.reusable.shared import VehicleDetailedInfo
_STAT_STUN_FIELD_NAMES = ('damageAssistedStun', 'stunNum', 'stunDuration')

def _getStunFilter():
    lobbyContext = dependency.instance(ILobbyContext)
    filters = ()
    if not lobbyContext.getServerSettings().spgRedesignFeatures.isStunEnabled():
        filters += _STAT_STUN_FIELD_NAMES
    return filters


class FieldsReplacer(object):
    _STAT_VALUES_VO_REPLACER = {'damageAssisted': 'damageAssistedSelf',
     'damageAssistedStun': 'damageAssistedStunSelf'}

    def __init__(self, result, isPersonal):
        self.replacerFields = {}
        if isPersonal:
            self.replacerFields.update(self._STAT_VALUES_VO_REPLACER)
        isWithFlamethrower = isinstance(result, VehicleSummarizeInfo) and any((data.vehicle is not None and vehicles.isFlamethrower(data.vehicle.intCD) for data in result.vehicles))
        if isWithFlamethrower or result.vehicle is not None and vehicles.isFlamethrower(result.vehicle.intCD):
            self.replacerFields['explosionHits'] = 'flameExplosionHits'
        return

    def __contains__(self, key):
        return key in self.replacerFields

    def __getitem__(self, key):
        return self.replacerFields[key]

    def __eq__(self, cmpDict):
        return self.replacerFields == cmpDict


class TeamPlayerNameBlock(shared.PlayerNameBlock):
    __slots__ = ('igrType',)

    def setPlayerInfo(self, playerInfo):
        super(TeamPlayerNameBlock, self).setPlayerInfo(playerInfo)
        self.igrType = playerInfo.igrType

    def setRecord(self, result, reusable):
        self.setPlayerInfo(result)


class RegularVehicleStatsBlock(base.StatsBlock):
    __slots__ = ('_isObserver', 'achievements', 'achievementsCount', 'vehicleState', 'vehicleStatePrefix', 'vehicleStateSuffix', 'killerID', 'deathReason', 'isPrematureLeave', 'vehicleName', 'vehicleShortName', 'vehicleIcon', 'vehicleSort', 'isPersonal', 'isTeamKiller', 'kills', 'tkills', 'realKills', 'xp', 'damageDealt', 'vehicles', 'playerID', 'player', 'statValues', 'fortResource', 'squadIndex', 'isPersonalSquad', 'xpSort', 'intCD', 'rank', 'rankIcon', 'suffixBadgeIcon', 'isKilledByTeamKiller', 'playerRank', 'respawns', 'badge', 'hasSelectedBadge', 'suffixBadgeStripIcon')

    def __init__(self, meta=None, field='', *path):
        super(RegularVehicleStatsBlock, self).__init__(meta, field, *path)
        self._isObserver = False
        self.isPersonal = None
        self.isPersonalSquad = None
        self.isTeamKiller = False
        self.isKilledByTeamKiller = False
        self.vehicleSort = None
        self.suffixBadgeIcon = None
        self.suffixBadgeStripIcon = None
        self.hasSelectedBadge = False
        return

    def setRecord(self, result, reusable):
        player = result.player
        avatar = reusable.avatars.getAvatarInfo(player.dbID)
        noPenalties = not avatar.hasPenalties()
        self.suffixBadgeIcon = None
        self.suffixBadgeStripIcon = None
        if avatar is not None:
            self.hasSelectedBadge = avatar.badge > 0
            if self.hasSelectedBadge:
                self._setBadge(result, reusable)
            if avatar.suffixBadge:
                self.suffixBadgeIcon = style.makeBadgeIcon(avatar.suffixBadge)
                stripImg = R.images.gui.maps.icons.library.badges.strips.c_64x24.dyn('strip_{}'.format(avatar.suffixBadge))
                self.suffixBadgeStripIcon = backport.image(stripImg()) if stripImg else ''
        self._processVehicles(result)
        self._setPlayerInfo(player)
        self._setTotalStats(result, noPenalties)
        self._setVehiclesStats(result, reusable)
        if not self.isPersonal or noPenalties:
            self._setAchievements(result, reusable)
        if not self._isObserver:
            self._setVehicleState(result, reusable)
        return

    def _setBadge(self, result, reusable):
        self.badge = PropertyValue(result, reusable)

    def _processVehicles(self, result):
        self._setVehicleInfo(result.vehicle)

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

    def _setVehiclesStats(self, result, reusable):
        self.statValues = ((self.isPersonal, result.getVehiclesIterator()), reusable)

    def _setAchievements(self, result, reusable):
        achievements = result.getAchievements()
        self.achievementsCount = len(achievements)
        self.achievements = PropertyValue(achievements, reusable)

    def _setVehicleState(self, result, reusable):
        if self._isObserver:
            return
        self.killerID = result.killerID
        self.deathReason = result.deathReason
        if self.isPersonal and reusable.personal.avatar.isPrematureLeave:
            state = backport.text(R.strings.battle_results.common.vehicleState.prematureLeave())
            self.vehicleState = state
            self.vehicleStatePrefix = state
        elif self.deathReason > DEATH_REASON_ALIVE:
            if self.killerID:
                fillKillerInfoBlock(self, self.deathReason, self.killerID, reusable, result)
            elif self.deathReason in NO_OWNER_DEATH_REASON_IDS:
                state = backport.text(R.strings.battle_results.common.vehicleState.dyn('dead{}'.format(self.deathReason), R.invalid)())
                self.vehicleState = state
        else:
            self.vehicleState = backport.text(R.strings.battle_results.common.vehicleState.alive())
        self.isTeamKiller = result.isTeamKiller


class RankedBattlesVehicleStatsBlock(RegularVehicleStatsBlock):
    __slots__ = ('rank', 'rankIcon')
    __rankedController = dependency.descriptor(IRankedBattlesController)

    def __init__(self, meta=None, field='', *path):
        super(RankedBattlesVehicleStatsBlock, self).__init__(meta, field, *path)
        self.rankIcon = None
        self.rank = 0
        return

    def setRecord(self, result, reusable):
        super(RankedBattlesVehicleStatsBlock, self).setRecord(result, reusable)
        player = result.player
        avatar = reusable.avatars.getAvatarInfo(player.dbID)
        prevRank = avatar.prevAccRank
        self.rankIcon = self.__makeRankIcon(prevRank)
        self.rank = prevRank

    def _setTotalStats(self, result, noPenalties):
        super(RankedBattlesVehicleStatsBlock, self)._setTotalStats(result, noPenalties)
        if noPenalties:
            self.xp = result.xp - result.xpPenalty
            self.xpSort = result.xp - result.xpPenalty

    def __makeRankIcon(self, rankID):
        displayInfo = self.__rankedController.getRankDisplayInfoForBattle(rankID)
        return backport.image(R.images.gui.maps.icons.rankedBattles.ranks.c_24x24.dyn('ranks_group{}_{}'.format(displayInfo.division, displayInfo.level))()) if displayInfo.isGroup else backport.image(R.images.gui.maps.icons.rankedBattles.ranks.c_24x24.dyn('rank{}_{}'.format(displayInfo.division, displayInfo.level))())


class EpicVehicleStatsBlock(RegularVehicleStatsBlock):
    __slots__ = ('playerRank', 'respawns', '__allAdded')

    def __init__(self, meta=None, field='', *path):
        super(EpicVehicleStatsBlock, self).__init__(meta, field, *path)
        self.vehicles = []
        self.__allAdded = False

    def _processVehicles(self, result):
        for vehicleInfo in result.vehicles:
            self._setVehicleInfo(vehicleInfo.vehicle)

    def _setVehicleInfo(self, vehicle):
        self.vehicles.append({'icon': getIconPath(vehicle.name),
         'label': vehicle.shortUserName})

    def setRecord(self, result, reusable):
        super(EpicVehicleStatsBlock, self).setRecord(result, reusable)
        self.playerRank = 0
        avatar = reusable.avatars.getAvatarInfo(result.player.dbID)
        extensionInfo = avatar.extensionInfo
        if extensionInfo is not None and 'playerRank' in extensionInfo:
            self.playerRank = extensionInfo['playerRank']
        self.respawns = result.respawns
        return

    def getVO(self):
        if len(self.vehicles) > 1 and not self.__allAdded:
            self.vehicles.insert(0, {'label': i18n.makeString(BATTLE_RESULTS.ALLVEHICLES),
             'icon': RES_ICONS.MAPS_ICONS_LIBRARY_EPICVEHICLESALL})
            self.__allAdded = True
        return super(EpicVehicleStatsBlock, self).getVO()


class StrongholdVehicleStatsBlock(RegularVehicleStatsBlock):
    pass


class RegularVehicleStatValuesBlock(base.StatsBlock):
    __slots__ = ('_isPersonal', '_filters', 'shots', 'hits', 'explosionHits', 'damageDealt', 'sniperDamageDealt', 'directHitsReceived', 'piercingsReceived', 'noDamageDirectHitsReceived', 'explosionHitsReceived', 'damageBlockedByArmor', 'teamHitsDamage', 'spotted', 'damagedKilled', 'damageAssisted', 'damageAssistedStun', 'stunNum', 'stunDuration', 'capturePoints', 'mileage', '__rawDamageAssistedStun', '__rawStunNum', '__fieldsReplacer')
    lobbyContext = dependency.descriptor(ILobbyContext)

    def __init__(self, meta=None, field='', *path):
        super(RegularVehicleStatValuesBlock, self).__init__(meta, field, *path)
        self._filters = set()
        self.__fieldsReplacer = None
        return

    def setPersonal(self, flag):
        self._isPersonal = flag

    def addFilters(self, filters):
        self._filters.update(filters)

    def setRecord(self, result, reusable):
        self.__rawDamageAssistedStun = result.damageAssistedStun
        self.__rawStunNum = result.stunNum
        self.__fieldsReplacer = FieldsReplacer(result, self._isPersonal)
        if self.__rawStunNum == 0:
            self.addFilters(_STAT_STUN_FIELD_NAMES)
        self.shots = style.getIntegralFormatIfNoEmpty(result.shots)
        self.hits = (result.directEnemyHits, result.piercingEnemyHits)
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
        self.stunDuration = style.getFractionalFormatIfNoEmpty(result.stunDuration)
        self.capturePoints = (result.capturePoints, result.droppedCapturePoints)
        self.mileage = result.mileage

    def getVO(self):
        vo = []
        for component in self._components:
            field = component.getField()
            if field in list(self._filters):
                continue
            value = component.getVO()
            if field in self.__fieldsReplacer:
                field = self.__fieldsReplacer[field]
            vo.append(style.makeStatValue(field, value))

        return vo


class RankedVehicleStatValuesBlock(RegularVehicleStatValuesBlock):
    __slots__ = ('xp', 'xpForAttack', 'xpForAssist', 'xpOther')

    def setRecord(self, result, reusable):
        super(RankedVehicleStatValuesBlock, self).setRecord(result, reusable)
        self.xp = result.xp - result.xpPenalty
        self.xpForAttack = result.xpForAttack - result.xpPenalty
        self.xpForAssist = result.xpForAssist
        self.xpOther = result.xpOther


class StrongholdVehicleStatValuesBlock(RegularVehicleStatValuesBlock):
    __slots__ = ('artilleryFortEquipDamageDealt',)

    def setRecord(self, result, reusable):
        super(StrongholdVehicleStatValuesBlock, self).setRecord(result, reusable)
        self.artilleryFortEquipDamageDealt = style.getIntegralFormatIfNoEmpty(result.artilleryFortEquipDamageDealt)
        if result.artilleryFortEquipDamageDealt == 0:
            self.addFilters(('artilleryFortEquipDamageDealt',))


class EpicVehicleStatValuesBlock(base.StatsBlock):
    __slots__ = ('_team', '_isPersonal', '_filters', 'shots', 'hits', 'explosionHits', 'damageDealt', 'sniperDamageDealt', 'destructiblesDamageDealt', 'equipmentDamageDealt', 'directHitsReceived', 'piercingsReceived', 'noDamageDirectHitsReceived', 'explosionHitsReceived', 'damageBlockedByArmor', 'teamHitsDamage', 'spotted', 'damagedKilled', 'damageAssisted', 'equipmentDamageAssisted', 'damageAssistedStun', 'stunNum', 'capturePoints', 'timesDestroyed', 'teamSpecificStat', '__rawDamageAssistedStun', '__rawStunNum', '__fieldsReplacer')

    def __init__(self, meta=None, field='', *path):
        super(EpicVehicleStatValuesBlock, self).__init__(meta, field, *path)
        self._filters = set()
        self.__fieldsReplacer = None
        return

    def setPersonal(self, flag):
        self._isPersonal = flag

    def addFilters(self, filters):
        self._filters.update(filters)

    def setRecord(self, result, reusable):
        self.timesDestroyed = str(result.deathCount)
        self._team = result.player.team
        self.__fieldsReplacer = FieldsReplacer(result, self._isPersonal)
        if self._team == EPIC_BATTLE_TEAM_ID.TEAM_ATTACKER:
            self.teamSpecificStat = '{0}/{1}'.format(result.numCaptured, result.numDestroyed)
        else:
            numDestructiblesDefended = reusable.common.numDefended
            self.teamSpecificStat = '{0}/{1}'.format(result.numDefended, numDestructiblesDefended)
        self.__rawDamageAssistedStun = result.damageAssistedStun
        self.__rawStunNum = result.stunNum
        if self.__rawStunNum == 0:
            self.addFilters(_STAT_STUN_FIELD_NAMES)
        self.shots = style.getIntegralFormatIfNoEmpty(result.shots)
        self.hits = (result.directEnemyHits, result.piercingEnemyHits)
        self.explosionHits = style.getIntegralFormatIfNoEmpty(result.explosionHits)
        self.damageDealt = style.getIntegralFormatIfNoEmpty(result.damageDealt)
        self.sniperDamageDealt = style.getIntegralFormatIfNoEmpty(result.sniperDamageDealt)
        self.destructiblesDamageDealt = style.getIntegralFormatIfNoEmpty(result.destructiblesDamageDealt)
        self.equipmentDamageDealt = style.getIntegralFormatIfNoEmpty(result.equipmentDamageDealt)
        self.directHitsReceived = style.getIntegralFormatIfNoEmpty(result.directHitsReceived)
        self.piercingsReceived = style.getIntegralFormatIfNoEmpty(result.piercingsReceived)
        self.noDamageDirectHitsReceived = style.getIntegralFormatIfNoEmpty(result.noDamageDirectHitsReceived)
        self.explosionHitsReceived = style.getIntegralFormatIfNoEmpty(result.explosionHitsReceived)
        self.damageBlockedByArmor = style.getIntegralFormatIfNoEmpty(result.damageBlockedByArmor)
        self.teamHitsDamage = (result.tkills, result.tdamageDealt)
        self.spotted = style.getIntegralFormatIfNoEmpty(result.spotted)
        self.damagedKilled = (result.damaged, result.kills)
        self.damageAssisted = style.getIntegralFormatIfNoEmpty(result.damageAssisted)
        self.equipmentDamageAssisted = style.getIntegralFormatIfNoEmpty(result.equipmentDamageAssisted)
        self.damageAssistedStun = style.getIntegralFormatIfNoEmpty(result.damageAssistedStun)
        self.stunNum = style.getIntegralFormatIfNoEmpty(result.stunNum)
        self.capturePoints = (result.capturePoints, result.droppedCapturePoints)

    def getVO(self):
        vo = []
        _TEAM_SPECIFIC_STAT_REPLACE = {EPIC_BATTLE_TEAM_ID.TEAM_ATTACKER: 'atkObjectives',
         EPIC_BATTLE_TEAM_ID.TEAM_DEFENDER: 'defObjectives'}
        for component in self._components:
            field = component.getField()
            if field in self._filters:
                continue
            if field == 'teamSpecificStat':
                field = _TEAM_SPECIFIC_STAT_REPLACE[self._team]
            value = component.getVO()
            if field in self.__fieldsReplacer:
                field = self.__fieldsReplacer[field]
            vo.append(style.makeStatValue(field, value))

        return vo


class AllRegularVehicleStatValuesBlock(base.StatsBlock):
    __slots__ = ()

    def setRecord(self, result, reusable):
        isPersonal, iterator = result
        add = self.addNextComponent
        stunFilter = _getStunFilter()
        for vehicle in iterator:
            block = RegularVehicleStatValuesBlock()
            block.setPersonal(isPersonal)
            block.addFilters(stunFilter)
            block.setRecord(vehicle, reusable)
            add(block)


class AllRankedVehicleStatValuesBlock(base.StatsBlock):
    __slots__ = ()

    def setRecord(self, result, reusable):
        isPersonal, iterator = result
        add = self.addNextComponent
        stunFilter = _getStunFilter()
        for vehicle in iterator:
            block = RankedVehicleStatValuesBlock()
            block.setPersonal(isPersonal)
            block.addFilters(stunFilter)
            block.setRecord(vehicle, reusable)
            add(block)


class AllEpicVehicleStatValuesBlock(base.StatsBlock):
    __slots__ = ()

    def setRecord(self, result, reusable):
        isPersonal, iterator = result
        add = self.addNextComponent
        stunFilter = _getStunFilter()
        for vehicle in iterator:
            block = EpicVehicleStatValuesBlock()
            block.setPersonal(isPersonal)
            block.addFilters(stunFilter)
            block.setRecord(vehicle, reusable)
            add(block)


class AllStrongholdVehicleStatValuesBlock(base.StatsBlock):
    __slots__ = ()

    def setRecord(self, result, reusable):
        isPersonal, iterator = result
        add = self.addNextComponent
        stunFilter = _getStunFilter()
        for vehicle in iterator:
            block = StrongholdVehicleStatValuesBlock()
            block.setPersonal(isPersonal)
            block.addFilters(stunFilter)
            block.setRecord(vehicle, reusable)
            add(block)


class PersonalVehiclesRegularStatsBlock(base.StatsBlock):
    __slots__ = ()

    def setRecord(self, result, reusable):
        info = reusable.getPersonalVehiclesInfo(result)
        add = self.addNextComponent
        stunFilter = _getStunFilter()
        for data in info.getVehiclesIterator():
            block = RegularVehicleStatValuesBlock()
            block.setPersonal(True)
            block.addFilters(stunFilter)
            block.setRecord(data, reusable)
            add(block)


class PersonalVehiclesRankedStatsBlock(base.StatsBlock):
    __slots__ = ()

    def setRecord(self, result, reusable):
        info = reusable.getPersonalVehiclesInfo(result)
        add = self.addNextComponent
        stunFilter = _getStunFilter()
        for data in info.getVehiclesIterator():
            block = RankedVehicleStatValuesBlock()
            block.setPersonal(True)
            block.addFilters(stunFilter)
            block.setRecord(data, reusable)
            add(block)


class PersonalVehiclesEpicStatsBlock(base.StatsBlock):
    __slots__ = ()

    def setRecord(self, result, reusable):
        info = reusable.getPersonalVehiclesInfo(result)
        add = self.addNextComponent
        stunFilter = _getStunFilter()
        for data in info.getVehiclesIterator():
            block = EpicVehicleStatValuesBlock()
            block.setPersonal(True)
            block.addFilters(stunFilter)
            block.setRecord(data, reusable)
            add(block)


class PersonalVehiclesStrongholdStatsBlock(base.StatsBlock):
    __slots__ = ()

    def setRecord(self, result, reusable):
        info = reusable.getPersonalVehiclesInfo(result)
        add = self.addNextComponent
        stunFilter = _getStunFilter()
        for data in info.getVehiclesIterator():
            block = StrongholdVehicleStatValuesBlock()
            block.setPersonal(True)
            block.addFilters(stunFilter)
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
            if isPersonal:
                player.addTag(USER_TAG.CURRENT)
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


class EpicTeamStatsBlock(TeamStatsBlock):
    __slots__ = ()

    def __init__(self, meta=None, field='', *path):
        super(EpicTeamStatsBlock, self).__init__(EpicVehicleStatsBlock, meta, field, *path)


class StrongholdTeamStatsBlock(TeamStatsBlock):
    __slots__ = ()

    def __init__(self, meta=None, field='', *path):
        super(StrongholdTeamStatsBlock, self).__init__(StrongholdVehicleStatsBlock, meta, field, *path)


class TwoTeamsStatsBlock(shared.BiDiStatsBlock):
    __slots__ = ()

    def addComponent(self, index, component):
        super(TwoTeamsStatsBlock, self).addComponent(index, component)

    def setRecord(self, result, reusable):
        allies, enemies = reusable.getBiDirectionTeamsIterator(result)
        self.left.setRecord(allies, reusable)
        self.right.setRecord(enemies, reusable)


class RankedResultsTeamStatsBlock(shared.BiDiStatsBlock):
    __slots__ = ()

    def setRecord(self, result, reusable):
        allies, enemies = reusable.getBiDirectionTeamsIterator(result, sort_keys.RankedVehicleXpSortKey)
        self.left.setRecord(allies, reusable)
        self.right.setRecord(enemies, reusable)


class RankedResultsTeamDataStatsBlock(base.StatsBlock):
    __slots__ = ('title', 'titleAlpha', 'teamList')

    def setRecord(self, result, reusable):
        helper = ranked.RankedResultsInfoHelper(reusable)
        winTeam = reusable.common.winnerTeam
        playerTeam = reusable.personal.avatar.team
        lists = []
        listsSteps = []
        isWon = False
        personalDBID = reusable.personal.avatar.accountDBID
        topListBlink = False
        playerCount = 0
        lastXP = 0
        lastListIdx = 0
        for idx, item in enumerate(result):
            isPlayer = item.player.dbID == personalDBID
            if playerCount == 0:
                isWon = self.__getIsWinTeam(currentTeam=item.player.team, winTeam=winTeam, playerTeam=playerTeam)
                lists, listsSteps = self.__createListsAndSteps(listsData=helper.getListsData(isLoser=not isWon))
            listIdx = self.__getPlayerListIndex(playerIndex=idx, listsSteps=listsSteps)
            if lastListIdx != listIdx:
                currXP = item.xp - item.xpPenalty
                if currXP == lastXP:
                    listIdx = lastListIdx
                else:
                    lastXP = currXP
                    lastListIdx = listIdx
            else:
                lastXP = item.xp - item.xpPenalty
            dataList = lists[listIdx]
            isTopList = dataList.isTopList()
            if isPlayer and isTopList and not topListBlink:
                topListBlink = True
                dataList.setListBlink(True)
            listItem = RankedResultsListItemStatsBlock()
            listItem.setRecord((item, RANKEDBATTLES_ALIASES.STANDOFF_INVISIBLE), reusable)
            dataList.appendPlayer(listItem.getVO())
            playerCount += 1

        if playerCount == 0:
            if not winTeam:
                isWon = False
            else:
                isWon = playerTeam != winTeam
            lists, listsSteps = self.__createListsAndSteps(listsData=helper.getListsData(isLoser=not isWon))
        self.__fillIncompleteTeam(playerCount, helper.getPlayersNumber(), lists, listsSteps)
        lists[:] = [ item for item in lists if item.validateList().capacity > 0 ]
        if isWon:
            self.title = text_styles.highTitle(backport.text(R.strings.ranked_battles.battleResult.winners()))
            self.titleAlpha = 1.0
        else:
            self.title = text_styles.highTitle(backport.text(R.strings.ranked_battles.battleResult.losers()))
            self.titleAlpha = 0.6
        self.teamList = []
        for listOfPlayers in lists:
            if listOfPlayers.getPlayersNumber() > 0:
                self.teamList.append(listOfPlayers.getVO())

    def __getIsWinTeam(self, currentTeam, playerTeam, winTeam):
        if not winTeam:
            isWon = False
        else:
            isPlayerTeam = playerTeam == currentTeam
            if isPlayerTeam:
                isWon = winTeam == playerTeam
            else:
                isWon = winTeam != playerTeam
        return isWon

    @staticmethod
    def __fillIncompleteTeam(membersCount, maxCount, lists, listsSteps):
        for idx in range(membersCount, maxCount):
            listIndex = RankedResultsTeamDataStatsBlock.__getPlayerListIndex(playerIndex=idx, listsSteps=listsSteps)
            dataList = lists[listIndex]
            dataList.appendPlayer(RankedResultsListItemStatsBlock().getVO())

    @staticmethod
    def __getPlayerListIndex(playerIndex, listsSteps):
        indx = 0
        for indx, value in enumerate(listsSteps):
            if playerIndex < value:
                return indx

        return indx

    @staticmethod
    def __createListsAndSteps(listsData):
        lists = []
        count = len(listsData)
        i = 0
        listsSteps = []
        step = 0
        while i < count:
            listBlock = RankedResultsTeamPartDataStatsBlock()
            listBlock.setListResources(listsData[i], i == 0)
            lists.append(listBlock)
            step += listBlock.getListCapacity()
            listsSteps.append(step)
            i += 1

        return (lists, listsSteps)


class RankedResultsTeamPartDataStatsBlock(base.StatsBlock):
    __slots__ = ('listData', 'backgroundType', 'backgroundBlink', 'icon', 'capacity', 'isColorBlind', 'iconType', 'iconMethod')
    settingsCore = dependency.descriptor(ISettingsCore)

    def __init__(self, meta=None, field='', *path):
        super(RankedResultsTeamPartDataStatsBlock, self).__init__(meta, field, *path)
        self.listData = []
        self.backgroundType = ''
        self.backgroundBlink = False
        self.icon = ''
        self.iconType = ''
        self.capacity = 0
        self.isColorBlind = False
        self.iconMethod = None
        return

    def appendPlayer(self, playerItem):
        self.listData.append(playerItem)

    def getPlayersNumber(self):
        return len(self.listData)

    def setListResources(self, listInfo, isTopList=False):
        self.capacity, resources = listInfo
        self.iconType, self.backgroundType, self.iconMethod = resources
        self.icon = ''
        if isTopList:
            self.icon = self.iconMethod(self.capacity)
        if self.backgroundType == RANKEDBATTLES_ALIASES.BACKGROUND_STATE_LOSE:
            self.isColorBlind = self.settingsCore.getSetting('isColorBlind')

    def setListBlink(self, isBlink):
        self.backgroundBlink = isBlink

    def getListCapacity(self):
        return self.capacity

    def isTopList(self):
        return not self.icon == ''

    def validateList(self):
        self.capacity = len(self.listData)
        if self.isTopList() and self.iconMethod:
            self.icon = self.iconMethod(self.capacity)
        return self


class RankedResultsListItemStatsBlock(base.StatsBlock):
    __slots__ = ('nickName', 'nickNameHuge', 'fakeName', 'fakeNameHuge', 'points', 'pointsHuge', 'selected', 'standoff', 'tags')
    settingsCore = dependency.descriptor(ISettingsCore)

    def setRecord(self, result, reusable):
        item, standoff = result
        self.nickName = style.makeRankedNickNameValue(item.player.realName)
        self.nickNameHuge = style.makeRankedNickNameHugeValue(item.player.realName)
        self.fakeName = style.makeRankedNickNameValue(item.player.fakeName)
        self.fakeNameHuge = style.makeRankedNickNameHugeValue(item.player.fakeName)
        self.points = style.makeRankedPointValue(item.xp - item.xpPenalty)
        self.pointsHuge = style.makeRankedPointHugeValue(item.xp - item.xpPenalty)
        self.selected = item.player.dbID == reusable.personal.avatar.accountDBID
        if self.settingsCore.getSetting('isColorBlind') and standoff == RANKEDBATTLES_ALIASES.STANDOFF_MINUS:
            standoff = RANKEDBATTLES_ALIASES.STANDOFF_MINUS_BLIND
        self.standoff = standoff
        self.tags = item.player.tags


class BadgeBlock(base.StatsBlock):
    __slots__ = ('icon', 'content', 'sizeContent', 'isDynamic', 'isAtlasSource')

    def __init__(self, meta=None, field='', *path):
        super(BadgeBlock, self).__init__(meta, field, *path)
        self.icon = ''
        self.content = ''
        self.sizeContent = ''
        self.isDynamic = False
        self.isAtlasSource = False

    def setRecord(self, result, reusable):
        player = result.player
        avatar = reusable.avatars.getAvatarInfo(player.dbID)
        badgeInfo = avatar.getFullBadgeInfo()
        if badgeInfo is not None:
            self.icon = badgeInfo.getThumbnailIcon()
            self.isDynamic = badgeInfo.hasDynamicContent()
            self.content = badgeInfo.getDynamicContent()
            self.sizeContent = ICONS_SIZES.X24
        return
