# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/helpers/rts_trajectory_drawer.py
import GUI
import Math
import BattleReplay
from AvatarInputHandler import cameras
from AvatarInputHandler.AimingSystems import getDesiredShotPoint, getShotPosition
from BattleReplay import CallbackDataNames
from helpers import dependency
from helpers.CallbackDelayer import CallbackDelayer
from projectile_trajectory import getShotAngles
from skeletons.gui.battle_session import IBattleSessionProvider
from gun_rotation_shared import calcPitchLimitsFromDesc, isOutOfLimits

class _RTSTrajectoryDrawer(CallbackDelayer):
    _TRAJECTORY_UPDATE_INTERVAL = 0.05
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        super(_RTSTrajectoryDrawer, self).__init__()
        self.__vehicleDrawers = {}
        self.__isEnabled = False
        self.__isVisible = False

    def enable(self):
        if self.__isEnabled:
            return
        self.__sessionProvider.dynamic.rtsCommander.vehicles.onSelectionChanged += self.__onSelectionChanged
        self.__sessionProvider.dynamic.rtsCommander.vehicles.onVehicleUpdated += self.__onVehicleUpdated
        for vID in self.__sessionProvider.dynamic.rtsCommander.vehicles.iterkeys(lambda e: e.isAllyBot):
            self.__initTrajectoryDrawer(vID)

        self.__isEnabled = True
        self.__isVisible = False

    def disable(self):
        if not self.__isEnabled:
            return
        self.__sessionProvider.dynamic.rtsCommander.vehicles.onSelectionChanged -= self.__onSelectionChanged
        self.__sessionProvider.dynamic.rtsCommander.vehicles.onVehicleUpdated -= self.__onVehicleUpdated
        self._setVisibility(False)
        self.__vehicleDrawers.clear()
        self.__stopTrajectoryDrawer()
        self.__isEnabled = False

    def destroy(self):
        CallbackDelayer.destroy(self)
        self.disable()

    @property
    def isVisible(self):
        return self.__isEnabled and self.__isVisible

    def handleKeyEvent(self, isDown, key, mods, event=None):
        if not self.__isEnabled:
            return False
        self._setVisibility(visible=isDown)
        return True

    def _setVisibility(self, visible):
        if visible == self.__isVisible:
            return
        self.__isVisible = visible
        anySelected = self.__updateVisibility()
        if visible:
            if anySelected:
                self.__startTrajectoryDrawer()
        else:
            self.__stopTrajectoryDrawer()

    def __updateVisibility(self, selectedVehiclesIDs=None):
        if not selectedVehiclesIDs:
            selectedVehiclesIDs = self.__sessionProvider.dynamic.rtsCommander.vehicles.keys(lambda v: v.isSelected)
        for vehicleID, drawer in self.__vehicleDrawers.items():
            if vehicleID in selectedVehiclesIDs:
                drawer.setVisible(self.__isVisible)
            drawer.setVisible(False)

        return bool(selectedVehiclesIDs)

    def __initTrajectoryDrawer(self, vehicleID):
        if vehicleID in self.__vehicleDrawers:
            return
        else:
            vehicle = self.__sessionProvider.dynamic.rtsCommander.vehicles.get(vehicleID)
            if vehicle is None or not vehicle.isAllyBot:
                return
            appearance = vehicle.appearance
            if appearance is None:
                return
            if appearance.trajectoryDrawer is None:
                appearance.initTrajectoryDrawer()
            self.__vehicleDrawers[vehicleID] = appearance.trajectoryDrawer
            return

    def __startTrajectoryDrawer(self):
        delay = self.__updateTrajectoryDrawer()
        if delay is not None:
            self.delayCallback(delay, self.__updateTrajectoryDrawer)
        return

    def __stopTrajectoryDrawer(self):
        self.stopCallback(self.__updateTrajectoryDrawer)

    def __updateTrajectoryDrawer(self):
        if not self.__isVisible:
            return
        else:
            vehicles = self.__sessionProvider.dynamic.rtsCommander.vehicles
            if not vehicles.hasSelection:
                return
            replayCtrl = BattleReplay.g_replayCtrl
            if replayCtrl.isPlaying:
                mouseCursor = replayCtrl.mouseCursor
            else:
                mouseCursor = GUI.mcursor()
            mousePos = mouseCursor.position
            direction, start = cameras.getWorldRayAndPoint(*mousePos)
            desiredPos = getDesiredShotPoint(start, direction, True, False, False)
            if desiredPos is None:
                return self._TRAJECTORY_UPDATE_INTERVAL
            for vehicleID, drawer in self.__vehicleDrawers.items():
                vehicle = vehicles.get(vehicleID)
                if vehicle is None:
                    continue
                shot = vehicle.typeDescriptor.shot
                startPos, startVelocity, isOutOfPitchLimits = self.__getBotShotParams(desiredPos, vehicle)
                drawer.setData(desiredPos, startPos, startVelocity, Math.Vector3(0, -shot.gravity, 0), mousePos, shot.maxDistance, self._TRAJECTORY_UPDATE_INTERVAL, vehicleID, isOutOfPitchLimits)

            return self._TRAJECTORY_UPDATE_INTERVAL

    def __onSelectionChanged(self, selectedVehiclesIDs):
        anySelected = self.__updateVisibility(selectedVehiclesIDs)
        if anySelected:
            if self.__isVisible:
                self.__startTrajectoryDrawer()
        else:
            self.__stopTrajectoryDrawer()

    def __onVehicleUpdated(self, vehicle):
        if vehicle.isAlive:
            if vehicle.id not in self.__vehicleDrawers:
                self.__initTrajectoryDrawer(vehicle.id)
        elif vehicle.id in self.__vehicleDrawers:
            drawer = self.__vehicleDrawers.pop(vehicle.id)
            drawer.setVisible(False)

    def __getBotShotParams(self, targetPoint, vehicle):
        descr = vehicle.typeDescriptor
        if descr.turret.gunPosition is None:
            return
        else:
            shotTurretYaw, shotGunPitch = getShotAngles(descr, vehicle.matrix, (0, 0), targetPoint, overrideGunPosition=descr.turret.gunPosition)
            gunPitchLimits = calcPitchLimitsFromDesc(shotTurretYaw, descr.gun.pitchLimits)
            isOutOfPitchLimits = False
            closestLimit = isOutOfLimits(shotGunPitch, gunPitchLimits)
            if closestLimit is not None:
                isOutOfPitchLimits = True
                shotGunPitch = closestLimit
            startPos, startVelocity = getShotPosition(vehicle.matrix, vehicle.typeDescriptor, shotTurretYaw, shotGunPitch)
            return (startPos, startVelocity, isOutOfPitchLimits)

    def __isCommanderEnabled(self):
        return self.__sessionProvider.dynamic.rtsCommander.enabled


