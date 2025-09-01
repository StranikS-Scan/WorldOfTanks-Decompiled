# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/cgf_components_common/managers/state_managers.py
import CGF
import logging
from cgf_script.managers_registrator import onAddedQuery, onRemovedQuery, autoregister
from GenericComponents import HealthGradationComponent, EHealthGradation, StateSwitcherComponent
from functools import partial
from HealthComponent import HealthComponent
_logger = logging.getLogger(__name__)

@autoregister(presentInAllWorlds=True, domain=CGF.DomainOption.DomainClient | CGF.DomainOption.DomainServer)
class StateSwitcherManager(CGF.ComponentManager):

    def __init__(self):
        super(StateSwitcherManager, self).__init__()
        self.__switcherCallbacks = {}

    @onAddedQuery(CGF.GameObject, HealthComponent, StateSwitcherComponent, HealthGradationComponent)
    def onAdded(self, go, health, *_):
        switcherLink = CGF.ComponentLink(go, StateSwitcherComponent)
        gradationLink = CGF.ComponentLink(go, HealthGradationComponent)
        callback = partial(self.__onHealthChanged, switcherLink, gradationLink)
        self.__switcherCallbacks[go.id] = callback
        health.onHealthChanged += callback
        self.__onHealthChanged(switcherLink, gradationLink, health.health, health.health, health.maxHealth)

    @onRemovedQuery(CGF.GameObject, StateSwitcherComponent, HealthComponent)
    def onRemoved(self, go, switcher, health, *_):
        callback = self.__switcherCallbacks.pop(go.id, None)
        entity = health.entity
        if callback is not None and entity is not None and not entity.isDestroyed:
            health.onHealthChanged -= callback
        switcher.requestState(StateSwitcherComponent.NONE_STATE)
        return

    def __onHealthChanged(self, switcherLink, gradationLink, old, health, maxHealth):
        switcher = switcherLink()
        gradation = gradationLink()
        if switcher is None:
            _logger.error('Failed to get StateSwitcherComponent, state is incorrect')
            return
        elif gradationLink is None:
            _logger.error('Failed to get HealthGradationComponent, state is incorrect')
            return
        zone = gradation.getHealthZone(health, maxHealth)
        if zone == EHealthGradation.GREEN_ZONE:
            switcher.requestState(StateSwitcherComponent.NORMAL_STATE)
            return
        elif zone == EHealthGradation.YELLOW_ZONE:
            switcher.requestState(StateSwitcherComponent.DAMAGED_STATE)
            return
        elif zone == EHealthGradation.RED_ZONE:
            switcher.requestState(StateSwitcherComponent.CRITICAL_STATE)
            return
        else:
            return
