# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/vehicle_preview/hangar_switchers.py
from enum import Enum, unique
import BigWorld
from gui.hangar_cameras.c11n_hangar_camera_manager import C11nHangarCameraManager
from gui.impl.lobby.offers import getGfImagePath
from gui.Scaleform.daapi.view.lobby.customization.sound_constants import C11N_SOUND_SPACE
from gui.Scaleform.Waiting import Waiting
from gui.shared import g_eventBus, events, EVENT_BUS_SCOPE
from helpers import dependency
from skeletons.gui.customization import ICustomizationService
from skeletons.gui.shared.utils import IHangarSpace

@unique
class CustomHangars(Enum):
    CUSTOMIZATION_HANGAR = 'customizationHangar'

    @classmethod
    def hasValue(cls, value):
        return value in cls._value2member_map_


class _CustomizationHangarSwitcher(object):
    __customization = dependency.descriptor(ICustomizationService)
    __hangarSpace = dependency.descriptor(IHangarSpace)
    __waitingBgImg = 'gui/maps/icons/lobby/bmWaitingBg.png'
    __waitingStrPath = 'hof/loading'

    def __init__(self):
        self.__cameraManager = C11nHangarCameraManager(verticalOffset=0.0)
        self.__callbackID = None
        self.__renderEnv = None
        Waiting.show(self.__waitingStrPath, backgroundImage=getGfImagePath(self.__waitingBgImg), isAlwaysOnTop=True, isSingle=True)
        return

    def switchToHangar(self):
        self.__cameraManager.init()
        self.__renderEnv = BigWorld.CustomizationEnvironment()
        if not self.__hangarSpace.spaceInited or not self.__hangarSpace.isModelLoaded:
            self.__hangarSpace.onVehicleChanged += self.__hangarVehicleLoaded
            self.__hangarSpace.onSpaceChanged += self.__hangarVehicleLoaded
        else:
            self.__hangarVehicleLoaded()

    def returnFromHangar(self):
        if self.__callbackID is not None:
            BigWorld.cancelCallback(self.__callbackID)
            self.__callbackID = None
        self.__hangarSpace.onVehicleChanged -= self.__hangarVehicleLoaded
        self.__hangarSpace.onSpaceChanged -= self.__hangarVehicleLoaded
        g_eventBus.handleEvent(events.HangarCustomizationEvent(events.HangarCustomizationEvent.RESET_VEHICLE_MODEL_TRANSFORM), scope=EVENT_BUS_SCOPE.LOBBY)
        if self.__renderEnv:
            self.__renderEnv.enable(False)
            self.__renderEnv = None
        self.__cameraManager.locateCameraToStartState()
        self.__cameraManager.fini()
        return

    def __hangarVehicleLoaded(self):
        self.__hangarSpace.onVehicleChanged -= self.__hangarVehicleLoaded
        self.__hangarSpace.onSpaceChanged -= self.__hangarVehicleLoaded
        self.__customization.moveHangarVehicleToCustomizationRoom()
        self.__callbackID = BigWorld.callback(0.1, self.__cameraCallback)

    def __cameraCallback(self):
        self.__cameraManager.locateCameraToCustomizationPreview(forceLocate=True)
        self.__callbackID = BigWorld.callback(0.1, self.__renderEnvCallback)

    def __renderEnvCallback(self):
        self.__renderEnv.enable(True)
        self.__callbackID = None
        Waiting.hide(self.__waitingStrPath)
        return


def getHangarSwitcher(hangarAlias):
    hangarAliasToSwitcher = {CustomHangars.CUSTOMIZATION_HANGAR.value: _CustomizationHangarSwitcher}
    hangarSwitcherClass = hangarAliasToSwitcher.get(hangarAlias)
    return hangarSwitcherClass() if hangarSwitcherClass else None


def getHangarSoundSpace(hangarAlias):
    hangarAliasToSpundSpace = {CustomHangars.CUSTOMIZATION_HANGAR.value: C11N_SOUND_SPACE}
    return hangarAliasToSpundSpace.get(hangarAlias)
