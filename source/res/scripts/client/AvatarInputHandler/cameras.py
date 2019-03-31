# Python bytecode 2.6 (decompiled from Python 2.7)
# Embedded file name: scripts/client/AvatarInputHandler/cameras.py
# Compiled at: 2019-03-08 23:07:53
import BigWorld, Math, ResMgr
import math
import Settings
import weakref
from functools import partial
from debug_utils import *
from projectile_trajectory import getShotAngles
from gun_rotation_shared import calcPitchLimitsFromDesc

class ICamera():

    def create(self):
        pass

    def destroy(self):
        pass

    def enable(self, **args):
        pass

    def disable(self):
        pass

    def restoreDefaultsState(self):
        pass

    def getUserConfigValue(self, name):
        pass

    def setUserConfigValue(self, name, value):
        pass

    def update(self):
        pass

    def autoUpdate(self):
        pass


class ArcadeCamera():
    camera = property(lambda self: self.__cam)
    angles = property(lambda self: (self.__yaw, self.__pitch))

    def __init__(self, dataSec):
        self.__readCfg(dataSec)
        self.__cam = BigWorld.CursorCamera()
        self.__camDist = 0
        self.__curSense = 0
        self.__curScrollSense = 0
        self.__pitch = 0.0
        self.__yaw = 0.0
        self.__cursorOffset = (0, 0)
        self.__postmortemMode = False
        self.__modelsToCollideWith = []
        self.__onChangeControlMode = None
        self.__autoUpdateCallbackId = None
        return

    def create(self, pivotPos, onChangeControlMode=None, postmortemMode=False):
        self.__onChangeControlMode = onChangeControlMode
        self.__postmortemMode = postmortemMode
        targetMat = BigWorld.entity(BigWorld.player().playerVehicleID).matrix
        self.__camDist = self.__cfg['startDist']
        self.__cam.pivotMaxDist = self.__camDist
        self.__cam.maxDistHalfLife = 0.0
        self.__cam.movementHalfLife = 0.0
        self.__cam.turningHalfLife = 0.0
        self.__cam.pivotPosition = pivotPos
        self.__pitch = self.__cfg['startAngle']
        self.__yaw = Math.Matrix(targetMat).yaw
        matrix = Math.Matrix()
        matrix.setRotateYPR(self.__updateAngles(0, 0))
        self.__cam.source = matrix

    def destroy(self):
        self.disable()
        self.__onChangeControlMode = None
        self.__cam = None
        self.__writeUserPreferences()
        return

    def addModelsToCollideWith(self, models):
        self.__modelsToCollideWith = self.__modelsToCollideWith + models
        if BigWorld.camera() == self.__cam:
            self.__cam.wg_setModelsToCollideWith(self.__modelsToCollideWith)

    def removeModelsToCollideWith(self, models):
        for model in models:
            if self.__modelsToCollideWith.count(model) > 0:
                self.__modelsToCollideWith.remove(model)

        if BigWorld.camera() == self.__cam:
            self.__cam.wg_setModelsToCollideWith(self.__modelsToCollideWith)

    def enable(self, preferredPos=None, yaw=None, closesDist=False, postmortemParams=None):
        camSource = None
        camTarget = None
        camDist = None
        if not self.__postmortemMode:
            camTarget = BigWorld.player().getOwnVehicleMatrix()
            camTargetTransOnly = Math.WGTranslationOnlyMP()
            camTargetTransOnly.source = camTarget
            camTarget = camTargetTransOnly
            if preferredPos is not None and yaw is not None:
                self.__calcStartAngles(camTarget, preferredPos, yaw)
            if closesDist:
                camDist = self.__cfg['distRange'][0]
        elif postmortemParams is not None:
            self.__yaw = postmortemParams[0][0]
            self.__pitch = postmortemParams[0][1]
            camDist = postmortemParams[1]
            camSource = Math.Matrix()
            camSource.setRotateYPR((self.__yaw, self.__pitch, 0))
        else:
            camDist = self.__cfg['distRange'][1]
        if camDist is not None:
            self.__camDist = camDist
            self.__cam.pivotMaxDist = camDist
        if camSource is not None:
            self.__cam.source = camSource
        if camTarget is not None:
            self.__cam.target = camTarget
        self.__cam.wg_setModelsToCollideWith(self.__modelsToCollideWith)
        BigWorld.camera(self.__cam)
        return

    def disable(self):
        self.__cam.wg_setModelsToCollideWith([])
        BigWorld.camera(None)
        if self.__autoUpdateCallbackId is not None:
            BigWorld.cancelCallback(self.__autoUpdateCallbackId)
            self.__autoUpdateCallbackId = None
        return

    def update(self, dx, dy, dz, rotateMode=True, zoomMode=True):
        self.__curSense = self.__cfg['sensitivity']
        self.__curScrollSense = self.__cfg['scrollSensitivity']
        self.__update(dx, dy, dz, rotateMode, zoomMode, False)

    def autoUpdate(self, dx, dy, dz, rotateMode=True, zoomMode=True, onlyOnce=False):
        self.__curSense = self.__cfg['keySensitivity']
        self.__curScrollSense = self.__cfg['keySensitivity']
        if self.__autoUpdateCallbackId is not None:
            BigWorld.cancelCallback(self.__autoUpdateCallbackId)
            self.__autoUpdateCallbackId = None
        if onlyOnce:
            self.__update(dx, dy, dz, rotateMode, zoomMode, False)
        else:
            self.__autoUpdateCallbackId = BigWorld.callback(0.001, partial(self.__update, dx, dy, dz, rotateMode, zoomMode, True))
        return

    def restoreDefaultsState(self):
        self.__camDist = self.__cfg['startDist']
        self.__cam.pivotMaxDist = self.__camDist
        self.__cam.maxDistHalfLife = 0.025
        self.__cam.movementHalfLife = 0.0
        self.__cam.turningHalfLife = 0.025
        self.__pitch = self.__cfg['startAngle']
        self.__yaw = Math.Matrix(self.__cam.target).yaw
        matrix = Math.Matrix()
        matrix.setRotateYPR(self.__updateAngles(0, 0))
        self.__cam.source = matrix

    def getUserConfigValue(self, name):
        return self.__userCfg.get(name)

    def setUserConfigValue(self, name, value):
        if name not in self.__userCfg:
            return
        self.__userCfg[name] = value
        if name not in ('keySensitivity', 'sensitivity', 'scrollSensitivity'):
            self.__cfg[name] = self.__userCfg[name]
        else:
            self.__cfg[name] = self.__baseCfg[name] * self.__userCfg[name]

    def cursorOffset(self, offset):
        self.__cursorOffset = offset

    def setPivotPosition(self, position):
        self.__cam.pivotPosition = position

    def getPivotPosition(self):
        return self.__cam.pivotPosition

    def setCameraDistance(self, distance):
        distRange = self.__cfg['distRange']
        self.__camDist = distance
        self.__camDist = _clamp(distRange[0], distRange[1], self.__camDist)
        self.__cam.pivotMaxDist = self.__camDist

    def getCameraDistance(self):
        return self.__camDist

    def setYawPitch(self, yaw, pitch):
        anglesRange = self.__cfg['angleRange']
        self.__pitch = pitch
        self.__pitch = _clamp(anglesRange[0], anglesRange[1], self.__pitch)
        self.__yaw = yaw
        if self.__yaw > 2.0 * math.pi:
            self.__yaw -= 2.0 * math.pi
        elif self.__yaw < -2.0 * math.pi:
            self.__yaw += 2.0 * math.pi
        matrix = Math.Matrix()
        matrix.setRotateYPR((self.__yaw, self.__pitch, 0))
        self.__cam.source = matrix

    def getYawPitch(self):
        return (self.__yaw, self.__pitch)

    def __calcStartAngles(self, targetMat, preferredPos, yaw):
        rotMat = Math.Matrix()
        rotMat.setRotateY(yaw)
        camDist = self.__camDist
        camPivotPos = self.__cam.pivotPosition
        posOnEntity = Math.Matrix(targetMat).applyPoint(Math.Vector3(0, camPivotPos[1], 0))
        pivotPos = posOnEntity + rotMat.applyPoint(Math.Vector3(camPivotPos[0], 0, camPivotPos[2]))
        dir = preferredPos - pivotPos
        posDir = preferredPos - Math.Matrix(targetMat).applyToOrigin()
        pitch = -posDir.pitch
        yaw = dir.yaw
        try:
            pitch = self.__calcPitchAngle(camDist, dir)
            dist = self.__sceneCheck(yaw, pitch, pivotPos, camDist)
            if dist != 0:
                pitch = self.__calcPitchAngle(dist, dir)
        except:
            LOG_CURRENT_EXCEPTION()

        self.__pitch = pitch
        self.__yaw = yaw
        matrix = Math.Matrix()
        matrix.setRotateYPR(self.__updateAngles(0, 0))
        self.__cam.source = matrix

    def __getRotateAngle(self, vec2f):
        fov = BigWorld.projection().fov
        near = BigWorld.projection().nearPlane
        yLength = near * math.tan(fov * 0.5)
        return math.atan2(yLength * vec2f[1], near)

    def __sceneCheck(self, yaw, pitch, pivotPos, dist):
        dir = _vec3fFromYawPitch(yaw, -pitch)
        start = pivotPos - dir.scale(0.1)
        end = pivotPos - dir.scale(dist)
        colRes = BigWorld.wg_collideSegment(BigWorld.player().spaceID, start, end, 128)
        if colRes is not None:
            return Math.Vector3(colRes[0] - pivotPos).length
        else:
            return 0

    def __calcPitchAngle(self, camDist, dir):
        alpha = self.__getRotateAngle(self.__cursorOffset)
        a = camDist
        b = dir.length
        A = 2.0 * a * math.cos(alpha)
        B = a * a - b * b
        D = A * A - 4.0 * B
        if D > 0.0:
            c1 = (A + math.sqrt(D)) * 0.5
            c2 = (A - math.sqrt(D)) * 0.5
            c = c1 if c1 > c2 else c2
            beta = math.acos((a * a + b * b - c * c) / (2.0 * a * b))
            eta = math.pi - beta
            return -dir.pitch - eta
        else:
            return -dir.pitch

    def __readCfg(self, dataSec):
        if dataSec is None:
            LOG_WARNING('Invalid section <arcadeMode/camera> in avatar_input_handler.xml')
        self.__baseCfg = dict()
        bcfg = self.__baseCfg
        bcfg['keySensitivity'] = readFloat(dataSec, 'keySensitivity', 0, 10, 0.01)
        bcfg['sensitivity'] = readFloat(dataSec, 'sensitivity', 0, 10, 0.01)
        bcfg['scrollSensitivity'] = readFloat(dataSec, 'scrollSensitivity', 0, 10, 0.01)
        bcfg['angleRange'] = readVec2(dataSec, 'angleRange', (0, 0), (180, 180), (10, 110))
        bcfg['distRange'] = readVec2(dataSec, 'distRange', (1, 1), (100, 100), (2, 20))
        bcfg['angleRange'][0] = math.radians(bcfg['angleRange'][0]) - math.pi * 0.5
        bcfg['angleRange'][1] = math.radians(bcfg['angleRange'][1]) - math.pi * 0.5
        ds = Settings.g_instance.userPrefs[Settings.KEY_CONTROL_MODE]
        if ds is not None:
            ds = ds['arcadeMode/camera']
        self.__userCfg = dict()
        ucfg = self.__userCfg
        ucfg['horzInvert'] = readBool(ds, 'horzInvert', False)
        ucfg['vertInvert'] = readBool(ds, 'vertInvert', False)
        ucfg['keySensitivity'] = readFloat(ds, 'keySensitivity', 0.0, 10.0, 0.025)
        ucfg['sensitivity'] = readFloat(ds, 'sensitivity', 0.0, 10.0, 1.0)
        ucfg['scrollSensitivity'] = readFloat(ds, 'scrollSensitivity', 0.0, 10.0, 1.0)
        ucfg['startDist'] = readFloat(ds, 'startDist', 2, 500, 10)
        ucfg['startAngle'] = readFloat(ds, 'startAngle', 5, 180, 60)
        ucfg['startAngle'] = math.radians(ucfg['startAngle']) - math.pi * 0.5
        self.__cfg = dict()
        cfg = self.__cfg
        cfg['keySensitivity'] = bcfg['keySensitivity']
        cfg['sensitivity'] = bcfg['sensitivity']
        cfg['scrollSensitivity'] = bcfg['scrollSensitivity']
        cfg['angleRange'] = bcfg['angleRange']
        cfg['distRange'] = bcfg['distRange']
        cfg['horzInvert'] = ucfg['horzInvert']
        cfg['vertInvert'] = ucfg['vertInvert']
        cfg['keySensitivity'] *= ucfg['keySensitivity']
        cfg['sensitivity'] *= ucfg['sensitivity']
        cfg['scrollSensitivity'] *= ucfg['scrollSensitivity']
        cfg['startDist'] = ucfg['startDist']
        cfg['startAngle'] = ucfg['startAngle']
        return

    def __writeUserPreferences(self):
        ds = Settings.g_instance.userPrefs
        if not ds.has_key(Settings.KEY_CONTROL_MODE):
            ds.write(Settings.KEY_CONTROL_MODE, '')
        ucfg = self.__userCfg
        ds = ds[Settings.KEY_CONTROL_MODE]
        ds.writeBool('arcadeMode/camera/horzInvert', ucfg['horzInvert'])
        ds.writeBool('arcadeMode/camera/vertInvert', ucfg['vertInvert'])
        ds.writeFloat('arcadeMode/camera/keySensitivity', ucfg['keySensitivity'])
        ds.writeFloat('arcadeMode/camera/sensitivity', ucfg['sensitivity'])
        ds.writeFloat('arcadeMode/camera/scrollSensitivity', ucfg['scrollSensitivity'])
        ds.writeFloat('arcadeMode/camera/startDist', ucfg['startDist'])
        ucfg['startAngle'] = math.degrees(ucfg['startAngle'] + math.pi * 0.5)
        ds.writeFloat('arcadeMode/camera/startAngle', ucfg['startAngle'])

    def __updateAngles(self, dx, dy):
        cfg = self.__cfg
        anglesRange = cfg['angleRange']
        offset = 0
        self.__pitch -= dy * self.__curSense * (-1 if cfg['vertInvert'] else 1)
        self.__pitch = _clamp(anglesRange[0] + offset, anglesRange[1] + offset, self.__pitch)
        self.__yaw += dx * self.__curSense * (-1 if cfg['horzInvert'] else 1)
        if self.__yaw > 2.0 * math.pi:
            self.__yaw -= 2.0 * math.pi
        elif self.__yaw < -2.0 * math.pi:
            self.__yaw += 2.0 * math.pi
        return (self.__yaw, self.__pitch, 0)

    def __update(self, dx, dy, dz, rotateMode=True, zoomMode=True, isCallback=False):
        if isCallback:
            self.__autoUpdateCallbackId = BigWorld.callback(0.001, partial(self.__update, dx, dy, dz, rotateMode, zoomMode, True))
        cfg = self.__cfg
        if zoomMode and dz != 0:
            distRange = cfg['distRange']
            prevCam = self.__camDist
            self.__camDist -= dz * float(self.__curScrollSense)
            self.__camDist = _clamp(distRange[0], distRange[1], self.__camDist)
            self.__userCfg['startDist'] = self.__camDist
            if prevCam == self.__camDist and self.__onChangeControlMode is not None:
                if _almostZero(self.__camDist - distRange[0]):
                    self.__onChangeControlMode()
            self.__cam.pivotMaxDist = self.__camDist
        if rotateMode:
            matrix = Math.Matrix()
            matrix.setRotateYPR(self.__updateAngles(dx, dy))
            self.__cam.source = matrix
        return


