# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/battle_results/components.py
from gui.battle_results.components.common import RegularFinishResultBlock
from gui.battle_results.components.vehicles import RegularVehicleStatsBlock, TeamStatsBlock, FieldsReplacer, _STAT_STUN_FIELD_NAMES, _getStunFilter
from gui.battle_results import stored_sorting
from gui.battle_results.components import base
from gui.battle_results.components import common
from gui.battle_results.components.progress import isQuestCompleted
from gui.battle_results.components.shared import SortingBlock
from gui.impl import backport
from gui.impl.gen import R
from gui.server_events import conditions
from gui.shared.gui_items.Vehicle import getIconPath
from gui.shared.utils import toUpper
from halloween.gui.battle_results.style import makeStatValue, makeRegularFinishResultLabel
from halloween.gui.impl.gen.view_models.views.lobby.base_info_model import BaseStateEnum
from halloween.hw_constants import QuestType
from skeletons.gui.game_control import IHalloweenController
from helpers import dependency
from helpers.time_utils import ONE_MINUTE
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.server_events import IEventsCache

class VehicleNameItem(base.StatsItem):
    __slots__ = ()

    def _convert(self, result, reusable):
        info = reusable.getPersonalVehiclesInfo(result)
        return info.vehicle.descriptor.type.shortUserString


class RespawnsItem(base.StatsItem):
    __slots__ = ()

    def _convert(self, result, reusable):
        info = reusable.getPersonalVehiclesInfo(result)
        return info.respawns


class HalloweenXPItem(base.StatsItem):
    __slots__ = ()

    def _convert(self, result, reusable):
        info = reusable.getPersonalVehiclesInfo(result)
        return info.hwXP


class DamageItem(base.StatsItem):
    __slots__ = ()

    def _convert(self, result, reusable):
        info = reusable.getPersonalVehiclesInfo(result)
        return info.damageDealt


class KillsItem(base.StatsItem):
    __slots__ = ()

    def _convert(self, result, reusable):
        info = reusable.getPersonalVehiclesInfo(result)
        return info.kills


class PlayerNameItem(base.StatsItem):
    __slots__ = ()

    def _convert(self, result, reusable):
        info = reusable.getPersonalVehiclesInfo(result)
        return info.player.realName


class PlayerClanItem(base.StatsItem):
    __slots__ = ()

    def _convert(self, result, reusable):
        info = reusable.getPersonalVehiclesInfo(result)
        return info.player.clanAbbrev


class PlayerDBIDItem(base.StatsItem):
    __slots__ = ()

    def _convert(self, result, reusable):
        return reusable.getPlayerInfo().dbID


class HWBattleVehicleStatsBlock(RegularVehicleStatsBlock):
    __slots__ = ('hwXP', 'vehicleLvl', 'vehicleType', 'badgeID', 'respawns', 'isPrematureLeave', 'fairplayViolations', 'isPremiumIGR')

    def __init__(self, meta=None, field='', *path):
        super(HWBattleVehicleStatsBlock, self).__init__(meta, field, *path)
        self.hwXP = 0
        self.badgeID = 0
        self.respawns = 0
        self.vehicleLvl = 0
        self.vehicleType = ''
        self.isPrematureLeave = False
        self.fairplayViolations = False
        self.isPremiumIGR = False

    def setRecord(self, result, reusable):
        super(HWBattleVehicleStatsBlock, self).setRecord(result, reusable)
        self.hwXP = result.hwXP
        player = result.player
        self.respawns = result.respawns
        avatar = reusable.avatars.getAvatarInfo(player.dbID)
        self.badgeID = avatar.badge
        self.isPrematureLeave = avatar.isPrematureLeave
        self.fairplayViolations = avatar.hasPenalties()

    def _setVehicleInfo(self, vehicle):
        super(HWBattleVehicleStatsBlock, self)._setVehicleInfo(vehicle)
        if vehicle is not None:
            self.isPremiumIGR = vehicle.isPremiumIGR
            self.vehicleLvl = vehicle.level
            self.vehicleType = vehicle.type
            self.vehicleIcon = getIconPath(vehicle.name)
            self.vehicleName = vehicle.descriptor.type.userString
            self.vehicleShortName = vehicle.descriptor.type.shortUserString
        return


