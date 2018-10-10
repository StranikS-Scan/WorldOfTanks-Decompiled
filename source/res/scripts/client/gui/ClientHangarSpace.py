# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/ClientHangarSpace.py
import copy
import json
import math
from logging import getLogger
import BigWorld
import Math
import MusicControllerWWISE
import ResMgr
import constants
from PlayerEvents import g_playerEvents
from debug_utils import LOG_DEBUG, LOG_ERROR, LOG_CURRENT_EXCEPTION
from gui.Scaleform.framework.managers.optimization_manager import GraphicsOptimizationManager
from helpers import dependency
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.game_control import IIGRController
from gui.hangar_cameras.hangar_camera_manager import HangarCameraManager
from skeletons.gui.shared.gui_items import IGuiItemsFactory
from skeletons.map_activities import IMapActivities
from skeletons.gui.shared.utils import IHangarSpace
_DEFAULT_SPACES_PATH = 'spaces'
_SERVER_CMD_CHANGE_HANGAR = 'cmd_change_hangar'
_SERVER_CMD_CHANGE_HANGAR_PREM = 'cmd_change_hangar_prem'
_CUSTOMIZATION_HANGAR_SETTINGS_SEC = 'customizationHangarSettings'

def _getDefaultHangarPath(isPremium):
    return '%s/hangar_v3' % _DEFAULT_SPACES_PATH


def _getHangarPath(isPremium, isPremIGR):
    global _HANGAR_CFGS
    global _EVENT_HANGAR_PATHS
    if isPremium in _EVENT_HANGAR_PATHS:
        return _EVENT_HANGAR_PATHS[isPremium]
    return _HANGAR_CFGS[_getDefaultHangarPath(False)][_IGR_HANGAR_PATH_KEY] if isPremIGR else _getDefaultHangarPath(isPremium)


def _getHangarKey(path):
    return path.lower()


def _getHangarType(isPremium):
    return 'premium' if isPremium else 'basic'


_CFG = {}
_HANGAR_CFGS = {}
_EVENT_HANGAR_PATHS = {}
_IGR_HANGAR_PATH_KEY = 'igrPremHangarPath' + ('CN' if constants.IS_CHINA else '')
_logger = getLogger(__name__)

def hangarCFG():
    global _CFG
    return _CFG


def customizationHangarCFG():
    return _CFG.get(_CUSTOMIZATION_HANGAR_SETTINGS_SEC)


def _readHangarSettings():
    hangarsXml = ResMgr.openSection('gui/hangars.xml')
    paths = [ path for path, _ in ResMgr.openSection(_DEFAULT_SPACES_PATH).items() ]
    configset = {}
    for folderName in paths:
        spacePath = '{prefix}/{node}'.format(prefix=_DEFAULT_SPACES_PATH, node=folderName)
        spaceKey = _getHangarKey(spacePath)
        settingsXmlPath = '{path}/{file}/{sec}'.format(path=spacePath, file='space.settings', sec='hangarSettings')
        ResMgr.purge(settingsXmlPath, True)
        settingsXml = ResMgr.openSection(settingsXmlPath)
        if settingsXml is None:
            continue
        cfg = {}
        loadConfigValue('shadow_model_name', hangarsXml, hangarsXml.readString, cfg)
        loadConfigValue('shadow_default_texture_name', hangarsXml, hangarsXml.readString, cfg)
        loadConfigValue('shadow_empty_texture_name', hangarsXml, hangarsXml.readString, cfg)
        loadConfigValue(_IGR_HANGAR_PATH_KEY, hangarsXml, hangarsXml.readString, cfg)
        loadConfig(cfg, settingsXml)
        if settingsXml.has_key(_CUSTOMIZATION_HANGAR_SETTINGS_SEC):
            customizationXmlSection = settingsXml[_CUSTOMIZATION_HANGAR_SETTINGS_SEC]
            customizationCfg = {}
            _loadCustomizationConfig(customizationCfg, customizationXmlSection)
            cfg[_CUSTOMIZATION_HANGAR_SETTINGS_SEC] = customizationCfg
        configset[spaceKey] = cfg
        _validateConfigValues(cfg)

    return configset


