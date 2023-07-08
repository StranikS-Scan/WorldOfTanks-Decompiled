# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/gui/battle_results/components.py
from arena_bonus_type_caps import ARENA_BONUS_TYPE_CAPS as _BONUS_CAPS
from constants import ARENA_BONUS_TYPE
from fun_random.gui.feature.util.fun_mixins import FunAssetPacksMixin
from fun_random.gui.battle_results.formatters import formatTwoValues
from gui.battle_results.components.common import RegularArenaFullNameItem, makeArenaFullName
from gui.battle_results.components.personal import DynamicPremiumState
from gui.battle_results.components.vehicles import PersonalVehiclesRegularStatsBlock, RegularVehicleStatValuesBlock
from gui.Scaleform.genConsts.BATTLE_RESULTS_PREMIUM_STATES import BATTLE_RESULTS_PREMIUM_STATES

class FunRandomArenaFullNameItem(RegularArenaFullNameItem, FunAssetPacksMixin):
    __slots__ = ()

    def _convert(self, record, reusable):
        arenaType = reusable.common.arenaType
        return makeArenaFullName(arenaType.getName(), self.getModeUserName())


class FunRandomDynamicPremiumState(DynamicPremiumState):
    __slots__ = ()

    def getVO(self):
        hasXP = bool(_BONUS_CAPS.checkAny(ARENA_BONUS_TYPE.FUN_RANDOM, _BONUS_CAPS.XP))
        hasCredits = bool(_BONUS_CAPS.checkAny(ARENA_BONUS_TYPE.FUN_RANDOM, _BONUS_CAPS.CREDITS))
        hasPremSquadCredits = bool(_BONUS_CAPS.checkAny(ARENA_BONUS_TYPE.FUN_RANDOM, _BONUS_CAPS.PREM_SQUAD_CREDITS))
        if not hasXP and not hasCredits and not hasPremSquadCredits:
            self._value = BATTLE_RESULTS_PREMIUM_STATES.WHITHOUT_PREMIUM
            return self._value
        return super(FunRandomDynamicPremiumState, self).getVO()


class FunRandomPersonalVehiclesStatsBlock(PersonalVehiclesRegularStatsBlock):
    __slots__ = ()

    def _createVehicleStatValuesBlock(self):
        return FunRandomPersonalVehicleStatValuesBlock()


class FunRandomPersonalVehicleStatValuesBlock(RegularVehicleStatValuesBlock):
    __slots__ = ()

    def setRecord(self, result, reusable):
        super(FunRandomPersonalVehicleStatValuesBlock, self).setRecord(result, reusable)
        self.hits = formatTwoValues((result.directEnemyHits, result.piercingEnemyHits))
