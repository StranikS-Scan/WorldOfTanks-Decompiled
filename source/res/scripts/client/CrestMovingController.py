# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/CrestMovingController.py
from __future__ import absolute_import
import logging
import typing
from constants import CREST_MOVING_STATE
from vehicles.components.vehicle_component import VehicleDynamicComponent
from vehicles.mechanics.common import IMechanicComponent
from vehicles.mechanics.mechanic_constants import VehicleMechanic
from vehicles.mechanics.mechanic_states import IMechanicState, IMechanicStatesComponent, createMechanicStatesEvents
if typing.TYPE_CHECKING:
    from typing import Any
    from vehicles.mechanics.mechanic_states import IMechanicStatesEvents
_logger = logging.getLogger(__name__)

class CrestMovingState(typing.NamedTuple('CrestMovingState', (('state', CREST_MOVING_STATE),)), IMechanicState):

    @classmethod
    def fromComponentStatus(cls, status):
        return cls(CREST_MOVING_STATE(status))

    def isTransition(self, other):
        return self.state != other.state


class CrestMovingController(VehicleDynamicComponent, IMechanicComponent, IMechanicStatesComponent):
    DEFAULT_MODE_STATE = CrestMovingState(CREST_MOVING_STATE.STOPPED)

    def __init__(self):
        super(CrestMovingController, self).__init__()
        self.__statesEvents = createMechanicStatesEvents(self)
        self._initComponent()

    @property
    def vehicleMechanic(self):
        return VehicleMechanic.CREST_MOVING

    @property
    def statesEvents(self):
        return self.__statesEvents

    def getMechanicState(self):
        return CrestMovingState.fromComponentStatus(self.state) if self.state is not None else self.DEFAULT_MODE_STATE

    def set_state(self, prevState=None):
        _logger.debug('set_state: prev=%s, current=%s', prevState, self.state)
        self._updateComponentAppearance()

    def onDestroy(self):
        self.__statesEvents.destroy()
        super(CrestMovingController, self).onDestroy()

    def _onAppearanceReady(self):
        super(CrestMovingController, self)._onAppearanceReady()
        self.__statesEvents.processStatePrepared()

    def _onComponentAppearanceUpdate(self, **kwargs):
        super(CrestMovingController, self)._onComponentAppearanceUpdate(**kwargs)
        self.__statesEvents.updateMechanicState(self.getMechanicState())
