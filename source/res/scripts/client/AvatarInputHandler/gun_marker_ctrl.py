# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/AvatarInputHandler/gun_marker_ctrl.py
import math
import BattleReplay
import BigWorld
import GUI
import Math
import constants
from AvatarInputHandler import AimingSystems
from AvatarInputHandler import aih_constants, aih_global_binding
from ProjectileMover import getCollidableEntities
from debug_utils import LOG_UNEXPECTED
from helpers import dependency
from helpers.CallbackDelayer import CallbackDelayer
from skeletons.account_helpers.settings_core import ISettingsCore
_MARKER_TYPE = aih_constants.GUN_MARKER_TYPE
_MARKER_FLAG = aih_constants.GUN_MARKER_FLAG
_SHOT_RESULT = aih_constants.SHOT_RESULT
_BINDING_ID = aih_global_binding.BINDING_ID

def useServerGunMarker():
    """ Is server's gun marker used.
    :return: bool.
    """
    replayCtrl = BattleReplay.g_replayCtrl
    if replayCtrl.isPlaying:
        return False
    settingsCore = dependency.instance(ISettingsCore)
    return settingsCore.getSetting('useServerAim')


def useClientGunMarker():
    """ Is client's gun marker used.
    :return: bool.
    """
    return constants.HAS_DEV_RESOURCES or not useServerGunMarker()


def useDefaultGunMarkers():
    """ Uses default behavior to show gun markers (release version) - there is one marker
    in one period of time. Otherwise, uses development behavior - there are two markers
    (client and server) in one period of time if player choose setting item "Use server gun marker".
    :return: bool.
    """
    from gui import GUI_SETTINGS
    return not constants.HAS_DEV_RESOURCES or GUI_SETTINGS.useDefaultGunMarkers


def createGunMarker(isStrategic):
    """ Create gun marker controller.
    :param isStrategic: is strategic gun marker.
    :return: instance of gun marker that implements IGunMarkerController.
    """
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


def getShotResult(hitPoint, collision, excludeTeam=0):
    """ Gets shot result by present state of gun marker.
    :param hitPoint: Vector3 containing shot position.
    :param collision: instance of EntityCollisionData.
    :param excludeTeam: integer containing number of team that is excluded from result.
    :return: one of SHOT_RESULT.*.
    """
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
        ppDesc = vDesc.shot['piercingPower']
        maxDist = vDesc.shot['maxDistance']
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


def _setupGunMarkerSizeLimits(dataProvider, scale=None):
    """Setups actual size limits of gun marker, because of interface scale increases view port
    and min size to multiply by scale to show same min size of gun marker in GUI
    on different values of interface scale. See WOTD-72315."""
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
    """Interface defines methods of controller of gun marker."""

    def create(self):
        """Creates all internal data of controller."""
        raise NotImplementedError

    def destroy(self):
        """Destroys all internal data of controller."""
        raise NotImplementedError

    def enable(self):
        """Enables desired controller. One controller can be enabled on one period of time."""
        raise NotImplementedError

    def disable(self):
        """Disables desired controller."""
        raise NotImplementedError

    def reset(self):
        """Resets all internal data of controller."""
        raise NotImplementedError

    def update(self, markerType, position, dir, size, relaxTime, collData):
        """ Updates desired controller.
        :param markerType: one of GUN_MARKER_TYPE.
        :param position: Vector3 containing present position of gun marker.
        :param dir: Vector3 containing present direction of gun marker.
        :param size: float containing present size of gun marker.
        :param relaxTime: float containing present time of relax.
        :param collData: instance of EntityCollision.
        """
        raise NotImplementedError

    def setFlag(self, positive, bit):
        """ Sets new flag.
        :param positive: bool.
        :param bit: one of GUN_MARKER_FLAG.
        """
        raise NotImplementedError

    def getPosition(self):
        """ Gets present position of gun marker.
        :return: Vector3.
        """
        raise NotImplementedError

    def setPosition(self, position):
        """ Sets new position of gun marker.
         :param position: Vector3 containing present position of gun marker.
        """
        raise NotImplementedError

    def setVisible(self, flag):
        raise NotImplementedError

    def onRecreateDevice(self):
        """Callback that is invoked when screen size is changed."""
        raise NotImplementedError


class _GunMarkersDPFactory(object):
    """Class creates/gets required data provider and configures it."""
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
        dataProvider = GUI.WGSPGGunMarkerDataProvider(aih_constants.SPG_GUN_MARKER_ELEMENTS_COUNT)
        dataProvider.positionMatrixProvider = Math.MatrixAnimation()
        dataProvider.maxTime = 5.0
        dataProvider.serverTickLength = constants.SERVER_TICK_LENGTH
        dataProvider.sizeScaleRate = aih_constants.SPG_GUN_MARKER_SCALE_RATE
        dataProvider.sizeConstraint = (aih_constants.SPG_GUN_MARKER_MIN_SIZE, aih_constants.SPG_GUN_MARKER_MAX_SIZE)
        dataProvider.setRelaxTime(constants.SERVER_TICK_LENGTH)
        return dataProvider


