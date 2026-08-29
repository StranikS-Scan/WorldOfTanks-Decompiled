# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/vehicles/mechanics/mechanic_inputs/mechanic_base_input.py
from __future__ import absolute_import
from typing import TYPE_CHECKING
from events_containers.common.containers import ContainersListener
from events_containers.components.life_cycle import IComponentLifeCycleListenerLogic
from events_handler import eventHandler
if TYPE_CHECKING:
    from events_containers.components.life_cycle import ILifeCycleComponent
    from vehicles.mechanics.mechanic_inputs.mechanic_input_profile import MechanicInputProfile

class BaseMechanicInput(ContainersListener, IComponentLifeCycleListenerLogic):

    def __init__(self):
        super(BaseMechanicInput, self).__init__()
        self._profiles = []

    @eventHandler
    def onComponentAvatarReady(self, _):
        for profile in self._profiles:
            profile.attach()

    @eventHandler
    def onComponentDestroyed(self, _):
        for profile in self._profiles:
            profile.deactivate()
            profile.destroy()

    def _register(self, profile):
        self._profiles.append(profile)
        return profile
