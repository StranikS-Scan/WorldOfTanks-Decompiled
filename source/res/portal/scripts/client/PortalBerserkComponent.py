# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: portal/scripts/client/PortalBerserkComponent.py
import logging
import BigWorld
import CGF
import Math
from items import vehicles
from script_component.DynamicScriptComponent import DynamicScriptComponent
_logger = logging.getLogger(__name__)

class PortalBerserkComponent(DynamicScriptComponent):

    def __init__(self):
        super(PortalBerserkComponent, self).__init__()
        self.__go = None
        return

    def onDestroy(self):
        self.__setBinocularVisibility(False)
        super(PortalBerserkComponent, self).onDestroy()

    def set_isBerserkActive(self, prev):
        if self.isBerserkActive:
            self.__onActivated()
        else:
            self.__onDeactivated()

    def __onActivated(self):
        self.__loadEffect()
        self.__setBinocularVisibility(True)

    def __onDeactivated(self):
        self.__unloadEffect()
        self.__setBinocularVisibility(False)

    def __loadEffect(self):
        if not self.equipmentID:
            _logger.error("Can't load PortalBerserk effect. Invalid equipmentID %s", self.equipmentID)
            return
        equipment = vehicles.g_cache.equipments()[self.equipmentID]
        if equipment.duration < 0:
            _logger.error('PortalBerserk Effect duration must be greater then 0')
            return
        CGF.loadGameObjectIntoHierarchy(equipment.usagePrefab, self.entity.entityGameObject, Math.Vector3(0, 0, 0), self.__onEffectLoaded)

    def __unloadEffect(self):
        if self.__go is not None:
            CGF.removeGameObject(self.__go)
        self.__go = None
        return

    def __onEffectLoaded(self, gameObject):
        self.__go = gameObject

    def __setBinocularVisibility(self, isVisible):
        if self.entity.avatarID != BigWorld.player().id:
            return
        binoculars = BigWorld.binoculars()
        if binoculars:
            binoculars.setIsFlame(isVisible)
