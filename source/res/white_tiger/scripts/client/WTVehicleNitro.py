# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/WTVehicleNitro.py
import CGF
import logging
from items import vehicles
from vehicle_systems.model_assembler import loadAppearancePrefab
from script_component.DynamicScriptComponent import DynamicScriptComponent
_logger = logging.getLogger(__name__)

class WTVehicleNitro(DynamicScriptComponent):

    def __init__(self):
        super(WTVehicleNitro, self).__init__()
        self.__go = None
        return

    def onDestroy(self):
        if self.__go and self.__go.isValid():
            CGF.removeGameObject(self.__go)
        self.__go = None
        super(WTVehicleNitro, self).onDestroy()
        return

    def _onAvatarReady(self):
        if self.isNitroActive:
            self.__startEffect()

    def set_isNitroActive(self, prev):
        if self.isNitroActive:
            self.__startEffect()
        else:
            self.__stopEffect()

    def __startEffect(self):
        if self.__go is None:
            appearance = self.entity.appearance
            if appearance is None or not appearance.isConstructed:
                return
            equipment = vehicles.g_cache.equipments().get(self.equipmentID)
            usagePrefab = equipment.usagePrefab
            if not usagePrefab:
                _logger.error("Can't load WTVehicleNitro effect. Invalid usagePrefab %s", usagePrefab)
                return
            loadAppearancePrefab(usagePrefab, appearance, self.__onEffectLoaded)
        else:
            self.__go.activate()
        return

    def __onEffectLoaded(self, go):
        if not self.isNitroActive or self.__go is not None:
            CGF.removeGameObject(go)
            return
        else:
            self.__go = go
            return

    def __stopEffect(self):
        if self.__go and self.__go.isValid():
            self.__go.deactivate()
