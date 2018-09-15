# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/ClientHangarSpace.py
import copy
import functools
import json
import math
import weakref
from collections import namedtuple
from functools import partial
import BigWorld
import Keys
import MapActivities
import Math
import MusicControllerWWISE
import ResMgr
import SoundGroups
import TankHangarShadowProxy
import VehicleStickers
import constants
from AvatarInputHandler import mathUtils
from AvatarInputHandler.cameras import FovExtended
from HangarVehicle import HangarVehicle
from ModelHitTester import ModelHitTester
from PlayerEvents import g_playerEvents
from debug_utils import LOG_DEBUG, LOG_ERROR, LOG_CURRENT_EXCEPTION
from dossiers2.ui.achievements import MARK_ON_GUN_RECORD
from gui import g_keyEventHandlers, g_mouseEventHandlers
from gui import g_tankActiveCamouflage
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.gui_items.customization.outfit import Outfit, Area
from gui.shared.items_cache import CACHE_SYNC_REASON
from helpers import dependency
from items.components.c11n_constants import ApplyArea, ModificationType, SeasonType
from post_processing import g_postProcessing
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.game_control import IIGRController
from skeletons.gui.shared import IItemsCache
from vehicle_systems import camouflages
from vehicle_systems.stricted_loading import makeCallbackWeak
from vehicle_systems.tankStructure import TankPartNames
from vehicle_systems.tankStructure import VehiclePartsTuple
from vehicle_systems import model_assembler
from svarog_script.py_component_system import ComponentDescriptor, ComponentSystem
from CurrentVehicle import g_currentVehicle, g_currentPreviewVehicle
_DEFAULT_SPACES_PATH = 'spaces'
_SERVER_CMD_CHANGE_HANGAR = 'cmd_change_hangar'
_SERVER_CMD_CHANGE_HANGAR_PREM = 'cmd_change_hangar_prem'

def _getDefaultHangarPath(isPremium):
    if isPremium:
        template = '%s/hangar_premium_v2'
    else:
        template = '%s/hangar_v2'
    return template % _DEFAULT_SPACES_PATH


_HANGAR_UNDERGUN_EMBLEM_ANGLE_SHIFT = math.pi / 4
_CAMOUFLAGE_MIN_INTENSITY = 1.0
_CFG = {}
_DEFAULT_CFG = {}
_HANGAR_CFGS = {}
_EVENT_HANGAR_PATHS = {}
_EVENT_HANGAR_VISIBILITY_MASK = {}
EmblemSlotHelper = namedtuple('EmblemSlotHelper', ['tankAreaSlot',
 'tankAreaId',
 'bspModel',
 'worldMatrix'])
Anchor = namedtuple('Anchor', ['pos', 'normal'])

class OutfitComponent():
    CAMO = 1
    PAINT = 2
    DECAL = 4
    ALL = CAMO | PAINT | DECAL


class HangarCameraYawFilter():

    def __init__(self, start, end, camSens):
        self.__start = start
        self.__end = end
        self.__camSens = camSens
        self.__reversed = self.__start > self.__end
        self.__cycled = int(math.degrees(math.fabs(self.__end - self.__start))) >= 359.0
        self.__prevDirection = 0.0
        if int(math.fabs(math.degrees(self.__start)) + 0.5) >= 180:
            self.__start *= 179 / 180.0
        if int(math.fabs(math.degrees(self.__end)) + 0.5) >= 180:
            self.__end *= 179 / 180.0

    def toLimit(self, inAngle):
        inAngle = mathUtils.reduceToPI(inAngle)
        if self.__cycled:
            return inAngle
        if self.__reversed:
            if inAngle >= self.__start and inAngle <= self.__end:
                return inAngle
        elif self.__start <= inAngle <= self.__end:
            return inAngle
        delta1 = self.__start - inAngle
        delta2 = self.__end - inAngle
        return self.__end if math.fabs(delta1) > math.fabs(delta2) else self.__start

    def getNextYaw(self, currentYaw, targetYaw, delta):
        if delta == 0.0 or self.__prevDirection * delta < 0:
            targetYaw = currentYaw
        self.__prevDirection = delta
        nextYaw = targetYaw + delta * self.__camSens
        if delta > 0.0:
            if nextYaw >= currentYaw:
                deltaYaw = nextYaw - currentYaw
            else:
                deltaYaw = 2.0 * math.pi - currentYaw + nextYaw
            if deltaYaw > math.pi:
                nextYaw = currentYaw + math.pi * 0.9
        else:
            if nextYaw <= currentYaw:
                deltaYaw = currentYaw - nextYaw
            else:
                deltaYaw = 2.0 * math.pi + currentYaw - nextYaw
            if deltaYaw > math.pi:
                nextYaw = currentYaw - math.pi * 0.9
        if not self.__cycled:
            if not self.__reversed:
                if delta > 0.0 and (nextYaw > self.__end or nextYaw < currentYaw):
                    nextYaw = self.__end
                elif delta < 0.0 and (nextYaw < self.__start or nextYaw > currentYaw):
                    nextYaw = self.__start
            elif delta > 0.0 and nextYaw > self.__end and nextYaw <= self.__start:
                nextYaw = self.__end
            elif delta < 0.0 and nextYaw < self.__start and nextYaw >= self.__end:
                nextYaw = self.__start
        return nextYaw


def readHangarSettings(igrKey):
    global _HANGAR_CFGS
    global _DEFAULT_CFG
    global _CFG
    hangarsXml = ResMgr.openSection('gui/hangars.xml')
    for isPremium in (False, True):
        spacePath = _getDefaultHangarPath(isPremium)
        settingsXmlPath = spacePath + '/space.settings'
        ResMgr.purge(settingsXmlPath, True)
        settingsXml = ResMgr.openSection(settingsXmlPath)
        settingsXml = settingsXml['hangarSettings']
        cfg = {'path': spacePath,
         'cam_yaw_constr': Math.Vector2(-180, 180),
         'cam_pitch_constr': Math.Vector2(-70, -5)}
        loadConfig(cfg, settingsXml)
        loadConfigValue('shadow_model_name', hangarsXml, hangarsXml.readString, cfg)
        loadConfigValue('shadow_default_texture_name', hangarsXml, hangarsXml.readString, cfg)
        loadConfigValue('shadow_empty_texture_name', hangarsXml, hangarsXml.readString, cfg)
        loadConfigValue(igrKey, hangarsXml, hangarsXml.readString, cfg)
        _DEFAULT_CFG[getSpaceType(isPremium)] = cfg
        _HANGAR_CFGS[spacePath.lower()] = settingsXml

    for folderName, folderDS in ResMgr.openSection(_DEFAULT_SPACES_PATH).items():
        settingsXml = ResMgr.openSection(_DEFAULT_SPACES_PATH + '/' + folderName + '/space.settings/hangarSettings')
        if settingsXml is not None:
            _HANGAR_CFGS[('spaces/' + folderName).lower()] = settingsXml

    _CFG = copy.copy(_DEFAULT_CFG[getSpaceType(False)])
    return


