# Embedded file name: scripts/client/gui/ClientHangarSpace.py
from collections import namedtuple
import functools
from AvatarInputHandler.cameras import FovExtended
import BigWorld, Math, ResMgr
import Keys
import copy
import MusicController
from account_helpers.settings_core import g_settingsCore
from debug_utils import *
from dossiers2.ui.achievements import MARK_ON_GUN_RECORD
from functools import partial
from gui import g_tankActiveCamouflage
from gui import game_control, g_keyEventHandlers, g_mouseEventHandlers
import items.vehicles
import math
import time
import VehicleStickers
from HangarVehicle import HangarVehicle
import constants
from PlayerEvents import g_playerEvents
from ConnectionManager import connectionManager
from post_processing import g_postProcessing
from ModelHitTester import ModelHitTester
from AvatarInputHandler import mathUtils
import MapActivities
from gui.shared.ItemsCache import g_itemsCache, CACHE_SYNC_REASON
import TankHangarShadowProxy
import weakref
import FMOD
import json
if FMOD.enabled:
    import VehicleAppearance
from VehicleEffects import RepaintParams
_DEFAULT_HANGAR_SPACE_PATH_BASIC = 'spaces/hangar_v2'
_DEFAULT_HANGAR_SPACE_PATH_PREM = 'spaces/hangar_premium_v2'
_SERVER_CMD_CHANGE_HANGAR = 'cmd_change_hangar'
_SERVER_CMD_CHANGE_HANGAR_PREM = 'cmd_change_hangar_prem'
_HANGAR_UNDERGUN_EMBLEM_ANGLE_SHIFT = math.pi / 4
_CAMOUFLAGE_MIN_INTENSITY = 1.0
_CFG = {}
_DEFAULT_CFG = {}
_HANGAR_CFGS = {}
_EVENT_HANGAR_PATHS = {}
_EVENT_HANGAR_VISIBILITY_MASK = {}

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
        if math.fabs(delta1) > math.fabs(delta2):
            return self.__end
        return self.__start

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


