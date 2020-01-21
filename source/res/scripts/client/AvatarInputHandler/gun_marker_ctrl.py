# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/AvatarInputHandler/gun_marker_ctrl.py
import logging
import math
from collections import namedtuple
import BattleReplay
import BigWorld
import GUI
import Math
import constants
import aih_constants
from AvatarInputHandler import AimingSystems
from AvatarInputHandler import aih_global_binding
from helpers import dependency
from helpers.CallbackDelayer import CallbackDelayer
from skeletons.account_helpers.settings_core import ISettingsCore
_MARKER_TYPE = aih_constants.GUN_MARKER_TYPE
_MARKER_FLAG = aih_constants.GUN_MARKER_FLAG
_SHOT_RESULT = aih_constants.SHOT_RESULT
_BINDING_ID = aih_global_binding.BINDING_ID
_IS_EXTENDED_GUN_MARKER_ENABLED = True
_MIN_PIERCING_DIST = 100.0
_MAX_PIERCING_DIST = 500.0
_LERP_RANGE_PIERCING_DIST = _MAX_PIERCING_DIST - _MIN_PIERCING_DIST
_BASE_PIERCING_PERCENT = 100.0
_ENABLED_MAX_PROJECTION_CHECK = True
_MAX_PROJECTION_ANGLE = math.radians(60.0)
_MAX_PROJECTION_ANGLE_COS = math.cos(_MAX_PROJECTION_ANGLE)
_logger = logging.getLogger(__name__)

def _computePiercingPowerAtDistImpl(dist, maxDist, p100, p500):
    if dist <= _MIN_PIERCING_DIST:
        return p100
    if dist < maxDist:
        power = p100 + (p500 - p100) * (dist - _MIN_PIERCING_DIST) / _LERP_RANGE_PIERCING_DIST
        if power > 0.0:
            return power
        return 0.0


def _computePiercingPowerRandomizationImpl(piercingPowerRandomization, minimum, maximum):
    minPP = _BASE_PIERCING_PERCENT * (1.0 - piercingPowerRandomization * minimum)
    maxPP = _BASE_PIERCING_PERCENT * (1.0 + piercingPowerRandomization * maximum)
    return (minPP, maxPP)


def useServerGunMarker():
    replayCtrl = BattleReplay.g_replayCtrl
    if replayCtrl.isPlaying:
        return False
    settingsCore = dependency.instance(ISettingsCore)
    return settingsCore.getSetting('useServerAim')


def useClientGunMarker():
    return constants.HAS_DEV_RESOURCES or not useServerGunMarker()


def useDefaultGunMarkers():
    from gui import GUI_SETTINGS
    return not constants.HAS_DEV_RESOURCES or GUI_SETTINGS.useDefaultGunMarkers


def createGunMarker(isStrategic):
    factory = _GunMarkersDPFactory()
    if isStrategic:
        clientMarker = _SPGGunMarkerController(_MARKER_TYPE.CLIENT, factory.getClientSPGProvider())
        serverMarker = _SPGGunMarkerController(_MARKER_TYPE.SERVER, factory.getServerSPGProvider())
    else:
        clientMarker = _DefaultGunMarkerController(_MARKER_TYPE.CLIENT, factory.getClientProvider())
        serverMarker = _DefaultGunMarkerController(_MARKER_TYPE.SERVER, factory.getServerProvider())
    return _GunMarkersDecorator(clientMarker, serverMarker)


def createArtyHit(artyEquipmentUDO, areaRadius):
    factory = _GunMarkersDPFactory()
    return _ArtyHitMarkerController(_MARKER_TYPE.CLIENT, factory.getClientSPGProvider(), artyEquipmentUDO, areaRadius, interval=0.0 if BattleReplay.g_replayCtrl.isPlaying else 0.1)


if _IS_EXTENDED_GUN_MARKER_ENABLED:

    def createShotResultResolver():
        return _CrosshairShotResults


else:

    def createShotResultResolver():
        return _StandardShotResult


