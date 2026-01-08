# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/hangar/modified_vehicle_parameters.py
import copy
from battle_modifiers_common import ModifiersContext
from constants import BonusTypes, PenaltyTypes
from gui.impl.lobby.hangar.modified_vehicle import g_modifiedVehicle
from gui.Scaleform.daapi.view.lobby.hangar.VehicleParameters import VehicleParameters, _VehParamsDataProvider, _VehParamsGenerator
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.impl.lobby.stronghold.stronghold_helpers import getBattleModifiersByPrbEntity, getBattleModifiersObject, getBattleModifiersDomain
from gui.prb_control.dispatcher import g_prbLoader
from gui.prb_control.entities.listener import IGlobalListener
from gui.shared.items_parameters import params
from gui.shared.items_parameters.comparator import VehiclesComparator
from gui.shared.items_parameters.params import _PenaltyInfo
from gui.shared.items_parameters.params_cache import g_paramsCache
from helpers import dependency
from skeletons.gui.shared import IItemsCache
from CurrentVehicle import g_currentVehicle

def _simpleValueDiff(value, originalValue):
    return value - originalValue


def _visionRadiusCalcDiff(value, originalValue):
    if isinstance(value, tuple):
        return tuple([ val - original for val, original in zip(value, originalValue) ])
    return value - originalValue


_SUPPORTED_MODIFIERS = {'visionRadius': ('circularVisionRadius', _visionRadiusCalcDiff),
 'radioDistance': ('radioDistance', _simpleValueDiff),
 'vehicleHealth': ('maxHealth', _simpleValueDiff),
 'thermalVisionDistance': ('thermalVisionDistance', _simpleValueDiff)}

def _getPrbEntity():
    dispatcher = g_prbLoader.getDispatcher()
    return dispatcher.getEntity()


def appendBattleModifiersPenalties(penalties, modifiedParams, originalParams):
    modifiers = getBattleModifiersObject(getBattleModifiersByPrbEntity(_getPrbEntity()))
    if modifiers is not None:
        for _, modifier in modifiers:
            if modifier.gameplayImpact == 2 and modifier.param.name in _SUPPORTED_MODIFIERS:
                paramName, calcDiff = _SUPPORTED_MODIFIERS.get(modifier.param.name)
                if paramName not in modifiedParams or paramName not in originalParams:
                    continue
                section = penalties.get(paramName, [])
                value = modifiedParams[paramName]
                originalValue = originalParams[paramName]
                diff = calcDiff(value, originalValue)
                section.append(_PenaltyInfo(getBattleModifiersDomain(), diff, False, PenaltyTypes.BATTLE_MODIFIERS))
                penalties[paramName] = section

    return


def appendBattleModifiersBonuses(bonuses):
    modifiers = getBattleModifiersObject(getBattleModifiersByPrbEntity(_getPrbEntity()))
    if modifiers is not None:
        for _, modifier in modifiers:
            if modifier.gameplayImpact == 1 and modifier.param.name in _SUPPORTED_MODIFIERS:
                bonuses.add((modifier.param.name, BonusTypes.BATTLE_MODIFIERS))

    return


def modifiedVehiclesComparator(modifiedVehicle, originalVehicle):
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


class ModifiedParamsDataProvider(_VehParamsDataProvider):

    def _getComparator(self):
        return modifiedVehiclesComparator(self._cache.item, self._cache.defaultItem)


class ModifiedVehicleParameters(VehicleParameters, IGlobalListener):
    _itemsCache = dependency.descriptor(IItemsCache)

    def _populate(self):
        super(ModifiedVehicleParameters, self)._populate()
        self.startGlobalListening()
        g_currentVehicle.onChanged += self._onVehicleChanged
        self._onVehicleChanged()

    def _dispose(self):
        g_currentVehicle.onChanged -= self._onVehicleChanged
        self.stopGlobalListening()
        g_modifiedVehicle.clear()
        super(ModifiedVehicleParameters, self)._dispose()

    def onStrongholdDataChanged(self, header, isFirstBattle, reserve, reserveOrder):
        self._onVehicleChanged()

    def onPrbEntitySwitched(self):
        self._onVehicleChanged()

    def _onVehicleChanged(self, *_):
        modifiers = getBattleModifiersObject(getBattleModifiersByPrbEntity(_getPrbEntity()))
        if modifiers is not None and g_currentVehicle.isPresent():
            vehicle = self._itemsCache.items.getVehicleCopy(g_currentVehicle.item)
            vehicle.descriptor.battleModifiers = ModifiersContext(modifiers, vehType=vehicle.descriptor.type)
            vehicle.descriptor.rebuildAttrs()
            g_modifiedVehicle.setCustomVehicle(vehicle)
        else:
            g_modifiedVehicle.setCustomVehicle(g_currentVehicle.item)
        self.rebuildParams()
        return

    def _getVehicleCache(self):
        return g_modifiedVehicle

    def _createDataProvider(self):
        return ModifiedParamsDataProvider(_VehParamsGenerator(tooltipType=TOOLTIPS_CONSTANTS.MODIFIED_VEHICLE_PARAMS_TOOLTIP))
