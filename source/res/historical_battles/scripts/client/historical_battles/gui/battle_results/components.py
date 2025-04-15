# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/battle_results/components.py
import typing
from ArenaType import g_geometryCache, parseTypeID
from account_shared import getFairPlayViolationName
from constants import ATTACK_REASON_VALUES, DEATH_REASON_ALIVE, EVENT, FINISH_REASON, FAIRPLAY_VIOLATIONS
from debug_utils import LOG_ERROR
from helpers import dependency
from helpers.time_utils import ONE_MINUTE
from gui.battle_results.components import base, common
from gui.battle_results.components import vehicles as veh_components
from gui.battle_results.reusable import sort_keys
from gui.battle_results.settings import PLAYER_TEAM_RESULT
from gui.impl.gen import R
from gui.impl import backport
from gui.shared.gui_items.Vehicle import VEHICLE_CLASS_NAME
from gui.shared.utils.functions import makeTooltip
from historical_battles.gui.impl.gen.view_models.views.lobby.battle_result_view_model import FairplayStatus
from skeletons.gui.server_events import IEventsCache
from historical_battles.skeletons.gui.game_event_controller import IGameEventController
if typing.TYPE_CHECKING:
    from gui.battle_results.reusable import _ReusableInfo

def makeSimpleTooltip(header, body):
    return {'tooltip': makeTooltip(header=header, body=body),
     'isSpecial': False,
     'specialArgs': []}


def _getTeamFightPlace(results):
    return results.hwTeamFightPlace if results.environmentID > 0 else EVENT.INVALID_BATTLE_PLACE


class IsWinItem(base.StatsItem):
    eventsCache = dependency.descriptor(IEventsCache)
    __slots__ = ()

    def _convert(self, result, reusable):
        teamResult = reusable.getPersonalTeamResult()
        return teamResult == PLAYER_TEAM_RESULT.WIN


class BattleResultTypeItem(base.StatsItem):
    __slots__ = ()

    def _convert(self, result, reusable):
        return reusable.getPersonalTeamResult()


class FinishReasonItem(base.StatsItem):
    __slots__ = ()
    _reasons = {FINISH_REASON.EXTERMINATION: 'allTeamKilled',
     FINISH_REASON.BASE: 'baseLost',
     FINISH_REASON.FAILURE: 'techFailure',
     FINISH_REASON.TIMEOUT: 'timeEnded',
     FINISH_REASON.HB_ENEMY_EXTERMINATION: 'allEnemiesKilled',
     FINISH_REASON.TECHNICAL: 'techFailure',
     FINISH_REASON.WIN_POINTS: 'allTasksCompleted',
     FINISH_REASON.UNKNOWN: 'abandonedGame',
     FINISH_REASON.HB_ALLY_SPG_EXTERMINATION: 'allArtilleryKilled'}

    def _convert(self, result, reusable):
        finishReason = reusable.common.finishReason
        reason = self._reasons.get(finishReason)
        if reason is None:
            LOG_ERROR('Unexpected finish reason: {}'.format(reusable.common.finishReason))
            reason = self._reasons[FINISH_REASON.FAILURE]
        strId = R.strings.hb_lobby.battleResults.subTitle.dyn(reason)()
        return strId


class TankNameItem(base.StatsItem):
    __slots__ = ()

    def _convert(self, result, reusable):
        info = reusable.getPersonalVehiclesInfo(result)
        return info.vehicle.shortUserName


class HeroVehicleItem(base.StatsItem):
    __slots__ = ('__gameEventController',)
    __gameEventController = dependency.descriptor(IGameEventController)

    def _convert(self, result, reusable):
        info = reusable.getPersonalVehiclesInfo(result)
        eventData = self.__gameEventController.getGameEventData()
        vehiclesList = []
        for _, v in eventData.get('frontmen', {}).items():
            vehiclesList.extend(v.get('vehicles', []))

        result = False
        for vehicle in vehiclesList:
            if vehicle.get('vehTypeCD') == info.vehicle.intCD:
                result = vehicle.get('isHero', False)
                break

        return result