class _StandardShotResult(object):

    @classmethod
    def getShotResult(cls, hitPoint, collision, _, excludeTeam=0):
        if collision is None:
            return _SHOT_RESULT.UNDEFINED
        else:
            entity = collision.entity
            if entity.health <= 0 or entity.publicInfo['team'] == excludeTeam:
                return _SHOT_RESULT.UNDEFINED
            player = BigWorld.player()
            if player is None:
                return _SHOT_RESULT.UNDEFINED
            vDesc = player.getVehicleDescriptor()
            ppDesc = vDesc.shot.piercingPower
            maxDist = vDesc.shot.maxDistance
            dist = (hitPoint - player.getOwnVehiclePosition()).length
            if dist <= 100.0:
                piercingPower = ppDesc[0]
            elif maxDist > dist:
                p100, p500 = ppDesc
                piercingPower = p100 + (p500 - p100) * (dist - 100.0) / 400.0
                if piercingPower < 0.0:
                    piercingPower = 0.0
            else:
                piercingPower = 0.0
            piercingPercent = 1000.0
            if piercingPower > 0.0:
                armor = collision.armor
                piercingPercent = 100.0 + (armor - piercingPower) / piercingPower * 100.0
            if piercingPercent >= 150:
                result = _SHOT_RESULT.NOT_PIERCED
            elif 90 < piercingPercent < 150:
                result = _SHOT_RESULT.LITTLE_PIERCED
            else:
                result = _SHOT_RESULT.GREAT_PIERCED
            return result