class _RTSTrajectoryDrawerRecorder(_RTSTrajectoryDrawer):

    def _setVisibility(self, visible):
        BattleReplay.g_replayCtrl.serializeCallbackData(CallbackDataNames.SET_TRAJECTORY_DRAWERS_VISIBILITY, (visible,))
        super(_RTSTrajectoryDrawerRecorder, self)._setVisibility(visible)


class _RTSTrajectoryDrawerPlayer(_RTSTrajectoryDrawer):

    def __init__(self):
        super(_RTSTrajectoryDrawerPlayer, self).__init__()
        BattleReplay.g_replayCtrl.setDataCallback(CallbackDataNames.SET_TRAJECTORY_DRAWERS_VISIBILITY, self._setVisibility)

    def destroy(self):
        BattleReplay.g_replayCtrl.delDataCallback(CallbackDataNames.SET_TRAJECTORY_DRAWERS_VISIBILITY, self._setVisibility)
        super(_RTSTrajectoryDrawerPlayer, self).destroy()


def createTrajectoryDrawer():
    replayCtrl = BattleReplay.g_replayCtrl
    if replayCtrl.isPlaying:
        trajectoryDrawerCls = _RTSTrajectoryDrawerPlayer
    elif replayCtrl.isRecording:
        trajectoryDrawerCls = _RTSTrajectoryDrawerRecorder
    else:
        trajectoryDrawerCls = _RTSTrajectoryDrawer
    return trajectoryDrawerCls()