class ClientHangarSpace():

    def __init__(self):
        global _HANGAR_CFGS
        global _DEFAULT_CFG
        global _CFG
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
        hangarsXml = ResMgr.openSection('gui/hangars.xml')
        for isPremium in (False, True):
            spacePath = _DEFAULT_HANGAR_SPACE_PATH_PREM if isPremium else _DEFAULT_HANGAR_SPACE_PATH_BASIC
            settingsXml = ResMgr.openSection(spacePath + '/space.settings')
            settingsXml = settingsXml['hangarSettings']
            cfg = {'path': spacePath,
             'cam_yaw_constr': Math.Vector2(-180, 180),
             'cam_pitch_constr': Math.Vector2(-70, -5)}
            self.__loadConfig(cfg, settingsXml)
            self.__loadConfigValue('shadow_model_name', hangarsXml, hangarsXml.readString, cfg)
            self.__loadConfigValue('shadow_default_texture_name', hangarsXml, hangarsXml.readString, cfg)
            self.__loadConfigValue('shadow_empty_texture_name', hangarsXml, hangarsXml.readString, cfg)
            self.__loadConfigValue(self.__igrHangarPathKey, hangarsXml, hangarsXml.readString, cfg)
            _DEFAULT_CFG[self.getSpaceType(isPremium)] = cfg
            _HANGAR_CFGS[spacePath.lower()] = settingsXml

        for folderName, folderDS in ResMgr.openSection('spaces').items():
            settingsXml = ResMgr.openSection('spaces/' + folderName + '/space.settings/hangarSettings')
            if settingsXml is not None:
                _HANGAR_CFGS[('spaces/' + folderName).lower()] = settingsXml

        _CFG = copy.copy(_DEFAULT_CFG[self.getSpaceType(False)])
        self.__yawCameraFilter = HangarCameraYawFilter(math.radians(_CFG['cam_yaw_constr'][0]), math.radians(_CFG['cam_yaw_constr'][1]), _CFG['cam_sens'])
        return

    def create(self, isPremium, onSpaceLoadedCallback = None):
        global _EVENT_HANGAR_PATHS
        global _CFG
        BigWorld.worldDrawEnabled(False)
        BigWorld.wg_setSpecialFPSMode()
        self.__onLoadedCallback = onSpaceLoadedCallback
        self.__spaceId = BigWorld.createSpace()
        type = self.getSpaceType(isPremium)
        _CFG = copy.copy(_DEFAULT_CFG[type])
        spacePath = _DEFAULT_CFG[type]['path']
        LOG_DEBUG('load hangar: hangar type = <{0:>s}>, space = <{1:>s}>'.format(type, spacePath))
        visibilityMask = 4294967295L
        if game_control.g_instance.igr.getRoomType() == constants.IGR_TYPE.PREMIUM:
            if _CFG.get(self.__igrHangarPathKey) is not None:
                spacePath = _CFG[self.__igrHangarPathKey]
        if _EVENT_HANGAR_PATHS.has_key(isPremium):
            spacePath = _EVENT_HANGAR_PATHS[isPremium]
        if _EVENT_HANGAR_VISIBILITY_MASK.has_key(isPremium):
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
        if _HANGAR_CFGS.has_key(spacePathLC):
            self.__loadConfig(_CFG, _HANGAR_CFGS[spacePathLC], _CFG)
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

    def playHangarMusic(self, restart = False):
        MusicController.g_musicController.setAccountAttrs(g_itemsCache.items.stats.attributes, restart)
        MusicController.g_musicController.play(MusicController.MUSIC_EVENT_LOBBY)
        MusicController.g_musicController.play(MusicController.AMBIENT_EVENT_LOBBY)

    def recreateVehicle(self, vDesc, vState, onVehicleLoadedCallback = None):
        if self.__vAppearance is None:
            LOG_ERROR('ClientHangarSpace.recreateVehicle failed because hangar space has not been loaded correctly.')
            return
        else:
            self.__vAppearance.recreate(vDesc, vState, onVehicleLoadedCallback)
            hitTester = vDesc.hull['hitTester']
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

    def updateVehicleCamouflage(self, camouflageID = None):
        self.__vAppearance.updateCamouflage(camouflageID=camouflageID)

    def updateVehicleSticker(self, model):
        self.__vAppearance.updateVehicleSticker(model[0], model[1])

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

    def getCameraLocation(self):
        sourceMat = Math.Matrix(self.__cam.source)
        targetMat = Math.Matrix(self.__cam.target)
        return {'targetPos': targetMat.translation,
         'pivotPos': self.__cam.pivotPosition,
         'yaw': sourceMat.yaw,
         'pitch': sourceMat.pitch,
         'dist': self.__cam.pivotMaxDist}

    def setCameraLocation(self, targetPos = None, pivotPos = None, yaw = None, pitch = None, dist = None, ignoreConstraints = False):
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

    def locateCameraOnEmblem(self, onHull, emblemType, emblemIdx, relativeSize = 0.5):
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
        if g_settingsCore.getSetting('dynamicFov') and abs(distConstr[1] - distConstr[0]) > 0.001:
            relativeDist = (dist - distConstr[0]) / (distConstr[1] - distConstr[0])
            _, minFov, maxFov = g_settingsCore.getSetting('fov')
            fov = mathUtils.lerp(minFov, maxFov, relativeDist)
            BigWorld.callback(0, functools.partial(FovExtended.instance().setFovByAbsoluteValue, math.radians(fov), 0.1))
        return

    def spaceLoaded(self):
        return not self.__loadingStatus < 1

    def spaceLoading(self):
        return self.__waitCallback is not None

    def getSpaceType(self, isPremium):
        if isPremium:
            return 'premium'
        return 'basic'

    def __destroy(self):
        LOG_DEBUG('Hangar successfully destroyed.')
        MusicController.g_musicController.unloadCustomSounds()
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
        return

    def __loadConfig(self, cfg, xml, defaultCfg = None):
        if defaultCfg is None:
            defaultCfg = cfg
        self.__loadConfigValue('v_scale', xml, xml.readFloat, cfg, defaultCfg)
        self.__loadConfigValue('v_start_angles', xml, xml.readVector3, cfg, defaultCfg)
        self.__loadConfigValue('v_start_pos', xml, xml.readVector3, cfg, defaultCfg)
        self.__loadConfigValue('cam_start_target_pos', xml, xml.readVector3, cfg, defaultCfg)
        self.__loadConfigValue('cam_start_dist', xml, xml.readFloat, cfg, defaultCfg)
        self.__loadConfigValue('cam_start_angles', xml, xml.readVector2, cfg, defaultCfg)
        self.__loadConfigValue('cam_dist_constr', xml, xml.readVector2, cfg, defaultCfg)
        self.__loadConfigValue('cam_pitch_constr', xml, xml.readVector2, cfg, defaultCfg)
        self.__loadConfigValue('cam_yaw_constr', xml, xml.readVector2, cfg, defaultCfg)
        self.__loadConfigValue('preview_cam_dist_constr', xml, xml.readVector2, cfg, defaultCfg)
        self.__loadConfigValue('cam_sens', xml, xml.readFloat, cfg, defaultCfg)
        self.__loadConfigValue('cam_pivot_pos', xml, xml.readVector3, cfg, defaultCfg)
        self.__loadConfigValue('cam_fluency', xml, xml.readFloat, cfg, defaultCfg)
        self.__loadConfigValue('emblems_alpha_damaged', xml, xml.readFloat, cfg, defaultCfg)
        self.__loadConfigValue('emblems_alpha_undamaged', xml, xml.readFloat, cfg, defaultCfg)
        self.__loadConfigValue('shadow_light_dir', xml, xml.readVector3, cfg, defaultCfg)
        self.__loadConfigValue('preview_cam_start_dist', xml, xml.readFloat, cfg, defaultCfg)
        self.__loadConfigValue('preview_cam_start_angles', xml, xml.readVector2, cfg, defaultCfg)
        self.__loadConfigValue('preview_cam_pivot_pos', xml, xml.readVector3, cfg, defaultCfg)
        self.__loadConfigValue('preview_cam_start_target_pos', xml, xml.readVector3, cfg, defaultCfg)
        self.__loadConfigValue('shadow_model_name', xml, xml.readString, cfg, defaultCfg)
        self.__loadConfigValue('shadow_default_texture_name', xml, xml.readString, cfg, defaultCfg)
        self.__loadConfigValue('shadow_empty_texture_name', xml, xml.readString, cfg, defaultCfg)
        for i in range(0, 3):
            cfg['v_start_angles'][i] = math.radians(cfg['v_start_angles'][i])

        return

    def __loadConfigValue(self, name, xml, fn, cfg, defaultCfg = None):
        if xml.has_key(name):
            cfg[name] = fn(name)
        else:
            cfg[name] = defaultCfg.get(name) if defaultCfg is not None else None
        return

    def __requestFakeShadowModel(self):
        resources = [_CFG['shadow_model_name']]
        BigWorld.loadResourceListBG(tuple(resources), partial(self.__onFakeShadowLoaded))

    def __onFakeShadowLoaded(self, resourceRefs):
        fakeShadowModel = resourceRefs[_CFG['shadow_model_name']]
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
        self.modifyFakeShadowScale(self.__fakeShadowScale)
        self.modifyFakeShadowAsset(self.__fakeShadowAsset)

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