class _CrosshairShotResults(object):
    _PP_RANDOM_ADJUSTMENT_MAX = 0.5
    _PP_RANDOM_ADJUSTMENT_MIN = 0.5
    _MAX_HIT_ANGLE_BOUND = math.pi / 2.0 - 1e-05
    _CRIT_ONLY_SHOT_RESULT = _SHOT_RESULT.NOT_PIERCED
    shellExtraData = namedtuple('shellExtraData', ('normAngle', 'ricochetAngle', 'mayRicochet', 'checkCaliberForRicochet', 'jetLossPPByDist'))
    _SHELL_EXTRA_DATA = {constants.SHELL_TYPES.ARMOR_PIERCING: shellExtraData(math.radians(5.0), math.cos(math.radians(70.0)), True, True, 0.0),
     constants.SHELL_TYPES.ARMOR_PIERCING_CR: shellExtraData(math.radians(2.0), math.cos(math.radians(70.0)), True, True, 0.0),
     constants.SHELL_TYPES.ARMOR_PIERCING_HE: shellExtraData(0.0, 0.0, False, False, 0.0),
     constants.SHELL_TYPES.HOLLOW_CHARGE: shellExtraData(0.0, math.cos(math.radians(85.0)), True, False, 0.5),
     constants.SHELL_TYPES.HIGH_EXPLOSIVE: shellExtraData(0.0, 0.0, False, False, 0.0)}
    _VEHICLE_TRACE_BACKWARD_LENGTH = 0.1
    _VEHICLE_TRACE_FORWARD_LENGTH = 20.0

    @classmethod
    def _computePiercingPowerAtDist(cls, ppDesc, dist, maxDist):
        p100, p500 = ppDesc
        return _computePiercingPowerAtDistImpl(dist, maxDist, p100, p500)

    @classmethod
    def _computePiercingPowerRandomization(cls, shell):
        piercingPowerRandomization = shell.piercingPowerRandomization
        return _computePiercingPowerRandomizationImpl(piercingPowerRandomization, cls._PP_RANDOM_ADJUSTMENT_MIN, cls._PP_RANDOM_ADJUSTMENT_MAX)

    @classmethod
    def _shouldRicochet(cls, shellKind, hitAngleCos, matInfo, caliber):
        if not matInfo.mayRicochet:
            return False
        shellExtraData = cls._SHELL_EXTRA_DATA[shellKind]
        if not shellExtraData.mayRicochet:
            return False
        if hitAngleCos <= shellExtraData.ricochetAngle:
            if not matInfo.checkCaliberForRichet:
                return True
            if not shellExtraData.checkCaliberForRicochet:
                return True
            armor = matInfo.armor
            if armor * 3 >= caliber:
                return True
        return False

    @classmethod
    def _computePenetrationArmor(cls, shellKind, hitAngleCos, matInfo, caliber):
        armor = matInfo.armor
        if not matInfo.useHitAngle:
            return armor
        normalizationAngle = cls._SHELL_EXTRA_DATA[shellKind].normAngle
        if normalizationAngle > 0.0 and hitAngleCos < 1.0:
            if matInfo.checkCaliberForHitAngleNorm:
                if caliber > armor * 2 > 0:
                    normalizationAngle *= 1.4 * caliber / (armor * 2)
            hitAngle = math.acos(hitAngleCos) - normalizationAngle
            if hitAngle < 0.0:
                hitAngleCos = 1.0
            else:
                if hitAngle > cls._MAX_HIT_ANGLE_BOUND:
                    hitAngle = cls._MAX_HIT_ANGLE_BOUND
                hitAngleCos = math.cos(hitAngle)
        if hitAngleCos < 1e-05:
            hitAngleCos = 1e-05
        return armor / hitAngleCos

    @classmethod
    def _getAllCollisionDetails(cls, hitPoint, direction, entity):
        startPoint = hitPoint - direction * cls._VEHICLE_TRACE_BACKWARD_LENGTH
        endPoint = hitPoint + direction * cls._VEHICLE_TRACE_FORWARD_LENGTH
        return entity.collideSegmentExt(startPoint, endPoint)

    @classmethod
    def getShotResult(cls, hitPoint, collision, direction, excludeTeam=0):
        if collision is None:
            return _SHOT_RESULT.UNDEFINED
        else:
            entity = collision.entity
            if entity.__class__.__name__ not in ('Vehicle', 'DestructibleEntity'):
                return _SHOT_RESULT.UNDEFINED
            if entity.health <= 0 or entity.publicInfo['team'] == excludeTeam:
                return _SHOT_RESULT.UNDEFINED
            player = BigWorld.player()
            if player is None:
                return _SHOT_RESULT.UNDEFINED
            vDesc = player.getVehicleDescriptor()
            shell = vDesc.shot.shell
            caliber = shell.caliber
            shellKind = shell.kind
            ppDesc = vDesc.shot.piercingPower
            maxDist = vDesc.shot.maxDistance
            dist = (hitPoint - player.getOwnVehiclePosition()).length
            piercingPower = cls._computePiercingPowerAtDist(ppDesc, dist, maxDist)
            fullPiercingPower = piercingPower
            minPP, maxPP = cls._computePiercingPowerRandomization(shell)
            result = _SHOT_RESULT.NOT_PIERCED
            isJet = False
            jetStartDist = None
            ignoredMaterials = set()
            collisionsDetails = cls._getAllCollisionDetails(hitPoint, direction, entity)
            if collisionsDetails is None:
                return _SHOT_RESULT.UNDEFINED
            for cDetails in collisionsDetails:
                if isJet:
                    jetDist = cDetails.dist - jetStartDist
                    if jetDist > 0.0:
                        piercingPower *= 1.0 - jetDist * cls._SHELL_EXTRA_DATA[shellKind].jetLossPPByDist
                if cDetails.matInfo is None:
                    result = cls._CRIT_ONLY_SHOT_RESULT
                else:
                    matInfo = cDetails.matInfo
                    if (cDetails.compName, matInfo.kind) in ignoredMaterials:
                        continue
                    hitAngleCos = cDetails.hitAngleCos if matInfo.useHitAngle else 1.0
                    if not isJet and cls._shouldRicochet(shellKind, hitAngleCos, matInfo, caliber):
                        break
                    piercingPercent = 1000.0
                    if piercingPower > 0.0:
                        penetrationArmor = cls._computePenetrationArmor(shellKind, hitAngleCos, matInfo, caliber)
                        piercingPercent = 100.0 + (penetrationArmor - piercingPower) / fullPiercingPower * 100.0
                        piercingPower -= penetrationArmor
                    if matInfo.vehicleDamageFactor:
                        if minPP < piercingPercent < maxPP:
                            result = _SHOT_RESULT.LITTLE_PIERCED
                        elif piercingPercent <= minPP:
                            result = _SHOT_RESULT.GREAT_PIERCED
                        break
                    elif matInfo.extra:
                        if piercingPercent <= maxPP:
                            result = cls._CRIT_ONLY_SHOT_RESULT
                    if matInfo.collideOnceOnly:
                        ignoredMaterials.add((cDetails.compName, matInfo.kind))
                if piercingPower <= 0.0:
                    break
                if cls._SHELL_EXTRA_DATA[shellKind].jetLossPPByDist > 0.0:
                    isJet = True
                    mInfo = cDetails.matInfo
                    armor = mInfo.armor if mInfo is not None else 0.0
                    jetStartDist = cDetails.dist + armor * 0.001

            return result


