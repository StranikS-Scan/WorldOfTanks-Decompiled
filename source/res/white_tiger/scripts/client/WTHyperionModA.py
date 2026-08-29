# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/WTHyperionModA.py
import BigWorld
import CGF
import GenericComponents
import SoundGroups
from cgf_components import sound_helpers
from items import vehicles
from Math import Matrix, Vector3
import logging
_logger = logging.getLogger(__name__)

class WTHyperionModA(BigWorld.Entity):
    __NOTIFICATION_TIMER_PREFAB = 'content/WtPrefabs/abilities/HyperionNotification.prefab'
    __HYPERION_ACTIVATION = 'ev_wt_gameplay_hyperion_active'
    __HYPERION_INTERRUPTION = {'vo': 'wt23_both_vo_hyperion_canceled',
     'sound': 'ev_wt_gameplay_hyperion_start_up_interrupted'}

    def __init__(self):
        BigWorld.Entity.__init__(self)
        self.__goCharging = None
        self.__goShot = None
        self.__goNotificationTimer = None
        self.__radius = 0
        self.__equipment = vehicles.g_cache.equipments().get(self.equipmentID)
        self.__hyperionActivationSoundObj = None
        self.__isShotLoading = False
        return

    def onEnterWorld(self, *args):
        self.__radius = self.__equipment.radius
        CGF.loadGameObject(self.__equipment.chargePrefab, self.spaceID, self.position, self.__onChargingLoaded)
        CGF.loadGameObjectIntoHierarchy(self.__NOTIFICATION_TIMER_PREFAB, self.entityGameObject, Vector3(), self.__onNotificationPrefabLoaded)
        self.__hyperionActivationSoundObj = self.__getSoundObject(self.__HYPERION_ACTIVATION)

    def onLeaveWorld(self):
        if self.shotIndex == -1:
            sound_helpers.playNotification(self.__HYPERION_INTERRUPTION['vo'])
            SoundGroups.g_instance.playSoundPos(self.__HYPERION_INTERRUPTION['sound'], self.position)
        if self.__hyperionActivationSoundObj:
            self.__hyperionActivationSoundObj.stopAll()
        self.__hyperionActivationSoundObj = None
        self.__clear()
        return

    def set_shotIndex(self, prev):
        if self.shotIndex <= 0:
            return
        else:
            if self.shotIndex == 1 and self.__hyperionActivationSoundObj:
                self.__hyperionActivationSoundObj.play(self.__HYPERION_ACTIVATION)
            if self.__goShot is None:
                if not self.__isShotLoading:
                    self.__isShotLoading = True
                    CGF.loadGameObject(self.__equipment.shotPrefab, self.spaceID, self.position, self.__onShotLoaded)
                return
            self.__restartShot()
            return

    @property
    def equipment(self):
        return self.__equipment

    def __restartShot(self):
        animator = self.__goShot.findComponentByType(GenericComponents.AnimatorComponent)
        animator.stop()
        animator.start()

    def __onChargingLoaded(self, go):
        if self.isDestroyed or self.__goShot is not None:
            self.__removeGO(go)
            return
        else:
            if self.__goCharging is None:
                self.__goCharging = go
            return

    def __onShotLoaded(self, go):
        if self.isDestroyed:
            self.__removeGO(go)
            return
        else:
            self.__removeGO(self.__goCharging)
            self.__goCharging = None
            if self.__goShot is None:
                self.__goShot = go
            self.__isShotLoading = False
            return

    def __onNotificationPrefabLoaded(self, go):
        if self.isDestroyed:
            self.__removeGO(go)
            return
        else:
            if self.__goNotificationTimer is None:
                self.__goNotificationTimer = go
            return

    def __removeGO(self, go):
        if go and go.isValid():
            CGF.removeGameObject(go)

    def __getSoundObject(self, name):
        mPos = Matrix()
        mPos.translation = self.position
        return SoundGroups.g_instance.WWgetSoundObject(name, mPos)

    def __clear(self):
        self.__removeGO(self.__goCharging)
        self.__goCharging = None
        self.__removeGO(self.__goShot)
        self.__goShot = None
        self.__removeGO(self.__goNotificationTimer)
        self.__goNotificationTimer = None
        self.__isShotLoading = False
        return
