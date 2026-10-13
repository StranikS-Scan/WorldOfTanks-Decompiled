# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: portal/scripts/client/PortalBerserkComponent.py
import logging
import BigWorld
import CGF
from items import vehicles
from script_component.DynamicScriptComponent import DynamicScriptComponent
from vehicle_systems.model_assembler import loadAppearancePrefab
_logger = logging.getLogger(__name__)

class PortalBerserkComponent(DynamicScriptComponent):

    def __init__(self):
        super(PortalBerserkComponent, self).__init__()
        self.__go = None
        self.__setBinocularVisibility(False)
        return

    def onDestroy(self):
        self.__setBinocularVisibility(False)
        super(PortalBerserkComponent, self).onDestroy()

    def set_isBerserkActive(self, prev):
        self.__handleEffects()

    def _onAvatarReady(self):
        if not hasattr(self.entity, 'appearance') or not hasattr(self.entity, 'onAppearanceReady'):
            return
        if self.entity.appearance and self.entity.appearance.isConstructed:
            self.__handleEffects()
        else:
            self.entity.onAppearanceReady += self.__onAppearanceReady

    def __onAppearanceReady(self):
        self.entity.onAppearanceReady -= self.__onAppearanceReady
        self.__handleEffects()

    def __handleEffects(self):
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
        loadAppearancePrefab(equipment.usagePrefab, self.entity.appearance, self.__onEffectLoaded)

    def __onEffectLoaded(self, go):
        if not self.isBerserkActive:
            self.__removeGO(go)
            return
        self.__go = go

    def __unloadEffect(self):
        if self.__go is not None:
            self.__removeGO(self.__go)
        self.__go = None
        return

    def __setBinocularVisibility(self, isVisible):
        if self.entity.avatarID != BigWorld.player().id:
            return
        self.__setBinocularsFlame(isVisible)

    def __setBinocularsFlame(self, isVisible):
        binoculars = BigWorld.binoculars()
        if binoculars and binoculars.getIsFlame() != isVisible:
            binoculars.setIsFlame(isVisible)

    def __removeGO(self, go):
        if go and go.isValid():
            CGF.removeGameObject(go)