def _setupGunMarkerSizeLimits(dataProvider, scale=None):
    if scale is None:
        settingsCore = dependency.instance(ISettingsCore)
        scale = settingsCore.interfaceScale.get()
    limits = (aih_constants.GUN_MARKER_MIN_SIZE * scale, min(GUI.screenResolution()))
    dataProvider.sizeConstraint = limits
    return limits


class _SizeFilter(object):

    def __init__(self):
        self.__outSize = 0.0
        self.__inSize = 0.0
        self.__k = 0.0
        self.__minLimit = 0.0

    def getSize(self):
        return self.__outSize

    def setStartSize(self, startSize):
        self.__outSize = self.__inSize = startSize

    def setMinLimit(self, minLimit):
        self.__minLimit = minLimit
        self.__k = 0.0

    def update(self, inSize, ideal):
        if inSize >= self.__inSize or self.__minLimit <= ideal:
            self.__outSize = self.__inSize = inSize
            self.__k = 0.0
            return
        if self.__k == 0.0 and inSize != ideal:
            self.__k = (inSize - self.__minLimit) / (inSize - ideal)
        self.__inSize = inSize
        self.__outSize = self.__minLimit + self.__k * (self.__inSize - ideal)


class IGunMarkerController(object):

    def create(self):
        raise NotImplementedError

    def destroy(self):
        raise NotImplementedError

    def enable(self):
        raise NotImplementedError

    def disable(self):
        raise NotImplementedError

    def reset(self):
        raise NotImplementedError

    def update(self, markerType, position, direction, size, relaxTime, collData):
        raise NotImplementedError

    def setFlag(self, positive, bit):
        raise NotImplementedError

    def getPosition(self):
        raise NotImplementedError

    def setPosition(self, position):
        raise NotImplementedError

    def setVisible(self, flag):
        raise NotImplementedError

    def onRecreateDevice(self):
        raise NotImplementedError

    def getSize(self):
        raise NotImplementedError

    def setSize(self, newSize):
        raise NotImplementedError


class _GunMarkersDPFactory(object):
    __clientDataProvider = aih_global_binding.bindRW(_BINDING_ID.CLIENT_GUN_MARKER_DATA_PROVIDER)
    __serverDataProvider = aih_global_binding.bindRW(_BINDING_ID.SERVER_GUN_MARKER_DATA_PROVIDER)
    __clientSPGDataProvider = aih_global_binding.bindRW(_BINDING_ID.CLIENT_SPG_GUN_MARKER_DATA_PROVIDER)
    __serverSPGDataProvider = aih_global_binding.bindRW(_BINDING_ID.SERVER_SPG_GUN_MARKER_DATA_PROVIDER)

    def getClientProvider(self):
        if self.__clientDataProvider is None:
            self.__clientDataProvider = self._makeDefaultProvider()
        return self.__clientDataProvider

    def getServerProvider(self):
        if self.__serverDataProvider is None:
            self.__serverDataProvider = self._makeDefaultProvider()
        return self.__serverDataProvider

    def getClientSPGProvider(self):
        if self.__clientSPGDataProvider is None:
            self.__clientSPGDataProvider = self._makeSPGProvider()
        return self.__clientSPGDataProvider

    def getServerSPGProvider(self):
        if self.__serverSPGDataProvider is None:
            self.__serverSPGDataProvider = self._makeSPGProvider()
        return self.__serverSPGDataProvider

    @staticmethod
    def _makeDefaultProvider():
        dataProvider = GUI.WGGunMarkerDataProvider()
        dataProvider.positionMatrixProvider = Math.MatrixAnimation()
        dataProvider.setStartSize(_setupGunMarkerSizeLimits(dataProvider)[0])
        return dataProvider

    @staticmethod
    def _makeSPGProvider():
        dataProvider = GUI.WGSPGGunMarkerDataProvider(aih_constants.SPG_GUN_MARKER_ELEMENTS_COUNT, aih_constants.SPG_GUN_MARKER_ELEMENTS_RATE)
        dataProvider.positionMatrixProvider = Math.MatrixAnimation()
        dataProvider.maxTime = 5.0
        dataProvider.serverTickLength = constants.SERVER_TICK_LENGTH
        dataProvider.sizeScaleRate = aih_constants.SPG_GUN_MARKER_SCALE_RATE
        dataProvider.sizeConstraint = (aih_constants.SPG_GUN_MARKER_MIN_SIZE, aih_constants.SPG_GUN_MARKER_MAX_SIZE)
        dataProvider.setRelaxTime(constants.SERVER_TICK_LENGTH)
        return dataProvider


