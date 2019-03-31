# Python bytecode 2.6 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/ClientHangarSpace.py
# Compiled at: 2019-03-27 03:52:54
import BigWorld, Math
from debug_utils import *
from functools import partial
import items.vehicles
import math
import time
import VehicleStickers
from MemoryCriticalController import g_critMemHandler
_CFG = {'basic': {'space_name': 'spaces/hangar',
           'v_scale': 1.0,
           'v_start_angles': (0, 0, 0),
           'v_start_pos': Math.Vector3(50, 0, 50),
           'cam_start_dist': 9.0,
           'cam_start_angles': [-25.0, 210.0],
           'cam_start_target_pos': Math.Vector3(50, 0, 50),
           'cam_dist_constr': [6.0, 11.0],
           'cam_pitch_constr': [-70.0, -5.0],
           'cam_sens': 0.005,
           'cam_pivot_pos': Math.Vector3(0, 1, 0),
           'cam_fluency': 0.05,
           'emblems_alpha_damaged': 0.3,
           'emblems_alpha_undamaged': 0.9,
           'shadow_light_dir': (0.55, -1, -1.7),
           'preview_cam_start_dist': 8.0,
           'preview_cam_start_angles': [-25.0, 140.0],
           'preview_cam_pivot_pos': Math.Vector3(-2, 1, 0),
           'preview_cam_start_target_pos': Math.Vector3(50, 0, 50)},
 'premium': {'space_name': 'spaces/hangar_premium',
             'v_scale': 1.0,
             'v_start_angles': (180, 0, 0),
             'v_start_pos': Math.Vector3(50, 0, 50),
             'cam_start_dist': 14.0,
             'cam_start_angles': [-10.0, 25.0],
             'cam_start_target_pos': Math.Vector3(50, 0, 50),
             'cam_dist_constr': [6.0, 14.0],
             'cam_pitch_constr': [-70.0, -5.0],
             'cam_sens': 0.005,
             'cam_pivot_pos': Math.Vector3(0, 1, 0),
             'cam_fluency': 0.05,
             'emblems_alpha_damaged': 0.3,
             'emblems_alpha_undamaged': 0.9,
             'shadow_light_dir': (-0.3, -0.5, 0.7),
             'preview_cam_start_dist': 8.0,
             'preview_cam_start_angles': [-25.0, -40.0],
             'preview_cam_pivot_pos': Math.Vector3(-2, 1, 0),
             'preview_cam_start_target_pos': Math.Vector3(50, 0, 50)}}
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
_PREVIEW_CAM_START_DIST = None
_PREVIEW_CAM_START_ANGLES = None
_PREVIEW_CAM_PIVOT_POS = None
_PREVIEW_CAM_START_TARGET_POS = None
_CAMOUFLAGE_MIN_INTENSITY = 1.0

