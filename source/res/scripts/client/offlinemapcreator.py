# Embedded file name: scripts/client/OfflineMapCreator.py
import BigWorld, Math, Keys, GUI
from debug_utils import *
from functools import partial
from gui.app_loader import g_appLoader
import items.vehicles
import math
import Account
from account_helpers import AccountSyncData, Inventory, Stats, Shop
import constants
import ResMgr
_CFG = {'basic': {'v_scale': 1.3,
           'v_start_angles': Math.Vector3(0, 0, 0),
           'v_start_pos': Math.Vector3(50, 0, 50),
           'cam_start_dist': 9.0,
           'cam_start_angles': [-25.0, 110.0],
           'cam_start_target_pos': Math.Vector3(50, 0, 50),
           'cam_dist_constr': [6.0, 11.0],
           'cam_pitch_constr': [-70.0, -5.0],
           'cam_yaw_constr': [-180.0, 180.0],
           'cam_sens': 0.005,
           'cam_pivot_pos': Math.Vector3(0, 1, 0),
           'cam_fluency': 0.05,
           'emblems_alpha_damaged': 0.3,
           'emblems_alpha_undamaged': 0.9,
           'shadow_light_dir': (0.55, -1, -1.7)}}
_SPACE_NAME = None
_V_SCALE = None
_V_START_ANGLES = None
_V_START_POS = None
_CAM_START_DIST = None
_CAM_START_ANGLES = None
_CAM_START_TARGET_POS = None
_CAM_DIST_CONSTR = None
_CAM_PITCH_CONSTR = None
_CAM_SENS = None
_CAM_PIVOT_POS = None
_CAM_FLUENCY = None
_EMBLEMS_ALPHA_DAMAGED = None
_EMBLEMS_ALPHA_UNDAMAGED = None
_SHADOW_LIGHT_DIR = None