class _GunMarkersDecorator(IGunMarkerController):
    __gunMarkersFlags = aih_global_binding.bindRW(_BINDING_ID.GUN_MARKERS_FLAGS)
    __clientState = aih_global_binding.bindRW(_BINDING_ID.CLIENT_GUN_MARKER_STATE)
    __serverState = aih_global_binding.bindRW(_BINDING_ID.SERVER_GUN_MARKER_STATE)

    def __init__(self, clientMarker, serverMarker):
        super(_GunMarkersDecorator, self).__init__()
        self.__clientMarker = clientMarker
        self.__serverMarker = serverMarker

    def create(self):
        self.__clientMarker.create()
        self.__serverMarker.create()

    def destroy(self):
        self.__clientMarker.destroy()
        self.__serverMarker.destroy()

    def enable(self):
        self.__clientMarker.enable()
        self.__clientMarker.setPosition(self.__clientState[0])
        self.__serverMarker.enable()
        self.__serverMarker.setPosition(self.__serverState[0])

    def disable(self):
        self.__clientMarker.disable()
        self.__serverMarker.disable()

    def reset(self):
        self.__clientMarker.reset()
        self.__serverMarker.reset()

    def onRecreateDevice(self):
        self.__clientMarker.onRecreateDevice()
        self.__serverMarker.onRecreateDevice()

    def getPosition(self, markerType=_MARKER_TYPE.CLIENT):
        if markerType == _MARKER_TYPE.CLIENT:
            return self.__clientMarker.getPosition()
        if markerType == _MARKER_TYPE.SERVER:
            return self.__serverMarker.getPosition()
        _logger.warning('Gun maker control is not found by type: %d', markerType)
        return Math.Vector3()

    def setPosition(self, position, markerType=_MARKER_TYPE.CLIENT):
        if markerType == _MARKER_TYPE.CLIENT:
            self.__clientMarker.setPosition(position)
        elif markerType == _MARKER_TYPE.SERVER:
            self.__serverMarker.setPosition(position)
        else:
            _logger.warning('Gun maker control is not found by type: %d', markerType)

    def setFlag(self, positive, bit):
        if positive:
            self.__gunMarkersFlags |= bit
            if bit == _MARKER_FLAG.SERVER_MODE_ENABLED:
                self.__serverMarker.setPosition(self.__clientMarker.getPosition())
                self.__serverMarker.setSize(self.__clientMarker.getSize())
        else:
            self.__gunMarkersFlags &= ~bit

    def update(self, markerType, position, direction, size, relaxTime, collData):
        if markerType == _MARKER_TYPE.CLIENT:
            self.__clientState = (position, direction, collData)
            if self.__gunMarkersFlags & _MARKER_FLAG.CLIENT_MODE_ENABLED:
                self.__clientMarker.update(markerType, position, direction, size, relaxTime, collData)
        elif markerType == _MARKER_TYPE.SERVER:
            self.__serverState = (position, direction, collData)
            if self.__gunMarkersFlags & _MARKER_FLAG.SERVER_MODE_ENABLED:
                self.__serverMarker.update(markerType, position, direction, size, relaxTime, collData)
        else:
            _logger.warning('Gun maker control is not found by type: %d', markerType)

    def setVisible(self, flag):
        pass

    def getSize(self):
        pass

    def setSize(self, newSize):
        pass


