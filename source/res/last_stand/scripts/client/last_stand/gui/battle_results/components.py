# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/gui/battle_results/components.py
from constants import DEATH_REASON_ALIVE
from gui.battle_results.reusable import sort_keys
from gui.battle_results.components import base, common
from last_stand_common.last_stand_constants import INVALID_BATTLE_PLACE

class LSTimeItem(base.StatsItem):

    def _convert(self, record, reusable):
        return record if record else 0


class LSPrevBestMissionsCountItem(base.StatsItem):

    def _convert(self, result, reusable):
        return reusable.getPersonalVehiclesInfo(result).prevBestMissionsCount


class LSCompletedDifficultyMissions(base.StatsItem):

    def _convert(self, result, reusable):
        return reusable.getPersonalVehiclesInfo(result).completedDifficultyMissions


class LSPhaseItem(base.StatsItem):

    def _convert(self, result, reusable):
        return reusable.getPersonalVehiclesInfo(result).phase


class LSPhasesCountItem(base.StatsItem):

    def _convert(self, result, reusable):
        return reusable.getPersonalVehiclesInfo(result).phasesCount


class LSEffectivenessArtefactKeysItem(base.StatsItem):
    __slots__ = ()

    def _convert(self, result, reusable):
        return reusable.getPersonalVehiclesInfo(result).effectivenessKeys


class PersonalFirstTeamItemSortKey(sort_keys.TeamItemSortKey):
    __slots__ = ('_sortKey',)

    def __init__(self, vehicleInfo, compareKey):
        super(PersonalFirstTeamItemSortKey, self).__init__(vehicleInfo)
        self._sortKey = compareKey

    def _cmp(self, other):
        sortKey = self._sortKey
        return cmp(getattr(other.info, sortKey), getattr(self.info, sortKey))


class LSAfkSortKey(sort_keys.TeamItemSortKey):
    __slots__ = ()

    def _cmp(self, other):
        return cmp(self._isAfk(self.info), self._isAfk(other.info))

    @staticmethod
    def _isAfk(info):
        return getattr(info, 'teamFightPlace') == INVALID_BATTLE_PLACE


class LSVehicleStatsBlock(base.StatsBlock):
    __slots__ = ('playerDBID', 'playerName', 'vehicleName', 'vehicleType', 'vehicleCD', 'vehicleLvl', 'clanAbbrev', 'artefactKeys', 'isPlayer', 'squadID', 'isOwnSquad', 'killerName', 'deathReason', 'kills', 'damageDealt', 'badgeID', 'badgeSuffixID', 'respawnsCount', 'hasPenalties', 'vehicleShortName', 'vehicleIsIGR')

    def __init__(self, meta=None, field='', *path):
        super(LSVehicleStatsBlock, self).__init__(meta, field, *path)
        self.playerDBID = 0
        self.playerName = ''
        self.vehicleName = ''
        self.vehicleShortName = ''
        self.vehicleType = ''
        self.vehicleCD = 0
        self.vehicleLvl = -1
        self.clanAbbrev = ''
        self.artefactKeys = 0
        self.killerName = ''
        self.deathReason = -1
        self.kills = 0
        self.damageDealt = 0
        self.isPlayer = False
        self.squadID = -1
        self.isOwnSquad = False
        self.badgeID = 0
        self.badgeSuffixID = 0
        self.respawnsCount = 0
        self.hasPenalties = False
        self.vehicleIsIGR = False

    def setRecord(self, result, reusable):
        super(LSVehicleStatsBlock, self).setRecord(result, reusable)
        self.playerDBID = result.player.dbID
        self.playerName = result.player.realName
        self.vehicleName = result.vehicle.userName
        if result.vehicle.isPremiumIGR:
            self.vehicleShortName = result.vehicle.typeDescr.shortUserString
        else:
            self.vehicleShortName = result.vehicle.shortUserName
        self.vehicleIsIGR = result.vehicle.isPremiumIGR
        self.vehicleType = result.vehicle.type
        self.vehicleCD = result.vehicle.intCD
        self.vehicleLvl = result.vehicle.level
        self.clanAbbrev = result.player.clanAbbrev
        self.artefactKeys = result.totalKeys
        self.deathReason = result.deathReason
        self.kills = result.kills
        self.damageDealt = result.damageDealt
        self.isPlayer = self.playerDBID == reusable.personal.avatar.accountDBID
        self.squadID = result.player.squadIndex
        self.hasPenalties = reusable.personal.avatar.hasPenalties()
        self.respawnsCount = result.respawnsCount
        personalInfo = reusable.getPlayerInfo()
        personalPrebattleID = personalInfo.prebattleID if personalInfo.squadIndex else 0
        self.isOwnSquad = personalPrebattleID != 0 and personalPrebattleID == result.player.prebattleID
        avatar = reusable.avatars.getAvatarInfo(result.player.dbID)
        self.badgeID = avatar.badge if avatar else 0
        self.badgeSuffixID = avatar.suffixBadge
        if self.deathReason > DEATH_REASON_ALIVE:
            if result.killerID:
                killerVehicle = reusable.getPlayerInfoByVehicleID(result.killerID)
                self.killerName = killerVehicle.fakeName


class LSBattlesTeamStatsBlock(base.StatsBlock):
    __slots__ = ()

    def setRecord(self, result, reusable):
        allies, _ = reusable.getBiDirectionTeamsIterator(result, sortKey=lambda info: (LSAfkSortKey(info),
         PersonalFirstTeamItemSortKey(info, 'totalKeys'),
         PersonalFirstTeamItemSortKey(info, 'teamContribution'),
         PersonalFirstTeamItemSortKey(info, 'kills')))
        for item in allies:
            block = LSVehicleStatsBlock()
            block.setRecord(item, reusable)
            self.addComponent(self.getNextComponentIndex(), block)


class LSBattleFinishResultBlock(common.RegularFinishResultBlock):

    def setRecord(self, result, reusable):
        teamRes = reusable.getPersonalTeamResult()
        self.shortResultLabel = teamRes
        self.fullResultLabel = ''
        self.finishReasonLabel = ''
        self.finishReasonClarificationLabel = ''