def loadConfig(cfg, xml, defaultCfg=None):
    if defaultCfg is None:
        defaultCfg = cfg
    defaultFakeShadowOffsetsCfg = {'shadow_forward_y_offset': 0.0,
     'shadow_deferred_y_offset': 0.0}
    loadConfigValue('v_scale', xml, xml.readFloat, cfg, defaultCfg)
    loadConfigValue('v_start_angles', xml, xml.readVector3, cfg, defaultCfg)
    loadConfigValue('v_start_pos', xml, xml.readVector3, cfg, defaultCfg)
    loadConfigValue('cam_start_target_pos', xml, xml.readVector3, cfg, defaultCfg)
    loadConfigValue('cam_start_dist', xml, xml.readFloat, cfg, defaultCfg)
    loadConfigValue('cam_start_angles', xml, xml.readVector2, cfg, defaultCfg)
    loadConfigValue('cam_dist_constr', xml, xml.readVector2, cfg, defaultCfg)
    loadConfigValue('cam_min_dist_vehicle_hull_length_k', xml, xml.readFloat, cfg, defaultCfg)
    loadConfigValue('cam_pitch_constr', xml, xml.readVector2, cfg, defaultCfg)
    loadConfigValue('cam_yaw_constr', xml, xml.readVector2, cfg, defaultCfg)
    loadConfigValue('preview_cam_dist_constr', xml, xml.readVector2, cfg, defaultCfg)
    loadConfigValue('cam_sens', xml, xml.readFloat, cfg, defaultCfg)
    loadConfigValue('cam_dist_sens', xml, xml.readFloat, cfg, defaultCfg)
    loadConfigValue('cam_pivot_pos', xml, xml.readVector3, cfg, defaultCfg)
    loadConfigValue('cam_fluency', xml, xml.readFloat, cfg, defaultCfg)
    loadConfigValue('emblems_alpha_damaged', xml, xml.readFloat, cfg, defaultCfg)
    loadConfigValue('emblems_alpha_undamaged', xml, xml.readFloat, cfg, defaultCfg)
    loadConfigValue('shadow_light_dir', xml, xml.readVector3, cfg, defaultCfg)
    loadConfigValue('preview_cam_start_dist', xml, xml.readFloat, cfg, defaultCfg)
    loadConfigValue('preview_cam_start_angles', xml, xml.readVector2, cfg, defaultCfg)
    loadConfigValue('preview_cam_pivot_pos', xml, xml.readVector3, cfg, defaultCfg)
    loadConfigValue('preview_cam_start_target_pos', xml, xml.readVector3, cfg, defaultCfg)
    loadConfigValue('shadow_model_name', xml, xml.readString, cfg, defaultCfg)
    loadConfigValue('shadow_forward_y_offset', xml, xml.readFloat, cfg, defaultFakeShadowOffsetsCfg)
    loadConfigValue('shadow_deferred_y_offset', xml, xml.readFloat, cfg, defaultFakeShadowOffsetsCfg)
    loadConfigValue('shadow_default_texture_name', xml, xml.readString, cfg, defaultCfg)
    loadConfigValue('shadow_empty_texture_name', xml, xml.readString, cfg, defaultCfg)
    loadConfigValue('cam_capsule_scale', xml, xml.readVector3, cfg, defaultCfg)
    loadConfigValue('cam_capsule_gun_scale', xml, xml.readVector3, cfg, defaultCfg)
    defaultIdleCfg = {'cam_idle_pitch_constr': Math.Vector2(0.0, 0.0),
     'cam_idle_dist_constr': Math.Vector2(10.0, 10.0),
     'cam_idle_yaw_period': 0.0,
     'cam_idle_pitch_period': 0.0,
     'cam_idle_dist_period': 0.0,
     'cam_idle_easing_in_time': 0.0}
    loadConfigValue('cam_idle_pitch_constr', xml, xml.readVector2, cfg, defaultIdleCfg)
    loadConfigValue('cam_idle_dist_constr', xml, xml.readVector2, cfg, defaultIdleCfg)
    loadConfigValue('cam_idle_yaw_period', xml, xml.readFloat, cfg, defaultIdleCfg)
    loadConfigValue('cam_idle_pitch_period', xml, xml.readFloat, cfg, defaultIdleCfg)
    loadConfigValue('cam_idle_dist_period', xml, xml.readFloat, cfg, defaultIdleCfg)
    loadConfigValue('cam_idle_easing_in_time', xml, xml.readFloat, cfg, defaultIdleCfg)
    defaultParallaxCfg = {'cam_parallax_distance': Math.Vector2(0.0, 0.0),
     'cam_parallax_angles': Math.Vector2(0.0, 0.0),
     'cam_parallax_smoothing': 0.0}
    loadConfigValue('cam_parallax_distance', xml, xml.readVector2, cfg, defaultParallaxCfg)
    loadConfigValue('cam_parallax_angles', xml, xml.readVector2, cfg, defaultParallaxCfg)
    loadConfigValue('cam_parallax_smoothing', xml, xml.readFloat, cfg, defaultParallaxCfg)
    defaultVehicleAnglesCfg = {'vehicle_gun_pitch': 0.0,
     'vehicle_turret_yaw': 0.0}
    loadConfigValue('vehicle_gun_pitch', xml, xml.readFloat, cfg, defaultVehicleAnglesCfg)
    loadConfigValue('vehicle_turret_yaw', xml, xml.readFloat, cfg, defaultVehicleAnglesCfg)
    for i in range(0, 3):
        cfg['v_start_angles'][i] = math.radians(cfg['v_start_angles'][i])

    return


