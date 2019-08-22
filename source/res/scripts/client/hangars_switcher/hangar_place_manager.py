# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/hangars_switcher/hangar_place_manager.py
import math
from collections import namedtuple
import BigWorld
import WWISE
from helpers import dependency
from skeletons.hangars_switcher import IHangarPlaceManager
from skeletons.gui.shared.utils import IHangarSpace
from skeletons.hangars_switcher import IHangarsSwitchManager
from skeletons.hangars_switcher import HangarNames
from gui.ClientHangarSpace import hangarCFG
from gui.ClientHangarSpace import secondaryHangarCFG
from gui.shared import g_eventBus, events, EVENT_BUS_SCOPE
from gui.hangar_cameras.hangar_camera_manager import IMMEDIATE_CAMERA_MOVEMENT_MODE
_PlaceParams = namedtuple('_PlaceParams', ('hangarConfig', 'environment', 'isHeroTankMarkerDisabled', 'soundEvent'))
_HANGAR_PLACE_PARAMS = {HangarNames.BATTLE_ROYALE: _PlaceParams(secondaryHangarCFG, 'h26', True, 'hangar_br_enter')}
_HYBRID_HANGAR_SPACE_PATH = 'spaces/h20_wot_bday_h26_br'

class HangarPlaceManager(IHangarPlaceManager):
    hangarSpace = dependency.descriptor(IHangarSpace)
    hangarsSwitchMgr = dependency.descriptor(IHangarsSwitchManager)

    def __init__(self):
        super(HangarPlaceManager, self).__init__()
        self.__defaultPlaceParams = _PlaceParams(hangarCFG, '', False, 'hangar_h20_enter')
        self.__placeNameDuringWaitingForHangarVehicle = None
        self.__currentPlace = ''
        return

    def init(self):
        self.hangarSpace.onSpaceCreate += self.__onHangarSpaceCreated
        self.hangarSpace.onSpaceDestroy += self.__onHangarSpaceDestroy
        self.hangarSpace.onVehicleChanged += self.__onHangarVehicleChanged

    def destroy(self):
        self.hangarSpace.onSpaceCreate -= self.__onHangarSpaceCreated
        self.hangarSpace.onSpaceDestroy -= self.__onHangarSpaceDestroy
        self.hangarSpace.onVehicleChanged -= self.__onHangarVehicleChanged
        self.__clear()

    def __clear(self):
        self.__placeNameDuringWaitingForHangarVehicle = None
        self.__currentPlace = ''
        return

    def switchPlaceTo(self, placeName):
        if not placeName:
            return
        else:
            self.__clear()
            if placeName in _HANGAR_PLACE_PARAMS:
                placeParams = _HANGAR_PLACE_PARAMS[placeName]
            else:
                placeParams = self.__defaultPlaceParams
            hangarVehicle = self.__getHangarVehicleEntity()
            if hangarVehicle is None or not hangarVehicle.isVehicleLoaded:
                self.__placeNameDuringWaitingForHangarVehicle = placeName
                return
            cfg = placeParams.hangarConfig()
            if self.__switchCamera(cfg):
                self.__switchHangarEnvironment(placeParams.environment)
                self.__switchHangarVehicle(cfg)
                WWISE.WW_eventGlobal(placeParams.soundEvent)
                self.__currentPlace = placeName
                g_eventBus.handleEvent(events.HangarPlaceManagerEvent(events.HangarPlaceManagerEvent.ON_PLACE_SWITCHED), EVENT_BUS_SCOPE.LOBBY)
                g_eventBus.handleEvent(events.HangarVehicleEvent(events.HangarVehicleEvent.HERO_TANK_MARKER, ctx={'isDisable': placeParams.isHeroTankMarkerDisabled}), EVENT_BUS_SCOPE.LOBBY)
            return

    @property
    def currentPlace(self):
        return self.__currentPlace

    def __switchCamera(self, cfg):
        if not self.hangarSpace.spaceInited:
            return False
        elif cfg is None:
            return False
        else:
            mainCfg = hangarCFG()
            targetPos = cfg['cam_start_target_pos']
            pivotPos = cfg['cam_pivot_pos']
            initYaw = math.radians(cfg['cam_start_angles'][0])
            initPitch = math.radians(cfg['cam_start_angles'][1])
            dist = cfg['cam_start_dist']
            camConstraints = [mainCfg['cam_pitch_constr'], mainCfg['cam_yaw_constr'], cfg['cam_dist_constr']]
            self.hangarSpace.space.getCameraManager().setCameraLocation(targetPos=targetPos, pivotPos=pivotPos, yaw=initYaw, pitch=initPitch, dist=dist, camConstraints=camConstraints, movementMode=IMMEDIATE_CAMERA_MOVEMENT_MODE)
            return True

    @staticmethod
    def __switchHangarVehicle(cfg):
        targetPos = cfg['v_start_pos']
        yaw, pitch, roll = cfg['v_start_angles']
        shadowYOffset = cfg['shadow_forward_y_offset'] if BigWorld.getGraphicsSetting('RENDER_PIPELINE') == 1 else cfg['shadow_deferred_y_offset']
        g_eventBus.handleEvent(events.HangarCustomizationEvent(events.HangarCustomizationEvent.CHANGE_VEHICLE_MODEL_TRANSFORM, ctx={'targetPos': targetPos,
         'rotateYPR': (yaw, pitch, roll),
         'shadowYOffset': shadowYOffset}), scope=EVENT_BUS_SCOPE.LOBBY)

    @staticmethod
    def __switchHangarEnvironment(envName):
        env = BigWorld.EnvironmentSwitcher(envName)
        if envName:
            env.enable(True)
        else:
            env.enable(False)

    def __onHangarSpaceCreated(self):
        if self.hangarSpace.spacePath != _HYBRID_HANGAR_SPACE_PATH:
            return
        if self.hangarsSwitchMgr.lastHangarName == HangarNames.BATTLE_ROYALE:
            self.switchPlaceTo(HangarNames.BATTLE_ROYALE)
        else:
            WWISE.WW_eventGlobal(self.__defaultPlaceParams.soundEvent)

    def __onHangarVehicleChanged(self):
        if self.__placeNameDuringWaitingForHangarVehicle:
            self.switchPlaceTo(self.__placeNameDuringWaitingForHangarVehicle)

    def __onHangarSpaceDestroy(self, _):
        if self.__currentPlace:
            g_eventBus.handleEvent(events.HangarVehicleEvent(events.HangarVehicleEvent.HERO_TANK_MARKER, ctx={'isDisable': False}), EVENT_BUS_SCOPE.LOBBY)
        self.__clear()

    def __getHangarVehicleEntity(self):
        if self.hangarSpace.space is None:
            return
        else:
            entityId = self.hangarSpace.space.vehicleEntityId
            return BigWorld.entities.get(entityId, None)