class _VehicleAppearance():
    __ROOT_NODE_NAME = 'V'

    def __init__(self, spaceId, vEntityId, hangarSpace):
        self.__isLoaded = False
        self.__curBuildInd = 0
        self.__vDesc = None
        self.__vState = None
        self.__componentIDs = {}
        self.__spaceId = spaceId
        self.__vEntityId = vEntityId
        self.__onLoadedCallback = None
        self.__emblemsAlpha = _CFG['emblems_alpha_undamaged']
        self.__models = ()
        self.__vehicleStickers = None
        self.__isVehicleDestroyed = False
        self.__smCb = None
        self.__smRemoveCb = None
        self.__setupModelCb = None
        self.__hangarSpace = weakref.proxy(hangarSpace)
        self.__removeHangarShadowMap()
        from account_helpers.settings_core.SettingsCore import g_settingsCore
        self.__showMarksOnGun = g_settingsCore.getSetting('showMarksOnGun')
        g_settingsCore.onSettingsChanged += self.__onSettingsChanged
        g_itemsCache.onSyncCompleted += self.__onItemsCacheSyncCompleted
        return

    def recreate(self, vDesc, vState, onVehicleLoadedCallback = None):
        self.__onLoadedCallback = onVehicleLoadedCallback
        self.__isLoaded = False
        self.__startBuild(vDesc, vState)

    def refresh(self):
        if self.__isLoaded:
            self.__onLoadedCallback = None
            self.__isLoaded = False
            self.__startBuild(self.__vDesc, self.__vState)
        return

    def destroy(self):
        self.__onLoadedCallback = None
        self.__vDesc = None
        self.__vState = None
        self.__isLoaded = False
        self.__curBuildInd = 0
        self.__vEntityId = None
        self.__componentIDs = {}
        if self.__smCb is not None:
            BigWorld.cancelCallback(self.__smCb)
            self.__smCb = None
        if self.__smRemoveCb is not None:
            BigWorld.cancelCallback(self.__smRemoveCb)
            self.__smRemoveCb = None
        if self.__setupModelCb is not None:
            BigWorld.cancelCallback(self.__setupModelCb)
        from account_helpers.settings_core.SettingsCore import g_settingsCore
        g_settingsCore.onSettingsChanged -= self.__onSettingsChanged
        g_itemsCache.onSyncCompleted -= self.__onItemsCacheSyncCompleted
        return

    def isLoaded(self):
        return self.__isLoaded

    def __startBuild(self, vDesc, vState):
        self.__curBuildInd += 1
        self.__vDesc = vDesc
        self.__vState = vState
        self.__resources = {}
        self.__vehicleStickers = None
        self.__componentIDs = {'chassis': vDesc.chassis['models'][vState],
         'hull': vDesc.hull['models'][vState],
         'turret': vDesc.turret['models'][vState],
         'gun': vDesc.gun['models'][vState],
         'camouflageExclusionMask': vDesc.type.camouflageExclusionMask}
        customization = items.vehicles.g_cache.customization(vDesc.type.customizationNationID)
        if customization is not None and vDesc.camouflages is not None:
            activeCamo = g_tankActiveCamouflage['historical'].get(vDesc.type.compactDescr)
            if activeCamo is None:
                activeCamo = g_tankActiveCamouflage.get(vDesc.type.compactDescr, 0)
            camouflageID = vDesc.camouflages[activeCamo][0]
            camouflageDesc = customization['camouflages'].get(camouflageID)
            if camouflageDesc is not None:
                self.__componentIDs['camouflageTexture'] = camouflageDesc['texture']
        if vState == 'undamaged':
            self.__emblemsAlpha = _CFG['emblems_alpha_undamaged']
            self.__isVehicleDestroyed = False
        else:
            self.__emblemsAlpha = _CFG['emblems_alpha_damaged']
            self.__isVehicleDestroyed = True
        resources = self.__componentIDs.values()
        splineDesc = vDesc.chassis['splineDesc']
        if splineDesc is not None:
            resources.extend(splineDesc.values())
        BigWorld.loadResourceListBG(tuple(resources), partial(self.__onResourcesLoaded, self.__curBuildInd))
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
            else:
                LOG_ERROR('Could not load %s' % resID)
                succesLoaded = False

        if succesLoaded:
            self.__setupModel(buildInd)

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

    def __assembleModel(self):
        resources = self.__resources
        compIDs = self.__componentIDs
        chassis = resources[compIDs['chassis']]
        hull = resources[compIDs['hull']]
        turret = resources[compIDs['turret']]
        gun = resources[compIDs['gun']]
        self.__models = (chassis,
         hull,
         turret,
         gun)
        chassis.node(self.__ROOT_NODE_NAME).attach(hull)
        turretJointName = self.__vDesc.hull['turretHardPoints'][0]
        hull.node(turretJointName).attach(turret)
        turret.node('HP_gunJoint').attach(gun)
        self.__setupEmblems(self.__vDesc)
        self.__vehicleStickers.show = False
        if not self.__isVehicleDestroyed:
            fashion = BigWorld.WGVehicleFashion(False, _CFG['v_scale'])
            import FMOD
            if FMOD.enabled:
                import VehicleAppearance
                VehicleAppearance.setupTracksFashion(fashion, self.__vDesc, self.__isVehicleDestroyed)
            chassis.wg_fashion = fashion
            fashion.initialUpdateTracks(1.0, 10.0)
            if FMOD.enabled:
                import VehicleAppearance
                VehicleAppearance.setupSplineTracks(fashion, self.__vDesc, chassis, self.__resources)
        for model in self.__models:
            model.visible = False
            model.visibleAttachments = False

        return chassis

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
            self.__smCb = BigWorld.callback(0, self.__setupHangarShadowMap)
            return
        else:
            self.__smCb = None
            if 'observer' in self.__vDesc.type.tags:
                self.__removeHangarShadowMap()
                return
            vehiclePath = self.__vDesc.chassis['models']['undamaged']
            vehiclePath = vehiclePath[:vehiclePath.rfind('/normal')]
            dsVehicle = ResMgr.openSection(vehiclePath)
            shadowMapTexFileName = _CFG['shadow_default_texture_name']
            if dsVehicle is not None:
                for fileName, _ in dsVehicle.items():
                    if fileName.lower().find('_hangarshadowmap.dds') != -1:
                        shadowMapTexFileName = vehiclePath + '/' + fileName

            self.__hangarSpace.modifyFakeShadowAsset(shadowMapTexFileName)
            return

    def __onItemsCacheSyncCompleted(self, updateReason, invalidItems):
        if updateReason == CACHE_SYNC_REASON.DOSSIER_RESYNC and self.__vehicleStickers is not None and self.__getThisVehicleDossierInsigniaRank() != self.__vehicleStickers.getCurrentInsigniaRank():
            self.refresh()
        return

    def __getThisVehicleDossierInsigniaRank(self):
        vehicleDossier = g_itemsCache.items.getVehicleDossier(self.__vDesc.type.compactDescr)
        return vehicleDossier.getRandomStats().getAchievement(MARK_ON_GUN_RECORD).getValue()

    def __setupEmblems(self, vDesc):
        if self.__vehicleStickers is not None:
            self.__vehicleStickers.detach()
        insigniaRank = 0
        if self.__showMarksOnGun:
            insigniaRank = self.__getThisVehicleDossierInsigniaRank()
        self.__vehicleStickers = VehicleStickers.VehicleStickers(vDesc, insigniaRank)
        self.__vehicleStickers.alpha = self.__emblemsAlpha
        chassis = self.__models[0]
        hull = self.__models[1]
        turret = self.__models[2]
        gun = self.__models[3]
        turretJointName = self.__vDesc.hull['turretHardPoints'][0]
        modelsWithParents = ((hull, chassis.node(self.__ROOT_NODE_NAME)), (turret, hull.node(turretJointName)), (gun, turret.node('HP_gunJoint')))
        self.__vehicleStickers.attach(modelsWithParents, self.__isVehicleDestroyed, False)
        BigWorld.player().stats.get('clanDBID', self.__onClanDBIDRetrieved)
        return

    def updateVehicleSticker(self, playerEmblems, playerInscriptions):
        initialEmblems = copy.deepcopy(self.__vDesc.playerEmblems)
        initialInscriptions = copy.deepcopy(self.__vDesc.playerInscriptions)
        for idx, (emblemId, startTime, duration) in enumerate(playerEmblems):
            self.__vDesc.setPlayerEmblem(idx, emblemId, startTime, duration)

        for idx, (inscriptionId, startTime, duration, color) in enumerate(playerInscriptions):
            self.__vDesc.setPlayerInscription(idx, inscriptionId, startTime, duration, color)

        self.__setupEmblems(self.__vDesc)
        self.__vDesc.playerEmblems = initialEmblems
        self.__vDesc.playerInscriptions = initialInscriptions

    def __onClanDBIDRetrieved(self, _, clanID):
        self.__vehicleStickers.setClanID(clanID)

    def __setupModel(self, buildIdx):
        model = self.__assembleModel()
        model.addMotor(BigWorld.Servo(_createMatrix(_CFG['v_scale'], _CFG['v_start_angles'], _CFG['v_start_pos'])))
        entity = BigWorld.entity(self.__vEntityId)
        if isinstance(entity, HangarVehicle):
            entity.typeDescriptor = self.__vDesc
        BigWorld.addModel(model)
        if self.__setupModelCb is not None:
            BigWorld.cancelCallback(self.__setupModelCb)
        self.__setupModelCb = BigWorld.callback(0.0, partial(self.__doFinalSetup, buildIdx, model, True))
        return

    def __doFinalSetup(self, buildIdx, model, delModel):
        if delModel:
            BigWorld.delModel(model)
        if model.attached:
            self.__setupModelCb = BigWorld.callback(0.0, partial(self.__doFinalSetup, buildIdx, model, False))
            return
        else:
            self.__setupModelCb = None
            if buildIdx != self.__curBuildInd:
                return
            entity = BigWorld.entity(self.__vEntityId)
            if entity:
                for m in self.__models:
                    m.visible = True
                    m.visibleAttachments = True

                self.__vehicleStickers.show = True
                entity.model = model
                entity.model.delMotor(entity.model.motors[0])
                entity.model.addMotor(BigWorld.Servo(_createMatrix(_CFG['v_scale'], _CFG['v_start_angles'], _CFG['v_start_pos'])))
                self.__isLoaded = True
                if self.__onLoadedCallback is not None:
                    self.__onLoadedCallback()
                    self.__onLoadedCallback = None
                self.updateCamouflage()
                self.updateRepaint()
                if self.__smCb is None:
                    self.__setupHangarShadowMap()
            if self.__vDesc is not None and 'observer' in self.__vDesc.type.tags:
                model.visible = False
                model.visibleAttachments = False
            return

    def getEmblemPos(self, onHull, emblemType, emblemIdx):
        model = None
        emblemsDesc = None
        hitTester = ModelHitTester()
        worldMat = None
        chassis = self.__models[0]
        if onHull:
            model = self.__models[1]
            hitTester.bspModelName = self.__vDesc.hull['models']['undamaged']
            emblemsDesc = self.__vDesc.hull['emblemSlots']
            worldMat = Math.Matrix(model.matrix)
        else:
            if self.__vDesc.turret['showEmblemsOnGun']:
                model = self.__models[3]
                hitTester.bspModelName = self.__vDesc.gun['models']['undamaged']
            else:
                model = self.__models[2]
                hitTester.bspModelName = self.__vDesc.turret['models']['undamaged']
            emblemsDesc = self.__vDesc.turret['emblemSlots']
            worldMat = Math.Matrix(model.matrix)
        if model is None:
            return
        else:
            desiredEmblems = [ emblem for emblem in emblemsDesc if emblem.type == emblemType ]
            if emblemIdx >= len(desiredEmblems):
                return
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
        turretModel = self.__models[2]
        gunModel = self.__models[3]
        hitTester = self.__vDesc.gun['hitTester']
        hitTester.loadBspModel()
        toLocalGun = Math.Matrix(gunModel.matrix)
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
        turretMat = Math.Matrix(turretModel.matrix)
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

    def updateCamouflage(self, camouflageID = None):
        texture = ''
        colors = [0,
         0,
         0,
         0]
        weights = Math.Vector4(1, 0, 0, 0)
        camouflagePresent = True
        vDesc = self.__vDesc
        if vDesc is None:
            return
        else:
            if camouflageID is None and vDesc.camouflages is not None:
                activeCamo = g_tankActiveCamouflage['historical'].get(vDesc.type.compactDescr)
                if activeCamo is None:
                    activeCamo = g_tankActiveCamouflage.get(vDesc.type.compactDescr, 0)
                camouflageID = vDesc.camouflages[activeCamo][0]
            if camouflageID is None:
                for camouflageData in vDesc.camouflages:
                    if camouflageData[0] is not None:
                        camouflageID = camouflageData[0]
                        break

            customization = items.vehicles.g_cache.customization(vDesc.type.customizationNationID)
            defaultTiling = None
            if camouflageID is not None and customization is not None:
                camouflage = customization['camouflages'].get(camouflageID)
                if camouflage is not None:
                    camouflagePresent = True
                    texture = camouflage['texture']
                    colors = camouflage['colors']
                    weights = Math.Vector4(*[ (c >> 24) / 255.0 for c in colors ])
                    defaultTiling = camouflage['tiling'].get(vDesc.type.compactDescr)
            if self.__isVehicleDestroyed:
                weights *= 0.1
            if vDesc.camouflages is not None:
                _, camStartTime, camNumDays = vDesc.camouflages[g_tankActiveCamouflage.get(vDesc.type.compactDescr, 0)]
                if camNumDays > 0:
                    timeAmount = (time.time() - camStartTime) / (camNumDays * 86400)
                    if timeAmount > 1.0:
                        weights *= _CAMOUFLAGE_MIN_INTENSITY
                    elif timeAmount > 0:
                        weights *= (1.0 - timeAmount) * (1.0 - _CAMOUFLAGE_MIN_INTENSITY) + _CAMOUFLAGE_MIN_INTENSITY
            for model in self.__models:
                exclusionMap = vDesc.type.camouflageExclusionMask
                tiling = defaultTiling
                if tiling is None:
                    tiling = vDesc.type.camouflageTiling
                if model == self.__models[0]:
                    compDesc = vDesc.chassis
                elif model == self.__models[1]:
                    compDesc = vDesc.hull
                elif model == self.__models[2]:
                    compDesc = vDesc.turret
                elif model == self.__models[3]:
                    compDesc = vDesc.gun
                else:
                    compDesc = None
                if compDesc is not None:
                    coeff = compDesc.get('camouflageTiling')
                    if coeff is not None:
                        if tiling is not None:
                            tiling = (tiling[0] * coeff[0],
                             tiling[1] * coeff[1],
                             tiling[2] * coeff[2],
                             tiling[3] * coeff[3])
                        else:
                            tiling = coeff
                    if compDesc.get('camouflageExclusionMask'):
                        exclusionMap = compDesc['camouflageExclusionMask']
                useCamouflage = camouflagePresent and texture
                fashion = None
                if hasattr(model, 'wg_fashion'):
                    fashion = model.wg_fashion
                elif hasattr(model, 'wg_gunRecoil'):
                    fashion = model.wg_gunRecoil
                elif useCamouflage:
                    fashion = model.wg_baseFashion = BigWorld.WGBaseFashion()
                elif hasattr(model, 'wg_baseFashion'):
                    delattr(model, 'wg_baseFashion')
                if fashion is not None:
                    if useCamouflage:
                        fashion.setCamouflage(texture, exclusionMap, tiling, colors[0], colors[1], colors[2], colors[3], weights)
                    else:
                        fashion.removeCamouflage()

            return

    def updateRepaint(self):
        if not hasattr(self.__vDesc.type, 'repaintParameters'):
            return
        else:
            repaintReferenceColor, repaintReplaceColor, repaintGlossRangeScale = RepaintParams.getRepaintParams(self.__vDesc)
            for model in self.__models:
                fashion = None
                if hasattr(model, 'wg_fashion'):
                    fashion = model.wg_fashion
                elif hasattr(model, 'wg_baseFashion'):
                    fashion = model.wg_baseFashion
                elif hasattr(model, 'wg_gunRecoil'):
                    fashion = model.wg_gunRecoil
                else:
                    fashion = model.wg_baseFashion = BigWorld.WGBaseFashion()
                if fashion is not None:
                    fashion.setRepaint(repaintReferenceColor, repaintReplaceColor, repaintGlossRangeScale)

            return


class _ClientHangarSpacePathOverride():

    def __init__(self):
        g_playerEvents.onEventNotificationsChanged += self.__onEventNotificationsChanged
        connectionManager.onDisconnected += self.__onDisconnected

    def destroy(self):
        g_playerEvents.onEventNotificationsChanged -= self.__onEventNotificationsChanged
        connectionManager.onDisconnected -= self.__onDisconnected

    def setPremium(self, isPremium):
        from gui.shared.utils.HangarSpace import g_hangarSpace
        g_hangarSpace.refreshSpace(isPremium, True)

    def setPath(self, path, isPremium = None):
        if path is not None and not path.startswith('spaces/'):
            path = 'spaces/' + path
        from gui.shared.utils.HangarSpace import g_hangarSpace
        if isPremium is None:
            isPremium = g_hangarSpace.isPremium
        if path is not None:
            _EVENT_HANGAR_PATHS[isPremium] = path
        elif _EVENT_HANGAR_PATHS.has_key(isPremium):
            del _EVENT_HANGAR_PATHS[isPremium]
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
            elif notification['type'] == _SERVER_CMD_CHANGE_HANGAR_PREM:
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
            elif notification['type'] == _SERVER_CMD_CHANGE_HANGAR_PREM:
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
