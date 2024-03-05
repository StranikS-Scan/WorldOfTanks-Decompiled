# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/comp7/gui/Scaleform/daapi/view/lobby/hangar/comp7_vehicle_parameters.py
import copy
from constants import BonusTypes, PenaltyTypes
from gui.Scaleform.daapi.view.lobby.hangar.VehicleParameters import VehicleParameters, _VehParamsDataProvider, _VehParamsGenerator
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.shared.items_parameters import params
from gui.shared.items_parameters.comparator import VehiclesComparator
from gui.shared.items_parameters.params import _PenaltyInfo
from gui.shared.items_parameters.params_cache import g_paramsCache
from helpers import dependency
from skeletons.gui.game_control import IComp7Controller
from skeletons.gui.shared import IItemsCache
from CurrentVehicle import g_currentVehicle
from comp7.gui.Scaleform.daapi.view.lobby.hangar.comp7_vehicle import g_comp7Vehicle

def _vehicleHealthCalcDiff(value, originalValue):
    return value - originalValue


def _visionRadiusCalcDiff(value, originalValue):
    if isinstance(value, tuple):
        return tuple([ val - original for val, original in zip(value, originalValue) ])
    return value - originalValue


_SUPPORTED_MODIFIERS = {'visionRadius': ('circularVisionRadius', _visionRadiusCalcDiff),
 'vehicleHealth': ('maxHealth', _vehicleHealthCalcDiff)}

@dependency.replace_none_kwargs(comp7Controller=IComp7Controller)
def appendBattleModifiersPenalties(penalties, modifiedParams, originalParams, comp7Controller=None):
    modifiers = comp7Controller.getBattleModifiersObject()
    if modifiers is not None:
        for _, modifier in modifiers:
            if modifier.gameplayImpact == 2 and modifier.param.name in _SUPPORTED_MODIFIERS:
                paramName, calcDiff = _SUPPORTED_MODIFIERS.get(modifier.param.name)
                section = penalties.get(paramName, [])
                value = modifiedParams[paramName]
                originalValue = originalParams[paramName]
                diff = calcDiff(value, originalValue)
                section.append(_PenaltyInfo('comp7', diff, False, PenaltyTypes.BATTLE_MODIFIERS))
                penalties[paramName] = section

    return


@dependency.replace_none_kwargs(comp7Controller=IComp7Controller)
def appendBattleModifiersBonuses(bonuses, comp7Controller=None):
    modifiers = comp7Controller.getBattleModifiersObject()
    if modifiers is not None:
        for _, modifier in modifiers:
            if modifier.gameplayImpact == 1 and modifier.param.name in _SUPPORTED_MODIFIERS:
                bonuses.add((modifier.param.name, BonusTypes.BATTLE_MODIFIERS))

    return


def comp7VehiclesComparator(modifiedVehicle, originalVehicle):
    vehicleParamsObject = params.VehicleParams(modifiedVehicle)
    originalVehicleParams = params.VehicleParams(originalVehicle).getParamsDict()
    vehicleParams = vehicleParamsObject.getParamsDict()
    bonuses = vehicleParamsObject.getBonuses(modifiedVehicle)
    appendBattleModifiersBonuses(bonuses)
    penalties = vehicleParamsObject.getPenalties(modifiedVehicle)
    appendBattleModifiersPenalties(penalties, vehicleParams, originalVehicleParams)
    compatibleArtefacts = g_paramsCache.getCompatibleArtefacts(modifiedVehicle)
    idealCrewVehicle = copy.copy(originalVehicle)
    idealCrewVehicle.crew = originalVehicle.getPerfectCrew()
    perfectVehicleParams = params.VehicleParams(idealCrewVehicle).getParamsDict()
    return VehiclesComparator(vehicleParams, perfectVehicleParams, compatibleArtefacts, bonuses, penalties)


class Comp7ParamsDataProvider(_VehParamsDataProvider):

    def _getComparator(self):
        return comp7VehiclesComparator(self._cache.item, self._cache.defaultItem)


class Comp7VehicleParameters(VehicleParameters):
    _comp7Controller = dependency.descriptor(IComp7Controller)
    _itemsCache = dependency.descriptor(IItemsCache)

    def _populate(self):
        super(Comp7VehicleParameters, self)._populate()
        g_currentVehicle.onChanged += self._onVehicleChanged
        self._onVehicleChanged()

    def _dispose(self):
        g_currentVehicle.onChanged -= self._onVehicleChanged
        g_comp7Vehicle.clear()
        super(Comp7VehicleParameters, self)._dispose()

    def _onVehicleChanged(self, *_):
        modifiers = self._comp7Controller.getBattleModifiersObject()
        if modifiers is not None and g_currentVehicle.isPresent():
            vehicle = self._itemsCache.items.getVehicleCopy(g_currentVehicle.item)
            vehicle.descriptor.battleModifiers = modifiers
            vehicle.descriptor.rebuildAttrs()
            g_comp7Vehicle.setCustomVehicle(vehicle)
        else:
            g_comp7Vehicle.setCustomVehicle(g_currentVehicle.item)
        self.rebuildParams()
        return

    def _getVehicleCache(self):
        return g_comp7Vehicle

    def _createDataProvider(self):
        return Comp7ParamsDataProvider(_VehParamsGenerator(tooltipType=TOOLTIPS_CONSTANTS.COMP7_VEHICLE_PARAMS_TOOLTIP))
