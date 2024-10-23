# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/wt_event_models_helper.py
from typing import TYPE_CHECKING
from gui.battle_pass.battle_pass_bonuses_packers import packBonusModelAndTooltipData
from white_tiger.gui.impl.gen.view_models.views.lobby.portal_premium_tanks import PortalPremiumTanks
from white_tiger.gui.impl.lobby.wt_event_constants import BonusGroup, WhiteTigerLootBoxes
from gui.shared.gui_items.Vehicle import getNationLessName
from gui.wt_event.wt_event_helpers import getSpecialVehicles
from white_tiger.gui.impl.lobby.packers.wt_event_simple_bonus_packers import sortBonuses
from white_tiger.gui.impl.lobby.packers.wt_event_bonuses_packers import getWtEventBonusPacker, BOSS_ALL_BONUSES_ORDER
from helpers.dependency import replace_none_kwargs
from skeletons.gui.game_control import ILootBoxesController
if TYPE_CHECKING:
    from white_tiger.gui.impl.gen.view_models.views.lobby.wt_event_vehicle_model import WtEventVehicleModel
    from white_tiger.gui.impl.gen.view_models.views.lobby.wt_event_portal_availability import WtEventPortalAvailability
    from white_tiger.gui.impl.gen.view_models.views.lobby.wt_event_guaranteed_award import WtEventGuaranteedAward
    from gui.impl.wrappers.user_list_model import UserListModel

def fillVehicleModel(model, vehicle):
    model.setType(vehicle.type)
    model.setLevel(vehicle.level)
    model.setName(vehicle.userName)
    model.setSpecName(getNationLessName(vehicle.name))
    model.setNation(vehicle.nationName)
    model.setIsElite(vehicle.isElite)
    model.setIntCD(vehicle.intCD)


@replace_none_kwargs(boxesCtrl=ILootBoxesController)
def setLootBoxesCount(model, lootBoxType, boxesCtrl=None):
    lootBoxesCount = boxesCtrl.getLootBoxesCountByTypeForUI(lootBoxType)
    model.setLootBoxesCount(lootBoxesCount)


@replace_none_kwargs(boxesCtrl=ILootBoxesController)
def setBonusVehicles(model, withoutSpecialTank, isShortName=False, boxesCtrl=None):
    bossBonuses = boxesCtrl.getLootBoxesRewards(WhiteTigerLootBoxes.WT_BOSS)
    vehicleGroup = bossBonuses.get(BonusGroup.VEHICLES)
    if vehicleGroup is None:
        return
    else:
        specialVehicles = getSpecialVehicles()
        if specialVehicles is None:
            return
        vehicles = [ bonus.getVehicles()[0][0] for bonus in vehicleGroup.bonuses if bonus.getName() == 'vehicles' ]

        def isSpecialVehicle(veh):
            for specialVehicle in specialVehicles:
                if veh.name == specialVehicle.name:
                    return True

            return False

        vehicles.sort(key=lambda veh: not isSpecialVehicle(veh))
        model.clearItems()
        for vehicle in vehicles:
            if withoutSpecialTank and isSpecialVehicle(vehicle):
                continue
            item = PortalPremiumTanks()
            item.setName(vehicle.shortUserName if isShortName else vehicle.userName)
            model.addViewModel(item)

        model.invalidate()
        return


@replace_none_kwargs(boxesCtrl=ILootBoxesController)
def setGuaranteedAward(model, boxesCtrl=None):
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
    return boxesCtrl.getReRollAttemptsCount(lootBoxType) > 0


def fillVehicleAward(model, bonusVehicle):
    if bonusVehicle is None:
        return
    else:
        fillVehicleModel(model.vehicle, bonusVehicle)
        return


def fillAdditionalAwards(model, bonuses, tooltipItems):
    model.clearItems()
    bonuses = sorted(bonuses, key=lambda bonus: sortBonuses(bonus, BOSS_ALL_BONUSES_ORDER))
    packBonusModelAndTooltipData(bonuses, model, tooltipItems, getWtEventBonusPacker())