def _validateConfigValues(cfg):
    if cfg['cam_pitch_constr'][0] <= -90.0:
        _logger.warning('incorrect value - cam_pitch_constr[0] must be greater than -90 degrees!')
        cfg['cam_pitch_constr'][0] = -89.9


def _loadCustomizationConfig(cfg, xml):
    defaultFakeShadowOffsetsCfg = {'shadow_forward_y_offset': 0.0,
     'shadow_deferred_y_offset': 0.0}
    loadConfigValue('v_start_pos', xml, xml.readVector3, cfg, cfg)
    loadConfigValue('v_start_angles', xml, xml.readVector3, cfg, cfg)
    loadConfigValue('cam_start_dist', xml, xml.readFloat, cfg, cfg)
    loadConfigValue('cam_dist_constr', xml, xml.readVector2, cfg, cfg)
    loadConfigValue('cam_start_angles', xml, xml.readVector2, cfg, cfg)
    loadConfigValue('cam_pivot_pos', xml, xml.readVector3, cfg, cfg)
    loadConfigValue('cam_start_target_pos', xml, xml.readVector3, cfg, cfg)
    loadConfigValue('shadow_forward_y_offset', xml, xml.readFloat, cfg, defaultFakeShadowOffsetsCfg)
    loadConfigValue('shadow_deferred_y_offset', xml, xml.readFloat, cfg, defaultFakeShadowOffsetsCfg)
    loadConfigValue('cam_fluency', xml, xml.readFloat, cfg, cfg)


def loadConfigValue(name, xml, fn, cfg, defaultCfg=None):
    if xml.has_key(name):
        cfg[name] = fn(name)
    else:
        cfg[name] = defaultCfg.get(name) if defaultCfg is not None else None
    return


