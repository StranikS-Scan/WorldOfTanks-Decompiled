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
from historical_battles_common.helpers_common import getFrontCouponModifier
from skeletons.gui.server_events import IEventsCache
from items import vehicles
from historical_battles_common.hb_constants import FrontmanRoleID
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
     FINISH_REASON.ALLY_KILLED: 'allArtilleryKilled',
     FINISH_REASON.FAILURE: 'techFailure',
     FINISH_REASON.TIMEOUT: 'timeEnded',
     FINISH_REASON.HB_ENEMY_EXTERMINATION: 'allEnemiesKilled',
     FINISH_REASON.TECHNICAL: 'techFailure',
     FINISH_REASON.WIN_POINTS: 'allTasksCompleted',
     FINISH_REASON.UNKNOWN: 'abandonedGame'}

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


class FrontManBlock(base.StatsBlock):

    def setRecord(self, result, reusable):
        avatarResults = result['personal']['avatar']
        frontmanID = avatarResults['frontmanID']
        frontmanRoleID = avatarResults['frontmanRoleID']
        roleID = None
        if frontmanRoleID >= 0:
            roleID = FrontmanRoleID(avatarResults['frontmanRoleID']).name
        self.addNextComponent(base.DirectStatsItem('id', frontmanID))
        self.addNextComponent(base.DirectStatsItem('role', roleID))
        return


class EventVehicleStatsBlock(veh_components.RegularVehicleStatsBlock):
    __slots__ = ('damageAssisted', 'damageBlockedByArmor', 'tankType', 'role', 'badgeID', 'violationName')

    def __init__(self, meta=None, field='', *path):
        super(EventVehicleStatsBlock, self).__init__(meta, field, *path)
        self.damageBlockedByArmor = 0
        self.damageAssisted = 0
        self.tankType = ''
        self.role = None
        self.badgeID = 0
        self.violationName = None
        return

    def setRecord(self, result, reusable):
        super(EventVehicleStatsBlock, self).setRecord(result, reusable)
        self.damageBlockedByArmor = result.damageBlockedByArmor
        self.damageAssisted = result.damageAssisted
        self.role = FrontmanRoleID(result.frontmanRoleID).name
        self.badgeID = result.avatar and result.avatar.badge or 0
        self.violationName = result.avatar and result.avatar.modelViolationName or None
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


class FrontCouponUsedItem(base.StatsItem):

    def _convert(self, result, reusable):
        modifier = getFrontCouponModifier(result['avatar']['frontCoupon'])
        return 'X{}'.format(modifier) if modifier else None


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
        name = backport.text(R.strings.hb_arenas.dyn('c_{}'.format(geometryName)).name())
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


class RoleAbilityBlock(base.StatsBlock):
    _gameEventController = dependency.descriptor(IGameEventController)

    def setRecord(self, result, reusable):
        avatarResults = result['avatar']
        roleObtained = avatarResults['roleObtained']
        frontmanID = avatarResults['frontmanID']
        frontID = avatarResults['frontID']
        front = self._gameEventController.frontController.getFront(frontID)
        if not front:
            eventData = self._gameEventController.getGameEventData()
            frontmen = eventData.get('frontmen', {})
            roleAbilityID = frontmen.get(frontmanID, {}).get('roleAbilities', {}).get('eqId', '')
        else:
            frontman = front.getFrontmen()[frontmanID]
            roleAbilityID = frontman.getRoleAbility()
        roleAbility = vehicles.g_cache.equipments()[roleAbilityID]
        self.addNextComponent(base.DirectStatsItem('obtained', roleObtained))
        self.addNextComponent(base.DirectStatsItem('name', roleAbility.userString))
        self.addNextComponent(base.DirectStatsItem('icon', roleAbility.iconName))
        self.addNextComponent(base.DirectStatsItem('id', roleAbilityID))


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
