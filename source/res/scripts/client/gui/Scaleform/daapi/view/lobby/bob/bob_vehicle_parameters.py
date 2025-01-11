# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/bob/bob_vehicle_parameters.py
import copy
from constants import BonusTypes, PenaltyTypes
from gui.Scaleform.daapi.view.lobby.hangar.VehicleParameters import VehicleParameters, _VehParamsDataProvider, _VehParamsGenerator
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.shared.items_parameters import params
from gui.shared.items_parameters.comparator import VehiclesComparator
from gui.shared.items_parameters.params import _PenaltyInfo
from gui.shared.items_parameters.params_cache import g_paramsCache
from gui.Scaleform.daapi.view.lobby.bob.bob_vehicle import g_bobVehicle
from skeletons.gui.game_control import IBobController
from helpers import dependency
from skeletons.gui.shared import IItemsCache
from CurrentVehicle import g_currentVehicle
from battle_modifiers_common import BattleModifiers

def _vehicleHealthCalcDiff(value, originalValue):
    return value - originalValue


def _visionRadiusCalcDiff(value, originalValue):
    if isinstance(value, tuple):
        return tuple([ val - original for val, original in zip(value, originalValue) ])
    return value - originalValue


_SUPPORTED_MODIFIERS = {'visionRadius': ('circularVisionRadius', _visionRadiusCalcDiff),
 'vehicleHealth': ('maxHealth', _vehicleHealthCalcDiff)}

@dependency.replace_none_kwargs(bobController=IBobController)
def appendBattleModifiersPenalties(penalties, modifiedParams, originalParams, bobController=None):
    modifiers = BattleModifiers(bobController.battleModifiers)
    for _, modifier in modifiers:
        if modifier.gameplayImpact == 2 and modifier.param.name in _SUPPORTED_MODIFIERS:
            paramName, calcDiff = _SUPPORTED_MODIFIERS.get(modifier.param.name)
            section = penalties.get(paramName, [])
            value = modifiedParams[paramName]
            originalValue = originalParams[paramName]
            diff = calcDiff(value, originalValue)
            section.append(_PenaltyInfo('bob', diff, False, PenaltyTypes.BATTLE_MODIFIERS))
            penalties[paramName] = section


@dependency.replace_none_kwargs(bobController=IBobController)
def appendBattleModifiersBonuses(bonuses, bobController=None):
    modifiers = BattleModifiers(bobController.battleModifiers)
    for _, modifier in modifiers:
        if modifier.gameplayImpact == 1 and modifier.param.name in _SUPPORTED_MODIFIERS:
            bonuses.add((modifier.param.name, BonusTypes.BATTLE_MODIFIERS))


def bobVehiclesComparator(modifiedVehicle, originalVehicle):
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


class BobParamsDataProvider(_VehParamsDataProvider):

    def _getComparator(self):
        return bobVehiclesComparator(self._cache.item, self._cache.defaultItem)


class BobVehicleParameters(VehicleParameters):
    _bobController = dependency.descriptor(IBobController)
    _itemsCache = dependency.descriptor(IItemsCache)

    def _populate(self):
        super(BobVehicleParameters, self)._populate()
        g_currentVehicle.onChanged += self._onVehicleChanged
        self._onVehicleChanged()

    def _dispose(self):
        g_currentVehicle.onChanged -= self._onVehicleChanged
        g_bobVehicle.clear()
        super(BobVehicleParameters, self)._dispose()

    def _onVehicleChanged(self, *_):
        modifiers = BattleModifiers(self._bobController.battleModifiers)
        if g_currentVehicle.isPresent():
            vehicle = self._itemsCache.items.getVehicleCopy(g_currentVehicle.item, battleModifiers=modifiers)
            g_bobVehicle.setCustomVehicle(vehicle)
        self.rebuildParams()

    def _getVehicleCache(self):
        return g_bobVehicle

    def _createDataProvider(self):
        return BobParamsDataProvider(_VehParamsGenerator(tooltipType=TOOLTIPS_CONSTANTS.BOB_VEHICLE_PARAMS_TOOLTIP))