class StrategicCamera():
    camera = property(lambda self: self.__cam)

    def __init__(self, dataSec):
        self.__readCfg(dataSec)
        self.__cam = BigWorld.CursorCamera()
        self.__requaredHeight = 0.0
        self.__totalMove = Math.Vector3(0, 0, 0)
        self.__yaw = 0.0
        self.__curSense = 0
        self.__autoUpdateCallbackId = None
        self.__onChangeControlMode = None
        return

    def create(self, onChangeControlMode=None):
        self.__onChangeControlMode = onChangeControlMode
        self.__camDist = self.__cfg['camDist']
        self.__cam.pivotMaxDist = 0.0
        self.__cam.maxDistHalfLife = 0.01
        self.__cam.movementHalfLife = 0.0
        self.__cam.turningHalfLife = 0.01
        self.__cam.pivotPosition = Math.Vector3(0.0, self.__camDist, 0.0)

    def destroy(self):
        self.disable()
        self.__onChangeControlMode = None
        self.__cam = None
        self.__writeUserPreferences()
        return

    def enable(self, targetPos, saveDist):
        vPos = BigWorld.player().getOwnVehiclePosition()
        dir = targetPos - vPos
        srcMat = Math.Matrix()
        srcMat.setRotateYPR((0.0, -math.pi * 0.499, 0.0))
        self.__yaw = dir.yaw
        if not saveDist:
            self.__camDist = self.__cfg['camDist']
        self.__totalMove = Math.Vector3(targetPos[0], 0.0, targetPos[2])
        self.__cam.pivotPosition = Math.Vector3(0.0, targetPos[1] + self.__camDist, 0.0)
        self.__update(0, 0, 0, False)
        trgMat = Math.Matrix()
        trgMat.setTranslate(self.__totalMove)
        self.__cam.source = srcMat
        self.__cam.target = trgMat
        BigWorld.camera(self.__cam)
        BigWorld.player().positionControl.moveTo(self.__totalMove)
        BigWorld.player().positionControl.followCamera(True)
        self.__cam.sptHiding = False

    def disable(self):
        BigWorld.camera(None)
        BigWorld.player().positionControl.followCamera(False)
        if self.__autoUpdateCallbackId is not None:
            BigWorld.cancelCallback(self.__autoUpdateCallbackId)
            self.__autoUpdateCallbackId = None
        self.__cam.sptHiding = True
        return

    def teleport(self, pos):
        self.moveToPosition(pos)

    def restoreDefaultsState(self):
        vPos = BigWorld.player().getOwnVehiclePosition()
        self.__totalMove = Math.Vector3(vPos[0], 0.0, vPos[2])
        self.__camDist = self.__cfg['camDist']
        self.__cam.pivotMaxDist = 0.0
        self.__cam.maxDistHalfLife = 0.01
        self.__cam.movementHalfLife = 0.0
        self.__cam.turningHalfLife = 0.01
        self.__cam.pivotPosition = Math.Vector3(0.0, vPos[1] + self.__camDist, 0.0)
        trgMat = Math.Matrix()
        trgMat.setTranslate(self.__totalMove)
        self.__cam.target = trgMat
        BigWorld.player().positionControl.moveTo(self.__totalMove)

    def getUserConfigValue(self, name):
        return self.__userCfg.get(name)

    def setUserConfigValue(self, name, value):
        if name not in self.__userCfg:
            return
        self.__userCfg[name] = value
        if name not in ('keySensitivity', 'sensitivity', 'scrollSensitivity'):
            self.__cfg[name] = self.__userCfg[name]
        else:
            self.__cfg[name] = self.__baseCfg[name] * self.__userCfg[name]

    def update(self, dx, dy, dz):
        self.__curSense = self.__cfg['sensitivity']
        self.__update(dx, dy, dz, False)

    def autoUpdate(self, dx, dy, dz, onlyOnce):
        self.__curSense = self.__cfg['keySensitivity']
        if self.__autoUpdateCallbackId is not None:
            BigWorld.cancelCallback(self.__autoUpdateCallbackId)
            self.__autoUpdateCallbackId = None
        if onlyOnce:
            self.__update(dx, dy, dz, False)
        else:
            self.__autoUpdateCallbackId = BigWorld.callback(0.001, partial(self.__update, dx, dy, dz, True))
        return

    def moveToPosition(self, pos):
        self.__totalMove = pos
        self.update(0.0, 0.0, 0.0)

    def __readCfg(self, dataSec):
        if not dataSec:
            LOG_WARNING('Invalid section <strategicMode/camera> in avatar_input_handler.xml')
        self.__baseCfg = dict()
        bcfg = self.__baseCfg
        bcfg['keySensitivity'] = readFloat(dataSec, 'keySensitivity', 0.005, 10, 0.025)
        bcfg['sensitivity'] = readFloat(dataSec, 'sensitivity', 0.005, 10, 0.025)
        bcfg['scrollSensitivity'] = readFloat(dataSec, 'scrollSensitivity', 0.005, 10, 0.025)
        bcfg['distRange'] = readVec2(dataSec, 'distRange', (1, 1), (100, 100), (2, 30))
        ds = Settings.g_instance.userPrefs[Settings.KEY_CONTROL_MODE]
        if ds is not None:
            ds = ds['strategicMode/camera']
        self.__userCfg = dict()
        ucfg = self.__userCfg
        ucfg['keySensitivity'] = readFloat(ds, 'keySensitivity', 0.0, 10.0, 0.025)
        ucfg['sensitivity'] = readFloat(ds, 'sensitivity', 0.0, 10.0, 1.0)
        ucfg['scrollSensitivity'] = readFloat(ds, 'scrollSensitivity', 0.0, 10.0, 1.0)
        ucfg['camDist'] = readFloat(ds, 'camDist', 40.0, 100.0, bcfg['distRange'][0])
        self.__cfg = dict()
        cfg = self.__cfg
        cfg['keySensitivity'] = bcfg['keySensitivity']
        cfg['sensitivity'] = bcfg['sensitivity']
        cfg['scrollSensitivity'] = bcfg['scrollSensitivity']
        cfg['distRange'] = bcfg['distRange']
        cfg['camDist'] = ucfg['camDist']
        cfg['keySensitivity'] *= ucfg['keySensitivity']
        cfg['sensitivity'] *= ucfg['sensitivity']
        cfg['scrollSensitivity'] *= ucfg['scrollSensitivity']
        return

    def __writeUserPreferences(self):
        ds = Settings.g_instance.userPrefs
        if not ds.has_key(Settings.KEY_CONTROL_MODE):
            ds.write(Settings.KEY_CONTROL_MODE, '')
        ucfg = self.__userCfg
        ds = ds[Settings.KEY_CONTROL_MODE]
        ds.writeFloat('strategicMode/camera/keySensitivity', ucfg['keySensitivity'])
        ds.writeFloat('strategicMode/camera/sensitivity', ucfg['sensitivity'])
        ds.writeFloat('strategicMode/camera/scrollSensitivity', ucfg['scrollSensitivity'])
        ds.writeFloat('strategicMode/camera/camDist', self.__cfg['camDist'])

    def __updateDir(self, dx):
        delta = math.radians(dx * float(self.__curSense))
        self.__yaw += delta
        if self.__yaw < 0.0:
            self.__yaw = math.pi * 2.0 + self.__yaw
        elif self.__yaw > 2.0 * math.pi:
            self.__yaw = 0.0
        rotMat = Math.Matrix()
        rotMat.setRotateY(self.__yaw)
        return rotMat.applyVector(Math.Vector3(0, 0, 1))

    def __move(self, dx, dy):
        move_z = -dy * self.__curSense
        move_x = dx * self.__curSense
        dir = Math.Vector3(move_x, 0.0, move_z)
        matrix = Math.Matrix()
        matrix.setRotateY(Math.Matrix(self.__cam.invViewMatrix).yaw)
        dir = matrix.applyVector(dir)
        length = dir.length
        dir.normalise()
        dir = dir.scale(length)
        destPos = self.__totalMove + dir
        bb = BigWorld.player().arena.typeDescriptor.boundingBox
        pos2D = _clampPoint2DInBox2D(bb[0], bb[1], Math.Vector2(destPos[0], destPos[2]))
        self.__totalMove[0] = pos2D[0]
        self.__totalMove[2] = pos2D[1]
        collPoint = BigWorld.wg_collideSegment(BigWorld.player().spaceID, self.__totalMove + Math.Vector3(0, 250.0, 0), self.__totalMove + Math.Vector3(0, -250.0, 0), 3)
        if collPoint is not None:
            self.__requaredHeight = collPoint[0][1]
        else:
            self.__requaredHeight = 0.0
        matrix.setTranslate(self.__totalMove)
        self.__cam.target = matrix
        return

    def __update(self, dx, dy, dz, isCallback=False):
        if isCallback:
            self.__autoUpdateCallbackId = BigWorld.callback(0.001, partial(self.__update, dx, dy, dz, True))
        self.__move(dx, dy)
        distRange = self.__cfg['distRange']
        self.__camDist -= dz * float(self.__curSense)
        self.__camDist = _clamp(distRange[0], distRange[1], self.__camDist)
        self.__cfg['camDist'] = self.__camDist
        self.__cam.pivotPosition = Math.Vector3(0.0, self.__camDist + self.__requaredHeight, 0.0)
        if dz != 0 and self.__onChangeControlMode is not None:
            if _almostZero(self.__camDist - distRange[0]):
                self.__onChangeControlMode()
        return


