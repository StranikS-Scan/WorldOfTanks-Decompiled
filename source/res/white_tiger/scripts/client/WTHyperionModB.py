# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/WTHyperionModB.py
import BigWorld
import CGF
import Math
from items import vehicles
from white_tiger.gui.battle_control.controllers.consumables.equipment_sound import playHyperionModBShooting, playHyperionModBCharging, playHyperionModBInterruption

class WTHyperionModB(BigWorld.Entity):
    __NOTIFICATION_TIMER_PREFAB = 'content/WtPrefabs/abilities/HyperionNotification.prefab'

    def __init__(self):
        BigWorld.Entity.__init__(self)
        self.__goCharging = None
        self.__goShooting = None
        self.__goNotificationTimer = None
        self.__isHyperionCharging = False
        self.__equipment = vehicles.g_cache.equipments().get(self.equipmentID)
        return

    def onEnterWorld(self, *args):
        CGF.loadGameObject(self.__equipment.chargePrefab, self.spaceID, self.position, self.__onChargingLoaded)
        CGF.loadGameObjectIntoHierarchy(self.__NOTIFICATION_TIMER_PREFAB, self.entityGameObject, Math.Vector3(), self.__onNotificationPrefabLoaded)
        playHyperionModBCharging(self.position)
        self.__isHyperionCharging = True

    def onLeaveWorld(self):
        if self.__isHyperionCharging and not self.isFiring:
            playHyperionModBInterruption(self.position)
        self.__clear()

    def set_isFiring(self, prev):
        if self.isFiring:
            playHyperionModBShooting(self.position)
            CGF.loadGameObject(self.__equipment.shotPrefab, self.spaceID, self.position, self.__onShootingLoaded)

    @property
    def equipment(self):
        return self.__equipment

    def __onChargingLoaded(self, go):
        if self.isDestroyed or self.__goShooting is not None:
            self.__removeGO(go)
            return
        else:
            if self.__goCharging is None:
                self.__goCharging = go
            return

    def __onShootingLoaded(self, go):
        if self.isDestroyed:
            self.__removeGO(go)
            return
        else:
            self.__clearCharging()
            if self.__goShooting is None:
                self.__goShooting = go
            return

    def __onNotificationPrefabLoaded(self, go):
        if self.isDestroyed:
            self.__removeGO(go)
            return
        else:
            if self.__goNotificationTimer is None:
                self.__goNotificationTimer = go
            return

    def __clearCharging(self):
        self.__removeGO(self.__goCharging)
        self.__goCharging = None
        self.__isHyperionCharging = False
        return

    def __removeGO(self, go):
        if go and go.isValid():
            CGF.removeGameObject(go)

    def __clear(self):
        self.__clearCharging()
        self.__removeGO(self.__goShooting)
        self.__goShooting = None
        self.__removeGO(self.__goNotificationTimer)
        self.__goNotificationTimer = None
        return
