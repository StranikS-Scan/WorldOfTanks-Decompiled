# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/wt_event/wt_event_models_helper.py
from typing import TYPE_CHECKING, Type
from gui.battle_pass.battle_pass_bonuses_packers import packBonusModelAndTooltipData
from gui.impl.gen.view_models.views.lobby.wt_event.portal_premium_tanks import PortalPremiumTanks
from gui.impl.lobby.wt_event.wt_event_constants import BonusGroup
from gui.shared.gui_items.loot_box import EventLootBoxes
from gui.shared.gui_items.Vehicle import getNationLessName
from gui.wt_event.wt_event_helpers import getSpecialVehicle
from gui.wt_event.wt_event_simple_bonus_packers import sortBonuses
from gui.wt_event.wt_event_bonuses_packers import getWtEventBonusPacker, BOSS_ALL_BONUSES_ORDER
from helpers.dependency import replace_none_kwargs
from skeletons.gui.game_control import ILootBoxesController, IGameEventController
if TYPE_CHECKING:
    from gui.impl.gen.view_models.views.lobby.wt_event.wt_event_portals_base import WtEventPortalsBase
    from gui.impl.gen.view_models.views.lobby.wt_event.wt_event_vehicle_model import WtEventVehicleModel
    from gui.impl.gen.view_models.views.lobby.wt_event.wt_event_portal_availability import WtEventPortalAvailability
    from gui.impl.gen.view_models.views.lobby.wt_event.wt_event_guaranteed_award import WtEventGuaranteedAward
    from gui.impl.wrappers.user_list_model import UserListModel

def fillVehicleModel(model, vehicle):
    model.setType(vehicle.type)
    model.setLevel(vehicle.level)
    model.setName(vehicle.shortUserName)
    model.setSpecName(getNationLessName(vehicle.name))
    model.setNation(vehicle.nationName)
    model.setIsElite(vehicle.isElite)
    model.setIntCD(vehicle.intCD)


@replace_none_kwargs(boxesCtrl=ILootBoxesController)
def setLootBoxesCount(model, lootBoxType, boxesCtrl=None):
    lootBoxesCount = boxesCtrl.getLootBoxesCountByType(lootBoxType)
    model.setLootBoxesCount(lootBoxesCount)


@replace_none_kwargs(eventCtrl=IGameEventController)
def setVehicleExchangeCost(model, eventCtrl=None):
    exchangeConfig = eventCtrl.getConfig().exchange
    model.setAttemptPrice(exchangeConfig['count'])


def setSpecialTankAvailability(model):
    vehicle = getSpecialVehicle()
    if vehicle is not None:
        model.setIsTankInHangar(vehicle.isInInventory or vehicle.isRestorePossible())
    return


@replace_none_kwargs(boxesCtrl=ILootBoxesController)
def setBonusVehicles(model, withoutSpecialTank, isShortName=False, boxesCtrl=None):
    bossBonuses = boxesCtrl.getLootBoxesRewards(EventLootBoxes.WT_BOSS)
    vehicleGroup = bossBonuses.get(BonusGroup.VEHICLES)
    if vehicleGroup is None:
        return
    else:
        specialVehicle = getSpecialVehicle()
        if specialVehicle is None:
            return
        vehicles = [ bonus.getVehicles()[0][0] for bonus in vehicleGroup.bonuses if bonus.getName() == 'vehicles' ]
        vehicles.sort(key=lambda veh: veh.name != specialVehicle.name)
        model.clearItems()
        for vehicle in vehicles:
            if withoutSpecialTank and vehicle.name == specialVehicle.name:
                continue
            item = PortalPremiumTanks()
            item.setName(vehicle.shortUserName if isShortName else vehicle.userName)
            model.addViewModel(item)

        model.invalidate()
        return


@replace_none_kwargs(boxesCtrl=ILootBoxesController)
def setGuaranteedAward(model, boxesCtrl=None):
    guaranteed, left = boxesCtrl.getLootBoxLimitsInfo(EventLootBoxes.WT_BOSS)
    model.setGuaranteedTankAttemptCount(guaranteed)
    model.setLeftAttemptsCount(left)
    model.setAttemptsCount(guaranteed - left)


def fillVehicleAward(model, bonusVehicle):
    if bonusVehicle is None:
        return
    else:
        fillVehicleModel(model.vehicle, bonusVehicle)
        return


def fillAdditionalAwards(model, bonuses, tooltipItems):
    model.clearItems()
    bonuses = sorted(bonuses, key=lambda bonus: sortBonuses(bonus, BOSS_ALL_BONUSES_ORDER))
    packBonusModelAndTooltipData(bonuses, model, tooltipItems, getWtEventBonusPacker)