class _GunMarkerController(IGunMarkerController):
    _gunMarkersFlags = aih_global_binding.bindRW(_BINDING_ID.GUN_MARKERS_FLAGS)

    def __init__(self, gunMakerType, dataProvider, enabledFlag=_MARKER_FLAG.UNDEFINED):
        super(_GunMarkerController, self).__init__()
        self._gunMarkerType = gunMakerType
        self._dataProvider = dataProvider
        self._enabledFlag = enabledFlag
        self._position = Math.Vector3()

    def create(self):
        pass

    def destroy(self):
        self._dataProvider = None
        return

    def enable(self):
        if self._enabledFlag != _MARKER_FLAG.UNDEFINED:
            self.setFlag(True, self._enabledFlag)

    def disable(self):
        if self._enabledFlag != _MARKER_FLAG.UNDEFINED:
            self.setFlag(False, self._enabledFlag)

    def reset(self):
        pass

    def update(self, markerType, position, direction, size, relaxTime, collData):
        if self._gunMarkerType == markerType:
            self._position = position
        else:
            _logger.warning('Position can not be defined, type of marker does not equal: required = %d, received = %d', self._gunMarkerType, markerType)

    def setFlag(self, positive, bit):
        if positive:
            self._gunMarkersFlags |= bit
        else:
            self._gunMarkersFlags &= ~bit

    def onRecreateDevice(self):
        pass

    def getPosition(self):
        return self._position

    def setPosition(self, position):
        self._position = position
        positionMatrix = Math.Matrix()
        positionMatrix.setTranslate(position)
        self._updateMatrixProvider(positionMatrix)

    def setVisible(self, flag):
        pass

    def getSize(self):
        pass

    def setSize(self, newSize):
        pass

    def _updateMatrixProvider(self, positionMatrix, relaxTime=0.0):
        animationMatrix = self._dataProvider.positionMatrixProvider
        animationMatrix.keyframes = ((0.0, Math.Matrix(animationMatrix)), (relaxTime, positionMatrix))
        animationMatrix.time = 0.0


class _DefaultGunMarkerController(_GunMarkerController):
    settingsCore = dependency.descriptor(ISettingsCore)

    def __init__(self, gunMakerType, dataProvider, enabledFlag=_MARKER_FLAG.UNDEFINED):
        super(_DefaultGunMarkerController, self).__init__(gunMakerType, dataProvider, enabledFlag=enabledFlag)
        self.__replSwitchTime = 0.0
        self.__sizeFilter = _SizeFilter()
        self.__curSize = 0.0
        self.__screenRatio = 0.0

    def create(self):
        minSize = self._dataProvider.sizeConstraint[0]
        self.__sizeFilter.setStartSize(minSize)
        self.__sizeFilter.setMinLimit(0)
        self.settingsCore.interfaceScale.onScaleChanged += self.__onScaleChanged

    def destroy(self):
        self.settingsCore.interfaceScale.onScaleChanged -= self.__onScaleChanged
        super(_DefaultGunMarkerController, self).destroy()

    def enable(self):
        super(_DefaultGunMarkerController, self).enable()
        self.__updateScreenRatio()
        replayCtrl = BattleReplay.g_replayCtrl
        if replayCtrl.isPlaying and replayCtrl.isClientReady:
            self.__replSwitchTime = 0.2

    def update(self, markerType, pos, direction, sizeVector, relaxTime, collData):
        super(_DefaultGunMarkerController, self).update(markerType, pos, direction, sizeVector, relaxTime, collData)
        positionMatrix = Math.Matrix()
        positionMatrix.setTranslate(pos)
        self._updateMatrixProvider(positionMatrix, relaxTime)
        size = sizeVector[0]
        idealSize = sizeVector[1]
        replayCtrl = BattleReplay.g_replayCtrl
        if replayCtrl.isPlaying and replayCtrl.isClientReady:
            s = replayCtrl.getArcadeGunMarkerSize()
            if s != -1.0:
                size = s
        elif replayCtrl.isRecording:
            if replayCtrl.isServerAim and self._gunMarkerType == _MARKER_TYPE.SERVER:
                replayCtrl.setArcadeGunMarkerSize(size)
            elif self._gunMarkerType == _MARKER_TYPE.CLIENT:
                replayCtrl.setArcadeGunMarkerSize(size)
        positionMatrixForScale = self.__checkAndRecalculateIfPositionInExtremeProjection(positionMatrix)
        worldMatrix = _makeWorldMatrix(positionMatrixForScale)
        currentSize = _calcScale(worldMatrix, size) * self.__screenRatio
        idealSize = _calcScale(worldMatrix, idealSize) * self.__screenRatio
        self.__sizeFilter.update(currentSize, idealSize)
        self.__curSize = self.__sizeFilter.getSize()
        if self.__replSwitchTime > 0.0:
            self.__replSwitchTime -= relaxTime
            self._dataProvider.updateSize(self.__curSize, 0.0)
        else:
            self._dataProvider.updateSize(self.__curSize, relaxTime)

    def getSize(self):
        return self.__curSize

    def setSize(self, newSize):
        self.__curSize = newSize
        self._dataProvider.setStartSize(newSize)

    def onRecreateDevice(self):
        self.__updateScreenRatio()

    def __updateScreenRatio(self):
        self.__screenRatio = GUI.screenResolution()[0] * 0.5

    def __onScaleChanged(self, scale):
        _setupGunMarkerSizeLimits(self._dataProvider, scale=scale)

    def __checkAndRecalculateIfPositionInExtremeProjection(self, positionMatrix):
        if not _ENABLED_MAX_PROJECTION_CHECK:
            return positionMatrix
        camera = BigWorld.camera()
        cameraDirection = camera.direction
        cameraPosition = camera.position
        shotDirection = positionMatrix.applyToOrigin() - cameraPosition
        shotDistance = shotDirection.length
        shotDirection.normalise()
        dotProduct = cameraDirection.dot(shotDirection)
        if -_MAX_PROJECTION_ANGLE_COS < dotProduct < _MAX_PROJECTION_ANGLE_COS:
            rotationMatrix = Math.Matrix()
            rotationMatrix.setRotateY(_MAX_PROJECTION_ANGLE_COS)
            rotationMatrix.postMultiply(BigWorld.camera().invViewMatrix)
            newShotDirection = rotationMatrix.applyToAxis(2)
            newShotPosition = cameraPosition + shotDistance * newShotDirection
            positionMatrix = Math.Matrix()
            positionMatrix.setTranslate(newShotPosition)
        return positionMatrix


