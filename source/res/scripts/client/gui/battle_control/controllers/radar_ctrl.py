# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/controllers/radar_ctrl.py
import logging
import BigWorld
from constants import ARENA_PERIOD
from gui.battle_control.view_components import ViewComponentsController
from gui.battle_control.battle_constants import BATTLE_CTRL_ID
from gui.battle_control.arena_info.interfaces import IRadarController
from gui.battle_control import avatar_getter
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
_logger = logging.getLogger(__name__)

class RadarResponseCode(object):
    SUCCESS, FAILURE, WRONG_ARENA_PERIOD, COOLDOWN, DESTROYED_VEHICLE = range(1, 6)


class IRadarListener(object):

    def startTimeOut(self, timeLeft, duration):
        pass

    def timeOutDone(self):
        pass

    def radarActivated(self, radarRadius):
        pass

    def radarActivationFailed(self, code):
        pass

    def radarInfoReceived(self, radarInfo):
        pass


class RadarController(ViewComponentsController, IRadarController):
    __guiSessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        super(RadarController, self).__init__()
        self.__dynamicViews = []
        self.__callbackID = None
        return

    def getControllerID(self):
        return BATTLE_CTRL_ID.RADAR_CTRL

    def startControl(self, *args):
        avatar = BigWorld.player()
        arena = avatar.arena
        if arena is not None:
            arena.onRadarInfoReceived += self.__onRadarInfoReceived
        playerVehicle = avatar.vehicle
        if playerVehicle is not None:
            self.updateRadarReadinessTime(playerVehicle.radarReadinessTime)
        else:
            avatar.onVehicleEnterWorld += self.__onVehicleEnterWorld
        return

    def stopControl(self):
        self.__cancelCallback()
        avatar = BigWorld.player()
        arena = avatar.arena
        if arena is not None:
            arena.onRadarInfoReceived -= self.__onRadarInfoReceived
        avatar.onVehicleEnterWorld -= self.__onVehicleEnterWorld
        self.clearViewComponents()
        return

    def activateRadar(self):
        avatar = BigWorld.player()
        responseCode = self.__canActivate(avatar)
        allListeners = self._viewComponents + self.__dynamicViews
        if responseCode == RadarResponseCode.SUCCESS:
            avatar.vehicle.cell.activateRadar()
            coolDown = self.__getRadarCooldown()
            radius = self.__getRadarRadius()
            for listener in allListeners:
                listener.radarActivated(radius)
                listener.startTimeOut(coolDown, coolDown)

        else:
            for listener in allListeners:
                listener.radarActivationFailed(responseCode)

    def updateRadarReadinessTime(self, radarReadinessTime):
        actualTime = radarReadinessTime - BigWorld.serverTime()
        if actualTime > 0:
            duration = max(self.__getRadarCooldown(), actualTime)
            for listener in self._viewComponents + self.__dynamicViews:
                listener.startTimeOut(actualTime, duration)

            self.__cancelCallback()
            if self.__guiSessionProvider.shared.arenaPeriod.getPeriod() == ARENA_PERIOD.BATTLE:
                self.__callbackID = BigWorld.callback(actualTime, self.__onRadarReloaded)

    def setViewComponents(self, *components):
        self._viewComponents = list(components)

    def clearViewComponents(self):
        super(RadarController, self).clearViewComponents()
        self.__dynamicViews = []

    def addRuntimeView(self, view):
        if view in self.__dynamicViews:
            _logger.warning('View already added - %s', view)
        else:
            self.__dynamicViews.append(view)

    def removeRuntimeView(self, view):
        if view in self.__dynamicViews:
            self.__dynamicViews.remove(view)
        else:
            _logger.warning('View has not been found - %s', view)

    def __canActivate(self, avatar):
        if avatar is not None:
            ctrl = self.__guiSessionProvider.shared.arenaPeriod
            if ctrl.getPeriod() != ARENA_PERIOD.BATTLE:
                return RadarResponseCode.WRONG_ARENA_PERIOD
            vehicle = avatar.vehicle
            if not vehicle or avatar.vehicle.health <= 0:
                return RadarResponseCode.DESTROYED_VEHICLE
            ctrl = self.__guiSessionProvider.shared.vehicleState
            if avatar.isObserver() or ctrl.isInPostmortem:
                return RadarResponseCode.DESTROYED_VEHICLE
            if avatar.vehicle.radarReadinessTime >= BigWorld.serverTime():
                return RadarResponseCode.COOLDOWN
            return RadarResponseCode.SUCCESS
        else:
            return RadarResponseCode.FAILURE

    @staticmethod
    def __getRadarRadius():
        avatar = BigWorld.player()
        return avatar.vehicle.typeDescriptor.radio.radarRadius

    @staticmethod
    def __getRadarCooldown():
        avatar = BigWorld.player()
        return avatar.vehicle.typeDescriptor.radio.radarCooldown

    def __onRadarInfoReceived(self, radarInfo):
        for listener in self._viewComponents + self.__dynamicViews:
            listener.radarInfoReceived(radarInfo)

    def __onVehicleEnterWorld(self, vehicle):
        if vehicle.id == avatar_getter.getPlayerVehicleID():
            BigWorld.player().onVehicleEnterWorld -= self.__onVehicleEnterWorld
            self.updateRadarReadinessTime(vehicle.radarReadinessTime)

    def __cancelCallback(self):
        if self.__callbackID is not None:
            BigWorld.cancelCallback(self.__callbackID)
            self.__callbackID = None
        return

    def __onRadarReloaded(self):
        self.__callbackID = None
        for listener in self._viewComponents + self.__dynamicViews:
            listener.timeOutDone()

        return
