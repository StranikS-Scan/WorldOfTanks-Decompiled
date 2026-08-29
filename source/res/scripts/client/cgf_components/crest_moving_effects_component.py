# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/cgf_components/crest_moving_effects_component.py
from __future__ import absolute_import
import logging
from typing import TYPE_CHECKING
import CGF
from Event import Event
from Sound import Sound3DComponent
from cgf_script.registration import ComponentProperty, registerComponent
from events_containers.common.containers import ContainersListener
from events_handler import eventHandler
from vehicles.mechanics.mechanic_states import IMechanicStatesListenerLogic
from vehicles.mechanics.mechanic_trackers import IVehicleMechanicsTrackerListenerLogic
if TYPE_CHECKING:
    pass
_logger = logging.getLogger(__name__)

@registerComponent
class CrestMovingEffectsComponent(ContainersListener, IVehicleMechanicsTrackerListenerLogic, IMechanicStatesListenerLogic):
    category = 'Vehicle Mechanics'
    editorTitle = 'Crest Moving Effects Component'
    domain = CGF.Domain.Client | CGF.Domain.Editor
    soundMoveUp = ComponentProperty(type=CGF.PropertyType.Link, editorName='Sound Move up node', value=Sound3DComponent)
    soundMoveDown = ComponentProperty(type=CGF.PropertyType.Link, editorName='Sound Move down node', value=Sound3DComponent)
    soundStopUp = ComponentProperty(type=CGF.PropertyType.Link, editorName='Sound Stop up node', value=Sound3DComponent)
    soundStopDown = ComponentProperty(type=CGF.PropertyType.Link, editorName='Sound Stop down node', value=Sound3DComponent)

    def __init__(self):
        super(CrestMovingEffectsComponent, self).__init__()
        self.onStateTransitionEvent = Event()
        self.activeSound = None
        self.stopSound = None
        self.vehicleID = None
        return

    @eventHandler
    def onMechanicComponentCatching(self, component):
        _logger.debug('onMechanicComponentCatching: %s', component)
        component.statesEvents.lateSubscribe(self)

    @eventHandler
    def onMechanicComponentReleasing(self, component):
        _logger.debug('onMechanicComponentReleasing: %s', component)
        self.unsubscribeFrom(component.statesEvents)

    @eventHandler
    def onStateTransition(self, prevState, newState):
        _logger.debug('onStateTransition: %s -> %s', prevState, newState)
        self.onStateTransitionEvent(self, prevState, newState)