class TankTypeItem(base.StatsItem):
    __slots__ = ()

    def _convert(self, result, reusable):
        info = reusable.getPersonalVehiclesInfo(result)
        return info.vehicle.type


class DeathReason(base.StatsItem):
    __slots__ = ()

    def _convert(self, result, reusable):
        info = reusable.getPersonalVehiclesInfo(result)
        return '' if info.deathReason == DEATH_REASON_ALIVE else ATTACK_REASON_VALUES.get(info.deathReason)


class DamageItem(base.StatsItem):
    __slots__ = ()

    def _convert(self, result, reusable):
        info = reusable.getPersonalVehiclesInfo(result)
        return info.damageDealt


class DamageBlockedItem(base.StatsItem):
    __slots__ = ()

    def _convert(self, result, reusable):
        info = reusable.getPersonalVehiclesInfo(result)
        return info.damageBlockedByArmor


class DamageAssistedItem(base.StatsItem):
    __slots__ = ()

    def _convert(self, result, reusable):
        info = reusable.getPersonalVehiclesInfo(result)
        return info.damageAssisted


class KillsItem(base.StatsItem):
    __slots__ = ()

    def _convert(self, result, reusable):
        info = reusable.getPersonalVehiclesInfo(result)
        return info.kills


class IsKilledItem(base.StatsItem):
    __slots__ = ()

    def _convert(self, result, reusable):
        info = reusable.getPersonalVehiclesInfo(result)
        return info.deathReason != DEATH_REASON_ALIVE


class FairplayItem(base.StatsItem):
    __slots__ = ()

    def _convert(self, result, reusable):
        fairplayViolations = result['avatar']['fairplayViolations']
        for violation in fairplayViolations:
            violationName = getFairPlayViolationName(violation)
            if violationName == FAIRPLAY_VIOLATIONS.HB_DESERTER:
                return FairplayStatus.DESERTER
            if violationName == FAIRPLAY_VIOLATIONS.HB_AFK:
                return FairplayStatus.AFK


class KillerVehicleBlock(base.StatsBlock):
    __slots__ = ()

    def setRecord(self, result, reusable):
        info = reusable.getPersonalVehiclesInfo(result)
        if info.killerID == 0:
            return ''
        killer = reusable.vehicles.getVehicleInfo(info.killerID)
        killerVehicle = reusable.vehicles.itemsCache.items.getVehicles()[killer.intCD]
        self.addNextComponent(base.DirectStatsItem('name', killerVehicle.shortUserName))
        self.addNextComponent(base.DirectStatsItem('type', killerVehicle.type))


class DivisionBlock(base.StatsBlock):

    def setRecord(self, result, reusable):
        avatarResults = result['personal']['avatar']
        divisionID = avatarResults['divisionID']
        self.addNextComponent(base.DirectStatsItem('id', divisionID))


class EventVehicleStatsBlock(veh_components.RegularVehicleStatsBlock):
    __slots__ = ('damageAssisted', 'damageBlockedByArmor', 'tankType', 'badgeID', 'violationName', 'divisionLevel')

    def __init__(self, meta=None, field='', *path):
        super(EventVehicleStatsBlock, self).__init__(meta, field, *path)
        self.damageBlockedByArmor = 0
        self.damageAssisted = 0
        self.tankType = ''
        self.badgeID = 0
        self.violationName = None
        self.divisionLevel = 1
        return

    def setRecord(self, result, reusable):
        super(EventVehicleStatsBlock, self).setRecord(result, reusable)
        self.damageBlockedByArmor = result.damageBlockedByArmor
        self.damageAssisted = result.damageAssisted
        self.badgeID = result.avatar and result.avatar.badge or 0
        self.violationName = result.avatar and result.avatar.modelViolationName or None
        self.divisionLevel = result.avatar and result.avatar.divisionLevel or 1
        return

    def _setVehicleInfo(self, vehicle):
        super(EventVehicleStatsBlock, self)._setVehicleInfo(vehicle)
        self.tankType = vehicle.type

    def getVO(self):
        vo = super(EventVehicleStatsBlock, self).getVO()
        if self.violationName:
            vo['violationName'] = self.violationName
        return vo