def loadConfig(cfg, xml, defaultCfg=None):
    if defaultCfg is None:
        defaultCfg = cfg
    loadConfigValue('v_scale', xml, xml.readFloat, cfg, defaultCfg)
    loadConfigValue('v_start_angles', xml, xml.readVector3, cfg, defaultCfg)
    loadConfigValue('v_start_pos', xml, xml.readVector3, cfg, defaultCfg)
    loadConfigValue('cam_start_target_pos', xml, xml.readVector3, cfg, defaultCfg)
    loadConfigValue('cam_start_dist', xml, xml.readFloat, cfg, defaultCfg)
    loadConfigValue('cam_start_angles', xml, xml.readVector2, cfg, defaultCfg)
    loadConfigValue('cam_dist_constr', xml, xml.readVector2, cfg, defaultCfg)
    loadConfigValue('cam_pitch_constr', xml, xml.readVector2, cfg, defaultCfg)
    loadConfigValue('cam_yaw_constr', xml, xml.readVector2, cfg, defaultCfg)
    loadConfigValue('preview_cam_dist_constr', xml, xml.readVector2, cfg, defaultCfg)
    loadConfigValue('cam_sens', xml, xml.readFloat, cfg, defaultCfg)
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
    loadConfigValue('shadow_default_texture_name', xml, xml.readString, cfg, defaultCfg)
    loadConfigValue('shadow_empty_texture_name', xml, xml.readString, cfg, defaultCfg)
    for i in range(0, 3):
        cfg['v_start_angles'][i] = math.radians(cfg['v_start_angles'][i])

    return


def loadConfigValue(name, xml, fn, cfg, defaultCfg=None):
    if xml.has_key(name):
        cfg[name] = fn(name)
    else:
        cfg[name] = defaultCfg.get(name) if defaultCfg is not None else None
    return


def getSpaceType(isPremium):
    return 'premium' if isPremium else 'basic'


