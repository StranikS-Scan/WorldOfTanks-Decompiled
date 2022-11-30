# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/new_year/sound_rtpc_controller.py
import math
import BigWorld
from NewYearJukeboxObject import NewYearJukeboxObject
from gui.shared import g_eventBus
from gui.hangar_cameras.hangar_camera_common import CameraRelatedEvents
from gui.impl.new_year.sounds import NewYearSoundVars, NewYearSoundsManager
from new_year.ny_constants import CustomizationObjects
_MIN_DIST = 0.1
_RTPC_MUSIC_POSITION_CONTROL_MIN_VALUE = 0
_RTPC_MUSIC_POSITION_CONTROL_MAX_VALUE = 100
_RTPC_GIFT_AVAILABILITY_MIN_VALUE = 0
_RTPC_GIFT_AVAILABILITY_MAX_VALUE = 100

class SoundRTPCController(object):
    __slots__ = ('__entityID', '__callbackID', '__lastDistance', '__currentLocation')

    def __init__(self):
        self.__entityID = None
        self.__callbackID = None
        self.__lastDistance = 0
        self.__currentLocation = None
        return

    def init(self, location):
        g_eventBus.addListener(CameraRelatedEvents.IDLE_CAMERA, self.__handleIdleCameraActivation)
        self.setCurrentLocation(location, True)

    def fini(self):
        NewYearSoundsManager.setRTPC(NewYearSoundVars.RTPC_MUSIC_POSITION_CONTROL, _RTPC_MUSIC_POSITION_CONTROL_MIN_VALUE)
        g_eventBus.removeListener(CameraRelatedEvents.IDLE_CAMERA, self.__handleIdleCameraActivation)
        self.__stopTicker()
        self.__entityID = None
        return

    def setCurrentLocation(self, location, force=False):
        if force or self.__currentLocation != location:
            self.__currentLocation = location
            if self.__currentLocation == CustomizationObjects.FAIR:
                self.__startTicker()
            else:
                self.__stopTicker()
                NewYearSoundsManager.setRTPC(NewYearSoundVars.RTPC_JUKEBOX_DISTANCE, 0)
            if self.__currentLocation is not None:
                positionControlValue = _RTPC_MUSIC_POSITION_CONTROL_MAX_VALUE
            else:
                positionControlValue = _RTPC_MUSIC_POSITION_CONTROL_MIN_VALUE
            NewYearSoundsManager.setRTPC(NewYearSoundVars.RTPC_MUSIC_POSITION_CONTROL, positionControlValue)
        NewYearSoundsManager.setRTPC(NewYearSoundVars.RTPC_GIFT_AVAILABILITY, _RTPC_GIFT_AVAILABILITY_MIN_VALUE)
        return

    @staticmethod
    def setLevelAtmosphere(level):
        NewYearSoundsManager.setRTPC(NewYearSoundVars.RTPC_LEVEL_ATMOSPHERE, level)

    @staticmethod
    def __getJukeboxEntityId():
        for entity in BigWorld.entities.values():
            if isinstance(entity, NewYearJukeboxObject):
                return entity.id

        return None

    def __getJukeboxEntity(self):
        if self.__entityID is None:
            self.__entityID = self.__getJukeboxEntityId()
        return BigWorld.entities.get(self.__entityID, None) if self.__entityID is not None else None

    def __startTicker(self):
        if self.__callbackID is None:
            self.__lastDistance = 0
        return

    def __stopTicker(self):
        if self.__callbackID is not None:
            BigWorld.cancelCallback(self.__callbackID)
            self.__callbackID = None
        return

    def __update(self):
        jukeboxEntity = self.__getJukeboxEntity()
        if jukeboxEntity is None:
            return
        else:
            camera = BigWorld.camera()
            cameraPos = camera.position
            distance = jukeboxEntity.position.distTo(cameraPos)
            diff = math.fabs(self.__lastDistance - distance)
            if diff > _MIN_DIST:
                NewYearSoundsManager.setRTPC(NewYearSoundVars.RTPC_JUKEBOX_DISTANCE, distance)
                self.__lastDistance = distance
            return

    def __tick(self):
        self.__update()
        self.__callbackID = BigWorld.callback(0.0, self.__tick)

    def __handleIdleCameraActivation(self, event):
        if self.__currentLocation is not None:
            return
        else:
            positionControlValue = _RTPC_MUSIC_POSITION_CONTROL_MAX_VALUE if event.ctx['started'] else _RTPC_MUSIC_POSITION_CONTROL_MIN_VALUE
            NewYearSoundsManager.setRTPC(NewYearSoundVars.RTPC_MUSIC_POSITION_CONTROL, positionControlValue)
            return
