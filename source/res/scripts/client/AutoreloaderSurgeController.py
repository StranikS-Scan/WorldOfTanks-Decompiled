# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/AutoreloaderSurgeController.py
from __future__ import absolute_import, division
import logging
import typing
import BigWorld
from constants import AUTORELOADER_SURGE_RESTRICTION, AUTORELOADER_SURGE_STATE
from gui.shared.utils.decorators import ReprInjector
from math_utils import clamp01
from vehicles.components.vehicle_component import VehicleDynamicComponent
from vehicles.components.vehicle_prefabs import createMechanicPrefabSpawner
from vehicles.mechanics.common import IMechanicComponent
from vehicles.mechanics.mechanic_commands import IMechanicCommandsComponent, createMechanicCommandsEvents
from vehicles.mechanics.mechanic_constants import VehicleMechanic, VehicleMechanicCommand
from vehicles.mechanics.mechanic_helpers import getVehicleDescrMechanicParams
from vehicles.mechanics.mechanic_states import IMechanicState, IMechanicStatesComponent, createMechanicStatesEvents
if typing.TYPE_CHECKING:
    from typing import Any, Dict, Optional
    from items.components.shared_components import AutoreloaderSurgeParams
    from vehicles.mechanics.mechanic_commands import IMechanicCommandsEvents
    from vehicles.mechanics.mechanic_states import IMechanicStatesEvents
_LOG_AUTORELOADER_SURGE_DEBUG = True
_logger = logging.getLogger(__name__)

@ReprInjector.simple('state', 'restrictions', 'ncharges', 'chargeIntervalStart', 'chargeIntervalEnd')
class AutoreloaderSurgeState(typing.NamedTuple('AutoreloaderSurgeState', (('state', AUTORELOADER_SURGE_STATE),
 ('restrictions', AUTORELOADER_SURGE_RESTRICTION),
 ('ncharges', int),
 ('chargeIntervalStart', float),
 ('chargeIntervalEnd', float))), IMechanicState):

    def __init__(self, state, restrictions, *args):
        if state == AUTORELOADER_SURGE_STATE.UNAVAILABLE:
            restrictions |= AUTORELOADER_SURGE_RESTRICTION.UNAVAILABLE
        else:
            restrictions &= ~AUTORELOADER_SURGE_RESTRICTION.UNAVAILABLE
        if state == AUTORELOADER_SURGE_STATE.IN_USE:
            restrictions |= AUTORELOADER_SURGE_RESTRICTION.ALREADY_ACTIVE
        else:
            restrictions &= ~AUTORELOADER_SURGE_RESTRICTION.ALREADY_ACTIVE
        super(AutoreloaderSurgeState, self).__init__(state, restrictions, *args)

    @classmethod
    def fromComponentStatus(cls, status):
        return cls(AUTORELOADER_SURGE_STATE(status.state), status.restrictions, int(status.charges), status.chargeTimeInterval['startTime'], status.chargeTimeInterval['endTime'])

    @property
    def chargeTime(self):
        return self.chargeIntervalEnd - self.chargeIntervalStart

    @property
    def progress(self):
        if self.state != AUTORELOADER_SURGE_STATE.CHARGING:
            return 0.0
        chargeTime = self.chargeTime
        if chargeTime <= 0:
            _logger.error('chargeTime must be > 0, got %s, state=%s', chargeTime, self)
            return 0.0
        currTime = BigWorld.serverTime() - self.chargeIntervalStart
        return clamp01(currTime / chargeTime)

    def isTransition(self, other):
        return self.state != other.state or self.ncharges != other.ncharges


@ReprInjector.withParent()
class AutoreloaderSurgeController(VehicleDynamicComponent, IMechanicComponent, IMechanicCommandsComponent, IMechanicStatesComponent):

    def __init__(self):
        super(AutoreloaderSurgeController, self).__init__()
        self.__params = None
        self.__mechanicPrefabSpawner = createMechanicPrefabSpawner(self.entity, self)
        self.__commandsEvents = createMechanicCommandsEvents(self, withDebug=_LOG_AUTORELOADER_SURGE_DEBUG)
        self.__statesEvents = createMechanicStatesEvents(self, withDebug=_LOG_AUTORELOADER_SURGE_DEBUG)
        self.__mechanicState = AutoreloaderSurgeState(AUTORELOADER_SURGE_STATE.UNAVAILABLE, AUTORELOADER_SURGE_RESTRICTION.UNAVAILABLE, 0, 0.0, 0.0)
        self._initComponent()
        return

    @property
    def vehicleMechanic(self):
        return VehicleMechanic.AUTORELOADER_SURGE

    @property
    def commandsEvents(self):
        return self.__commandsEvents

    @property
    def statesEvents(self):
        return self.__statesEvents

    def getMechanicState(self):
        return self.__mechanicState

    def getComponentParams(self):
        return self.__params

    def set_abilityState(self, *_):
        self._updateComponentAppearance()

    def onDestroy(self):
        self.__params = None
        self.__commandsEvents.destroy()
        self.__statesEvents.destroy()
        super(AutoreloaderSurgeController, self).onDestroy()
        return

    def tryActivate(self):
        self.__commandsEvents.processMechanicCommand(VehicleMechanicCommand.ACTIVATE)
        if self.__mechanicState.restrictions == AUTORELOADER_SURGE_RESTRICTION.NO_RESTRICTION:
            self.cell.activate()
            return True
        return False

    def _onAppearanceReady(self):
        super(AutoreloaderSurgeController, self)._onAppearanceReady()
        self.__updateMechanicState()
        self.__statesEvents.processStatePrepared()

    def _onComponentAppearanceUpdate(self, **kwargs):
        super(AutoreloaderSurgeController, self)._onComponentAppearanceUpdate(**kwargs)
        self.__updateMechanicState()
        self.__statesEvents.updateMechanicState(self.__mechanicState)

    def _collectComponentParams(self, typeDescriptor):
        super(AutoreloaderSurgeController, self)._collectComponentParams(typeDescriptor)
        self.__params = getVehicleDescrMechanicParams(typeDescriptor, self.vehicleMechanic)

    def __updateMechanicState(self):
        self.__mechanicState = AutoreloaderSurgeState.fromComponentStatus(self.abilityState)