class ClientHangarSpace():
    igrCtrl = dependency.descriptor(IIGRController)
    settingsCore = dependency.descriptor(ISettingsCore)

    def __init__(self):
        self.__spaceId = None
        self.__cam = None
        self.__waitCallback = None
        self.__loadingStatus = 0.0
        self.__destroyFunc = None
        self.__spaceMappingId = None
        self.__onLoadedCallback = None
        self.__boundingRadius = None
        self.__vAppearance = None
        self.__vEntityId = None
        self.__isMouseDown = False
        self.__igrHangarPathKey = 'igrPremHangarPath' + ('CN' if constants.IS_CHINA else '')
        self.__selectedEmblemInfo = None
        self.__showMarksOnGun = False
        self.__fakeShadowId = None
        self.__fakeShadowAsset = None
        self.__fakeShadowScale = 1.0
        self.__prevDirection = 0.0
        self.__camDistConstr = ((0.0, 0.0), (0.0, 0.0))
        self.__locatedOnEmbelem = False
        readHangarSettings(self.__igrHangarPathKey)
        self.__yawCameraFilter = HangarCameraYawFilter(math.radians(_CFG['cam_yaw_constr'][0]), math.radians(_CFG['cam_yaw_constr'][1]), _CFG['cam_sens'])
        return

    def create(self, isPremium, onSpaceLoadedCallback=None):
        global _EVENT_HANGAR_PATHS
        global _CFG
        BigWorld.worldDrawEnabled(False)
        BigWorld.wg_setSpecialFPSMode()
        self.__onLoadedCallback = onSpaceLoadedCallback
        self.__spaceId = BigWorld.createSpace()
        type = getSpaceType(isPremium)
        _CFG = copy.copy(_DEFAULT_CFG[type])
        spacePath = _DEFAULT_CFG[type]['path']
        LOG_DEBUG('load hangar: hangar type = <{0:>s}>, space = <{1:>s}>'.format(type, spacePath))
        visibilityMask = 4294967295L
        if self.igrCtrl.getRoomType() == constants.IGR_TYPE.PREMIUM:
            if _CFG.get(self.__igrHangarPathKey) is not None:
                spacePath = _CFG[self.__igrHangarPathKey]
        if isPremium in _EVENT_HANGAR_PATHS:
            spacePath = _EVENT_HANGAR_PATHS[isPremium]
        if isPremium in _EVENT_HANGAR_VISIBILITY_MASK:
            visibilityMask = _EVENT_HANGAR_VISIBILITY_MASK[isPremium]
        safeSpacePath = _DEFAULT_CFG[type]['path']
        if ResMgr.openSection(spacePath) is None:
            LOG_ERROR('Failed to load hangar from path: %s; default hangar will be loaded instead' % spacePath)
            spacePath = safeSpacePath
            visibilityMask = 4294967295L
        BigWorld.wg_setSpaceItemsVisibilityMask(self.__spaceId, visibilityMask)
        try:
            self.__spaceMappingId = BigWorld.addSpaceGeometryMapping(self.__spaceId, None, spacePath)
        except:
            try:
                LOG_CURRENT_EXCEPTION()
                spacePath = safeSpacePath
                self.__spaceMappingId = BigWorld.addSpaceGeometryMapping(self.__spaceId, None, spacePath)
            except:
                BigWorld.releaseSpace(self.__spaceId)
                self.__spaceMappingId = None
                self.__spaceId = None
                LOG_CURRENT_EXCEPTION()
                return

        spacePathLC = spacePath.lower()
        if spacePathLC in _HANGAR_CFGS:
            loadConfig(_CFG, _HANGAR_CFGS[spacePathLC], _CFG)
        self.__vEntityId = BigWorld.createEntity('HangarVehicle', self.__spaceId, 0, _CFG['v_start_pos'], (_CFG['v_start_angles'][2], _CFG['v_start_angles'][1], _CFG['v_start_angles'][0]), dict())
        self.__vAppearance = _VehicleAppearance(self.__spaceId, self.__vEntityId, self)
        self.__yawCameraFilter = HangarCameraYawFilter(math.radians(_CFG['cam_yaw_constr'][0]), math.radians(_CFG['cam_yaw_constr'][1]), _CFG['cam_sens'])
        self.__setupCamera()
        distConstrs = _CFG['cam_dist_constr']
        previewConstr = _CFG.get('preview_cam_dist_constr', distConstrs)
        if distConstrs is not None:
            if previewConstr is not None:
                self.__camDistConstr = (distConstrs, previewConstr)
            else:
                self.__camDistConstr = (distConstrs, distConstrs)
        else:
            self.__camDistConstr = ((0.0, 0.0), (0.0, 0.0))
        self.__waitCallback = BigWorld.callback(0.1, self.__waitLoadingSpace)
        self.__destroyFunc = None
        MapActivities.g_mapActivities.generateOfflineActivities(spacePath)
        g_keyEventHandlers.add(self.handleKeyEvent)
        g_mouseEventHandlers.add(self.handleMouseEventGlobal)
        g_postProcessing.enable('hangar')
        BigWorld.pauseDRRAutoscaling(True)
        return

    def recreateVehicle(self, vDesc, vState, onVehicleLoadedCallback=None):
        if self.__vAppearance is None:
            LOG_ERROR('ClientHangarSpace.recreateVehicle failed because hangar space has not been loaded correctly.')
            return
        else:
            self.__vAppearance.recreate(vDesc, vState, onVehicleLoadedCallback)
            hitTester = vDesc.hull.hitTester
            hitTester.loadBspModel()
            self.__boundingRadius = (hitTester.bbox[2] + 1) * _CFG['v_scale']
            hitTester.releaseBspModel()
            return

    def removeVehicle(self):
        self.__boundingRadius = None
        if self.__vAppearance is not None:
            self.__vAppearance.destroy()
        self.__vAppearance = _VehicleAppearance(self.__spaceId, self.__vEntityId, self)
        try:
            BigWorld.entities[self.__vEntityId].model = None
        except KeyError:
            pass

        self.__selectedEmblemInfo = None
        return

    def moveVehicleTo(self, position):
        try:
            vehicle = BigWorld.entity(self.__vEntityId)
            vehicle.model.motors[0].signal = _createMatrix(_CFG['v_scale'], _CFG['v_start_angles'], position)
        except Exception:
            LOG_CURRENT_EXCEPTION()

    def setVehicleSelectable(self, flag):
        """Include/exclude vehicle to select as target. Vehicle does not have any interaction
            when player goes from hangar to other screen (for example, shop), because of
            GUI overlaps model of vehicle.
        :param flag: boolean.
        """
        if self.__vEntityId is not None:
            entity = BigWorld.entity(self.__vEntityId)
            if isinstance(entity, HangarVehicle):
                entity.setSelectable(flag)
        return

    def updateVehicleCustomization(self, outfit, component=OutfitComponent.ALL):
        if outfit is None:
            outfit = Outfit()
        self.__vAppearance.updateCustomization(outfit, component)
        return

    def getCentralPointForArea(self, areaId):
        return self.__vAppearance.getCentralPointForArea(areaId)

    def destroy(self):
        self.__onLoadedCallback = None
        if self.__waitCallback is not None:
            BigWorld.cancelCallback(self.__waitCallback)
            self.__waitCallback = None
            if not self.spaceLoaded():
                self.__destroyFunc = self.__destroy
                return
        self.__destroy()
        return

    def handleMouseEvent(self, dx, dy, dz):
        if not self.spaceLoaded():
            return False
        self.updateCameraByMouseMove(dx, dy, dz)
        return True

    def handleKeyEvent(self, event):
        if event.key == Keys.KEY_LEFTMOUSE:
            self.__isMouseDown = event.isKeyDown()
            if self.__isMouseDown:
                from gui.shared.utils.HangarSpace import g_hangarSpace
                g_hangarSpace.leftButtonClicked()
        return False

    def handleMouseEventGlobal(self, event):
        if self.__isMouseDown:
            isGuiVisible = BigWorld.getWatcher('Visibility/GUI')
            if isGuiVisible is not None and isGuiVisible.lower() == 'false':
                self.updateCameraByMouseMove(event.dx, event.dy, event.dz)
                return True
        return False

    def getCamera(self):
        return self.__cam

    def getVehicleEntity(self):
        return BigWorld.entities[self.__vEntityId]

    def getCameraLocation(self):
        sourceMat = Math.Matrix(self.__cam.source)
        targetMat = Math.Matrix(self.__cam.target)
        return {'targetPos': targetMat.translation,
         'pivotPos': self.__cam.pivotPosition,
         'yaw': sourceMat.yaw,
         'pitch': sourceMat.pitch,
         'dist': self.__cam.pivotMaxDist}

    def setCameraLocation(self, targetPos=None, pivotPos=None, yaw=None, pitch=None, dist=None, ignoreConstraints=False):
        sourceMat = Math.Matrix(self.__cam.source)
        if yaw is None:
            yaw = sourceMat.yaw
        if pitch is None:
            pitch = sourceMat.pitch
        if dist is None:
            dist = self.__cam.pivotMaxDist
        if not ignoreConstraints:
            yaw = self.__yawCameraFilter.toLimit(yaw)
            pitch = mathUtils.clamp(math.radians(_CFG['cam_pitch_constr'][0]), math.radians(_CFG['cam_pitch_constr'][1]), pitch)
            if self.__selectedEmblemInfo is not None:
                dist = mathUtils.clamp(self.__camDistConstr[1][0], self.__camDistConstr[1][1], dist)
            else:
                dist = mathUtils.clamp(self.__camDistConstr[0][0], self.__camDistConstr[0][1], dist)
            if self.__boundingRadius is not None:
                dist = dist if dist > self.__boundingRadius else self.__boundingRadius
        mat = Math.Matrix()
        pitch = mathUtils.clamp(-math.pi / 2 * 0.99, math.pi / 2 * 0.99, pitch)
        mat.setRotateYPR((yaw, pitch, 0.0))
        self.__cam.source = mat
        self.__cam.pivotMaxDist = dist
        if targetPos is not None:
            self.__cam.target.setTranslate(targetPos)
        if pivotPos is not None:
            self.__cam.pivotPosition = pivotPos
        return

    def locateCameraToPreview(self):
        self.setCameraLocation(targetPos=_CFG['preview_cam_start_target_pos'], pivotPos=_CFG['preview_cam_pivot_pos'], yaw=math.radians(_CFG['preview_cam_start_angles'][0]), pitch=math.radians(_CFG['preview_cam_start_angles'][1]), dist=_CFG['preview_cam_start_dist'])

    def locateCameraOnEmblem(self, onHull, emblemType, emblemIdx, relativeSize=0.5):
        self.__selectedEmblemInfo = (onHull,
         emblemType,
         emblemIdx,
         relativeSize)
        targetPosDirEmblem = self.__vAppearance.getEmblemPos(onHull, emblemType, emblemIdx)
        if targetPosDirEmblem is None:
            return False
        else:
            targetPos, dir, emblemDesc = targetPosDirEmblem
            emblemSize = emblemDesc[3] * _CFG['v_scale']
            halfF = emblemSize / (2 * relativeSize)
            dist = halfF / math.tan(BigWorld.projection().fov / 2)
            self.setCameraLocation(targetPos, Math.Vector3(0, 0, 0), dir.yaw, -dir.pitch, dist, True)
            self.__locatedOnEmbelem = True
            return True

    def clearSelectedEmblemInfo(self):
        self.__selectedEmblemInfo = None
        return

    def updateCameraByMouseMove(self, dx, dy, dz):
        if self.__selectedEmblemInfo is not None:
            self.__cam.target.setTranslate(_CFG['preview_cam_start_target_pos'])
            self.__cam.pivotPosition = _CFG['preview_cam_pivot_pos']
            if self.__locatedOnEmbelem:
                self.__cam.maxDistHalfLife = 0.0
            else:
                self.__cam.maxDistHalfLife = _CFG['cam_fluency']
        sourceMat = Math.Matrix(self.__cam.source)
        yaw = sourceMat.yaw
        pitch = sourceMat.pitch
        dist = self.__cam.pivotMaxDist
        currentMatrix = Math.Matrix(self.__cam.invViewMatrix)
        currentYaw = currentMatrix.yaw
        yaw = self.__yawCameraFilter.getNextYaw(currentYaw, yaw, dx)
        pitch -= dy * _CFG['cam_sens']
        dist -= dz * _CFG['cam_sens']
        pitch = mathUtils.clamp(math.radians(_CFG['cam_pitch_constr'][0]), math.radians(_CFG['cam_pitch_constr'][1]), pitch)
        prevDist = dist
        distConstr = self.__camDistConstr[1] if self.__selectedEmblemInfo is not None else self.__camDistConstr[0]
        dist = mathUtils.clamp(distConstr[0], distConstr[1], dist)
        if self.__boundingRadius is not None:
            boundingRadius = self.__boundingRadius if self.__boundingRadius < distConstr[1] else distConstr[1]
            dist = dist if dist > boundingRadius else boundingRadius
        if dist > prevDist and dz > 0:
            if self.__selectedEmblemInfo is not None:
                self.locateCameraOnEmblem(*self.__selectedEmblemInfo)
                return
        self.__locatedOnEmbelem = False
        mat = Math.Matrix()
        mat.setRotateYPR((yaw, pitch, 0.0))
        self.__cam.source = mat
        self.__cam.pivotMaxDist = dist
        if self.settingsCore.getSetting('dynamicFov') and abs(distConstr[1] - distConstr[0]) > 0.001:
            relativeDist = (dist - distConstr[0]) / (distConstr[1] - distConstr[0])
            _, minFov, maxFov = self.settingsCore.getSetting('fov')
            fov = mathUtils.lerp(minFov, maxFov, relativeDist)
            BigWorld.callback(0, functools.partial(FovExtended.instance().setFovByAbsoluteValue, math.radians(fov), 0.1))
        return

    def spaceLoaded(self):
        return not self.__loadingStatus < 1

    def spaceLoading(self):
        return self.__waitCallback is not None

    def getSlotPositions(self):
        return self.__vAppearance.getSlotPositions()

    def __destroy(self):
        LOG_DEBUG('Hangar successfully destroyed.')
        MusicControllerWWISE.unloadCustomSounds()
        if self.__cam == BigWorld.camera():
            self.__cam.spaceID = 0
            BigWorld.camera(None)
            BigWorld.worldDrawEnabled(False)
        self.__cam = None
        self.__loadingStatus = 0.0
        if self.__vAppearance is not None:
            self.__vAppearance.destroy()
            self.__vAppearance = None
        self.__onLoadedCallback = None
        self.__boundingRadius = None
        if self.__waitCallback is not None:
            BigWorld.cancelCallback(self.__waitCallback)
            self.__waitCallback = None
        g_keyEventHandlers.remove(self.handleKeyEvent)
        g_mouseEventHandlers.remove(self.handleMouseEventGlobal)
        BigWorld.SetDrawInflux(False)
        MapActivities.g_mapActivities.stop()
        if self.__spaceId is not None and BigWorld.isClientSpace(self.__spaceId):
            if self.__spaceMappingId is not None:
                BigWorld.delSpaceGeometryMapping(self.__spaceId, self.__spaceMappingId)
            BigWorld.clearSpace(self.__spaceId)
            BigWorld.releaseSpace(self.__spaceId)
        self.__spaceMappingId = None
        self.__spaceId = None
        self.__vEntityId = None
        BigWorld.wg_disableSpecialFPSMode()
        g_postProcessing.disable()
        FovExtended.instance().resetFov()
        return

    def __setupCamera(self):
        self.__cam = BigWorld.CursorCamera()
        self.__cam.spaceID = self.__spaceId
        self.__cam.pivotMaxDist = mathUtils.clamp(_CFG['cam_dist_constr'][0], _CFG['cam_dist_constr'][1], _CFG['cam_start_dist'])
        self.__cam.pivotMinDist = 0.0
        self.__cam.maxDistHalfLife = _CFG['cam_fluency']
        self.__cam.turningHalfLife = _CFG['cam_fluency']
        self.__cam.movementHalfLife = 0.0
        self.__cam.pivotPosition = _CFG['cam_pivot_pos']
        mat = Math.Matrix()
        yaw = self.__yawCameraFilter.toLimit(math.radians(_CFG['cam_start_angles'][0]))
        mat.setRotateYPR((yaw, math.radians(_CFG['cam_start_angles'][1]), 0.0))
        self.__cam.source = mat
        mat = Math.Matrix()
        mat.setTranslate(_CFG['cam_start_target_pos'])
        self.__cam.target = mat
        self.__cam.wg_applyParams()
        BigWorld.camera(self.__cam)

    def __waitLoadingSpace(self):
        self.__loadingStatus = BigWorld.spaceLoadStatus()
        if self.__loadingStatus < 1:
            self.__waitCallback = BigWorld.callback(0.1, self.__waitLoadingSpace)
        else:
            self.__waitCallback = None
            BigWorld.worldDrawEnabled(True)
            self.__requestFakeShadowModel()
            self.modifyFakeShadowScale(_CFG['v_scale'])
            if self.__onLoadedCallback is not None:
                self.__onLoadedCallback()
                self.__onLoadedCallback = None
            if self.__destroyFunc:
                self.__destroyFunc()
                self.__destroyFunc = None
            SoundGroups.LSstartAll()
        return

    def __requestFakeShadowModel(self):
        resources = [_CFG['shadow_model_name']]
        BigWorld.loadResourceListBG(tuple(resources), makeCallbackWeak(self.__onFakeShadowLoaded))

    def __onFakeShadowLoaded(self, resourceRefs):
        modelName = _CFG['shadow_model_name']
        fakeShadowModel = None
        if modelName not in resourceRefs.failedIDs and resourceRefs.has_key(modelName):
            fakeShadowModel = resourceRefs[modelName]
        if fakeShadowModel is None:
            LOG_ERROR('Could not load model %s' % modelName)
            return
        else:
            shadowProxyNodes = [ udo for udo in BigWorld.userDataObjects.values() if isinstance(udo, TankHangarShadowProxy.TankHangarShadowProxy) ]
            if len(shadowProxyNodes) == 1:
                shadowProxy = shadowProxyNodes[0]
                shadowXFormPosition = shadowProxy.position
                shadowXFormOrientation = (shadowProxy.roll, shadowProxy.pitch, shadowProxy.yaw)
            else:
                LOG_DEBUG('Too many TankHangarShadowProxies? Or not enough.')
                return
            self.__fakeShadowId = BigWorld.createEntity('OfflineEntity', self.__spaceId, 0, shadowXFormPosition, shadowXFormOrientation, dict())
            entity = BigWorld.entity(self.__fakeShadowId)
            entity.model = fakeShadowModel
            entity.model.position = shadowProxy.position
            entity.model.yaw = shadowProxy.yaw
            self.modifyFakeShadowScale(self.__fakeShadowScale)
            self.modifyFakeShadowAsset(self.__fakeShadowAsset)
            return

    def __getFakeShadowModel(self):
        fakeShadowId = self.__fakeShadowId
        if fakeShadowId is None:
            return
        else:
            entity = BigWorld.entity(fakeShadowId)
            if entity is None:
                return
            fakeShadowModel = entity.model
            return fakeShadowModel

    def modifyFakeShadowScale(self, scale):
        self.__fakeShadowScale = scale
        fakeShadowModel = self.__getFakeShadowModel()
        if fakeShadowModel is None:
            return
        else:
            fakeShadowModel.scale = Math.Vector3(scale, 1.0, scale)
            return

    def modifyFakeShadowAsset(self, asset):
        self.__fakeShadowAsset = asset
        fakeShadowModel = self.__getFakeShadowModel()
        if fakeShadowModel is None:
            return
        else:
            BigWorld.wg_setPyModelTexture(fakeShadowModel, 'diffuseMap', asset)
            return