class RegularVehicleStatValuesBlock(base.StatsBlock):
    __slots__ = ('_isPersonal', '_filters', 'shots', 'hits', 'explosionHits', 'damageDealt', 'sniperDamageDealt', 'directHitsReceived', 'piercingsReceived', 'noDamageDirectHitsReceived', 'explosionHitsReceived', 'damageBlockedByArmor', 'teamHitsDamage', 'spotted', 'damagedKilled', 'damageAssisted', 'damageAssistedStun', 'stunNum', 'stunDuration', 'mileage', '__rawDamageAssistedStun', '__rawStunNum', 'respawns')
    lobbyContext = dependency.descriptor(ILobbyContext)

    def __init__(self, meta=None, field='', *path):
        super(RegularVehicleStatValuesBlock, self).__init__(meta, field, *path)
        self._filters = set()

    def setPersonal(self, flag):
        self._isPersonal = flag

    def addFilters(self, filters):
        self._filters.update(filters)

    def setRecord(self, result, reusable):
        self.__rawDamageAssistedStun = result.damageAssistedStun
        self.__rawStunNum = result.stunNum
        if self.__rawStunNum == 0:
            self.addFilters(_STAT_STUN_FIELD_NAMES)
        self.shots = result.shots
        self.hits = '{} / {}'.format(result.directEnemyHits, result.piercingEnemyHits)
        self.explosionHits = result.explosionHits
        self.damageDealt = result.damageDealt
        self.sniperDamageDealt = result.sniperDamageDealt
        self.directHitsReceived = result.directHitsReceived
        self.piercingsReceived = result.piercingsReceived
        self.noDamageDirectHitsReceived = result.noDamageDirectHitsReceived
        self.explosionHitsReceived = result.explosionHitsReceived
        self.damageBlockedByArmor = result.damageBlockedByArmor
        self.teamHitsDamage = '{} / {}'.format(result.tkills, result.tdamageDealt)
        self.spotted = result.spotted
        self.damagedKilled = '{} / {}'.format(result.damaged, result.kills)
        self.damageAssisted = result.damageAssisted
        self.damageAssistedStun = result.damageAssistedStun
        self.stunNum = result.stunNum
        self.stunDuration = result.stunDuration
        self.mileage = result.mileage
        self.respawns = result.respawns

    def getVO(self):
        vo = []
        for component in self._components:
            field = component.getField()
            if field in list(self._filters):
                continue
            value = component.getVO()
            if self._isPersonal and field in FieldsReplacer._STAT_VALUES_VO_REPLACER:
                field = FieldsReplacer._STAT_VALUES_VO_REPLACER[field]
            vo.append(makeStatValue(field, value))

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


class HWBattleTeamStatsBlock(TeamStatsBlock):
    __slots__ = ()

    def __init__(self, meta=None, field='', *path):
        super(HWBattleTeamStatsBlock, self).__init__(HWBattleVehicleStatsBlock, meta, field, *path)


class AllyTeamDamage(base.StatsItem):

    def _convert(self, result, reusable):
        allies, _ = reusable.getBiDirectionTeamsIterator(result)
        return sum((info.damageDealt for info in allies))


class EnemyTeamDamage(base.StatsItem):

    def _convert(self, result, reusable):
        _, enemies = reusable.getBiDirectionTeamsIterator(result)
        return sum((info.damageDealt for info in enemies))


class ArenaDurationItem(base.StatsItem):
    __slots__ = ()

    def _convert(self, record, reusable):
        return backport.text(R.strings.battle_results.hw_details.time.value(), min=self.formatted(int(record / ONE_MINUTE)), sec=self.formatted(int(record % ONE_MINUTE))) if record else ''

    def formatted(self, value):
        return '{:02d}'.format(value)


class HWSortingBlock(SortingBlock):
    __slots__ = ()

    def __init__(self, meta=None, field='', *path):
        super(HWSortingBlock, self).__init__(stored_sorting.STATS_EVENT_SORTING, meta, field, *path)


