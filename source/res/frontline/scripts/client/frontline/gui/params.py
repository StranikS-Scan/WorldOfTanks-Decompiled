# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: frontline/scripts/client/frontline/gui/params.py
from gui.shared.gui_items.Vehicle import Vehicle
from gui.shared.items_parameters.formatters import formatParameter, FORMAT_SETTINGS, _niceRangeFormat
from gui.shared.items_parameters.params import VehicleParams
from helpers import dependency
from skeletons.gui.game_control import IEpicBattleMetaGameController
from supply_shared import Supply
SUPPLY_PARAMS_KEYS = ('avgDamage', 'avgPiercingPower', 'flameMaxDistance', 'clipFireRate', 'reloadTimeSecs', 'shotDispersionAngle', 'maxHealth', 'turretArmor', 'circularVisionRadius', 'captureTime', 'resurrectTime', 'cooldownTime', 'healTime', 'gunYawLimits')

def _generateSettings():
    s = {'healTime': _niceRangeFormat}
    s.update(FORMAT_SETTINGS)
    return s


_FORMAT_SETTINGS = _generateSettings()

class SupplyParams(VehicleParams):
    __epicMetaController = dependency.descriptor(IEpicBattleMetaGameController)

    @property
    def resurrectTime(self):
        supplyID = Supply.getID(self._itemDescr.type)
        return self.__epicMetaController.getSupplyParams()[supplyID]['resurrectTime'] if supplyID != Supply.AIRSHIP else None

    @property
    def captureTime(self):
        supplyID = Supply.getID(self._itemDescr.type)
        return None if supplyID != Supply.AIRSHIP else self.__epicMetaController.getSupplyParams()[supplyID]['captureTime']

    @property
    def cooldownTime(self):
        supplyID = Supply.getID(self._itemDescr.type)
        return None if supplyID != Supply.AIRSHIP else self.__epicMetaController.getSupplyParams()[supplyID]['cooldownTime']


def getSupplyParameters(vehicle):
    params = SupplyParams(vehicle).getParamsDict()
    filteredParams = {key:formatParameter(key, params.get(key), formatSettings=_FORMAT_SETTINGS) for key in SUPPLY_PARAMS_KEYS}
    return filteredParams


def getArmorDamageFactors(descriptor):
    hullDamageFactor = min((matInfo.vehicleDamageFactor for matInfo in descriptor.hull.materials.itervalues()))
    turretDamageFactor = min((matInfo.vehicleDamageFactor for matInfo in descriptor.turret.materials.itervalues()))
    return (hullDamageFactor, turretDamageFactor)
