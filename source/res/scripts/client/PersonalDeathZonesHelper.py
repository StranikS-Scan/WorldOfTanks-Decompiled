# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/PersonalDeathZonesHelper.py
import BigWorld
_NOTIFICATION_ON_APPEAR = 'se20_player_personal_death_zone'

class PersonalDeathZonesHelper(BigWorld.Entity):

    def __init__(self):
        super(PersonalDeathZonesHelper, self).__init__()
        self._vehicleId = 0
        self._notificationTimerCB = None
        return

    def onEnterDZ(self, vehicleID):
        avatar = BigWorld.player()
        if avatar and avatar.playerVehicleID == vehicleID:
            self._vehicleId = vehicleID
            avatar.updatePersonalDeathZoneWarningNotification(self.id, True, self.warningTimeShouldEndAt)
            self._clearCB()
            time = self.warningTimeShouldEndAt - BigWorld.serverTime()
            if time > 0:
                self._notificationTimerCB = BigWorld.callback(time, self._onNotificationTimerFinished)

    def onLeaveDZ(self, vehicleID):
        self._clearCB()
        avatar = BigWorld.player()
        if avatar and avatar.playerVehicleID == vehicleID:
            self._vehicleId = 0
            avatar.updatePersonalDeathZoneWarningNotification(self.id, False)

    def onEnterWorld(self, prereqs=None):
        avatar = BigWorld.player()
        if avatar and avatar.soundNotifications:
            avatar.soundNotifications.play(_NOTIFICATION_ON_APPEAR)

    def onLeaveWorld(self):
        self._clearCB()
        avatar = BigWorld.player()
        if avatar and avatar.playerVehicleID == self._vehicleId:
            self._vehicleId = 0
            avatar.updatePersonalDeathZoneWarningNotification(self.id, False)

    def _onNotificationTimerFinished(self):
        self._clearCB()
        avatar = BigWorld.player()
        if avatar:
            avatar.updatePersonalDeathZoneWarningNotification(self.id, True)

    def _clearCB(self):
        if self._notificationTimerCB:
            BigWorld.cancelCallback(self._notificationTimerCB)
            self._notificationTimerCB = None
        return