class _SPGGunMarkerController(_GunMarkerController):

    def __init__(self, gunMakerType, dataProvider, enabledFlag=_MARKER_FLAG.UNDEFINED):
        super(_SPGGunMarkerController, self).__init__(gunMakerType, dataProvider, enabledFlag=enabledFlag)
        self._size = 0.0
        self._gunRotator = None
        self._shotSpeed = 0
        self._shotGravity = 0
        return

    def enable(self):
        super(_SPGGunMarkerController, self).enable()
        player = BigWorld.player()
        self._gunRotator = player.gunRotator
        shotDescr = player.getVehicleDescriptor().shot
        self._shotSpeed = shotDescr.speed
        self._shotGravity = shotDescr.gravity

    def disable(self):
        self._gunRotator = None
        self._shotSpeed = 0.0
        self._shotGravity = 0.0
        super(_SPGGunMarkerController, self).disable()
        return

    def update(self, markerType, position, direction, size, relaxTime, collData):
        super(_SPGGunMarkerController, self).update(markerType, position, direction, size, relaxTime, collData)
        positionMatrix = Math.Matrix()
        positionMatrix.setTranslate(position)
        self._updateMatrixProvider(positionMatrix, relaxTime)
        self._size = size[0]
        self._update()

    def reset(self):
        self._dataProvider.reset()
        self._update()

    def _getCurrentShotInfo(self):
        gunMat = AimingSystems.getPlayerGunMat(self._gunRotator.turretYaw, self._gunRotator.gunPitch)
        position = gunMat.translation
        velocity = gunMat.applyVector(Math.Vector3(0, 0, self._shotSpeed))
        return (position, velocity, Math.Vector3(0, -self._shotGravity, 0))

    def _updateDispersionData(self):
        dispersionAngle = self._gunRotator.dispersionAngle
        isServerAim = self._gunMarkerType == _MARKER_TYPE.SERVER
        replayCtrl = BattleReplay.g_replayCtrl
        if replayCtrl.isPlaying and replayCtrl.isClientReady:
            d, s = replayCtrl.getSPGGunMarkerParams()
            if d != -1.0 and s != -1.0:
                dispersionAngle = d
        elif replayCtrl.isRecording:
            if replayCtrl.isServerAim and isServerAim:
                replayCtrl.setSPGGunMarkerParams(dispersionAngle, 0.0)
            elif not isServerAim:
                replayCtrl.setSPGGunMarkerParams(dispersionAngle, 0.0)
        self._dataProvider.setupConicDispersion(dispersionAngle)

    def _update(self):
        pos3d, vel3d, gravity3d = self._getCurrentShotInfo()
        self._updateDispersionData()
        self._dataProvider.update(pos3d, vel3d, gravity3d, self._size)


