# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/ClientHangarSpace.py
import copy
from logging import getLogger
import itertools
import BigWorld
import Math
import MusicControllerWWISE
import ResMgr
import WebBrowser
import constants
import AnimationSequence
from PlayerEvents import g_playerEvents
from debug_utils import LOG_DEBUG, LOG_ERROR, LOG_CURRENT_EXCEPTION
from gui.hangar_config import HangarConfig
from helpers import dependency
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.game_control import IIGRController, IEpicBattleMetaGameController
from skeletons.gui.shared.gui_items import IGuiItemsFactory
from skeletons.gui.turret_gun_angles import ITurretAndGunAngles
from skeletons.map_activities import IMapActivities
from visual_script.multi_plan_provider import makeMultiPlanProvider, CallableProviderType
from visual_script.misc import ASPECT, VisualScriptTag, readVisualScriptPlans
from SpaceVisibilityFlags import SpaceVisibilityFlagsFactory
from constants import HANGAR_VISIBILITY_TAGS
from skeletons.gui.shared.utils import IHangarSpace
_DEFAULT_SPACES_PATH = 'spaces'
SERVER_CMD_CHANGE_HANGAR = 'cmd_change_hangar'
SERVER_CMD_CHANGE_HANGAR_PREM = 'cmd_change_hangar_prem'
SERVER_CMD_CHANGE_HANGAR_ALT = 'cmd_change_hangar_alt'
_CUSTOMIZATION_HANGAR_SETTINGS_SEC = 'customizationHangarSettings'
_LOGIN_BLACK_BG_IMG = 'gui/maps/login/blackBg.png'
_SECONDARY_HANGAR_SETTINGS_SEC = 'secondaryHangarSettings'
FULL_VISIBILITY_TAG_IDS = set((HANGAR_VISIBILITY_TAGS.IDS[key] for key in itertools.chain(HANGAR_VISIBILITY_TAGS.LAYERS, HANGAR_VISIBILITY_TAGS.REGIONS)))

def getDefaultHangarPath(isPremium):
    global _HANGAR_CFGS
    return _HANGAR_CFGS[constants.DEFAULT_HANGAR_SCENE]


def _getHangarPath(isPremium, isPremIGR):
    global _EVENT_HANGAR_PATHS
    if isPremium in _EVENT_HANGAR_PATHS:
        return _EVENT_HANGAR_PATHS[isPremium][0]
    return _HANGAR_CFGS[getDefaultHangarPath(False)][_IGR_HANGAR_PATH_KEY] if isPremIGR else getDefaultHangarPath(isPremium)


def _getHangarKey(path):
    return path.lower()


def _getHangarType(isPremium):
    return 'premium' if isPremium else 'basic'


def getHangarFullVisibilityMask(spacePath):
    spaceName = _getSpaceNameFromPath(spacePath)
    spaceVisibilityFlags = SpaceVisibilityFlagsFactory.create(spaceName)
    availableFullVisibilityIDs = FULL_VISIBILITY_TAG_IDS.intersection(spaceVisibilityFlags.typeIDToIndex.iterkeys())
    return spaceVisibilityFlags.getMaskForGameplayIDs(availableFullVisibilityIDs)


def _getHangarVisibilityMask(isPremium, spacePath):
    return _EVENT_HANGAR_PATHS[isPremium][1] if isPremium in _EVENT_HANGAR_PATHS else getHangarFullVisibilityMask(spacePath)


_CFG = HangarConfig()
_HANGAR_CFGS = HangarConfig()
_EVENT_HANGAR_PATHS = {}
_IGR_HANGAR_PATH_KEY = 'igrPremHangarPath' + ('CN' if constants.IS_CHINA else '')
_logger = getLogger(__name__)

def hangarCFG():
    global _CFG
    return _CFG


def customizationHangarCFG():
    return _CFG.get(_CUSTOMIZATION_HANGAR_SETTINGS_SEC)


def secondaryHangarCFG():
    return _CFG.get(_SECONDARY_HANGAR_SETTINGS_SEC)