class SniperCamera():
    _USE_SWINGING = False
    _USE_ALIGN_TO_VEHICLE = True
    camera = property(lambda self: self.__cam)

    def __init__(self, dataSec):
        self.__readCfg(dataSec)
        self.__cam = BigWorld.FreeCamera()
        self.__angles = [0.0, 0.0]
        self.__dxdydz = [0.0, 0.0, 0.0]
        self.__zoom = self.__cfg['zoom']
        self.__fov = BigWorld.projection().fov
        self.__curSense = 0
        self.__curScrollSense = 0
        self.__autoUpdate = False
        self.__autoUpdateCallbackId = None
        self.__waitVehicleCallbackId = None
        self.__onChangeControlMode = None
        self.__pitchCompensation = 0
        self.__pitchCompensationTimestamp = BigWorld.time()
        return

    def create(self, onChangeControlMode=None):
        self.__onChangeControlMode = onChangeControlMode

    def destroy(self):
        self.disable()
        self.__onChangeControlMode = None
        self.__cam = None
        self.__writeUserPreferences()
        return

    def enable(self, targetPos, saveZoom):
        player = BigWorld.player()
        if not saveZoom:
            self.__zoom = self.__cfg['zoom']
        self.__fov = BigWorld.projection().fov
        self.__dxdydz = [0, 0, 0]
        self.__applyFOV(self.__fov / self.__zoom)
        self.__setupCamera(targetPos)
        vehicle = BigWorld.entity(player.playerVehicleID)
        if vehicle is None:
            self.__whiteVehicleCallbackId = BigWorld.callback(0.1, self.__waitVehicle)
        else:
            self.__showVehicle(False)
        BigWorld.camera(self.__cam)
        self.__cameraUpdate()
        return

    def disable(self):
        BigWorld.camera(None)
        if self.__autoUpdateCallbackId is not None:
            BigWorld.cancelCallback(self.__autoUpdateCallbackId)
            self.__autoUpdateCallbackId = None
        if self.__waitVehicleCallbackId is not None:
            BigWorld.cancelCallback(self.__waitVehicleCallbackId)
            self.__waitVehicleCallbackId = None
        self.__applyFOV(self.__fov)
        self.__showVehicle(True)
        return

    def getUserConfigValue(self, name):
        return self.__userCfg.get(name)

    def setUserConfigValue(self, name, value):
        if name not in self.__userCfg:
            return
        self.__userCfg[name] = value
        if name not in ('keySensitivity', 'sensitivity', 'scrollSensitivity'):
            self.__cfg[name] = self.__userCfg[name]
        else:
            self.__cfg[name] = self.__baseCfg[name] * self.__userCfg[name]

    def update(self, dx, dy, dz, autoUpdate=False):
        self.__curSense = self.__cfg['keySensitivity'] if autoUpdate else self.__cfg['sensitivity']
        self.__curScrollSense = self.__cfg['keySensitivity'] if autoUpdate else self.__cfg['scrollSensitivity']
        self.__curSense *= 1.0 / self.__zoom
        self.__dxdydz = [dx, dy, dz]
        self.__autoUpdate = autoUpdate

    def onRecreateDevice(self):
        curFov = BigWorld.projection().fov
        if curFov != self.__fov and curFov != self.__fov / self.__zoom:
            self.__fov = BigWorld.projection().fov
            self.__applyFOV(self.__fov / self.__zoom)

    def __showVehicle(self, show):
        vehicle = BigWorld.entity(BigWorld.player().playerVehicleID)
        if vehicle is not None and vehicle.isStarted:
            va = vehicle.appearance
            va.changeVisibility('chassis', show, True)
            va.changeVisibility('hull', show, True)
            va.changeVisibility('turret', show, True)
            va.changeVisibility('gun', show, True)
            va.showStickers(show)
        return

    def __setupCamera(self, targetPos):
        player = BigWorld.player()
        desc = player.vehicleTypeDescriptor
        angles = self.__angles
        self.__yawLimits = desc.turret['yawLimits']
        angles[0], angles[1] = getShotAngles(desc, player.getOwnVehicleMatrix(), (0, 0), targetPos, False)
        self.__pitchLimits = calcPitchLimitsFromDesc(angles[0], desc.gun['pitchLimits'])
        gunOffs = desc.turret['gunPosition']
        self.__gunOffsetMat = Math.Matrix()
        self.__gunOffsetMat.setTranslate(gunOffs)
        calc = True
        if self._USE_SWINGING:
            vehicle = BigWorld.entity(player.playerVehicleID)
            if vehicle is not None and vehicle.isStarted:
                self.__turretJointMat = vehicle.appearance.modelsDesc['hull']['model'].node('HP_turretJoint')
                self.__chassisMat = vehicle.matrix
                calc = False
        if calc:
            turretOffs = desc.chassis['hullPosition'] + desc.hull['turretPositions'][0]
            turretOffsetMat = Math.Matrix()
            turretOffsetMat.setTranslate(turretOffs)
            self.__turretJointMat = Math.MatrixProduct()
            self.__turretJointMat.a = turretOffsetMat
            self.__turretJointMat.b = player.getOwnVehicleMatrix()
            self.__chassisMat = player.getOwnVehicleMatrix()
        invGunJointMat = Math.Matrix()
        invGunJointMat.set(self.__gunOffsetMat)
        invGunJointMat.postMultiply(self.__turretJointMat)
        invGunJointMat.invert()
        invTurretJointMat = Math.Matrix(self.__turretJointMat)
        invTurretJointMat.invert()
        gunYawRotateMat = Math.Matrix()
        gunYawRotateMat.setRotateY(angles[0])
        camPosMat = Math.Matrix()
        camPosMat.set(self.__gunOffsetMat)
        camPosMat.postMultiply(gunYawRotateMat)
        camPosMat.postMultiply(self.__turretJointMat)
        camDir = targetPos - camPosMat.applyToOrigin()
        angles[0] = invTurretJointMat.applyVector(camDir).yaw
        angles[1] = invGunJointMat.applyVector(camDir).pitch
        camMat = Math.Matrix()
        if self._USE_ALIGN_TO_VEHICLE:
            up = camPosMat.applyToAxis(1)
        else:
            up = Math.Vector3(0, 1, 0)
        camMat.lookAt(camPosMat.applyToOrigin(), camDir, up)
        self.__cam.set(camMat)
        return

    def __waitVehicle(self):
        vehicle = BigWorld.entity(BigWorld.player().playerVehicleID)
        if vehicle is not None and vehicle.isStarted:
            self.__waitVehicleCallbackId = None
        else:
            self.__waitVehicleCallbackId = BigWorld.callback(0.1, self.__waitVehicle)
            return
        if self._USE_SWINGING:
            self.__turretJointMat = vehicle.appearance.modelsDesc['hull']['model'].node('HP_turretJoint')
            self.__chassisMat = vehicle.matrix
        self.__showVehicle(False)
        return

    def __rotate(self, dx, dy):
        cfg = self.__cfg
        angles = self.__angles
        angles[0] += dx * self.__curSense * (-1 if cfg['horzInvert'] else 1)
        angles[1] += dy * self.__curSense * (-1 if cfg['vertInvert'] else 1)
        if self.__yawLimits is not None:
            angles[0] = _clamp(self.__yawLimits[0], self.__yawLimits[1], angles[0])
        desc = BigWorld.player().vehicleTypeDescriptor
        self.__pitchLimits = calcPitchLimitsFromDesc(angles[0], desc.gun['pitchLimits'])
        chassisMatInv = Math.Matrix(self.__chassisMat)
        chassisMatInv.invert()
        turretJointMat = Math.Matrix(self.__turretJointMat)
        turretJointMat.postMultiply(chassisMatInv)
        pitchDelta = abs(turretJointMat.pitch)
        dTime = min(2.0, BigWorld.time() - self.__pitchCompensationTimestamp)
        self.__pitchCompensation = (dTime * pitchDelta + (2.0 - dTime) * self.__pitchCompensation) * 0.5
        self.__pitchCompensationTimestamp = BigWorld.time()
        pitchLimitsMin = self.__pitchLimits[0] - self.__pitchCompensation
        pitchLimitsMax = self.__pitchLimits[1] + self.__pitchCompensation
        angles[1] = _clamp(pitchLimitsMin, pitchLimitsMax, angles[1])
        return

    def __applyFOV(self, fov):
        BigWorld.projection().fov = fov

    def __setupZoom(self, dz):
        if dz == 0:
            return
        else:
            zooms = self.__cfg['zooms']
            prevZoom = self.__zoom
            if self.__zoom == zooms[0] and dz < 0 and self.__onChangeControlMode is not None:
                self.__onChangeControlMode()
            if dz > 0:
                for elem in zooms:
                    if self.__zoom < elem:
                        self.__zoom = elem
                        self.__cfg['zoom'] = self.__zoom
                        break

            elif dz < 0:
                for i in range(len(zooms) - 1, -1, -1):
                    if self.__zoom > zooms[i]:
                        self.__zoom = zooms[i]
                        self.__cfg['zoom'] = self.__zoom
                        break

            if prevZoom != self.__zoom:
                self.__applyFOV(self.__fov / self.__zoom)
            return

    def __cameraUpdate(self):
        self.__autoUpdateCallbackId = BigWorld.callback(0.0, self.__cameraUpdate)
        self.__setupZoom(self.__dxdydz[2])
        self.__rotate(self.__dxdydz[0], self.__dxdydz[1])
        yawRotateMat = Math.Matrix()
        yawRotateMat.setRotateY(self.__angles[0])
        pitchRotateMat = Math.Matrix()
        pitchRotateMat.setRotateX(self.__angles[1])
        camMat = Math.Matrix()
        camMat.set(pitchRotateMat)
        camMat.postMultiply(self.__gunOffsetMat)
        camMat.postMultiply(yawRotateMat)
        camMat.postMultiply(self.__turretJointMat)
        if not self._USE_ALIGN_TO_VEHICLE:
            pos = camMat.applyToOrigin()
            dir = camMat.applyToAxis(2)
            camMat.lookAt(pos, dir, (0, 1, 0))
        else:
            camMat.invert()
        self.__cam.set(camMat)
        if not self.__autoUpdate:
            self.__dxdydz = [0, 0, 0]

    def __readCfg(self, dataSec):
        if not dataSec:
            LOG_WARNING('Invalid section <sniperMode/camera> in avatar_input_handler.xml')
        self.__baseCfg = dict()
        bcfg = self.__baseCfg
        bcfg['keySensitivity'] = readFloat(dataSec, 'keySensitivity', 0, 10, 0.005)
        bcfg['sensitivity'] = readFloat(dataSec, 'sensitivity', 0, 10, 0.005)
        bcfg['scrollSensitivity'] = readFloat(dataSec, 'scrollSensitivity', 0, 10, 0.005)
        zooms = readVec3(dataSec, 'zooms', (0, 0, 0), (10, 10, 10), (2, 4, 8))
        bcfg['zooms'] = [zooms.x, zooms.y, zooms.z]
        ds = Settings.g_instance.userPrefs[Settings.KEY_CONTROL_MODE]
        if ds is not None:
            ds = ds['sniperMode/camera']
        self.__userCfg = dict()
        ucfg = self.__userCfg
        ucfg['horzInvert'] = readBool(ds, 'horzInvert', False)
        ucfg['vertInvert'] = readBool(ds, 'vertInvert', False)
        ucfg['keySensitivity'] = readFloat(ds, 'keySensitivity', 0.0, 10.0, 0.025)
        ucfg['sensitivity'] = readFloat(ds, 'sensitivity', 0.0, 10.0, 1.0)
        ucfg['scrollSensitivity'] = readFloat(ds, 'scrollSensitivity', 0.0, 10.0, 1.0)
        ucfg['zoom'] = readFloat(ds, 'zoom', 0.0, 10.0, bcfg['zooms'][0])
        self.__cfg = dict()
        cfg = self.__cfg
        cfg['keySensitivity'] = bcfg['keySensitivity']
        cfg['sensitivity'] = bcfg['sensitivity']
        cfg['scrollSensitivity'] = bcfg['scrollSensitivity']
        cfg['zooms'] = bcfg['zooms']
        cfg['keySensitivity'] *= ucfg['keySensitivity']
        cfg['sensitivity'] *= ucfg['sensitivity']
        cfg['scrollSensitivity'] *= ucfg['scrollSensitivity']
        cfg['horzInvert'] = ucfg['horzInvert']
        cfg['vertInvert'] = ucfg['vertInvert']
        cfg['zoom'] = ucfg['zoom']
        return

    def __writeUserPreferences(self):
        ds = Settings.g_instance.userPrefs
        if not ds.has_key(Settings.KEY_CONTROL_MODE):
            ds.write(Settings.KEY_CONTROL_MODE, '')
        ucfg = self.__userCfg
        ds = ds[Settings.KEY_CONTROL_MODE]
        ds.writeBool('sniperMode/camera/horzInvert', ucfg['horzInvert'])
        ds.writeBool('sniperMode/camera/vertInvert', ucfg['vertInvert'])
        ds.writeFloat('sniperMode/camera/keySensitivity', ucfg['keySensitivity'])
        ds.writeFloat('sniperMode/camera/sensitivity', ucfg['sensitivity'])
        ds.writeFloat('sniperMode/camera/scrollSensitivity', ucfg['scrollSensitivity'])
        ds.writeFloat('sniperMode/camera/zoom', self.__cfg['zoom'])


