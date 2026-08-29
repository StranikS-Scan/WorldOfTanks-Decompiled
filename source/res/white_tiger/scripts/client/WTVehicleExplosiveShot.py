# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/WTVehicleExplosiveShot.py
from functools import partial
import BigWorld
from white_tiger.helpers.PrefabHelper import AppearancePrefabHandler
from white_tiger.gui.battle_control.controllers.consumables.equipment_sound import playEnhancedShotOnShotSound
from WTPrefabActivator import WTPrefabActivator

class WTVehicleExplosiveShot(WTPrefabActivator):

    def __init__(self):
        super(WTVehicleExplosiveShot, self).__init__()
        self._barrelFlashPrefabHandler = AppearancePrefabHandler(lambda : True)
        self._barrelFlashPrefabPath = None
        self._barrelFlashPrefabUnloadTimeoutAfterShot = None
        self.set_equipmentID(self.equipmentID)
        return

    def set_equipmentID(self, prev):
        if self.equipmentID == 0:
            return
        self._barrelFlashPrefabPath = WTPrefabActivator.getEquipment(self.equipmentID).barrelFlashPrefab
        self._barrelFlashPrefabUnloadTimeoutAfterShot = WTPrefabActivator.getEquipment(self.equipmentID).barrelFlashPrefabUnloadTimeoutAfterShot

    def set_isExplosiveShotActive(self, prev):
        self._updatePrefab()

    def set_firedShotID(self, prev):
        if self.firedShotID == 0:
            return
        playEnhancedShotOnShotSound(self.entity.position, self.entity.id == BigWorld.player().playerVehicleID)
        self._barrelFlashPrefabHandler.load(self.entity.appearance, self._barrelFlashPrefabPath, partial(BigWorld.callback, self._barrelFlashPrefabUnloadTimeoutAfterShot, self._barrelFlashPrefabHandler.unload))

    def onDestroy(self):
        self._barrelFlashPrefabUnloadTimeoutAfterShot = None
        self._barrelFlashPrefabPath = None
        if self._barrelFlashPrefabHandler:
            self._barrelFlashPrefabHandler.destroy()
        self._barrelFlashPrefabHandler = None
        super(WTVehicleExplosiveShot, self).onDestroy()
        return

    def _isAbilityActive(self):
        return self.isExplosiveShotActive
