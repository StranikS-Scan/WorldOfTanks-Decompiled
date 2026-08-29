# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/wt_event_models_helper.py
from typing import TYPE_CHECKING
from gui.battle_pass.battle_pass_bonuses_packers import packBonusModelAndTooltipData
from white_tiger.gui.impl.lobby.wt_event_constants import BonusGroup, WhiteTigerLootBoxes
from white_tiger.gui.impl.lobby.packers.wt_event_simple_bonus_packers import sortBonuses
from white_tiger.gui.impl.lobby.packers.wt_event_bonuses_packers import getWtEventBonusPacker, BOSS_ALL_BONUSES_ORDER
from helpers.dependency import replace_none_kwargs
from skeletons.gui.game_control import ILootBoxesController
from gui.wt_event.wt_event_helpers import getVehiclesFromAwards
if TYPE_CHECKING:
    from white_tiger.gui.impl.gen.view_models.views.lobby.common.wt_run_portal_model import WtRunPortalModel
    from white_tiger.gui.impl.gen.view_models.views.lobby.common.wt_guaranteed_reward_model import WtGuaranteedRewardModel

@replace_none_kwargs(boxesCtrl=ILootBoxesController)
def setLootBoxesCount(model, lootBoxType, openedBoxes=1, boxesCtrl=None):
    lootBoxesCount = boxesCtrl.getLootBoxesCountByTypeForUI(lootBoxType, openedBoxes)
    model.setLootBoxesCount(lootBoxesCount)


@replace_none_kwargs(boxesCtrl=ILootBoxesController)
def setBonusVehicles(model, isShortName=False, boxesCtrl=None):
    bossBonuses = boxesCtrl.getLootBoxesRewards(WhiteTigerLootBoxes.WT_BOSS)
    vehicleGroup = bossBonuses.get(BonusGroup.VEHICLES)
    if vehicleGroup is None:
        return
    else:
        vehicles = getVehiclesFromAwards(vehicleGroup.bonuses)
        model.clear()
        for vehicle in vehicles:
            if vehicle.name in ('poland:Pl26_Czolg_P_Wz_46_Verbesserter', 'france:F133_Projet_57_Ampere'):
                continue
            model.addString(vehicle.shortUserName if isShortName else vehicle.userName)

        model.invalidate()
        return


@replace_none_kwargs(boxesCtrl=ILootBoxesController)
def setGuaranteedReward(model, boxesCtrl=None):
    guaranteed, left, isIgnored = boxesCtrl.getLootBoxLimitsInfo(WhiteTigerLootBoxes.WT_BOSS)
    model.setGuaranteedTankAttemptCount(guaranteed - 1)
    model.setLeftAttemptsCount(left)
    model.setAttemptsCount(guaranteed - left)
    model.setIsIgnored(isIgnored)


@replace_none_kwargs(boxesCtrl=ILootBoxesController)
def fillFirstLaunchReward(model, lootBoxType, boxesCtrl=None):
    extra = boxesCtrl.getExtraRewards(lootBoxType, count=0)
    model.setFirstLaunchReward(extra.get('gold', 0) if extra else 0)


@replace_none_kwargs(boxesCtrl=ILootBoxesController)
def hasUnclaimedLoot(lootBoxType=WhiteTigerLootBoxes.WT_HUNTER, boxesCtrl=None):
    return boxesCtrl.hasPendingBoxes(lootBoxType)


def fillAdditionalAwards(model, bonuses, tooltipItems):
    model.clear()
    bonuses = sorted(bonuses, key=lambda bonus: sortBonuses(bonus, BOSS_ALL_BONUSES_ORDER))
    packBonusModelAndTooltipData(bonuses, model, tooltipItems, getWtEventBonusPacker())
    model.invalidate()