class _VehicleAppearance(ComponentSystem):
    __ROOT_NODE_NAME = 'V'
    itemsCache = dependency.descriptor(IItemsCache)
    settingsCore = dependency.descriptor(ISettingsCore)
    wheelsAnimator = ComponentDescriptor()
    trackNodesAnimator = ComponentDescriptor()

    def __init__(self, spaceId, vEntityId, hangarSpace):
        ComponentSystem.__init__(self)
        self.__isLoaded = False
        self.__curBuildInd = 0
        self.__vDesc = None
        self.__vState = None
        self.__fashions = VehiclePartsTuple(None, None, None, None)
        self.__repaintHandlers = [None,
         None,
         None,
         None]
        self.__camoHandlers = [None,
         None,
         None,
         None]
        self.__spaceId = spaceId
        self.__vEntityId = vEntityId
        self.__onLoadedCallback = None
        self.__emblemsAlpha = _CFG['emblems_alpha_undamaged']
        self.__vehicleStickers = None
        self.__isVehicleDestroyed = False
        self.__smCb = None
        self.__smRemoveCb = None
        self.__hangarSpace = weakref.proxy(hangarSpace)
        self.__removeHangarShadowMap()
        self.__showMarksOnGun = self.settingsCore.getSetting('showMarksOnGun')
        self.settingsCore.onSettingsChanged += self.__onSettingsChanged
        self.itemsCache.onSyncCompleted += self.__onItemsCacheSyncCompleted
        return

    def recreate(self, vDesc, vState, onVehicleLoadedCallback=None):
        ComponentSystem.deactivate(self)
        self.__onLoadedCallback = onVehicleLoadedCallback
        self.__isLoaded = False
        self.__startBuild(vDesc, vState)

    def refresh(self):
        if self.__isLoaded:
            self.__onLoadedCallback = None
            self.__isLoaded = False
            self.__startBuild(self.__vDesc, self.__vState)
        entity = BigWorld.entity(self.__vEntityId)
        if isinstance(entity, HangarVehicle):
            entity.releaseBspModels()
        return

    def destroy(self):
        ComponentSystem.deactivate(self)
        ComponentSystem.destroy(self)
        self.__onLoadedCallback = None
        self.__vDesc = None
        self.__vState = None
        self.__isLoaded = False
        self.__curBuildInd = 0
        self.__vEntityId = None
        if self.__smCb is not None:
            BigWorld.cancelCallback(self.__smCb)
            self.__smCb = None
        if self.__smRemoveCb is not None:
            BigWorld.cancelCallback(self.__smRemoveCb)
            self.__smRemoveCb = None
        self.settingsCore.onSettingsChanged -= self.__onSettingsChanged
        self.itemsCache.onSyncCompleted -= self.__onItemsCacheSyncCompleted
        return

    def isLoaded(self):
        return self.__isLoaded

    def __startBuild(self, vDesc, vState):
        self.__curBuildInd += 1
        self.__vDesc = vDesc
        self.__vState = vState
        self.__resources = {}
        self.__vehicleStickers = None
        if vState == 'undamaged':
            self.__emblemsAlpha = _CFG['emblems_alpha_undamaged']
            self.__isVehicleDestroyed = False
        else:
            self.__emblemsAlpha = _CFG['emblems_alpha_damaged']
            self.__isVehicleDestroyed = True
        outfit = self.__getActiveOutfit()
        resources = camouflages.getCamoPrereqs(outfit, vDesc)
        splineDesc = vDesc.chassis.splineDesc
        if splineDesc is not None:
            resources.append(splineDesc.segmentModelLeft)
            resources.append(splineDesc.segmentModelRight)
            resources.append(splineDesc.leftDesc)
            resources.append(splineDesc.rightDesc)
            resources.append(splineDesc.segment2ModelLeft)
            resources.append(splineDesc.segment2ModelRight)
        resources.append(model_assembler.prepareCompoundAssembler(self.__vDesc, self.__vState, self.__spaceId))
        BigWorld.loadResourceListBG(tuple(resources), makeCallbackWeak(self.__onResourcesLoaded, self.__curBuildInd))
        return

    def __onResourcesLoaded(self, buildInd, resourceRefs):
        if buildInd != self.__curBuildInd:
            return
        failedIDs = resourceRefs.failedIDs
        resources = self.__resources
        succesLoaded = True
        for resID, resource in resourceRefs.items():
            if resID not in failedIDs:
                resources[resID] = resource
            LOG_ERROR('Could not load %s' % resID)
            succesLoaded = False

        if succesLoaded:
            self.__setupModel(buildInd)
        super(_VehicleAppearance, self).activate()

    def __onSettingsChanged(self, diff):
        if 'showMarksOnGun' in diff:
            self.__showMarksOnGun = not diff['showMarksOnGun']
            self.refresh()
        elif 'dynamicFov' in diff or 'fov' in diff:
            if 'fov' in diff:
                staticFOV, dynamicFOVLow, dynamicFOVTop = diff['fov']
                defaultHorizontalFov = math.radians(dynamicFOVTop)

                def resetFov(value):
                    FovExtended.instance().defaultHorizontalFov = value

                BigWorld.callback(0.0, partial(resetFov, defaultHorizontalFov))
            self.__hangarSpace.updateCameraByMouseMove(0, 0, 0)

    def __getActiveOutfit(self):
        if g_currentPreviewVehicle.isPresent():
            return Outfit()
        vehicle = g_currentVehicle.item
        season = g_tankActiveCamouflage.get(vehicle.intCD, SeasonType.UNDEFINED)
        if season == SeasonType.UNDEFINED or not vehicle.hasOutfitWithItems(season):
            season = vehicle.getAnyOutfitSeason()
        g_tankActiveCamouflage[vehicle.intCD] = season
        return vehicle.getOutfit(season)

    def __assembleModel(self):
        resources = self.__resources
        self.__model = resources[self.__vDesc.name]
        if not self.__isVehicleDestroyed:
            self.__fashions = VehiclePartsTuple(BigWorld.WGVehicleFashion(False), BigWorld.WGBaseFashion(), BigWorld.WGBaseFashion(), BigWorld.WGBaseFashion())
            model_assembler.setupTracksFashion(self.__fashions.chassis, self.__vDesc, self.__isVehicleDestroyed)
            self.__model.setupFashions(self.__fashions)
            self.__initMaterialHandlers()
            chassisFashion = self.__fashions.chassis
            model_assembler.setupSplineTracks(chassisFashion, self.__vDesc, self.__model, self.__resources)
            self.wheelsAnimator = model_assembler.createWheelsAnimator(self.__model, self.__vDesc, None)
            self.trackNodesAnimator = model_assembler.createTrackNodesAnimator(self.__model, self.__vDesc, self.wheelsAnimator)
            outfit = self.__getActiveOutfit()
            self.updateCustomization(outfit, OutfitComponent.ALL)
        else:
            self.__fashions = VehiclePartsTuple(None, None, None, None)
            self.wheelsAnimator = None
            self.trackNodesAnimator = None
        yaw = self.__vDesc.gun.staticTurretYaw
        pitch = self.__vDesc.gun.staticPitch
        if yaw is None:
            yaw = 0.0
        if pitch is None:
            pitch = 0.0
        gunMatrix = mathUtils.createRTMatrix(Math.Vector3(yaw, pitch, 0.0), (0.0, 0.0, 0.0))
        self.__model.node('gun', gunMatrix)
        return self.__model

    def __removeHangarShadowMap(self):
        if self.__smCb is not None:
            BigWorld.cancelCallback(self.__smCb)
            self.__smCb = None
        if BigWorld.spaceLoadStatus() < 1.0:
            self.__smRemoveCb = BigWorld.callback(0, self.__removeHangarShadowMap)
            return
        else:
            self.__smRemoveCb = None
            self.__hangarSpace.modifyFakeShadowAsset(_CFG['shadow_empty_texture_name'])
            return

    VehicleProxy = namedtuple('VehicleProxy', 'typeDescriptor')

    def __setupHangarShadow(self):
        if self.__smCb is None:
            self.__setupHangarShadowMap()
        return

    def __setupHangarShadowMap(self):
        if self.__smRemoveCb is not None:
            BigWorld.cancelCallback(self.__smRemoveCb)
            self.__smRemoveCb = None
        if BigWorld.spaceLoadStatus() < 1.0:
            self.__smCb = BigWorld.callback(0.0, self.__setupHangarShadowMap)
            return
        else:
            self.__smCb = None
            if 'observer' in self.__vDesc.type.tags:
                self.__removeHangarShadowMap()
                return
            shadowMapTexFileName = self.__vDesc.hull.hangarShadowTexture
            if shadowMapTexFileName is None:
                shadowMapTexFileName = _CFG['shadow_default_texture_name']
            self.__hangarSpace.modifyFakeShadowAsset(shadowMapTexFileName)
            return

    def __onItemsCacheSyncCompleted(self, updateReason, invalidItems):
        if updateReason == CACHE_SYNC_REASON.DOSSIER_RESYNC and self.__vehicleStickers is not None and self.__getThisVehicleDossierInsigniaRank() != self.__vehicleStickers.getCurrentInsigniaRank():
            self.refresh()
        return

    def __getThisVehicleDossierInsigniaRank(self):
        vehicleDossier = self.itemsCache.items.getVehicleDossier(self.__vDesc.type.compactDescr)
        return vehicleDossier.getRandomStats().getAchievement(MARK_ON_GUN_RECORD).getValue()

    def __setupEmblems(self, outfit):
        if self.__vehicleStickers is not None:
            self.__vehicleStickers.detach()
        insigniaRank = 0
        if self.__showMarksOnGun:
            insigniaRank = self.__getThisVehicleDossierInsigniaRank()
        self.__vehicleStickers = VehicleStickers.VehicleStickers(self.__vDesc, insigniaRank, outfit)
        self.__vehicleStickers.alpha = self.__emblemsAlpha
        self.__vehicleStickers.attach(self.__model, self.__isVehicleDestroyed, False)
        BigWorld.player().stats.get('clanDBID', self.__onClanDBIDRetrieved)
        return

    def __onClanDBIDRetrieved(self, _, clanID):
        if self.__vehicleStickers is not None:
            self.__vehicleStickers.setClanID(clanID)
        return

    def __setupModel(self, buildIdx):
        model = self.__assembleModel()
        matrix = mathUtils.createSRTMatrix(Math.Vector3(_CFG['v_scale'], _CFG['v_scale'], _CFG['v_scale']), _CFG['v_start_angles'], _CFG['v_start_pos'])
        model.matrix = matrix
        self.__doFinalSetup(buildIdx, model)
        entity = BigWorld.entity(self.__vEntityId)
        if isinstance(entity, HangarVehicle):
            entity.typeDescriptor = self.__vDesc

    def __doFinalSetup(self, buildIdx, model):
        if buildIdx != self.__curBuildInd:
            return
        else:
            entity = BigWorld.entity(self.__vEntityId)
            if entity:
                entity.model = model
                self.__isLoaded = True
                if isinstance(entity, HangarVehicle):
                    entity.canDoHitTest(True)
                if self.__onLoadedCallback is not None:
                    self.__onLoadedCallback()
                    self.__onLoadedCallback = None
                if self.__smCb is None:
                    self.__setupHangarShadowMap()
            if self.__vDesc is not None and 'observer' in self.__vDesc.type.tags:
                model.visible = False
            return

    def getSlotPositions(self):
        slots = {area:{GUI_ITEM_TYPE.INSCRIPTION: [],
         GUI_ITEM_TYPE.EMBLEM: []} for area in Area.ALL}
        hullEmblemSlots = EmblemSlotHelper(self.__vDesc.hull.emblemSlots, Area.HULL, self.__vDesc.hull.models.undamaged, Math.Matrix(self.__model.node(TankPartNames.HULL)))
        if self.__vDesc.turret.showEmblemsOnGun:
            turretEmblemSlots = EmblemSlotHelper(self.__vDesc.turret.emblemSlots, Area.GUN, self.__vDesc.gun.models.undamaged, Math.Matrix(self.__model.node(TankPartNames.GUN)))
        else:
            turretEmblemSlots = EmblemSlotHelper(self.__vDesc.turret.emblemSlots, Area.TURRET, self.__vDesc.turret.models.undamaged, Math.Matrix(self.__model.node(TankPartNames.TURRET)))
        emblemSlotHelpers = (hullEmblemSlots, turretEmblemSlots)
        hitTester = ModelHitTester()
        for emblemSlotHelper in emblemSlotHelpers:
            hitTester.bspModelName = emblemSlotHelper.bspModel
            hitTester.loadBspModel()
            for emblemSlot in emblemSlotHelper.tankAreaSlot:
                startPos = emblemSlot.rayStart
                endPos = emblemSlot.rayEnd
                direction = endPos - startPos
                direction.normalise()
                hitResults = hitTester.localHitTest(startPos, endPos)
                if hitResults is not None:
                    distanceFromStart, normal = hitResults[0][0], hitResults[0][1]
                    normal = emblemSlotHelper.worldMatrix.applyVector(normal)
                    hitPos = startPos + direction * distanceFromStart
                    hitPos = emblemSlotHelper.worldMatrix.applyPoint(hitPos)
                    container = slots[emblemSlotHelper.tankAreaId]
                    if emblemSlot.type == 'inscription':
                        container[GUI_ITEM_TYPE.INSCRIPTION].append(Anchor(hitPos, normal))
                    elif emblemSlot.type == 'player':
                        container[GUI_ITEM_TYPE.EMBLEM].append(Anchor(hitPos, normal))

            hitTester.releaseBspModel()

        return slots

    def getEmblemPos(self, onHull, emblemType, emblemIdx):
        emblemsDesc = None
        hitTester = ModelHitTester()
        worldMat = None
        if onHull:
            hitTester.bspModelName = self.__vDesc.hull.models.undamaged
            emblemsDesc = self.__vDesc.hull.emblemSlots
            worldMat = Math.Matrix(self.__model.node(TankPartNames.HULL))
        else:
            if self.__vDesc.turret.showEmblemsOnGun:
                node = self.__model.node(TankPartNames.GUN)
                hitTester.bspModelName = self.__vDesc.gun.models.undamaged
            else:
                node = self.__model.node(TankPartNames.TURRET)
                hitTester.bspModelName = self.__vDesc.turret.models.undamaged
            emblemsDesc = self.__vDesc.turret.emblemSlots
            worldMat = Math.Matrix(node)
        desiredEmblems = [ emblem for emblem in emblemsDesc if emblem.type == emblemType ]
        if emblemIdx >= len(desiredEmblems):
            return
        else:
            emblem = desiredEmblems[emblemIdx]
            dir = emblem[1] - emblem[0]
            dir.normalise()
            startPos = emblem[0] - dir * 5
            endPos = emblem[1] + dir * 5
            hitTester.loadBspModel()
            collideRes = hitTester.localHitTest(startPos, endPos)
            hitTester.releaseBspModel()
            if collideRes is not None:
                collideRes = sorted(collideRes, lambda t1, t2: cmp(t1[0], t2[0]))
                distanceFromStart, normal = collideRes[0][0], collideRes[0][1]
                hitPos = startPos + dir * distanceFromStart
                hitPos = worldMat.applyPoint(hitPos)
                dir = -worldMat.applyVector(normal)
                dir.normalise()
                upVecWorld = worldMat.applyVector(emblem[2])
                upVecWorld.normalise()
                if abs(dir.pitch - math.pi / 2) < 0.1:
                    dir = Math.Vector3(0, -1, 0) + upVecWorld * 0.01
                    dir.normalise()
                dir = self.__correctEmblemLookAgainstGun(hitPos, dir, upVecWorld, emblem)
                return (hitPos, dir, emblem)
            return
            return

    def getCentralPointForArea(self, areaIdx):

        def _getBBCenter(tankPartName):
            partIdx = TankPartNames.getIdx(tankPartName)
            boundingBox = Math.Matrix(self.__model.getBoundsForPart(partIdx))
            bbCenter = boundingBox.applyPoint((0.5, 0.5, 0.5))
            return bbCenter

        if areaIdx == ApplyArea.HULL:
            trackLeftUpFront = self.__model.node('HP_TrackUp_LFront').position
            trackRightUpRear = self.__model.node('HP_TrackUp_RRear').position
            position = (trackLeftUpFront + trackRightUpRear) / 2.0
            bbCenter = _getBBCenter(TankPartNames.HULL)
            turretJointPosition = self.__model.node('HP_turretJoint').position
            position.y = min(turretJointPosition.y, bbCenter.y)
        elif areaIdx == ApplyArea.TURRET:
            position = _getBBCenter(TankPartNames.TURRET)
            position.y = self.__model.node('HP_gunJoint').position.y
        elif areaIdx == ApplyArea.GUN_2:
            position = self.__model.node('HP_gunJoint').position
        elif areaIdx == ApplyArea.GUN:
            gunJointPos = self.__model.node('HP_gunJoint').position
            gunFirePos = self.__model.node('HP_gunFire').position
            position = (gunFirePos + gunJointPos) / 2.0
        else:
            position = _getBBCenter(TankPartNames.CHASSIS)
        return position

    def __getEmblemCorners(self, hitPos, dir, up, emblem):
        size = emblem[3] * _CFG['v_scale']
        m = Math.Matrix()
        m.lookAt(hitPos, dir, up)
        m.invert()
        result = (Math.Vector3(size * 0.5, size * 0.5, -0.25),
         Math.Vector3(size * 0.5, -size * 0.5, -0.25),
         Math.Vector3(-size * 0.5, -size * 0.5, -0.25),
         Math.Vector3(-size * 0.5, size * 0.5, -0.25))
        return [ m.applyPoint(vec) for vec in result ]

    def __correctEmblemLookAgainstGun(self, hitPos, dir, up, emblem):
        hitTester = self.__vDesc.gun.hitTester
        hitTester.loadBspModel()
        toLocalGun = Math.Matrix(self.__model.node(TankPartNames.GUN))
        toLocalGun.invert()
        checkDirLocal = toLocalGun.applyVector(dir) * -10
        cornersLocal = self.__getEmblemCorners(hitPos, dir, up, emblem)
        cornersLocal = [ toLocalGun.applyPoint(vec) for vec in cornersLocal ]
        testResult = hitTester.localCollidesWithTriangle((cornersLocal[0], cornersLocal[2], cornersLocal[1]), checkDirLocal)
        testResult = testResult or hitTester.localCollidesWithTriangle((cornersLocal[0], cornersLocal[3], cornersLocal[2]), checkDirLocal)
        hitTester.releaseBspModel()
        if not testResult:
            return dir
        dirRot = Math.Matrix()
        angle = _HANGAR_UNDERGUN_EMBLEM_ANGLE_SHIFT
        turretMat = Math.Matrix(self.__model.node(TankPartNames.TURRET))
        fromTurretToHit = hitPos - turretMat.translation
        gunDir = turretMat.applyVector(Math.Vector3(0, 0, 1))
        if Math.Vector3(0, 1, 0).dot(gunDir * fromTurretToHit) < 0:
            angle = -angle
        dirRot.setRotateY(angle)
        normRot = Math.Matrix()
        normRot.setRotateYPR((dir.yaw, dir.pitch, 0))
        dirRot.postMultiply(normRot)
        dir = dirRot.applyVector(Math.Vector3(0, 0, 1))
        return dir

    def __initMaterialHandlers(self):
        for fashionIdx, descId in enumerate(TankPartNames.ALL):
            camoHandler = self.__camoHandlers[fashionIdx] = BigWorld.PyCamoHandler()
            repaintHandler = self.__repaintHandlers[fashionIdx] = BigWorld.PyRepaintHandler()
            self.__fashions[fashionIdx].addMaterialHandler(camoHandler)
            self.__fashions[fashionIdx].addMaterialHandler(repaintHandler)

    def updateCustomization(self, outfit, component):
        if self.__isVehicleDestroyed:
            return
        if component & OutfitComponent.CAMO:
            self.__updateCamouflage(outfit)
        if component & OutfitComponent.PAINT:
            self.__updatePaint(outfit)
        if component & OutfitComponent.DECAL:
            self.__updateDecals(outfit)

    def __updatePaint(self, outfit):
        for fashionIdx, _ in enumerate(TankPartNames.ALL):
            repaint = camouflages.getRepaint(outfit, fashionIdx, self.__vDesc)
            self.__repaintHandlers[fashionIdx].setRepaintParams(repaint)

    def __updateCamouflage(self, outfit):
        for fashionIdx, descId in enumerate(TankPartNames.ALL):
            camo = camouflages.getCamo(outfit, fashionIdx, self.__vDesc, descId, self.__vState != 'undamaged')
            if camo:
                self.__fashions[fashionIdx].setCamouflage()
                self.__camoHandlers[fashionIdx].setCamoParams(camo)
            self.__fashions[fashionIdx].removeCamouflage()

    def __updateDecals(self, outfit):
        self.__setupEmblems(outfit)