class PersonalFirstTeamItemSortKey(sort_keys.TeamItemSortKey):
    __slots__ = ('_sortKey',)

    def __init__(self, vehicleInfo, compareKey):
        super(PersonalFirstTeamItemSortKey, self).__init__(vehicleInfo)
        self._sortKey = compareKey

    def _cmp(self, other):
        sortKey = self._sortKey
        return cmp(getattr(other.info, sortKey), getattr(self.info, sortKey))


class HBTeamStatsBlock(veh_components.TeamStatsBlock):
    gameEventController = dependency.descriptor(IGameEventController)
    __slots__ = ()

    def __init__(self, meta=None, field='', *path):
        super(HBTeamStatsBlock, self).__init__(EventVehicleStatsBlock, meta, field, *path)

    def setRecord(self, result, reusable):
        allies, _ = reusable.getBiDirectionTeamsIterator(result, sortKey=lambda info: PersonalFirstTeamItemSortKey(info, 'kills'))
        allies = list(allies)
        allies = [ ally for ally in allies if ally.vehicle.type != VEHICLE_CLASS_NAME.SPG ]
        super(HBTeamStatsBlock, self).setRecord(allies, reusable)


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


class MapInfoBlock(base.StatsBlock):

    def setRecord(self, result, reusable):
        super(MapInfoBlock, self).setRecord(result, reusable)
        typeId = reusable.common.arenaType.getID()
        _, geometryID = parseTypeID(typeId)
        geometryType = g_geometryCache[geometryID]
        geometryName = geometryType.geometryName
        name = backport.text(R.strings.arenas.dyn('c_{}'.format(geometryName)).name())
        self.addNextComponent(base.DirectStatsItem('name', name.decode().upper()))
        self.addNextComponent(base.DirectStatsItem('id', geometryName))


class EarningsBlock(base.StatsBlock):

    def setRecord(self, result, reusable):
        super(EarningsBlock, self).setRecord(result, reusable)
        earning = result['personal']['avatar']['hbCoins']
        self.addNextComponent(base.DirectStatsItem('amount', earning['amount']))
        self.addNextComponent(base.DirectStatsItem('type', earning['type']))


class FrontItem(base.StatsItem):
    _gameEventController = dependency.descriptor(IGameEventController)

    def _convert(self, result, reusable):
        frontID = result['avatar']['frontID']
        front = self._gameEventController.frontController.getFront(frontID)
        return None if not front else front.getName()


class ArenaPhasesBlock(base.StatsBlock):

    def setRecord(self, result, reusable):
        phases = result['avatar']['arenaPhases']
        self.addNextComponent(base.DirectStatsItem('current', phases['current']))
        self.addNextComponent(base.DirectStatsItem('total', phases['total']))


class ArenaDurationItem(common.ArenaDurationItem):
    __slots__ = ()

    def _convert(self, record, reusable):
        if record is None:
            return
        else:
            duration = record['duration']
            return backport.text(R.strings.hb_time.duration.short.sec(), sec=int(duration % ONE_MINUTE)) if duration < ONE_MINUTE else super(ArenaDurationItem, self)._convert(duration, reusable)


class CommonStatsBlock(base.StatsBlock):
    __slots__ = ()

    def setRecord(self, result, reusable):
        from gui.battle_results.components import personal
        info = reusable.getPersonalVehiclesInfo(result)
        blocks = (personal.DamageDetailsBlock(),
         personal.ArmorUsingDetailsBlock(),
         personal.AssistDetailsBlock(),
         personal.CritsDetailsBlock(),
         personal.StunDetailsBlock())
        for block in blocks:
            block.setRecord(info, reusable)
            self.addNextComponent(block)
