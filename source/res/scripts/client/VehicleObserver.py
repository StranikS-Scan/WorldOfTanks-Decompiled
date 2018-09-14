# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/VehicleObserver.py
import BigWorld
from debug_utils import LOG_DEBUG_DEV
from AvatarInputHandler.aih_constants import CTRL_MODES
from AvatarInputHandler.control_modes import ArcadeControlMode, SniperControlMode, StrategicControlMode, ArtyControlMode

class VehicleObserver(object):

    def __init__(self):
        self.__cameraCaptureTime = 0.0
        self.__arcadeCameraShotPointToSend = None
        self.__arcadeCameraTranslationToSend = None
        self.__sniperCameraTranslationToSend = None
        self.__sniperCameraRotationToSend = None
        self.__sniperCameraZoomToSend = None
        self.__strategicCameraShotPointToSend = None
        self.__artyCameraShotPointToSend = None
        self.__artyCameraTranslationToSend = None
        self.__artyCameraRotationToSend = None
        return

    def setArcadeCameraDataForObservers(self, shotPoint, translation):
        self.__cameraCaptureTime = BigWorld.serverTime()
        self.__arcadeCameraShotPointToSend = shotPoint
        self.__arcadeCameraTranslationToSend = translation

    def setSniperCameraDataForObservers(self, translation, rotation, zoom):
        self.__cameraCaptureTime = BigWorld.serverTime()
        self.__sniperCameraTranslationToSend = translation
        self.__sniperCameraRotationToSend = rotation
        self.__sniperCameraZoomToSend = zoom

    def setStrategicCameraDataForObservers(self, shotPoint):
        self.__cameraCaptureTime = BigWorld.serverTime()
        self.__strategicCameraShotPointToSend = shotPoint

    def setArtyCameraDataForObservers(self, shotPoint, translation, rotation):
        self.__cameraCaptureTime = BigWorld.serverTime()
        self.__artyCameraShotPointToSend = shotPoint
        self.__artyCameraTranslationToSend = translation
        self.__artyCameraRotationToSend = rotation

    def transmitCameraData(self):
        player = BigWorld.player()
        if not player.isObserver():
            if isinstance(player.inputHandler.ctrl, ArcadeControlMode):
                if self.__arcadeCameraShotPointToSend:
                    self.cell.setRemoteCameraArcade({'time': self.__cameraCaptureTime,
                     'relTranslation': self.__arcadeCameraTranslationToSend,
                     'shotPoint': self.__arcadeCameraShotPointToSend})
            elif isinstance(player.inputHandler.ctrl, SniperControlMode):
                if self.__sniperCameraTranslationToSend:
                    self.cell.setRemoteCameraSniper({'time': self.__cameraCaptureTime,
                     'camMatrixTranslation': self.__sniperCameraTranslationToSend,
                     'camMatrixRotation': self.__sniperCameraRotationToSend,
                     'zoom': self.__sniperCameraZoomToSend})
            elif isinstance(player.inputHandler.ctrl, StrategicControlMode):
                if self.__strategicCameraShotPointToSend:
                    self.cell.setRemoteCameraStrategic({'time': self.__cameraCaptureTime,
                     'shotPoint': self.__strategicCameraShotPointToSend})
            elif isinstance(player.inputHandler.ctrl, ArtyControlMode):
                if self.__artyCameraShotPointToSend:
                    self.cell.setRemoteCameraArty({'time': self.__cameraCaptureTime,
                     'shotPoint': self.__artyCameraShotPointToSend,
                     'translation': self.__artyCameraTranslationToSend,
                     'rotation': self.__artyCameraRotationToSend})

    def __onCameraChanged(self, cameraName, currentVehicleId=None):
        observerFPVControlMode = CTRL_MODES.index(cameraName)
        if not BigWorld.player().isObserver():
            LOG_DEBUG_DEV('Vehicle.__onCameraChanged: switching to control mode', cameraName, observerFPVControlMode)
            self.cell.switchObserverFPVControlMode(observerFPVControlMode)

    def subscribeToCameraChanged(self):
        BigWorld.player().inputHandler.onCameraChanged += self.__onCameraChanged

    def unsubscribeFromCameraChanged(self):
        BigWorld.player().inputHandler.onCameraChanged -= self.__onCameraChanged

    def onLeaveWorld(self):
        self.unsubscribeFromCameraChanged()

    def startVisual(self):
        self.appearance.highlighter.setVehicleOwnership()
