# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/Scaleform/daapi/view/lobby/hangar/hw_vehicle_params.py
import functools
import copy
import BigWorld
from gui.Scaleform.daapi.view.lobby.hangar.VehicleParameters import VehicleParameters
from gui.prb_control.entities.listener import IGlobalListener
from gui.Scaleform.daapi.view.lobby.hangar.VehicleParameters import _VehParamsDataProvider, _VehParamsGenerator
from constants import QUEUE_TYPE, PREBATTLE_TYPE
from gui.shared import g_eventBus, EVENT_BUS_SCOPE
from gui.shared.events import AmmunitionSetupViewEvent
from gui.shared.items_parameters.comparator import VehiclesComparator
from gui.shared.items_parameters.params_cache import g_paramsCache
from buffs_helpers import makeBuffName, ModifiersDict, ValueSimpleModifier
from buffs import ClientBuffsRepository
from debug_utils import LOG_ERROR
from gui.shared.items_parameters import params

class PropertyAutoOverride(type):

    def __new__(mcs, name, bases, dct):
        x = super(PropertyAutoOverride, mcs).__new__(mcs, name, bases, dct)
        for b in bases:
            for k, v in b.__dict__.iteritems():
                if isinstance(v, property) and k not in dct:
                    setattr(x, k, property(functools.partial(x.overrideProperty, k)))

        return x


class HWVehicleParams(params.VehicleParams):
    __metaclass__ = PropertyAutoOverride
    TTC_MODIFIER_COMPONENT_NAME = 'ttcModifier'

    def __init__(self, vehicle):
        super(HWVehicleParams, self).__init__(vehicle)
        self.ttcModifiers = self.collectModifiers(vehicle)

    def collectModifiers(self, vehicle):
        buffsRepo = ClientBuffsRepository.getInstance()
        hwEq = [ eq.descriptor for eq in vehicle.hwConsumables.installed.getItems() ]
        buffsFactories = [ buffsRepo.getBuffFactoryByName(makeBuffName(buffName, vehicle.descriptor)) for eq in hwEq if hasattr(eq, 'buffNames') for buffName in eq.buffNames ]
        modifiers = sum((compFactory.config.ttcModifiers for buffFactory in buffsFactories if buffFactory is not None for compFactory in buffFactory.componentFactories if compFactory.name == self.TTC_MODIFIER_COMPONENT_NAME), ModifiersDict())
        return modifiers

    def __getattr__(self, name):
        return self.overrideProperty(name, self, super(HWVehicleParams, self).__getattr__(name))

    @classmethod
    def overrideProperty(cls, name, self, propertyValue=None):
        result = propertyValue if propertyValue is not None else getattr(super(cls, self), name)
        modifiers = self.ttcModifiers.getModifiers(name)
        if result is None or not modifiers:
            return result
        else:
            modifiedResult, error = ValueSimpleModifier(modifiers).apply(result)
            if modifiedResult is None:
                LOG_ERROR('HWVehicleParams unable to apply modifiers for property <{}>, error <{}>'.format(name, error))
                return result
            return modifiedResult


class HWDataProvider(_VehParamsDataProvider, IGlobalListener):

    def _getComparator(self):
        return self.hwVehicleComparator(self._cache.item) if self.prbDispatcher is not None and (self.prbDispatcher.getFunctionalState().isInPreQueue(QUEUE_TYPE.HALLOWEEN_BATTLES) or self.prbDispatcher.getFunctionalState().isInUnit(PREBATTLE_TYPE.HALLOWEEN_BATTLES) or self.prbDispatcher.getFunctionalState().isInPreQueue(QUEUE_TYPE.HALLOWEEN_BATTLES_WHEEL)) else super(HWDataProvider, self)._getComparator()

    @staticmethod
    def hwVehicleComparator(vehicle):
        hwEqCtrl = BigWorld.player().HWAccountEquipmentController
        vehicleParamsObject = HWVehicleParams(hwEqCtrl.makeVehicleHWAdapter(vehicle))
        vehicleParams = vehicleParamsObject.getParamsDict()
        bonuses = vehicleParamsObject.getBonuses(vehicle)
        penalties = vehicleParamsObject.getPenalties(vehicle)
        compatibleArtefacts = g_paramsCache.getCompatibleArtefacts(vehicle)
        idealCrewVehicle = copy.copy(vehicle)
        idealCrewVehicle.crew = vehicle.getPerfectCrew()
        perfectVehicleParams = HWVehicleParams(hwEqCtrl.makeVehicleHWAdapter(idealCrewVehicle)).getParamsDict()
        return VehiclesComparator(vehicleParams, perfectVehicleParams, compatibleArtefacts, bonuses, penalties)


class HWVehicleParameters(VehicleParameters, IGlobalListener):

    def onPrbEntitySwitched(self):
        self.update()

    def _populate(self):
        super(HWVehicleParameters, self)._populate()
        g_eventBus.addListener(AmmunitionSetupViewEvent.UPDATE_TTC, self.update, EVENT_BUS_SCOPE.LOBBY)

    def _dispose(self):
        g_eventBus.removeListener(AmmunitionSetupViewEvent.UPDATE_TTC, self.update, EVENT_BUS_SCOPE.LOBBY)
        super(HWVehicleParameters, self)._dispose()

    def _createDataProvider(self):
        return HWDataProvider(_VehParamsGenerator())
