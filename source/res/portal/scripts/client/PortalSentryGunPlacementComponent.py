# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: portal/scripts/client/PortalSentryGunPlacementComponent.py
import functools
import logging
import BigWorld
import CGF
from items import vehicles
from script_component.DynamicScriptComponent import DynamicScriptComponent
_logger = logging.getLogger(__name__)

class PortalSentryGunPlacementComponent(DynamicScriptComponent):

    def set_isSentryBotDeployed(self, prev):
        if not self.deployPosition:
            _logger.error('Deploy effect position is None')
            return
        if not prev and self.isSentryBotDeployed:
            equipment = vehicles.g_cache.equipments()[self.equipmentID]
            CGF.loadGameObject(equipment.usagePrefab, self.entity.spaceID, self.deployPosition, self.__onPrefabLoaded)

    def __onPrefabLoaded(self, gameObject):
        equipment = vehicles.g_cache.equipments()[self.equipmentID]
        BigWorld.callback(equipment.deployEffectDuration, functools.partial(CGF.removeGameObject, gameObject))