class ClientHangarSpace():

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
        return

    def create(self, isPremium, onSpaceLoadedCallback=None):
        global _V_START_POS
        global _V_START_ANGLES
        global _SPACE_NAME
        global _SHADOW_LIGHT_DIR
        BigWorld.drawSkySunAndMoon(False)
        accountType = 'premium' if isPremium else 'basic'
        self.__selectHangarType(accountType)
        LOG_DEBUG('load hangar: hangar type: <%s>' % accountType)
        BigWorld.worldDrawEnabled(False)
        BigWorld.wg_useAttachmentBboxesInShadowCasting(True)
        BigWorld.wg_setIndoorMainLightDir(_SHADOW_LIGHT_DIR)
        self.__onLoadedCallback = onSpaceLoadedCallback
        self.__spaceId = BigWorld.createSpace()
        self.__spaceMappingId = BigWorld.addSpaceGeometryMapping(self.__spaceId, None, _SPACE_NAME)
        self.__vEntityId = BigWorld.createEntity('OfflineEntity', self.__spaceId, 0, _V_START_POS, (_V_START_ANGLES[2], _V_START_ANGLES[1], _V_START_ANGLES[0]), dict())
        self.__vAppearance = _VehicleAppearance(self.__spaceId, self.__vEntityId)
        self.__setupCamera()
        self.__waitCallback = BigWorld.callback(0.1, self.__waitLoadingSpace)
        return

    def getCamera(self):
        return self.__cam

    def recreateVehicle(self, vDesc, vState, onVehicleLoadedCallback=None):
        global _V_SCALE
        global _CAM_START_DIST
        global _CAM_SENS
        self.__vAppearance.recreate(vDesc, vState, onVehicleLoadedCallback)
        self.__boundingRadius = _calculateBoundingRadius(vDesc, _V_SCALE)
        dz = 0
        if self.__cam.targetMaxDist > self.__cam.pivotMaxDist:
            dz = (self.__cam.pivotMaxDist - _CAM_START_DIST) / _CAM_SENS
        self.updateCameraByMouseMove(0, 0, dz)

    def removeVehicle(self):
        self.__boundingRadius = None
        self.__vAppearance.destroy()
        self.__vAppearance = _VehicleAppearance(self.__spaceId, self.__vEntityId)
        BigWorld.entity(self.__vEntityId).model = None
        return

    def moveVehicleTo(self, position):
        try:
            vehicle = BigWorld.entity(self.__vEntityId)
            vehicle.model.motors[0].signal = _createMatrix(_V_SCALE, _V_START_ANGLES, position)
        except:
            LOG_CURRENT_EXCEPTION()

    def updateVehicleCamouflage(self, camouflageID=None):
        self.__vAppearance.updateCamouflage(camouflageID=camouflageID)

    def destroy(self):
        if self.__waitCallback is not None and not self.spaceLoaded():
            self.__destroyFunc = self.__destroy
            return
        else:
            self.__destroy()
            return

    def handleMouseEvent(self, dx, dy, dz):
        if not self.spaceLoaded():
            return False
        self.updateCameraByMouseMove(dx, dy, dz)

    def getCameraLocation(self):
        sourceMat = Math.Matrix(self.__cam.source)
        targetMat = Math.Matrix(self.__cam.target)
        return {'targetPos': targetMat.translation,
         'pivotPos': self.__cam.pivotPosition,
         'yaw': sourceMat.yaw,
         'pitch': sourceMat.pitch,
         'dist': self.__cam.pivotMaxDist}

    def setCameraLocation(self, targetPos=None, pivotPos=None, yaw=None, pitch=None, dist=None):
        global _CAM_PITCH_CONSTR
        global _CAM_DIST_CONSTR
        sourceMat = Math.Matrix(self.__cam.source)
        if yaw is None:
            yaw = sourceMat.yaw
        if pitch is None:
            pitch = sourceMat.pitch
        if dist is None:
            dist = self.__cam.pivotMaxDist
        if yaw > 2.0 * math.pi:
            yaw -= 2.0 * math.pi
        elif yaw < -2.0 * math.pi:
            yaw += 2.0 * math.pi
        pitch = _clamp(math.radians(_CAM_PITCH_CONSTR[0]), math.radians(_CAM_PITCH_CONSTR[1]), pitch)
        dist = _clamp(_CAM_DIST_CONSTR[0], _CAM_DIST_CONSTR[1], dist)
        if self.__boundingRadius is not None:
            dist = dist if dist > self.__boundingRadius + 1.0 else self.__boundingRadius + 1.0
        mat = Math.Matrix()
        mat.setRotateYPR((yaw, pitch, 0.0))
        self.__cam.source = mat
        self.__cam.pivotMaxDist = dist
        if targetPos is not None:
            self.__cam.target.setTranslate(targetPos)
        if pivotPos is not None:
            self.__cam.pivotPosition = pivotPos
        return

    def locateCameraToPreview(self):
        global _PREVIEW_CAM_START_DIST
        global _PREVIEW_CAM_PIVOT_POS
        global _PREVIEW_CAM_START_TARGET_POS
        global _PREVIEW_CAM_START_ANGLES
        self.setCameraLocation(targetPos=_PREVIEW_CAM_START_TARGET_POS, pivotPos=_PREVIEW_CAM_PIVOT_POS, yaw=math.radians(_PREVIEW_CAM_START_ANGLES[1]), pitch=math.radians(_PREVIEW_CAM_START_ANGLES[0]), dist=_PREVIEW_CAM_START_DIST)

    def updateCameraByMouseMove(self, dx, dy, dz):
        sourceMat = Math.Matrix(self.__cam.source)
        yaw = sourceMat.yaw
        pitch = sourceMat.pitch
        dist = self.__cam.pivotMaxDist
        yaw += dx * _CAM_SENS
        pitch -= dy * _CAM_SENS
        dist -= dz * _CAM_SENS
        if yaw > 2.0 * math.pi:
            yaw -= 2.0 * math.pi
        elif yaw < -2.0 * math.pi:
            yaw += 2.0 * math.pi
        pitch = _clamp(math.radians(_CAM_PITCH_CONSTR[0]), math.radians(_CAM_PITCH_CONSTR[1]), pitch)
        dist = _clamp(_CAM_DIST_CONSTR[0], _CAM_DIST_CONSTR[1], dist)
        if self.__boundingRadius is not None:
            dist = dist if dist > self.__boundingRadius + 1.0 else self.__boundingRadius + 1.0
        mat = Math.Matrix()
        mat.setRotateYPR((yaw, pitch, 0.0))
        self.__cam.source = mat
        self.__cam.pivotMaxDist = dist
        return

    def spaceLoaded(self):
        return not self.__loadingStatus < 1

    def spaceLoading(self):
        return self.__waitCallback is not None

    def __destroy(self):
        LOG_DEBUG('Hangar successfully destroyed.')
        BigWorld.wg_useAttachmentBboxesInShadowCasting(False)
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
        entity = None if self.__vEntityId is None else BigWorld.entity(self.__vEntityId)
        BigWorld.drawSkySunAndMoon(True)
        BigWorld.SetDrawInflux(False)
        if self.__spaceId is not None and self.__spaceMappingId is not None:
            BigWorld.delSpaceGeometryMapping(self.__spaceId, self.__spaceMappingId)
        if self.__spaceId is not None:
            BigWorld.clearSpace(self.__spaceId)
            BigWorld.releaseSpace(self.__spaceId)
        self.__spaceMappingId = None
        self.__spaceId = None
        if entity is None or not entity.inWorld:
            return
        else:
            BigWorld.destroyEntity(self.__vEntityId)
            self.__vEntityId = None
            return

    def __setupCamera(self):
        global _CAM_START_TARGET_POS
        global _CAM_FLUENCY
        global _CAM_PIVOT_POS
        global _CAM_START_ANGLES
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

    def __waitLoadingSpace(self):
        self.__waitCallback = None
        self.__loadingStatus = BigWorld.spaceLoadStatus()
        if not BigWorld.worldDrawEnabled():
            BigWorld.worldDrawEnabled(True)
        if self.__loadingStatus < 1:
            self.__waitCallback = BigWorld.callback(0.1, self.__waitLoadingSpace)
        else:
            g_critMemHandler.restore()
            if self.__onLoadedCallback is not None:
                self.__onLoadedCallback()
                self.__onLoadedCallback = None
            if self.__destroyFunc:
                self.__destroyFunc()
                self.__destroyFunc = None
        return

    def __selectHangarType(self, type):
        global _PREVIEW_CAM_PIVOT_POS
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
        global _V_START_POS
        global _PREVIEW_CAM_START_TARGET_POS
        global _CAM_START_DIST
        global _CAM_DIST_CONSTR
        global _PREVIEW_CAM_START_DIST
        global _CAM_START_ANGLES
        global _PREVIEW_CAM_START_ANGLES
        global _CAM_SENS
        cfg = _CFG[type]
        _SPACE_NAME = cfg['space_name']
        _V_SCALE = cfg['v_scale']
        _V_START_ANGLES = _degToRadVec3(cfg['v_start_angles'])
        _V_START_POS = cfg['v_start_pos']
        _CAM_START_DIST = cfg['cam_start_dist']
        _CAM_START_ANGLES = cfg['cam_start_angles']
        _CAM_START_TARGET_POS = cfg['cam_start_target_pos']
        _CAM_DIST_CONSTR = cfg['cam_dist_constr']
        _CAM_PITCH_CONSTR = cfg['cam_pitch_constr']
        _CAM_SENS = cfg['cam_sens']
        _CAM_PIVOT_POS = cfg['cam_pivot_pos']
        _CAM_FLUENCY = cfg['cam_fluency']
        _EMBLEMS_ALPHA_DAMAGED = cfg['emblems_alpha_damaged']
        _EMBLEMS_ALPHA_UNDAMAGED = cfg['emblems_alpha_undamaged']
        _SHADOW_LIGHT_DIR = cfg['shadow_light_dir']
        _PREVIEW_CAM_START_DIST = cfg['preview_cam_start_dist']
        _PREVIEW_CAM_START_ANGLES = cfg['preview_cam_start_angles']
        _PREVIEW_CAM_PIVOT_POS = cfg['preview_cam_pivot_pos']
        _PREVIEW_CAM_START_TARGET_POS = cfg['preview_cam_start_target_pos']


