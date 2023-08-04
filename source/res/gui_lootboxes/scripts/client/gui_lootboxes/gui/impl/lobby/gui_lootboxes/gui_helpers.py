# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: gui_lootboxes/scripts/client/gui_lootboxes/gui/impl/lobby/gui_lootboxes/gui_helpers.py
from gui_lootboxes.gui.impl.gen.view_models.views.lobby.gui_lootboxes.lb_bonus_type_model import BonusType
VEHICLES_BONUS_NAME = 'vehicles'

def detectBonusType(bonuses):
    isVehicleBonus = any((bonus.getName() == VEHICLES_BONUS_NAME for bonus in bonuses))
    if isVehicleBonus:
        for bonus in bonuses:
            if bonus.getName() == VEHICLES_BONUS_NAME:
                _, vehInfo = bonus.getVehicles()[0]
                isRentedVehicle = bonus.isRentVehicle(vehInfo)
                if isRentedVehicle:
                    return BonusType.RENTEDVEHICLE
                return BonusType.VEHICLE

    return BonusType.DEFAULT
