# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/WTVehiclePassiveHealing.py
import CGF
import logging
from vehicle_systems.model_assembler import loadAppearancePrefab
from script_component.DynamicScriptComponent import DynamicScriptComponent
_logger = logging.getLogger(__name__)

class WTVehiclePassiveHealing(DynamicScriptComponent):

    def __init__(self):
        super(WTVehiclePassiveHealing, self).__init__()
        self.__go = None
        return

    def _onAvatarReady(self):
        if self.isHealActive:
            self.__playEffect()

    def set_isHealActive(self, prev):
        self.__playEffect()

    def onDestroy(self):
        self.__unloadEffect()
        super(WTVehiclePassiveHealing, self).onDestroy()

    def __playEffect(self):
        if self.isHealActive:
            self.__loadEffect()
        else:
            self.__unloadEffect()

    def __loadEffect(self):
        if not self.usagePrefab:
            _logger.error("Can't load PassiveHealing effect. Invalid usagePrefab %s", self.usagePrefab)
            return
        appearance = self.entity.appearance
        if appearance and appearance.isConstructed:
            loadAppearancePrefab(self.usagePrefab, appearance, self.__onEffectLoaded)

    def __onEffectLoaded(self, go):
        if not self.isHealActive or self.__go is not None:
            CGF.removeGameObject(go)
            return
        else:
            self.__go = go
            return

    def __unloadEffect(self):
        if self.__go is not None:
            CGF.removeGameObject(self.__go)
            self.__go = None
        return