def _readHangarSettings():
    hangarsXml = ResMgr.openSection('gui/hangars.xml')
    paths = [ path for path, _ in ResMgr.openSection(_DEFAULT_SPACES_PATH).items() ]
    defaultSpace = 'hangar_v3'
    if hangarsXml.has_key('hangar_scene_spaces'):
        switchItems = hangarsXml['hangar_scene_spaces']
        for item in switchItems.values():
            if item.readString('name') == constants.DEFAULT_HANGAR_SCENE:
                defaultSpace = item.readString('space')
                break

    configset = {constants.DEFAULT_HANGAR_SCENE: '{}/{}'.format(_DEFAULT_SPACES_PATH, defaultSpace)}
    for folderName in paths:
        spacePath = '{prefix}/{node}'.format(prefix=_DEFAULT_SPACES_PATH, node=folderName)
        spaceKey = _getHangarKey(spacePath)
        settingsXmlPath = '{path}/{file}/{sec}'.format(path=spacePath, file='space.settings', sec='hangarSettings')
        ResMgr.purge(settingsXmlPath, True)
        settingsXml = ResMgr.openSection(settingsXmlPath)
        if settingsXml is None:
            continue
        cfg = HangarConfig()
        cfg.loadDefaultHangarConfig(hangarsXml, _IGR_HANGAR_PATH_KEY)
        cfg.loadConfig(settingsXml)
        _loadVisualScript(cfg, settingsXml)
        if settingsXml.has_key(_CUSTOMIZATION_HANGAR_SETTINGS_SEC):
            customizationXmlSection = settingsXml[_CUSTOMIZATION_HANGAR_SETTINGS_SEC]
            customizationCfg = HangarConfig()
            customizationCfg.loadCustomizationConfig(customizationXmlSection)
            cfg[_CUSTOMIZATION_HANGAR_SETTINGS_SEC] = customizationCfg
        if settingsXml.has_key(_SECONDARY_HANGAR_SETTINGS_SEC):
            secondarySettingsXmlSection = settingsXml[_SECONDARY_HANGAR_SETTINGS_SEC]
            secondaryCfg = HangarConfig()
            secondaryCfg.loadSecondaryConfig(secondarySettingsXmlSection)
            cfg[_SECONDARY_HANGAR_SETTINGS_SEC] = secondaryCfg
        configset[spaceKey] = cfg
        _validateConfigValues(cfg)

    return configset


def _validateConfigValues(cfg):
    if cfg['cam_pitch_constr'][0] <= -90.0:
        _logger.warning('incorrect value - cam_pitch_constr[0] must be greater than -90 degrees!')
        cfg['cam_pitch_constr'][0] = -89.9


def _loadVisualScript(cfg, section):
    if section.has_key(VisualScriptTag):
        vseSection = section[VisualScriptTag]
        cfg['vse_plans'] = readVisualScriptPlans(vseSection)


def _getSpaceNameFromPath(path):
    return path if 'spaces' not in path else path.split('/')[-1]


