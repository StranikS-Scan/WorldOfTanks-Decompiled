# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: story_mode/scripts/client/story_mode/gui/battle_results/components.py
from gui.battle_results.components import base
from gui.impl.gen import R
from shared_utils import first

class FinishResultItem(base.StatsItem):
    __slots__ = ()

    def _convert(self, record, reusable):
        return reusable.getPersonalTeamResult()


class FinishReasonItem(base.StatsItem):
    __slots__ = ()

    def _convert(self, record, reusable):
        finishReason = reusable.common.finishReason
        rReason = R.strings.sm_battle.finish.reason
        return rReason.num(finishReason, rReason.default)()


class MissionIdItem(base.StatsItem):
    __slots__ = ()

    def _convert(self, record, reusable):
        return record['avatar']['missionId']


class IsForceOnboardingItem(base.StatsItem):
    __slots__ = ()

    def _convert(self, record, reusable):
        return record['avatar']['isForceOnboarding']


class VehicleNameItem(base.StatsItem):
    __slots__ = ()

    def _convert(self, record, reusable):
        _, item = first(reusable.personal.getVehicleItemsIterator())
        return item.userName


class VehicleBlock(base.StatsBlock):

    def setRecord(self, result, reusable):
        vehicleInfo = reusable.getPersonalVehiclesInfo(result['personal'])
        self.addNextComponent(base.DirectStatsItem('deathReason', vehicleInfo.deathReason))
        self.addNextComponent(base.DirectStatsItem('damageDealt', vehicleInfo.damageDealt))
        self.addNextComponent(base.DirectStatsItem('kills', vehicleInfo.kills))
        self.addNextComponent(base.DirectStatsItem('damageAssisted', vehicleInfo.damageAssisted + vehicleInfo.equipmentDamageAssisted))
        self.addNextComponent(base.DirectStatsItem('damageBlockedByArmor', vehicleInfo.damageBlockedByArmor))