class FreeCamera():
    camera = property(lambda self: self.__cam)

    def __init__(self):
        self.__cam = BigWorld.FreeCamera()

    def create(self):
        pass

    def destroy(self):
        self.__cam = None
        return

    def enable(self, camMat=None):
        if camMat is not None:
            self.__cam.set(camMat)
        BigWorld.camera(self.__cam)
        return

    def disable(self):
        BigWorld.camera(None)
        return

    def setWorldMatrix(self, matrix):
        matrix = Math.Matrix(matrix)
        matrix.invert()
        self.__cam.set(matrix)

    def getWorldMatrix(self):
        return Math.Matrix(self.__cam.invViewMatrix)

    def handleKey(self, event):
        return self.__cam.handleKeyEvent(event)

    def handleMouse(self, dx, dy, dz):
        return self.__cam.handleMouseEvent(BigWorld.MouseEvent(dx, dy, dz, (0, 0)))


def readBool(dataSec, name, defaultVal):
    if dataSec is None:
        return defaultVal
    else:
        return dataSec.readBool(name, defaultVal)


def readFloat(dataSec, name, minVal, maxVal, defaultVal):
    if dataSec is None:
        return defaultVal
    else:
        value = dataSec.readFloat(name, defaultVal)
        value = _clamp(minVal, maxVal, value)
        return value


