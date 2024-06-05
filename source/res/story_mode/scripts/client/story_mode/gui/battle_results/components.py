# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: story_mode/scripts/client/story_mode/gui/battle_results/components.py
from gui.battle_results.components import base
from gui.server_events.bonuses import getNonQuestBonuses, mergeBonuses
from gui.impl.gen import R
from helpers import dependency
from shared_utils import first
from skeletons.gui.game_control import IBattlePassController
from story_mode_common.configs.story_mode_missions import missionsSchema
from story_mode.gui.shared.utils import getRewardList

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


class RewardsBlock(base.StatsBlock):
    __slots__ = ()
    _battlePass = dependency.descriptor(IBattlePassController)

    def setRecord(self, result, reusable):
        progressInfo = result['personal']['avatar'].get('progressionInfo', {})
        missionSettings = missionsSchema.getModel()
        if missionSettings is None:
            return
        else:
            rewardsList = getRewardList(progressInfo, self._battlePass.isActive(), True)
            bonuses = []
            for rewardRecord in rewardsList:
                for rewardName, rewardData in rewardRecord.iteritems():
                    for item in getNonQuestBonuses(rewardName, rewardData):
                        bonuses.append(item)

            for item in mergeBonuses(bonuses):
                self.addNextComponent(base.DirectStatsItem('', item))

            return


class ProgressionInfoItem(base.StatsItem):
    __slots__ = ()

    def _convert(self, record, reusable):
        return record['avatar'].get('progressionInfo', {})