class _GunMarkersDecorator(IGunMarkerController):
    """Decorator that contains implementation of markers on client-side and server-side."""
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
        elif markerType == _MARKER_TYPE.SERVER:
            return self.__serverMarker.getPosition()
        else:
            LOG_UNEXPECTED('Gun maker control is not found by type', markerType)
            return Math.Vector3()

    def setPosition(self, position, markerType=_MARKER_TYPE.CLIENT):
        if markerType == _MARKER_TYPE.CLIENT:
            self.__clientMarker.setPosition(position)
        elif markerType == _MARKER_TYPE.SERVER:
            self.__serverMarker.setPosition(position)
        else:
            LOG_UNEXPECTED('Gun maker control is not found by type', markerType)

    def setFlag(self, positive, bit):
        if positive:
            self.__gunMarkersFlags |= bit
            if bit == _MARKER_FLAG.SERVER_MODE_ENABLED:
                self.__serverMarker.setPosition(self.__clientMarker.getPosition())
        else:
            self.__gunMarkersFlags &= ~bit

    def update(self, markerType, position, dir, size, relaxTime, collData):
        if markerType == _MARKER_TYPE.CLIENT:
            self.__clientState = (position, relaxTime, collData)
            if self.__gunMarkersFlags & _MARKER_FLAG.CLIENT_MODE_ENABLED:
                self.__clientMarker.update(markerType, position, dir, size, relaxTime, collData)
        elif markerType == _MARKER_TYPE.SERVER:
            self.__serverState = (position, relaxTime, collData)
            if self.__gunMarkersFlags & _MARKER_FLAG.SERVER_MODE_ENABLED:
                self.__serverMarker.update(markerType, position, dir, size, relaxTime, collData)
        else:
            LOG_UNEXPECTED('Gun maker control is not found by type', markerType)


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

    def update(self, markerType, position, dir, size, relaxTime, collData):
        assert self._gunMarkerType == markerType
        self._position = position

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

    def _updateMatrixProvider(self, positionMatrix, relaxTime=0.0):
        animationMatrix = self._dataProvider.positionMatrixProvider
        animationMatrix.keyframes = ((0.0, Math.Matrix(animationMatrix)), (relaxTime, positionMatrix))
        animationMatrix.time = 0.0


class _DefaultGunMarkerController(_GunMarkerController):
    """Class of controller that is used by default."""
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

    def update(self, markerType, pos, dir, sizeVector, relaxTime, collData):
        super(_DefaultGunMarkerController, self).update(markerType, pos, dir, sizeVector, relaxTime, collData)
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
        worldMatrix = _makeWorldMatrix(positionMatrix)
        currentSize = _calcScale(worldMatrix, size) * self.__screenRatio
        idealSize = _calcScale(worldMatrix, idealSize) * self.__screenRatio
        self.__sizeFilter.update(currentSize, idealSize)
        self.__curSize = self.__sizeFilter.getSize()
        if self.__replSwitchTime > 0.0:
            self.__replSwitchTime -= relaxTime
            self._dataProvider.updateSize(self.__curSize, 0.0)
        else:
            self._dataProvider.updateSize(self.__curSize, relaxTime)

    def onRecreateDevice(self):
        self.__updateScreenRatio()

    def __updateScreenRatio(self):
        self.__screenRatio = GUI.screenResolution()[0] * 0.5

    def __onScaleChanged(self, scale):
        _setupGunMarkerSizeLimits(self._dataProvider, scale=scale)


class _SPGGunMarkerController(_GunMarkerController):
    """Class of controller that is used in strategic mode."""

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
        assert player is not None
        self._gunRotator = player.gunRotator
        shotDescr = player.getVehicleDescriptor().shot
        self._shotSpeed = shotDescr['speed']
        self._shotGravity = shotDescr['gravity']
        return

    def disable(self):
        self._gunRotator = None
        self._shotSpeed = 0.0
        self._shotGravity = 0.0
        super(_SPGGunMarkerController, self).disable()
        return

    def update(self, markerType, position, dir, size, relaxTime, collData):
        super(_SPGGunMarkerController, self).update(markerType, position, dir, size, relaxTime, collData)
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
        self.__trajectoryDrawer.setGetDynamicCollidersCallback(lambda start, end: [ e.collideSegment for e in getCollidableEntities((BigWorld.player().playerVehicleID,), start, end) ])

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
    """Calculate scaling in clip space
    :param worldMatrix: result of function _makeWorldMatrix.
    :param size: size of gun marker.
    :return: float containing scale in clip space.
    """
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
