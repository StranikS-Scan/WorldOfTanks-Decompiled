# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/easy_tank_equip/easy_tank_equip_helpers.py
import typing
from account_helpers import AccountSettings
from account_helpers.AccountSettings import EasyTankEquip
from helpers import dependency
from skeletons.gui.game_control import IEasyTankEquipController
if typing.TYPE_CHECKING:
    from gui.shared.gui_items.Vehicle import Vehicle

@dependency.replace_none_kwargs(easyTankEquipController=IEasyTankEquipController)
def isAvailableForVehicle(vehicle, easyTankEquipController=None):
    return vehicle is not None and vehicle.level >= easyTankEquipController.config.minVehicleLevel


def getEasyTankEquipSetting(settingName):
    return AccountSettings.getSettings(EasyTankEquip.EASY_TANK_EQUIP_SETTINGS).get(settingName)


def setEasyTankEquipSetting(settingName, settingValue):
    settings = AccountSettings.getSettings(EasyTankEquip.EASY_TANK_EQUIP_SETTINGS)
    settings.update({settingName: settingValue})
    AccountSettings.setSettings(EasyTankEquip.EASY_TANK_EQUIP_SETTINGS, settings)