class OfflineMapCreator:

    def __init__(self):
        self.__spaceId = None
        self.__accountID = None
        self.__cam = None
        self.__waitCallback = None
        self.__loadingStatus = 0.0
        self.__destroyFunc = None
        self.__spaceMappingId = None
        self.__vEntityId = None
        self.__isActive = False
        self._loadListArenaNames()
        self.__arenaTypeID = 0
        return

    def create(self, mapName):
        global _V_START_POS
        global _V_START_ANGLES
        try:
            LOG_DEBUG('OfflineMapCreator.Create( %s )' % mapName)
            g_appLoader.showBattle()
            cfgType = 'basic'
            self.__loadCfg(cfgType, mapName)
            BigWorld.worldDrawEnabled(False)
            BigWorld.setWatcher('Visibility/GUI', False)
            self.__spaceId = BigWorld.createSpace()
            self.__isActive = True
            self.__arenaTypeID = self._arenaTypeIDByArenaName.get(mapName)
            self.__accountID = BigWorld.createEntity('Account', self.__spaceId, 0, _V_START_POS, (_V_START_ANGLES[2], _V_START_ANGLES[1], _V_START_ANGLES[0]), dict())
            self.__spaceMappingId = BigWorld.addSpaceGeometryMapping(self.__spaceId, None, 'spaces/' + mapName)
            self.__vEntityId = BigWorld.createEntity('Avatar', self.__spaceId, 0, _V_START_POS, (_V_START_ANGLES[2], _V_START_ANGLES[1], _V_START_ANGLES[0]), dict())
            BigWorld.player(BigWorld.entities[self.__vEntityId])
            self.__setupCamera()
            BigWorld.worldDrawEnabled(True)
        except:
            LOG_DEBUG('OfflineMapCreator.Create( %s ): FAILED with: ' % mapName)
            LOG_CURRENT_EXCEPTION()
            self.cancel()

        return

    def destroy(self):
        try:
            LOG_DEBUG('OfflineMapCreator.destroy()')
            self.__isActive = False
            BigWorld.worldDrawEnabled(False)
            BigWorld.setWatcher('Visibility/GUI', True)
            self.__spaceMappingId = 0
            BigWorld.cameraSpaceID(0)
            BigWorld.camera(None)
            self.__cam = None
            BigWorld.clearEntitiesAndSpaces()
            BigWorld.releaseSpace(self.__spaceId)
            self.__spaceId = 0
            self.__arenaTypeID = 0
            accountId = 0
            self.__vEntityId = 0
            BigWorld.worldDrawEnabled(True)
        except:
            LOG_DEBUG('OfflineMapCreator.destroy(): FAILED with: ')
            LOG_CURRENT_EXCEPTION()
            self.cancel()

        return

    def reset(self):
        LOG_DEBUG('OfflineMapCreator.reset()')
        self.destroy()
        self.__isActive = True

    def cancel(self):
        self.__spaceId = 0
        self.__spaceMappingId = 0
        self.__vEntityId = 0
        self.__isActive = False
        BigWorld.setWatcher('Visibility/GUI', True)
        BigWorld.worldDrawEnabled(True)

    def _clamp(self, minVal, maxVal, val):
        tmpVal = val
        tmpVal = max(minVal, val)
        tmpVal = min(maxVal, tmpVal)
        return tmpVal

    def Active(self):
        return self.__isActive

    def SetActive(self, _active):
        self.__isActive = _active

    def arenaId(self):
        return self.__arenaTypeID

    def _loadListArenaNames(self):
        self._arenaTypeIDByArenaName = {}
        ds = ResMgr.openSection(constants.ARENA_TYPE_XML_PATH + '_list_.xml')
        if ds is not None:
            for sec in ds.values():
                __arenaTypeID = sec.readInt('id')
                arenaName = sec.readString('name')
                self._arenaTypeIDByArenaName[arenaName] = __arenaTypeID

        return

    def __setupCamera(self):
        global _CAM_START_TARGET_POS
        global _CAM_START_DIST
        global _CAM_PIVOT_POS
        global _CAM_START_ANGLES
        global _CAM_FLUENCY
        self.__cam = BigWorld.CursorCamera()
        self.__cam.spaceID = self.__spaceId
        self.__cam.pivotMaxDist = _CAM_START_DIST
        self.__cam.maxDistHalfLife = _CAM_FLUENCY
        self.__cam.turningHalfLife = _CAM_FLUENCY
        self.__cam.movementHalfLife = 0.0
        self.__cam.pivotPosition = _CAM_PIVOT_POS
        mat = Math.Matrix()
        mat.setRotateYPR((math.radians(_CAM_START_ANGLES[1]), math.radians(_CAM_START_ANGLES[0]), 0.0))
        self.__cam.source = mat
        mat = Math.Matrix()
        mat.setTranslate(_CAM_START_TARGET_POS)
        self.__cam.target = mat
        BigWorld.camera(self.__cam)

    def __loadCfg(self, type, mapName):
        global _V_START_ANGLES
        global _CAM_PITCH_CONSTR
        global _CAM_PIVOT_POS
        global _EMBLEMS_ALPHA_DAMAGED
        global _EMBLEMS_ALPHA_UNDAMAGED
        global _CAM_FLUENCY
        global _SHADOW_LIGHT_DIR
        global _CAM_START_TARGET_POS
        global _V_SCALE
        global _SPACE_NAME
        global _CAM_START_ANGLES
        global _V_START_POS
        global _CAM_START_DIST
        global _CAM_DIST_CONSTR
        global _CAM_YAW_CONSTR
        global _CAM_SENS
        cfg = _CFG[type]
        _SPACE_NAME = mapName
        _V_SCALE = cfg['v_scale']
        _V_START_ANGLES = cfg['v_start_angles']
        _V_START_POS = cfg['v_start_pos']
        _CAM_START_DIST = cfg['cam_start_dist']
        _CAM_START_ANGLES = cfg['cam_start_angles']
        _CAM_START_TARGET_POS = cfg['cam_start_target_pos']
        _CAM_DIST_CONSTR = cfg['cam_dist_constr']
        _CAM_PITCH_CONSTR = cfg['cam_pitch_constr']
        _CAM_YAW_CONSTR = cfg['cam_yaw_constr']
        _CAM_SENS = cfg['cam_sens']
        _CAM_PIVOT_POS = cfg['cam_pivot_pos']
        _CAM_FLUENCY = cfg['cam_fluency']
        _EMBLEMS_ALPHA_DAMAGED = cfg['emblems_alpha_damaged']
        _EMBLEMS_ALPHA_UNDAMAGED = cfg['emblems_alpha_undamaged']
        _SHADOW_LIGHT_DIR = cfg['shadow_light_dir']


g_offlineMapCreator = OfflineMapCreator()