def readVec2(dataSec, name, minVal, maxVal, defaultVal):
    if dataSec is None:
        return Math.Vector2(defaultVal)
    else:
        value = dataSec.readVector2(name, Math.Vector2(defaultVal))
        for i in xrange(2):
            value[i] = _clamp(minVal[i], maxVal[i], value[i])

        return value


def readVec3(dataSec, name, minVal, maxVal, defaultVal):
    if dataSec is None:
        return Math.Vector3(defaultVal)
    else:
        value = dataSec.readVector3(name, Math.Vector3(defaultVal))
        for i in xrange(3):
            value[i] = _clamp(minVal[i], maxVal[i], value[i])

        return value


def getScreenAspectRatio():
    if BigWorld.isVideoWindowed():
        size = BigWorld.screenSize()
        return size[0] / size[1]
    else:
        return BigWorld.getFullScreenAspectRatio()


def getWorldRayAndPoint(x, y):
    fov = BigWorld.projection().fov
    near = BigWorld.projection().nearPlane
    aspect = getScreenAspectRatio()
    yLength = near * math.tan(fov * 0.5)
    xLength = yLength * aspect
    point = Math.Vector3(xLength * x, yLength * y, near)
    inv = Math.Matrix(BigWorld.camera().invViewMatrix)
    ray = inv.applyVector(point)
    wPoint = inv.applyPoint(point)
    return (ray, wPoint)


def _clampPoint2DInBox2D(bottomLeft, upperRight, point):
    retPoint = Math.Vector2(0, 0)
    retPoint[0] = max(bottomLeft[0], point[0])
    retPoint[0] = min(retPoint[0], upperRight[0])
    retPoint[1] = max(bottomLeft[1], point[1])
    retPoint[1] = min(retPoint[1], upperRight[1])
    return retPoint


def _almostZero(val, epsilon=0.0004):
    return -epsilon < val < epsilon


def _clamp(minVal, maxVal, val):
    tmpVal = val
    tmpVal = max(minVal, val)
    tmpVal = min(maxVal, tmpVal)
    return tmpVal


def _vec3fFromYawPitch(yaw, pitch):
    cosPitch = math.cos(+pitch)
    sinPitch = math.sin(-pitch)
    cosYaw = math.cos(yaw)
    sinYaw = math.sin(yaw)
    return Math.Vector3(cosPitch * sinYaw, sinPitch, cosPitch * cosYaw)
