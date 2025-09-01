# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/AvatarInputHandler/player_notifications/siege_mode/notifier.py
from Event import Event
from sound_notifications import SiegeModeSoundNotifications, TurboshaftModeSoundNotifications, TwinGunModeSoundNotifications, PillboxSiegeSoundNotifications
from camera_shaker import SiegeModeCameraShaker
from vehicles.mechanics.mechanic_info import hasVehicleMechanic, VehicleMechanic

class SiegeModeNotifier(object):

    def __init__(self):
        self.onSiegeStateChanged = Event()
        self.soundNotifications = None
        return

    def destroy(self):
        self.stop()
        self.onSiegeStateChanged.clear()

    def construct(self, vehicle):
        typeDescr = vehicle.typeDescriptor
        if not typeDescr.hasSiegeMode:
            return
        else:
            notificationsCls = SiegeModeNotifier._getSoundNotifications(typeDescr)
            if notificationsCls is None or not self.soundNotifications or notificationsCls.getModeType() != self.soundNotifications.getModeType() or self.soundNotifications.vehicleID != vehicle.id:
                if self.soundNotifications:
                    self.soundNotifications.stop()
                    self.soundNotifications = None
                if notificationsCls is not None:
                    notifications = notificationsCls(vehicle.id)
                    notifications.start()
                    self.soundNotifications = notifications
            return

    def start(self):
        if self.soundNotifications is not None:
            self.soundNotifications.start()
        return

    def stop(self):
        if self.soundNotifications is not None:
            self.soundNotifications.stop()
            self.soundNotifications = None
        return

    def notifySiegeModeChanged(self, vehicleID, newState, timeToNextMode):
        SiegeModeCameraShaker.shake(vehicleID, newState, timeToNextMode)
        if self.soundNotifications is not None:
            self.soundNotifications.onSiegeStateChanged(vehicleID, newState, timeToNextMode)
        self.onSiegeStateChanged(vehicleID, newState, timeToNextMode)
        return

    @staticmethod
    def _getSoundNotifications(typeDescr):
        notificationsCls = None
        if hasVehicleMechanic(typeDescr, VehicleMechanic.PILLBOX_SIEGE_MODE):
            notificationsCls = PillboxSiegeSoundNotifications
        elif typeDescr.hasHydraulicChassis or typeDescr.isWheeledVehicle:
            notificationsCls = SiegeModeSoundNotifications
        elif typeDescr.hasTurboshaftEngine:
            notificationsCls = TurboshaftModeSoundNotifications
        elif typeDescr.isTwinGunVehicle:
            notificationsCls = TwinGunModeSoundNotifications
        return notificationsCls
