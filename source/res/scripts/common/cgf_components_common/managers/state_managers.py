# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/cgf_components_common/managers/state_managers.py
from __future__ import absolute_import
import CGF
import logging
from GenericComponents import HealthGradationComponent, EHealthGradation, StateSwitcherComponent
from functools import partial
from constants import IS_UNKNOWN
_logger = logging.getLogger(__name__)
if IS_UNKNOWN:

    class HealthComponent(object):
        pass


else:
    from HealthComponent import HealthComponent

class StateSwitcherSystem(CGF.System):
    StateActivated = CGF.ActivateReaction(CGF.GameObject, CGF.ReactRw(StateSwitcherComponent), CGF.ReactRw(HealthComponent), CGF.Has(HealthGradationComponent))
    StateDeactivated = CGF.DeactivateReaction(CGF.GameObject, CGF.ReactRw(StateSwitcherComponent), CGF.ReactRw(HealthComponent))
    StateAccess = CGF.AccessReaction(CGF.Rw(StateSwitcherComponent))
    GradationAccess = CGF.AccessReaction(HealthGradationComponent)
    Reactions = CGF.Reactions(StateActivated, StateDeactivated, StateAccess, GradationAccess)

    def __init__(self):
        super(StateSwitcherSystem, self).__init__()
        self.__switcherCallbacks = {}

    def update(self):
        for go, switcher, health in self.reaction(self.StateDeactivated):
            callback = self.__switcherCallbacks.pop(go, None)
            entity = health.entity
            if callback is not None and entity is not None and not entity.isDestroyed:
                health.onHealthChanged -= callback
            switcher.requestState(StateSwitcherComponent.NONE_STATE)

        for go, switcher, health in self.reaction(self.StateActivated):
            callback = partial(self.__onHealthChanged, go)
            self.__switcherCallbacks[go] = callback
            health.onHealthChanged += callback
            self.__onHealthChanged(go, health.health, health.health, health.maxHealth)

        return

    def __onHealthChanged(self, go, old, health, maxHealth):
        stateAccess = self.reaction(self.StateAccess)
        switcher = stateAccess.find(go)
        if not switcher:
            _logger.error('Failed to get StateSwitcherComponent, state is incorrect')
            return
        gradationAccess = self.reaction(self.GradationAccess)
        gradation = gradationAccess.find(go)
        if not gradation:
            _logger.error('Failed to get HealthGradationComponent, state is incorrect')
            return
        zone = gradation.getHealthZone(health, maxHealth)
        if zone == EHealthGradation.GREEN_ZONE:
            switcher.requestState(StateSwitcherComponent.NORMAL_STATE)
            return
        if zone == EHealthGradation.YELLOW_ZONE:
            switcher.requestState(StateSwitcherComponent.DAMAGED_STATE)
            return
        if zone == EHealthGradation.RED_ZONE:
            switcher.requestState(StateSwitcherComponent.CRITICAL_STATE)
            return