class ClientHangarSpace(object):
    igrCtrl = dependency.descriptor(IIGRController)
    settingsCore = dependency.descriptor(ISettingsCore)
    itemsFactory = dependency.descriptor(IGuiItemsFactory)
    mapActivities = dependency.descriptor(IMapActivities)

    def __init__(self, onVehicleLoadedCallback):
        global _HANGAR_CFGS
        self.__spaceId = None
        self.__cameraManager = None
        self.__waitCallback = None
        self.__loadingStatus = 0.0
        self.__spaceMappingId = None
        self.__onLoadedCallback = None
        self.__vEntityId = None
        self.__selectedEmblemInfo = None
        self.__showMarksOnGun = False
        self.__prevDirection = 0.0
        self.__onVehicleLoadedCallback = onVehicleLoadedCallback
        self.__gfxOptimizerMgr = None
        self.__optimizerID = None
        _HANGAR_CFGS = _readHangarSettings()
        return

    def create(self, isPremium, onSpaceLoadedCallback=None):
        global _CFG
        BigWorld.worldDrawEnabled(False)
        BigWorld.wg_setSpecialFPSMode()
        self.__onLoadedCallback = onSpaceLoadedCallback
        self.__spaceId = BigWorld.createSpace()
        isIGR = self.igrCtrl.getRoomType() == constants.IGR_TYPE.PREMIUM
        spacePath = _getHangarPath(isPremium, isIGR)
        spaceType = _getHangarType(isPremium)
        LOG_DEBUG('load hangar: hangar type = <{0:>s}>, space = <{1:>s}>'.format(spaceType, spacePath))
        safeSpacePath = _getDefaultHangarPath(False)
        if ResMgr.openSection(spacePath) is None:
            LOG_ERROR('Failed to load hangar from path: %s; default hangar will be loaded instead' % spacePath)
            spacePath = safeSpacePath
        try:
            self.__spaceMappingId = BigWorld.addSpaceGeometryMapping(self.__spaceId, None, spacePath)
        except Exception:
            try:
                LOG_CURRENT_EXCEPTION()
                spacePath = safeSpacePath
                self.__spaceMappingId = BigWorld.addSpaceGeometryMapping(self.__spaceId, None, spacePath)
            except Exception:
                BigWorld.releaseSpace(self.__spaceId)
                self.__spaceMappingId = None
                self.__spaceId = None
                LOG_CURRENT_EXCEPTION()
                return

        spaceKey = _getHangarKey(spacePath)
        _CFG = copy.deepcopy(_HANGAR_CFGS[spaceKey])
        self.__vEntityId = BigWorld.createEntity('HangarVehicle', self.__spaceId, 0, _CFG['v_start_pos'], (_CFG['v_start_angles'][2], _CFG['v_start_angles'][1], _CFG['v_start_angles'][0]), dict())
        self.__cameraManager = HangarCameraManager(self.__spaceId)
        self.__cameraManager.init()
        self.__waitCallback = BigWorld.callback(0.1, self.__waitLoadingSpace)
        self.__gfxOptimizerMgr = GraphicsOptimizationManager()
        size = BigWorld.screenSize()
        self.__optimizerID = self.__gfxOptimizerMgr.registerOptimizationArea(0, 0, size[0], size[1])
        self.mapActivities.generateOfflineActivities(spacePath)
        BigWorld.pauseDRRAutoscaling(True)
        return

    def recreateVehicle(self, vDesc, vState, onVehicleLoadedCallback=None):
        if not self.__vEntityId:
            return
        else:
            vehicle = BigWorld.entity(self.__vEntityId)
            if not vehicle:
                if onVehicleLoadedCallback:
                    onVehicleLoadedCallback()
                return
            if onVehicleLoadedCallback is None:
                onVehicleLoadedCallback = self.__onVehicleLoadedCallback
            vehicle.recreateVehicle(vDesc, vState, onVehicleLoadedCallback)
            return

    def removeVehicle(self):
        vehicle = BigWorld.entity(self.__vEntityId)
        if vehicle is not None:
            vehicle.removeVehicle()
        self.__selectedEmblemInfo = None
        return

    def moveVehicleTo(self, position):
        try:
            vehicle = BigWorld.entity(self.__vEntityId)
            vehicle.model.motors[0].signal = _createMatrix(_CFG['v_scale'], _CFG['v_start_angles'], position)
        except Exception:
            LOG_CURRENT_EXCEPTION()

    def setVehicleSelectable(self, flag):
        for entity in BigWorld.entities.values():
            from ClientSelectableCameraVehicle import ClientSelectableCameraVehicle
            if isinstance(entity, ClientSelectableCameraVehicle):
                entity.setSelectable(flag)

    def updateVehicleCustomization(self, outfit):
        vEntity = self.getVehicleEntity()
        if vEntity is not None and vEntity.isVehicleLoaded:
            outfit = outfit or self.itemsFactory.createOutfit()
            vEntity.updateVehicleCustomization(outfit)
        return

    def getCentralPointForArea(self, areaId):
        vEntity = self.getVehicleEntity()
        return vEntity.appearance.getCentralPointForArea(areaId) if vEntity is not None and vEntity.isVehicleLoaded else None

    def destroy(self):
        self.__onLoadedCallback = None
        self.__closeOptimizedRegion()
        self.__destroy()
        return

    def spaceLoaded(self):
        return self.__loadingStatus >= 1

    def spaceLoading(self):
        return self.__waitCallback is not None

    def getSlotPositions(self):
        vEntity = self.getVehicleEntity()
        return vEntity.appearance.getSlotPositions() if vEntity is not None and vEntity.isVehicleLoaded else None

    def getVehicleEntity(self):
        return BigWorld.entity(self.__vEntityId) if self.__vEntityId else None

    @property
    def vehicleEntityId(self):
        return self.__vEntityId

    def __destroy(self):
        LOG_DEBUG('Hangar successfully destroyed.')
        MusicControllerWWISE.unloadCustomSounds()
        if self.__cameraManager:
            self.__cameraManager.destroy()
            self.__cameraManager = None
        self.__loadingStatus = 0.0
        self.__onLoadedCallback = None
        if self.__waitCallback is not None:
            BigWorld.cancelCallback(self.__waitCallback)
            self.__waitCallback = None
        BigWorld.SetDrawInflux(False)
        self.mapActivities.stop()
        if self.__spaceId is not None and BigWorld.isClientSpace(self.__spaceId):
            if self.__spaceMappingId is not None:
                BigWorld.delSpaceGeometryMapping(self.__spaceId, self.__spaceMappingId)
            BigWorld.clearSpace(self.__spaceId)
            BigWorld.releaseSpace(self.__spaceId)
        self.__spaceMappingId = None
        self.__spaceId = None
        self.__vEntityId = None
        BigWorld.wg_disableSpecialFPSMode()
        return

    def __waitLoadingSpace(self):
        self.__loadingStatus = BigWorld.spaceLoadStatus()
        BigWorld.worldDrawEnabled(True)
        if self.__loadingStatus < 1 or not BigWorld.virtualTextureRenderComplete():
            self.__waitCallback = BigWorld.callback(0.1, self.__waitLoadingSpace)
        else:
            BigWorld.uniprofSceneStart()
            self.__closeOptimizedRegion()
            self.__waitCallback = None
            if self.__onLoadedCallback is not None:
                self.__onLoadedCallback()
                self.__onLoadedCallback = None
        return

    def __closeOptimizedRegion(self):
        if self.__gfxOptimizerMgr is not None:
            self.__gfxOptimizerMgr.unregisterOptimizationArea(self.__optimizerID)
            self.__gfxOptimizerMgr = None
            self.__optimizerID = None
        return

    def setCameraLocation(self, *args):
        self.__cameraManager.setCameraLocation(*args)

    def getCameraLocation(self):
        return self.__cameraManager.getCameraLocation()

    def getCameraManager(self):
        return self.__cameraManager

    @property
    def camera(self):
        return self.__cameraManager.camera


