# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/cgf_components_common/managers/state_managers.py
import CGF
import logging
from cgf_script.managers_registrator import onAddedQuery, onRemovedQuery, autoregister
from constants import IS_CLIENT, IS_CELLAPP
from GenericComponents import HealthGradationComponent, EHealthGradation
from cgf_components_common.state_components import StateSwitcherComponent
from functools import partial
_logger = logging.getLogger(__name__)
if IS_CLIENT or IS_CELLAPP:
    from HealthComponent import HealthComponent
else:
    from cgf_components_common.state_components import HealthComponent

@autoregister(presentInAllWorlds=True, domain=CGF.DomainOption.DomainClient | CGF.DomainOption.DomainServer)
class StateSwitcherManager(CGF.ComponentManager):

    @onAddedQuery(CGF.GameObject, HealthComponent, StateSwitcherComponent, HealthGradationComponent)
    def onAdded(self, go, health, switcher, *_):
        stateLink = CGF.ComponentLink(go, StateSwitcherComponent)
        gradationLink = CGF.ComponentLink(go, HealthGradationComponent)
        self.__validateSettings(switcher)
        switcher.callback = partial(self.__onHealthChanged, stateLink, gradationLink)
        health.onHealthChanged += switcher.callback
        self.__onHealthChanged(stateLink, gradationLink, health.health, health.health, health.maxHealth)

    @onRemovedQuery(StateSwitcherComponent, HealthComponent)
    def onRemoved(self, switcher, health, *_):
        if not health.entity.isDestroyed:
            health.onHealthChanged -= switcher.callback
        self.__deactivateAll(switcher)

    def __activateState(self, go):
        if go is not None and go.isValid() and not go.isActive():
            go.activate()
        return

    def __deactivateState(self, go):
        if go is not None and go.isValid() and go.isActive():
            go.deactivate()
        return

    def __activateNormalState(self, switcher):
        self.__activateState(switcher.normal)
        self.__deactivateState(switcher.damaged)
        self.__deactivateState(switcher.critical)

    def __activateDamagedState(self, switcher):
        self.__deactivateState(switcher.normal)
        self.__activateState(switcher.damaged)
        self.__deactivateState(switcher.critical)

    def __activateCriticalState(self, switcher):
        self.__deactivateState(switcher.normal)
        self.__deactivateState(switcher.damaged)
        self.__activateState(switcher.critical)

    def __deactivateAll(self, switcher):
        self.__deactivateState(switcher.normal)
        self.__deactivateState(switcher.damaged)
        self.__deactivateState(switcher.critical)

    def __validateSettings(self, switcher):
        if not switcher.normal.isValid():
            _logger.warning('Incorrect switcher setup, missing Normal state prefab')
        if not switcher.damaged.isValid():
            _logger.warning('Incorrect switcher setup, missing Damaged state prefab')
        if not switcher.critical.isValid():
            _logger.warning('Incorrect switcher setup, missing Critical state prefab')

    def __onHealthChanged(self, stateLink, gradationLink, old, health, maxHealth):
        state = stateLink()
        gradation = gradationLink()
        if state is None:
            _logger.error('Failed to get StateSwitcherComponent, state is incorrect')
            return
        elif gradationLink is None:
            _logger.error('Failed to get HealthGradationComponent, state is incorrect')
            return
        zone = gradation.getHealthZone(health, maxHealth)
        if zone == EHealthGradation.GREEN_ZONE:
            self.__activateNormalState(state)
            return
        elif zone == EHealthGradation.YELLOW_ZONE:
            self.__activateDamagedState(state)
            return
        elif zone == EHealthGradation.RED_ZONE:
            self.__activateCriticalState(state)
            return
        else:
            return