class _ClientHangarSpacePathOverride():

    def __init__(self):
        g_playerEvents.onEventNotificationsChanged += self.__onEventNotificationsChanged
        g_playerEvents.onDisconnected += self.__onDisconnected

    def destroy(self):
        g_playerEvents.onEventNotificationsChanged -= self.__onEventNotificationsChanged
        g_playerEvents.onDisconnected -= self.__onDisconnected

    def setPremium(self, isPremium):
        from gui.shared.utils.HangarSpace import g_hangarSpace
        g_hangarSpace.refreshSpace(isPremium, True)

    def setPath(self, path, isPremium=None, reload=True):
        if path is not None and not path.startswith('spaces/'):
            path = 'spaces/' + path
        from gui.shared.utils.HangarSpace import g_hangarSpace
        if isPremium is None:
            isPremium = g_hangarSpace.isPremium
        if path is not None:
            _EVENT_HANGAR_PATHS[isPremium] = path
        elif _EVENT_HANGAR_PATHS.has_key(isPremium):
            del _EVENT_HANGAR_PATHS[isPremium]
        readHangarSettings('igrPremHangarPath' + ('CN' if constants.IS_CHINA else ''))
        if reload:
            g_hangarSpace.refreshSpace(g_hangarSpace.isPremium, True)
        return

    def __onDisconnected(self):
        global _EVENT_HANGAR_PATHS
        _EVENT_HANGAR_PATHS = {}

    def __onEventNotificationsChanged(self, diff):
        from gui.shared.utils.HangarSpace import g_hangarSpace
        isPremium = g_hangarSpace.isPremium
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
            visibilityMask = 4294967295L
            path = None
            try:
                data = json.loads(notification['data'])
                path = data['hangar']
                visibilityMask = int(data.get('visibilityMask', visibilityMask), base=16)
            except:
                path = notification['data']

            if notification['type'] == _SERVER_CMD_CHANGE_HANGAR:
                _EVENT_HANGAR_PATHS[False] = path
                _EVENT_HANGAR_VISIBILITY_MASK[False] = visibilityMask
                if not isPremium:
                    hasChanged = True
            if notification['type'] == _SERVER_CMD_CHANGE_HANGAR_PREM:
                _EVENT_HANGAR_PATHS[True] = path
                _EVENT_HANGAR_VISIBILITY_MASK[True] = visibilityMask
                if isPremium:
                    hasChanged = True

        if hasChanged and g_hangarSpace.inited:
            g_hangarSpace.refreshSpace(isPremium, True)
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
