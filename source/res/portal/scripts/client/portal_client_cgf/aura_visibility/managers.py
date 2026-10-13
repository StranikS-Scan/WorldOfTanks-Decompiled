# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: portal/scripts/client/portal_client_cgf/aura_visibility/managers.py
import typing
from GenericComponents import AnimatorComponent
from PortalAuraComponent import PortalAuraComponent
import BigWorld
import CGF
import logging
from cgf_script.managers_registrator import onRemovedQuery, onProcessQuery
from portal_common_cgf.portal_helpers import registerPortalManager
if typing.TYPE_CHECKING:
    from typing import Dict
_logger = logging.getLogger(__name__)

@registerPortalManager(CGF.DomainOption.DomainClient)
class AuraVisibilityManager(CGF.ComponentManager):

    def __init__(self):
        super(AuraVisibilityManager, self).__init__()
        self.__auraVisibilityStates = {}
        self.__auraReplicationSubscriptions = {}

    def activate(self):
        pass

    def deactivate(self):
        self.__auraVisibilityStates.clear()

    @onRemovedQuery(CGF.GameObject, PortalAuraComponent)
    def onAuraRemoved(self, go, auraComponent):
        self.__auraVisibilityStates.pop(go.id, None)
        return

    @onProcessQuery(CGF.GameObject, PortalAuraComponent)
    def onProcessAura(self, go, auraComponent):
        if auraComponent.bossVehicleID == -1:
            return
        elif go.id not in self.__auraVisibilityStates:
            self.__auraVisibilityStates[go.id] = False
            AuraVisibilityManager.__updateAuraVisibility(go, False)
            return
        else:
            playerVehicle = BigWorld.player().vehicle
            if playerVehicle is None:
                return
            currentVisibility = AuraVisibilityManager.__isBossVisible(playerVehicle, auraComponent.bossVehicleID)
            if currentVisibility != self.__auraVisibilityStates[go.id]:
                self.__auraVisibilityStates[go.id] = currentVisibility
                AuraVisibilityManager.__updateAuraVisibility(go, currentVisibility)
            return

    @staticmethod
    def __activateAura(auraGO, isVisible):
        animator = auraGO.findComponentByType(AnimatorComponent)
        if animator is None:
            _logger.error('AuraVisibilityManager::__updateAuraVisibility no animator')
            return
        else:
            if isVisible:
                auraGO.activate()
                animator.start()
            else:
                animator.stop()
            return

    @staticmethod
    def __updateAuraVisibility(auraGO, isVisible):
        if auraGO is None or not auraGO.isValid():
            return
        else:
            AuraVisibilityManager.__activateAura(auraGO, isVisible)
            return

    def __onAuraReplicationDone(self, auraGO, auraComponent):
        if auraComponent.bossVehicleID != -1:
            self.__auraVisibilityStates[auraGO.id] = False

    @staticmethod
    def __isBossVisible(playerVehicle, bossVehicleID):
        bossVehicle = BigWorld.entities.get(bossVehicleID, None)
        return bool(bossVehicle)