class _ArtyHitMarkerController(_SPGGunMarkerController):

    def __init__(self, gunMakerType, dataProvider, artyEquipmentUDO, areaRadius, interval=0.1):
        super(_ArtyHitMarkerController, self).__init__(gunMakerType, dataProvider, enabledFlag=_MARKER_FLAG.ARTY_HIT_ENABLED)
        self.__artyEquipmentUDO = artyEquipmentUDO
        self.__areaRadius = areaRadius
        self.__interval = interval
        self.__delayer = CallbackDelayer()
        self.__trajectoryDrawer = BigWorld.wg_trajectory_drawer()

    def create(self):
        super(_ArtyHitMarkerController, self).create()
        self.__trajectoryDrawer.setColors(Math.Vector4(0, 255, 0, 255), Math.Vector4(255, 0, 0, 255), Math.Vector4(128, 128, 128, 255))
        self.__trajectoryDrawer.setIgnoredID(BigWorld.player().playerVehicleID)

    def destroy(self):
        self.__artyEquipmentUDO = None
        if self.__trajectoryDrawer is not None:
            self.__trajectoryDrawer.visible = False
            self.__trajectoryDrawer = None
        if self.__delayer is not None:
            self.__delayer.destroy()
            self.__delayer = None
        super(_ArtyHitMarkerController, self).destroy()
        return

    def enable(self):
        super(_ArtyHitMarkerController, self).enable()
        self.__delayer.delayCallback(self.__interval, self.__tick)
        self.__trajectoryDrawer.setParams(1000.0, Math.Vector3(0, -self.__artyEquipmentUDO.gravity, 0), (0, 0))

    def disable(self):
        self.__delayer.stopCallback(self.__tick)
        super(_ArtyHitMarkerController, self).disable()

    def setVisible(self, flag):
        self.__trajectoryDrawer.visible = flag

    def getPointsInside(self, positions):
        return self._dataProvider.getPointsInside(positions)

    def _getCurrentShotInfo(self):
        launchPosition = self._position + self.__artyEquipmentUDO.position
        launchVelocity = self.__artyEquipmentUDO.launchVelocity
        gravity = Math.Vector3(0, -self.__artyEquipmentUDO.gravity, 0)
        return (launchPosition, launchVelocity, gravity)

    def _updateDispersionData(self):
        self._dataProvider.setupFlatRadialDispersion(self.__areaRadius)

    def __tick(self):
        self.__trajectoryDrawer.update(self._position, self._position + self.__artyEquipmentUDO.position, self.__artyEquipmentUDO.launchVelocity, self.__interval)
        return self.__interval


def _makeWorldMatrix(positionMatrix):
    sr = GUI.screenResolution()
    aspect = sr[0] / sr[1]
    proj = BigWorld.projection()
    worldMatrix = Math.Matrix()
    worldMatrix.perspectiveProjection(proj.fov, aspect, proj.nearPlane, proj.farPlane)
    worldMatrix.preMultiply(BigWorld.camera().matrix)
    worldMatrix.preMultiply(positionMatrix)
    return worldMatrix


def _calcScale(worldMatrix, size):
    pointMat = Math.Matrix()
    pointMat.set(BigWorld.camera().matrix)
    transl = Math.Matrix()
    transl.setTranslate(Math.Vector3(size, 0, 0))
    pointMat.postMultiply(transl)
    pointMat.postMultiply(BigWorld.camera().invViewMatrix)
    p = pointMat.applyToOrigin()
    pV4 = worldMatrix.applyV4Point(Math.Vector4(p[0], p[1], p[2], 1))
    oV4 = worldMatrix.applyV4Point(Math.Vector4(0, 0, 0, 1))
    pV3 = Math.Vector3(pV4[0], pV4[1], pV4[2]).scale(1.0 / pV4[3])
    oV3 = Math.Vector3(oV4[0], oV4[1], oV4[2]).scale(1.0 / oV4[3])
    return math.fabs(pV3[0] - oV3[0]) + math.fabs(pV3[1] - oV3[1])