class _ClientHangarSpacePathOverride(object):
    hangarSpace = dependency.descriptor(IHangarSpace)

    def __init__(self):
        g_playerEvents.onEventNotificationsChanged += self.__onEventNotificationsChanged
        g_playerEvents.onDisconnected += self.__onDisconnected

    def destroy(self):
        g_playerEvents.onEventNotificationsChanged -= self.__onEventNotificationsChanged
        g_playerEvents.onDisconnected -= self.__onDisconnected

    def setPremium(self, isPremium):
        self.hangarSpace.refreshSpace(isPremium, True)

    def setPath(self, path, isPremium=None, isReload=True):
        if path is not None and not path.startswith('spaces/'):
            path = 'spaces/' + path
        if isPremium is None:
            isPremium = self.hangarSpace.isPremium
        if path is not None:
            _EVENT_HANGAR_PATHS[isPremium] = path
        elif _EVENT_HANGAR_PATHS.has_key(isPremium):
            del _EVENT_HANGAR_PATHS[isPremium]
        if isReload:
            self.hangarSpace.refreshSpace(self.hangarSpace.isPremium, True)
            self.hangarSpace.onSpaceChanged()
        return

    def __onDisconnected(self):
        global _EVENT_HANGAR_PATHS
        _EVENT_HANGAR_PATHS = {}

    def __onEventNotificationsChanged(self, diff):
        isPremium = self.hangarSpace.isPremium
        hasChanged = False
        for notification in diff['removed']:
            if notification['type'] == _SERVER_CMD_CHANGE_HANGAR:
                if _EVENT_HANGAR_PATHS.has_key(False):
                    del _EVENT_HANGAR_PATHS[False]
                if not isPremium:
                    hasChanged = True
            if notification['type'] == _SERVER_CMD_CHANGE_HANGAR_PREM:
                if _EVENT_HANGAR_PATHS.has_key(True):
                    del _EVENT_HANGAR_PATHS[True]
                if isPremium:
                    hasChanged = True

        for notification in diff['added']:
            if not notification['data']:
                continue
            path = None
            try:
                data = json.loads(notification['data'])
                path = data['hangar']
            except Exception:
                path = notification['data']

            if notification['type'] == _SERVER_CMD_CHANGE_HANGAR:
                _EVENT_HANGAR_PATHS[False] = path
                if not isPremium:
                    hasChanged = True
            if notification['type'] == _SERVER_CMD_CHANGE_HANGAR_PREM:
                _EVENT_HANGAR_PATHS[True] = path
                if isPremium:
                    hasChanged = True

        if hasChanged and self.hangarSpace.inited:
            self.hangarSpace.refreshSpace(isPremium, True)
        return


g_clientHangarSpaceOverride = _ClientHangarSpacePathOverride()

def _createMatrix(scale, angles, pos):
    mat = Math.Matrix()
    mat.setScale((scale, scale, scale))
    mat2 = Math.Matrix()
    mat2.setTranslate(pos)
    mat3 = Math.Matrix()
    mat3.setRotateYPR(angles)
    mat.preMultiply(mat3)
    mat.postMultiply(mat2)
    return mat