class HWArenaFullNameItem(base.StatsItem):
    __slots__ = ()

    def _convert(self, record, reusable):
        arenaGuiType = reusable.common.arenaGuiType
        arenaType = reusable.common.arenaType
        return common.makeArenaFullName(arenaType.getName(), backport.text(R.strings.menu.loading.battleTypes.num(arenaGuiType)()))


class BaseStatValuesBlock(base.StatsBlock):
    __slots__ = ('baseLetter', 'baseState')

    def __init__(self, meta=None, field='', *path):
        super(BaseStatValuesBlock, self).__init__(meta, field, *path)
        self.baseLetter = ''
        self.baseState = BaseStateEnum.NEUTRAL

    def setRecord(self, result, reusable):
        self.baseLetter = result['baseLetter']
        self.baseState = result['baseState']


class AllBasesStatValuesBlock(base.StatsBlock):
    __slots__ = ()
    __LETTER_MAP = {1: 'A',
     2: 'B'}

    def setRecord(self, result, reusable):
        add = self.addNextComponent
        info = reusable.getPersonalVehiclesInfo(result)
        playerTeam = info.player.team
        for baseID, teamID in info.vehicles[0].hwBaseCaptured:
            baseState = BaseStateEnum.NEUTRAL
            if playerTeam == teamID:
                baseState = BaseStateEnum.PLAYERCAPTURED
            elif teamID != 0:
                baseState = BaseStateEnum.ENEMYCAPTURED
            baseInfo = {'baseLetter': self.__LETTER_MAP.get(baseID, ''),
             'baseState': baseState}
            block = BaseStatValuesBlock()
            block.setRecord(baseInfo, reusable)
            add(block)


class HalloweenFinishResultBlock(RegularFinishResultBlock):

    def setRecord(self, result, reusable):
        teamResult = reusable.getPersonalTeamResult()
        self.finishReasonLabel = makeRegularFinishResultLabel(reusable.common.finishReason, teamResult)
        self.shortResultLabel = teamResult
        self.fullResultLabel = toUpper(backport.text(R.strings.menu.finalStatistic.commonStats.resultlabel.dyn(teamResult)()))


class QuestsProgressBlock(base.StatsBlock):
    eventsCache = dependency.descriptor(IEventsCache)
    _hwController = dependency.descriptor(IHalloweenController)
    __slots__ = ()

    def getVO(self):
        vo = super(QuestsProgressBlock, self).getVO()
        return vo

    def setRecord(self, result, reusable):
        phaseIndex = reusable.personal.hwPhase
        currentPhase = self._hwController.phases.getPhaseByIndex(phaseIndex)
        if not currentPhase:
            return
        questsProgress = reusable.personal.getQuestsProgress()
        hwQuestProgress = reusable.personal.hwQuestProgress
        if not hwQuestProgress:
            return
        questItems = {item.getQuest().getID():item.getQuest() for item in currentPhase.getQuestsByType(QuestType.HALLOWEEN)}
        for qID, progress in sorted(hwQuestProgress.iteritems(), key=lambda item: item[0]):
            quest = questItems.get(qID)
            if not quest:
                continue
            isCompleted = progress.get('bonusCount', 0) > 0
            needShow = not isCompleted
            info = {'qID': qID,
             'currentProgress': 0,
             'totalProgress': 0,
             'prevProgress': 0,
             'isCompleted': isCompleted,
             'key': ''}
            for condition in quest.bonusCond.getConditions().items:
                if isinstance(condition, conditions._Cumulativable):
                    info.update({'key': condition.getKey(),
                     'totalProgress': condition.getTotalValue()})
                    break

            currentProgress = progress.get(info.get('key'), 0)
            info.update({'currentProgress': currentProgress,
             'prevProgress': currentProgress})
            if qID in questsProgress:
                _, pPrev, pCur = questsProgress[qID]
                if isQuestCompleted('', pPrev, pCur):
                    currentProgress = info['totalProgress']
                    needShow = True
                else:
                    currentProgress = pCur.get(info.get('key'), info['currentProgress'])
                pPrev = pPrev.get(info.get('key'), 0)
                info.update({'currentProgress': currentProgress,
                 'prevProgress': pPrev})
            if needShow:
                self.addComponent(self.getNextComponentIndex(), base.DirectStatsItem('', {'currentPhaseIndex': phaseIndex,
                 'info': info}))
