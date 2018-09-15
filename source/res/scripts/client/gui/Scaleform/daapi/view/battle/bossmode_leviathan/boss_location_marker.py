# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/bossmode_leviathan/boss_location_marker.py
import BigWorld
from gui.Scaleform.daapi.view.meta.BossLocationMarkerMeta import BossLocationMarkerMeta
from helpers import i18n, dependency
from gui.Scaleform.locale.INGAME_GUI import INGAME_GUI
from skeletons.gui.battle_session import IBattleSessionProvider
from Math import Matrix
from AvatarInputHandler import cameras
from gui.shared.gui_items.Vehicle import VEHICLE_TAGS
from AvatarInputHandler import AvatarInputHandler, aih_constants
from gui.battle_control import avatar_getter
from constants import ARENA_PERIOD
_CTRL_MODE = aih_constants.CTRL_MODE_NAME

class BossLocationMarker(BossLocationMarkerMeta):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        super(BossLocationMarker, self).__init__()
        self.__activeBossVehicleID = None
        self.__activeControlMode = None
        self.__noMoreSignals = False
        return

    def _dispose(self):
        super(BossLocationMarker, self)._dispose()
        handler = avatar_getter.getInputHandler()
        if handler is not None:
            if isinstance(handler, AvatarInputHandler):
                handler.onCameraChanged -= self.__onCameraChanged
        ctrl = self.sessionProvider.shared.feedback
        if ctrl is not None:
            ctrl.onVehicleMarkerUpdateDistance -= self.__onVehicleMarkerUpdateDistance
        BigWorld.player().arena.onPeriodChange -= self.__arena_onPeriodChange
        return

    def _populate(self):
        super(BossLocationMarker, self)._populate()
        self.hideMarker()
        BigWorld.player().arena.onPeriodChange += self.__arena_onPeriodChange
        ctrl = self.sessionProvider.shared.feedback
        if ctrl is not None:
            ctrl.onVehicleMarkerUpdateDistance += self.__onVehicleMarkerUpdateDistance
        handler = avatar_getter.getInputHandler()
        if handler is not None:
            if isinstance(handler, AvatarInputHandler):
                handler.onCameraChanged += self.__onCameraChanged
        return

    def hideMarker(self):
        self.as_hideS()

    def showMarker(self, onLeftSide):
        if not self.__noMoreSignals:
            self.as_showS(onLeftSide)

    def __onVehicleMarkerUpdateDistance(self, vehicleID):
        if vehicleID is None:
            return
        elif self.__activeControlMode is _CTRL_MODE.SNIPER or self.__activeControlMode is None or not avatar_getter.isVehicleAlive():
            self.hideMarker()
            return
        else:
            vehicle = BigWorld.entity(vehicleID)
            isLeviathanBoss = False
            if vehicle is not None:
                isLeviathanBoss = VEHICLE_TAGS.LEVIATHAN in vehicle.typeDescriptor.type.tags
            if not isLeviathanBoss:
                if vehicleID == self.__activeBossVehicleID:
                    self.__activeBossVehicleID = None
                    self.hideMarker()
                return
            elif vehicle.model is None:
                self.hideMarker()
                return
            self.__activeBossVehicleID = vehicleID
            vehicleMatrix = Matrix(vehicle.model.matrix)
            pointProjection = cameras.projectPoint(vehicleMatrix.translation)
            isBehind = pointProjection.z > 1.0
            onLeftSide = pointProjection.x > 0.0 if isBehind else pointProjection.x < -1.0
            onRightSide = pointProjection.x < 0.0 if isBehind else pointProjection.x > 1.0
            if cameras.isPointOnScreen(vehicleMatrix.translation) and not isBehind:
                self.hideMarker()
            elif onLeftSide:
                self.showMarker(onLeftSide=True)
            elif onRightSide:
                self.showMarker(onLeftSide=False)
            else:
                self.hideMarker()
            playerMatrix = Matrix(BigWorld.player().consistentMatrices.attachedVehicleMatrix)
            delta = vehicleMatrix.translation - playerMatrix.translation
            distance = delta.length
            distanceString = ''
            if distance > 0:
                distanceString = i18n.makeString(INGAME_GUI.DISTANCE_METERS, meters=distance)
            self.as_updateDistanceS(distanceString)
            return

    def __onCameraChanged(self, mode, vehicleID=0):
        """
        Listener of event "AvatarInputHandler.onCameraChanged".
        """
        if mode != self.__activeControlMode:
            self.__activeControlMode = mode
            if self.__activeControlMode is _CTRL_MODE.SNIPER:
                self.hideMarker()

    def __arena_onPeriodChange(self, period, periodEndTime, periodLength, periodAdditionalInfo):
        if period == ARENA_PERIOD.AFTERBATTLE:
            self.__noMoreSignals = True