class ClientHangarSpace(object):
    igrCtrl = dependency.descriptor(IIGRController)
    settingsCore = dependency.descriptor(ISettingsCore)
    itemsFactory = dependency.descriptor(IGuiItemsFactory)
    mapActivities = dependency.descriptor(IMapActivities)
    turretAndGunAngles = dependency.descriptor(ITurretAndGunAngles)
    epicController = dependency.descriptor(IEpicBattleMetaGameController)

    def __init__(self, onVehicleLoadedCallback):
        global _HANGAR_CFGS
        self.__spaceId = None
        self.__waitCallback = None
        self.__loadingStatus = 0.0
        self.__spaceMappingId = None
        self.__onLoadedCallback = None
        self.__vEntityId = None
        self.__selectedEmblemInfo = None
        self.__showMarksOnGun = False
        self.__prevDirection = 0.0
        self.__onVehicleLoadedCallback = onVehicleLoadedCallback
        self.__spacePath = None
        self.__spaceVisibilityMask = None
        self.__geometryID = None
        self._vsePlans = makeMultiPlanProvider(ASPECT.HANGAR, CallableProviderType.HANGAR)
        _HANGAR_CFGS = _readHangarSettings()
        return

    def create(self, isPremium, onSpaceLoadedCallback=None):
        global _CFG
        BigWorld.worldDrawEnabled(False)
        BigWorld.wg_setSpecialFPSMode()
        self.__onLoadedCallback = onSpaceLoadedCallback
        self.__spaceId = BigWorld.createSpace(True)
        isIGR = self.igrCtrl.getRoomType() == constants.IGR_TYPE.PREMIUM
        spacePath = _getHangarPath(isPremium, isIGR)
        spaceType = _getHangarType(isPremium)
        spaceVisibilityMask = _getHangarVisibilityMask(isPremium, spacePath)
        LOG_DEBUG('load hangar: hangar type = <{0:>s}>, space = <{1:>s}>'.format(spaceType, spacePath))
        safeSpacePath = getDefaultHangarPath(False)
        if ResMgr.openSection(spacePath) is None:
            LOG_ERROR('Failed to load hangar from path: %s; default hangar will be loaded instead' % spacePath)
            spacePath = safeSpacePath
        try:
            self.__spaceMappingId = BigWorld.addSpaceGeometryMapping(self.__spaceId, None, spacePath, spaceVisibilityMask)
        except Exception:
            try:
                LOG_CURRENT_EXCEPTION()
                spacePath = safeSpacePath
                self.__spaceMappingId = BigWorld.addSpaceGeometryMapping(self.__spaceId, None, spacePath, spaceVisibilityMask)
            except Exception:
                BigWorld.releaseSpace(self.__spaceId)
                self.__spaceMappingId = None
                self.__spaceId = None
                LOG_CURRENT_EXCEPTION()
                return

        self.__spacePath = spacePath
        self.__spaceVisibilityMask = spaceVisibilityMask
        spaceKey = _getHangarKey(spacePath)
        _CFG = copy.deepcopy(_HANGAR_CFGS[spaceKey])
        self.turretAndGunAngles.init()
        self.__vEntityId = BigWorld.createEntity('HangarVehicle', self.__spaceId, 0, _CFG['v_start_pos'], (_CFG['v_start_angles'][2], _CFG['v_start_angles'][1], _CFG['v_start_angles'][0]), dict())
        self.__waitCallback = BigWorld.callback(0.1, self.__waitLoadingSpace)
        BigWorld.wg_enableGUIBackground(True, False)
        BigWorld.wg_setGUIBackground(_LOGIN_BLACK_BG_IMG)
        self.mapActivities.generateOfflineActivities(spacePath)
        BigWorld.pauseDRRAutoscaling(True)
        vsePlans = _CFG.get('vse_plans', None)
        if vsePlans is not None:
            self._vsePlans.load(vsePlans)
            self._vsePlans.start()
        return

    def recreateVehicle(self, vDesc, vState, onVehicleLoadedCallback=None, outfit=None):
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
            vehicle.recreateVehicle(vDesc, vState, onVehicleLoadedCallback, outfit)
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
            vehicle.model.motors[0].signal = _createMatrix(1.0, _CFG['v_start_angles'], position)
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
            outfit = outfit or self.itemsFactory.createOutfit(vehicleCD=vEntity.typeDescriptor.makeCompactDescr())
            vEntity.updateVehicleCustomization(outfit)
        return

    def updateVehicleDescriptor(self, descr):
        vEntity = self.getVehicleEntity()
        if vEntity is not None and vEntity.isVehicleLoaded:
            vEntity.updateVehicleDescriptor(descr)
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

    def updateAnchorsParams(self, *args):
        vEntity = self.getVehicleEntity()
        if vEntity is not None and vEntity.appearance is not None:
            vEntity.appearance.updateAnchorsParams(*args)
        return

    def getAnchorParams(self, slotId, areaId, regionId):
        vEntity = self.getVehicleEntity()
        return vEntity.appearance.getAnchorParams(slotId, areaId, regionId) if vEntity is not None and vEntity.appearance is not None else None

    def getVehicleEntity(self):
        return BigWorld.entity(self.__vEntityId) if self.__vEntityId else None

    @property
    def vehicleEntityId(self):
        return self.__vEntityId

    def __destroy(self):
        LOG_DEBUG('Hangar successfully destroyed.')
        self._vsePlans.reset()
        MusicControllerWWISE.unloadCustomSounds()
        self.__loadingStatus = 0.0
        self.__onLoadedCallback = None
        if self.__waitCallback is not None:
            BigWorld.cancelCallback(self.__waitCallback)
            self.__waitCallback = None
        BigWorld.SetDrawInflux(False)
        BigWorld.worldDrawEnabled(False)
        self.mapActivities.stop()
        if self.__spaceId is not None and BigWorld.isClientSpace(self.__spaceId):
            if self.__spaceMappingId is not None:
                BigWorld.delSpaceGeometryMapping(self.__spaceId, self.__spaceMappingId)
            BigWorld.clearSpace(self.__spaceId)
            BigWorld.releaseSpace(self.__spaceId)
        self.__spaceMappingId = None
        self.__spaceId = None
        self.__spacePath = None
        self.__spaceVisibilityMask = None
        self.__vEntityId = None
        BigWorld.wg_disableSpecialFPSMode()
        return

    def __waitLoadingSpace(self):
        self.__loadingStatus = BigWorld.spaceLoadStatus()
        BigWorld.worldDrawEnabled(True)
        AnimationSequence.setEnableAnimationSequenceUpdate(True)
        WebBrowser.pauseExternalCache(False)
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
        BigWorld.wg_enableGUIBackground(False, True)

    def getSpaceID(self):
        return self.__spaceId

    @property
    def camera(self):
        return None

    @property
    def spacePath(self):
        return self.__spacePath

    @property
    def visibilityMask(self):
        return self.__spaceVisibilityMask


class _ClientHangarSpacePathOverride(object):
    hangarSpace = dependency.descriptor(IHangarSpace)

    def __init__(self):
        g_playerEvents.onDisconnected += self.__onDisconnected

    def destroy(self):
        g_playerEvents.onDisconnected -= self.__onDisconnected

    def setPremium(self, isPremium):
        self.hangarSpace.onPremiumChanged(isPremium, 0, 0)

    def setPath(self, path, visibilityMask=None, isPremium=None, isReload=True, event=None):
        if path is not None and not path.startswith('spaces/'):
            path = 'spaces/' + path
        if isPremium is None:
            isPremium = self.hangarSpace.isPremium
        if path is not None:
            if visibilityMask is None:
                visibilityMask = getHangarFullVisibilityMask(path)
            _EVENT_HANGAR_PATHS[isPremium] = (path, visibilityMask)
        elif isPremium in _EVENT_HANGAR_PATHS:
            del _EVENT_HANGAR_PATHS[isPremium]
        if isReload:
            self.hangarSpace.refreshSpace(self.hangarSpace.isPremium, True)
            if event is None:
                self.hangarSpace.onSpaceChanged()
            else:
                event()
        return

    def __onDisconnected(self):
        global _EVENT_HANGAR_PATHS
        _EVENT_HANGAR_PATHS = {}


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