class _VehicleAppearance():
    __ROOT_NODE_NAME = 'V'

    def __init__(self, spaceId, vEntityId):
        self.__isLoaded = False
        self.__curBuildInd = 0
        self.__vDesc = None
        self.__spaceId = spaceId
        self.__vEntityId = vEntityId
        self.__onLoadedCallback = None
        self.__emblemsAlpha = _EMBLEMS_ALPHA_UNDAMAGED
        self.__models = ()
        self.__stickers = []
        self.__isVehicleDestroyed = False
        return

    def recreate(self, vDesc, vState, onVehicleLoadedCallback=None):
        self.__onLoadedCallback = onVehicleLoadedCallback
        self.__isLoaded = False
        self.__startBuild(vDesc, vState)

    def destroy(self):
        self.__onLoadedCallback = None
        self.__vDesc = None
        self.__isLoaded = False
        self.__curBuildInd = 0
        self.__vEntityId = None
        return

    def isLoaded(self):
        return self.__isLoaded

    def __startBuild(self, vDesc, vState):
        self.__curBuildInd += 1
        self.__vDesc = vDesc
        self.__resources = {}
        self.__stickers = []
        playerEmblemDescrs = items.vehicles.g_cache.playerEmblems()['descrs']
        self.__componentIDs = {'chassis': vDesc.chassis['models'][vState],
         'hull': vDesc.hull['models'][vState],
         'turret': vDesc.turret['models'][vState],
         'gun': vDesc.gun['models'][vState],
         'emblemTexture': playerEmblemDescrs[vDesc.playerEmblemID]['texture'][0],
         'camouflageExclusionMask': vDesc.type.camouflageExclusionMask}
        customization = items.vehicles.g_cache.customization(vDesc.type.id[0])
        if vDesc.camouflage is not None and customization is not None:
            camouflageId = vDesc.camouflage[0]
            camouflageDesc = customization['camouflages'].get(camouflageId)
            if camouflageDesc is not None:
                self.__componentIDs['camouflageTexture'] = camouflageDesc['texture']
        if vState == 'undamaged':
            self.__emblemsAlpha = _EMBLEMS_ALPHA_UNDAMAGED
            self.__isVehicleDestroyed = False
        else:
            self.__emblemsAlpha = _EMBLEMS_ALPHA_DAMAGED
            self.__isVehicleDestroyed = True
        BigWorld.loadResourceListBG(tuple(self.__componentIDs.values()), partial(self.__onResourcesLoaded, self.__curBuildInd))
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
        hull.node('HP_turretJoint').attach(turret)
        turret.node('HP_gunJoint').attach(gun)
        self.__setupEmblems()
        for sticker, alpha in self.__stickers:
            sticker.setAlphas(0, 0)

        for model in self.__models:
            model.visible = False
            model.visibleAttachments = True

        return chassis

    def __setupEmblems(self):
        vDesc = self.__vDesc
        resources = self.__resources
        chassis = self.__models[0]
        hull = self.__models[1]
        turret = self.__models[2]
        gun = self.__models[3]
        emblemAlpha = self.__emblemsAlpha * vDesc.type.emblemsAlpha
        emblemPositions = ((hull, chassis.node(self.__ROOT_NODE_NAME), vDesc.hull['emblemSlots']), (gun if vDesc.turret['showEmblemsOnGun'] else turret, hull.node('HP_turretJoint'), vDesc.turret['emblemSlots']))
        for targetModel, parentNode, slots in emblemPositions:
            sticker = VehicleStickers.VehicleStickers(vDesc, slots)
            sticker.setAlphas(emblemAlpha, emblemAlpha)
            sticker.attachStickers(targetModel, parentNode, self.__isVehicleDestroyed)
            self.__stickers.append((sticker, emblemAlpha))

        BigWorld.player().stats.get('clanDBID', self.__onClanDBIDRetrieved)

    def __onClanDBIDRetrieved(self, _, clanID):
        for sticker, _ in self.__stickers:
            sticker.setClanID(clanID)

    def __setupModel(self, buildIdx):
        model = self.__assembleModel()
        model.addMotor(BigWorld.Servo(_createMatrix(_V_SCALE, _V_START_ANGLES, _V_START_POS)))
        BigWorld.addModel(model)
        BigWorld.callback(0.0, partial(self.__doFinalSetup, buildIdx, model))

    def __doFinalSetup(self, buildIdx, model):
        BigWorld.delModel(model)
        if buildIdx != self.__curBuildInd:
            return
        else:
            entity = BigWorld.entity(self.__vEntityId)
            if entity:
                for m in self.__models:
                    m.visible = True
                    m.visibleAttachments = True

                for sticker, alpha in self.__stickers:
                    sticker.setAlphas(alpha, alpha)

                entity.model = model
                entity.model.delMotor(entity.model.motors[0])
                entity.model.addMotor(BigWorld.Servo(_createMatrix(_V_SCALE, _V_START_ANGLES, _V_START_POS)))
                if self.__onLoadedCallback is not None:
                    self.__onLoadedCallback()
                    self.__onLoadedCallback = None
                self.updateCamouflage()
            return

    def updateCamouflage(self, camouflageID=None):
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
            if camouflageID is None and vDesc.camouflage is not None:
                camouflageID = vDesc.camouflage[0]
            customization = items.vehicles.g_cache.customization(vDesc.type.id[0])
            defaultTiling = None
            if camouflageID is not None and customization is not None:
                camouflage = customization['camouflages'].get(camouflageID)
                if camouflage is not None:
                    camouflagePresent = True
                    texture = camouflage['texture']
                    colors = camouflage['colors']
                    weights = Math.Vector4((colors[0] >> 24) / 255.0, (colors[1] >> 24) / 255.0, (colors[2] >> 24) / 255.0, (colors[3] >> 24) / 255.0)
                    defaultTiling = camouflage['tiling'].get(vDesc.type.compactDescr)
            if self.__isVehicleDestroyed:
                weights *= 0.1
            if vDesc.camouflage is not None:
                _, camStartTime, camNumDays = vDesc.camouflage
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
                tgDesc = None
                if model == self.__models[2]:
                    tgDesc = vDesc.turret
                elif model == self.__models[3]:
                    tgDesc = vDesc.gun
                if tgDesc is not None:
                    coeff = tgDesc.get('camouflageTiling')
                    if coeff is not None:
                        if tiling is not None:
                            tiling = (tiling[0] * coeff[0],
                             tiling[1] * coeff[1],
                             tiling[2] * coeff[2],
                             tiling[3] * coeff[3])
                        else:
                            tiling = coeff
                    if tgDesc.has_key('camouflageExclusionMask'):
                        exclusionMap = tgDesc['camouflageExclusionMask']
                if not camouflagePresent or exclusionMap == '' or texture == '':
                    if hasattr(model, 'wg_fashion'):
                        delattr(model, 'wg_fashion')
                else:
                    if not hasattr(model, 'wg_fashion'):
                        if model == self.__models[0]:
                            tracksCfg = vDesc.chassis['tracks']
                            fashion = BigWorld.WGVehicleFashion()
                            fashion.setTracks(tracksCfg['leftMaterial'], tracksCfg['rightMaterial'], tracksCfg['textureScale'])
                            model.wg_fashion = fashion
                        else:
                            model.wg_fashion = BigWorld.WGBaseFashion()
                    model.wg_fashion.setCamouflage(texture, exclusionMap, tiling, colors[0], colors[1], colors[2], colors[3], weights)

            return


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


def _clamp(minVal, maxVal, val):
    tmpVal = val
    tmpVal = max(minVal, val)
    tmpVal = min(maxVal, tmpVal)
    return tmpVal


def _calculateBoundingRadius(vehDescr, scale):
    hitTester = vehDescr.type.hull['hitTester']
    hitTester.loadBspModel()
    boundingRadius = hitTester.bbox[2] * scale
    hitTester.releaseBspModel()
    return boundingRadius


def _degToRadVec3(inVec):
    outVec = Math.Vector3()
    for i in range(0, 3):
        outVec[i] = math.radians(inVec[i])

    return outVec
