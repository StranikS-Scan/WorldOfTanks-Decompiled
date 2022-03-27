# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/controllers/commander/markers.py
import typing
from collections import namedtuple
import math
import logging
import Keys
import Math
import BigWorld
import ResMgr
import math_utils
from constants import CollisionFlags
from ClientArena import CollisionResult
from aih_constants import CTRL_MODE_NAME
from gui.shared.gui_items.Vehicle import VEHICLE_CLASS_NAME
from helpers import dependency, weakProxy
from helpers.CallbackDelayer import CallbackDelayer
from RTSShared import RTSOrder, RTSCommandQueuePosition, RTSManner, MOVEMENT_ORDERS
from gui.battle_control.controllers.commander.common import addModel, delModel, getWaterHeight, calculateScaleFactor
from gui.battle_control.controllers.commander.interfaces import IMarker, IMarkerEnabled, IMarkerColor, IMarkerVisible, IProxyVehicle
from skeletons.gui.battle_session import IBattleSessionProvider
from gui.battle_control import avatar_getter
from gui import InputHandler
from gui.battle_control.controllers.commander.common import isShowAlternateUI
from soft_exception import SoftException
if typing.TYPE_CHECKING:
    from gui.battle_control.controllers.commander.interfaces import ICommand
_logger = logging.getLogger(__name__)
_ALPHA_BITS_SHIFT = 24
_DEFAULT_COLOR = 16777215
_DEFAULT_ALPHA = 255
_DEFAULT_COLOR_WITH_ALPHA = _DEFAULT_ALPHA << _ALPHA_BITS_SHIFT | _DEFAULT_COLOR
_MARKERS_CONFIG_FILE = 'scripts/dynamic_objects.xml'

class _Marker(IMarker, CallbackDelayer):
    __slots__ = ('_position', '__overTerrainOffset', '_yaw', '__scale', '__size', '__queuePos')

    def __init__(self, position, yaw, size=None, overTerrainOffset=None, scale=None, queuePos=None, **kwargs):
        super(_Marker, self).__init__()
        self._position = Math.Vector3(position)
        self.__overTerrainOffset = overTerrainOffset
        self._yaw = yaw
        self.__scale = scale if scale is not None else Math.Vector3(1.0, 1.0, 1.0)
        self.__size = size
        self.__queuePos = queuePos
        self._setupMarker()
        if kwargs:
            _logger.warning('Unused arguments %s in IMarker:%s', kwargs.keys(), self.__class__.__name__)
        return

    def fini(self):
        pass

    @property
    def position(self):
        return self._position

    @property
    def overTerrainOffset(self):
        return self.__overTerrainOffset

    @property
    def yaw(self):
        return self._yaw

    @property
    def size(self):
        return self.__size

    @property
    def scale(self):
        return self.__scale

    @property
    def queuePos(self):
        return self.__queuePos

    def move(self, position, overTerrainOffset=None):
        isChanged = False
        if self._position != position:
            self._position = position
            isChanged = True
        if overTerrainOffset is not None:
            self.__overTerrainOffset = overTerrainOffset
            isChanged = True
        return isChanged

    def rotate(self, yaw):
        isChanged = False
        if self._yaw != yaw:
            self._yaw = yaw
            isChanged = True
        return isChanged

    def resize(self, size):
        isChanged = False
        if self.__size != size:
            self.__size = size
            isChanged = True
        return isChanged

    def scaling(self, scale):
        isChanged = False
        if self.__scale != scale:
            self.__scale = scale
            isChanged = True
        return isChanged

    def setCommandQueuePosition(self, queuePos):
        if queuePos != self.__queuePos:
            self.__queuePos = queuePos
            self._onQueuePosUpdated()

    def update(self, *args, **kwargs):
        pass

    def _setupMarker(self):
        pass

    def _onQueuePosUpdated(self):
        pass

    def _startListenOnCameraChanged(self):
        player = BigWorld.player()
        if player and player.inputHandler:
            player.inputHandler.onCameraChanged += self._onCameraChanged

    def _startListenOnHandleKeyEvent(self):
        InputHandler.g_instance.onKeyDown += self._handleKeyEvent
        InputHandler.g_instance.onKeyUp += self._handleKeyEvent

    def _stopListenOnCameraChanged(self):
        player = BigWorld.player()
        if player and player.inputHandler:
            player.inputHandler.onCameraChanged -= self._onCameraChanged

    def _stopListenOnHandleKeyEvent(self):
        InputHandler.g_instance.onKeyDown -= self._handleKeyEvent
        InputHandler.g_instance.onKeyUp -= self._handleKeyEvent

    def _onCameraChanged(self, cameraName, currentVehicleId=None):
        pass

    def _handleKeyEvent(self, event):
        pass


class _SimplexMarker(_Marker):
    _CUTOFF_DELTA = 2.5
    _CUTOFF_HEIGHT = 5.0
    _DO_CUTOFF = True
    _DO_RELATIVE_PROJECTION = False
    _ONLY_ON_TERRAIN = False
    _IS_ONLY_PROJECT_UPWARDS = False
    __slots__ = ('__model', '__visualArea', '__modelName', '__nodeName', '__visualPath')

    def __init__(self, position, yaw, visual, size, overTerrainOffset=0.0, scale=None, modelName='', nodeName=''):
        self.__model = BigWorld.Model(modelName)
        self.__visualArea = BigWorld.PyTerrainSelectedArea()
        self.__modelName = modelName
        self.__nodeName = nodeName
        self.__visualPath = visual
        super(_SimplexMarker, self).__init__(position=position, yaw=yaw, size=size, overTerrainOffset=overTerrainOffset, scale=scale or Math.Vector3(1.0, 1.0, 1.0))

    def fini(self):
        delModel(self.__model)
        self.__model.node('').detach(self.__visualArea)
        self.__visualArea = None
        self.__model = None
        return

    @property
    def model(self):
        return self.__model

    @property
    def visualArea(self):
        return self.__visualArea

    @property
    def visualPath(self):
        return self.__visualPath

    @property
    def modelName(self):
        return self.__modelName

    @property
    def nodeName(self):
        return self.__nodeName

    def move(self, position, overTerrainOffset=None):
        isChanged = super(_SimplexMarker, self).move(position, overTerrainOffset)
        if isChanged:
            self.__model.position = position
            if overTerrainOffset is not None and self.__visualArea is not None:
                self.__visualArea.setOverTerrainOffset(overTerrainOffset)
            self.__updateHeights()
        return isChanged

    def rotate(self, yaw):
        isChanged = super(_SimplexMarker, self).rotate(yaw)
        if isChanged:
            self.__model.yaw = yaw
            self.__updateHeights()
        return isChanged

    def resize(self, size):
        isChanged = super(_SimplexMarker, self).resize(size)
        if isChanged:
            self.__visualArea.setSize(size)
        return isChanged

    def scaling(self, scale):
        isChanged = super(_SimplexMarker, self).scaling(scale)
        if isChanged:
            self.__model.scale = scale
            self.__updateHeights()
        return isChanged

    def _setupMarker(self):
        self._setupModel()
        self._setupArea()
        self.move(self.position, self.overTerrainOffset)
        self.rotate(self.yaw)

    def _setupModel(self):
        addModel(self.model)
        self.model.visible = True
        self.model.yaw = self.yaw

    def _setupArea(self):
        area = self.__visualArea
        area.setup(self.__visualPath, self.size, self.overTerrainOffset, _DEFAULT_COLOR_WITH_ALPHA)
        self._setupAreaConfig(area)
        self.__model.node(self.__nodeName).attach(area)

    def _setupAreaConfig(self, area):
        area.enableAccurateCollision(not self._ONLY_ON_TERRAIN)
        area.setYCutOffDelta(self._CUTOFF_DELTA)
        area.setYCutOffDistance(self._CUTOFF_HEIGHT)
        area.doYCutOff(self._DO_CUTOFF)
        area.enableRelativeProjection(self._DO_RELATIVE_PROJECTION)
        area.setOnlyProjectUpwards(self._IS_ONLY_PROJECT_UPWARDS)

    def __updateHeights(self):
        self.__visualArea.updateHeights()


class _SimplexColorMarker(_SimplexMarker, IMarkerColor):
    __slots__ = ('__alpha', '__color')

    def __init__(self, position, yaw, visual, size, overTerrainOffset=0.0, scale=None, modelName='', nodeName='', color=_DEFAULT_COLOR, alpha=_DEFAULT_ALPHA):
        self.__color = color
        self.__alpha = alpha
        super(_SimplexColorMarker, self).__init__(position=position, yaw=yaw, size=size, overTerrainOffset=overTerrainOffset, scale=scale or Math.Vector3(1.0, 1.0, 1.0), visual=visual, modelName=modelName, nodeName=nodeName)

    @property
    def color(self):
        return self.__color

    @color.setter
    def color(self, color):
        if color != self.__color:
            self.__color = color
            self._setAreaColor()

    @property
    def alpha(self):
        return self.__alpha

    @alpha.setter
    def alpha(self, alpha):
        if alpha != self.__alpha:
            self.__alpha = alpha
            self._setAreaColor()

    @property
    def colorWithAlpha(self):
        return self.__alpha << _ALPHA_BITS_SHIFT | self.__color

    def setColorWithAlpha(self, color, alpha):
        if color == self.__color and alpha == self.__alpha:
            return
        self.__alpha = alpha
        self.__color = color
        self._setAreaColor()

    def _setAreaColor(self):
        self.visualArea.setColor(self.colorWithAlpha)

    def _setupArea(self):
        area = self.visualArea
        area.setup(self.visualPath, self.size, self.overTerrainOffset, self.colorWithAlpha)
        self._setupAreaConfig(area)
        self.model.node(self.nodeName).attach(area)


class InvalidPositionMarker(_SimplexColorMarker):
    _VISUAL = None
    _OVER_TERRAIN_OFFSET = 0.3
    _COLOR = 16711680
    _DIAMETER = 4.0
    _HIDE_DURATION = 1.0
    _DO_RELATIVE_PROJECTION = True

    def __init__(self, position):
        self._loadConfig()
        size = Math.Vector2(self._DIAMETER, self._DIAMETER)
        super(InvalidPositionMarker, self).__init__(position=position, yaw=0.0, size=size, overTerrainOffset=self._OVER_TERRAIN_OFFSET, visual=self._VISUAL, color=self._COLOR)
        self.__fadingStartTime = BigWorld.time()
        self.__timeLeft = 0.0
        self.__hide()

    @classmethod
    def _loadConfig(cls):
        if cls._VISUAL:
            return
        else:
            settingsData = ResMgr.openSection(_MARKERS_CONFIG_FILE)['RTSMarkers']['invalidPositionMarker']
            if settingsData is None:
                raise SoftException('Can not open ' + _MARKERS_CONFIG_FILE + 'with sections RTSMarkers/invalidPositionMarker')
            cls._VISUAL = settingsData.readString('visualPath')
            return

    def __hide(self):
        if self.__fadingStartTime is None:
            self.fini()
        else:
            self.__updateFadingOutAlpha()
            self.delayCallback(0.0, self.__hide)
        return

    def __updateFadingOutAlpha(self):
        delay = self._HIDE_DURATION
        deltaTime = BigWorld.time() - self.__fadingStartTime
        if deltaTime > delay:
            self.__fadingStartTime = None
            return
        else:
            alphaStep = 1.0 - math_utils.easeInOutSine(deltaTime, 1.0, delay)
            self.alpha = int(_DEFAULT_ALPHA * alphaStep)
            return


class OverwatchSectorMarker(_SimplexColorMarker, IMarkerVisible):
    _MODEL_PATH = None
    _LENGTH = 69.0
    _SECTOR_OFFSET_FROM_CENTER = 5.0
    _SIZE = Math.Vector2(_LENGTH, _LENGTH / 2)
    _OVER_TERRAIN_OFFSET = 1.3
    __slots__ = ('__isVisible',)

    def __init__(self, position, yaw):
        self._loadConfig()
        self.__isVisible = True
        self.__storedManner = None
        super(OverwatchSectorMarker, self).__init__(position=position, yaw=yaw, visual=self._MODEL_PATH, size=self._SIZE, overTerrainOffset=self._OVER_TERRAIN_OFFSET)
        return

    @classmethod
    def _loadConfig(cls):
        if cls._MODEL_PATH:
            return
        else:
            settingsData = ResMgr.openSection(_MARKERS_CONFIG_FILE)['RTSMarkers']['overwatchSector']
            if settingsData is None:
                raise SoftException('Can not open ' + _MARKERS_CONFIG_FILE + 'with sections RTSMarkers/overwatchSector')
            cls._MODEL_PATH = settingsData.readString('model')
            return

    @classmethod
    def isSuitedForVehicle(cls, proxyVehicle):
        vehicleClass = proxyVehicle.typeDescriptor.type.getVehicleClass()
        gunSettings = proxyVehicle.gunSettings
        return vehicleClass != VEHICLE_CLASS_NAME.SPG and gunSettings and bool(gunSettings.turretYawLimits)

    def isVisible(self):
        return self.__isVisible

    def setVisible(self, isVisible):
        isChanged = False
        if self.__isVisible != isVisible:
            self.__isVisible = self.model.visible = isVisible
            isChanged = True
        return isChanged

    def rotate(self, yaw):
        return super(OverwatchSectorMarker, self).rotate(yaw + math.pi)

    def update(self, position, yaw):
        self.move(position)
        self.rotate(yaw)

    def updateVisibilityFromVehicle(self, vehicle, definedManner=None):
        newManner = definedManner or vehicle.manner
        isVisible = newManner == RTSManner.HOLD and vehicle.isSelected
        isVisibilityChanged = self.setVisible(isVisible)
        if isVisibilityChanged and isVisible:
            if self.__storedManner != newManner:
                self._position = None
                self._yaw = None
        self.__storedManner = newManner
        return isVisibilityChanged


class _VehicleDirectionMarker(_SimplexColorMarker, IMarkerEnabled, IMarkerVisible):
    _VISUAL = None
    _OVER_TERRAIN_OFFSET = 0.3
    _IS_ONLY_PROJECT_UPWARDS = True
    _ENABLED_ALPHA = 1.0
    _DISABLED_ALPHA = 0.8
    _ARROW_WIDTH = 3.0
    _ARROW_POSITION_OFFSET = -1.5
    ARROW_WIDTH_TO_LENGTH_COEFFICIENT = 0.9
    __slots__ = ('__enabled', '__length', '__isVisible')

    def __init__(self, position, yaw, vehicleLength):
        self._loadConfig()
        self.__enabled = False
        self.__length = vehicleLength + self._ARROW_POSITION_OFFSET
        self.__isVisible = True
        size = Math.Vector2(self._ARROW_WIDTH, self._ARROW_WIDTH * self.ARROW_WIDTH_TO_LENGTH_COEFFICIENT)
        super(_VehicleDirectionMarker, self).__init__(position=position, yaw=yaw, size=size, overTerrainOffset=self._OVER_TERRAIN_OFFSET, visual=self._VISUAL, color=_DEFAULT_COLOR, alpha=int(_DEFAULT_ALPHA * self._DISABLED_ALPHA))

    def isEnabled(self):
        return self.__enabled

    def isVisible(self):
        return self.__isVisible

    def setVisible(self, isVisible):
        isChanged = False
        if self.__isVisible != isVisible:
            self.__isVisible = self.model.visible = isVisible
            isChanged = True
        return isChanged

    def setEnabled(self, isEnabled):
        isChanged = False
        if self.__enabled != isEnabled:
            self.__enabled = isEnabled
            self.alpha = int(_DEFAULT_ALPHA * (self._ENABLED_ALPHA if isEnabled else self._DISABLED_ALPHA))
            isChanged = True
        return isChanged

    def move(self, position, overTerrainOffset=None):
        position = Math.Vector3(position)
        position += self.__getOffset(self.yaw)
        return super(_VehicleDirectionMarker, self).move(position, overTerrainOffset)

    def update(self, position, yaw):
        self.move(position)
        self.rotate(yaw)

    @classmethod
    def _loadConfig(cls):
        if cls._VISUAL:
            return
        else:
            settingsData = ResMgr.openSection(_MARKERS_CONFIG_FILE)['RTSMarkers']['vehicleDirectionMarker']
            if settingsData is None:
                raise SoftException('Can not open ' + _MARKERS_CONFIG_FILE + 'with sections RTSMarkers/vehicleDirectionMarker')
            cls._VISUAL = settingsData.readString('visualPath')
            return

    def __getOffset(self, yaw):
        offset = Math.Vector3()
        offset.setPitchYaw(0.0, yaw)
        offset *= self.__length
        return offset


class ProxyDirectionMarker(IMarkerVisible):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)
    __MIN_SCALE = 1.0
    __MAX_SCALE = 2.0
    __CAM_STEP = 50.0

    def __init__(self, owner):
        self.__vehicle = weakProxy(owner)
        vehicleLength = self.__vehicle.appearance.computeFullVehicleLength()
        self.__arrow = _VehicleDirectionMarker(self.__vehicle.position, self.__vehicle.yaw, vehicleLength)

    def fini(self):
        self.__arrow.fini()

    def update(self):
        self.__arrow.update(self.__vehicle.position, self.__vehicle.yaw)
        self.__arrow.setEnabled(self.__vehicle.isSelected)
        cameraPosition = self.__sessionProvider.dynamic.rtsCommander.getCameraPosition()
        if cameraPosition is None:
            return
        else:
            scaleFactor = calculateScaleFactor(self.__vehicle.position, cameraPosition)
            self.__arrow.scaling(Math.Vector3(*([scaleFactor] * 3)))
            return

    def setVisible(self, isVisible):
        self.__arrow.setVisible(isVisible)

    def isVisible(self):
        return self.__arrow.isVisible() if self.__arrow else False


class _VehicleGhostMarker(_Marker, IMarkerEnabled, IMarkerVisible):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)
    _OVER_TERRAIN_OFFSET = 0
    _ARROW_LENGTH = 2.0
    _VISIBLE_POS_STATES = (RTSCommandQueuePosition.PREVIEW, RTSCommandQueuePosition.SINGLE, RTSCommandQueuePosition.LAST)
    _HALF_PI = math.pi / 2
    _TWO_PI = 2.0 * math.pi
    __slots__ = ('__arrow', '__model', '__heading', '__enabled', '__vehID', '__isVisible', '__overwatch')

    def __init__(self, vehID, position, heading, vehicleModel, **kwargs):
        self.__arrow = None
        self.__overwatch = None
        self.__model = vehicleModel
        self.__heading = heading
        self.__enabled = True
        self.__isVisible = True
        self.__vehID = vehID
        scale = Math.Vector3(1.0, 1.0, 1.0)
        yaw = self.__getYawFromHeading(heading)
        self.__rotation = (yaw + self._HALF_PI, 0.0, -self._HALF_PI)
        self._startListenOnCameraChanged()
        super(_VehicleGhostMarker, self).__init__(position=position, yaw=yaw, overTerrainOffset=self._OVER_TERRAIN_OFFSET, scale=scale, **kwargs)
        return

    def fini(self):
        if self.__arrow:
            self.__arrow.fini()
            self.__arrow = None
        if self.__overwatch:
            self.__overwatch.fini()
            rtsCommander = self.__sessionProvider.dynamic.rtsCommander
            rtsCommander.vehicles.onMannerChanged -= self.__onMannerChanged
            self.__overwatch = None
        if self.__model:
            self.__model.visible = False
        self.__model = None
        self._stopListenOnCameraChanged()
        super(_VehicleGhostMarker, self).fini()
        return

    @property
    def heading(self):
        return self.__heading

    def isEnabled(self):
        return self.__enabled

    def isVisible(self):
        return self.__isVisible

    def setVisible(self, isVisible):
        isChanged = False
        if self.__isVisible != isVisible:
            self._updateVisibility()
            isChanged = True
        return isChanged

    def setEnabled(self, isEnabled):
        if self.__enabled == isEnabled:
            return False
        self.__arrow.setEnabled(isEnabled)
        self.__enabled = isEnabled
        return True

    def move(self, position, overTerrainOffset=None):
        isChanged = super(_VehicleGhostMarker, self).move(position, overTerrainOffset)
        if isChanged:
            self.__updateModel()
            self.__moveArrow(position, overTerrainOffset)
        return isChanged

    def rotate(self, heading):
        self.__heading = heading
        yaw = self.__getYawFromHeading(heading)
        isChanged = super(_VehicleGhostMarker, self).rotate(yaw)
        if isChanged:
            self.__updateModel()
            self.__rotateArrow(yaw)
        return isChanged

    def scaling(self, scale):
        pass

    def update(self, position, heading):
        super(_VehicleGhostMarker, self).move(position)
        self.__heading = heading
        yaw = self.__getYawFromHeading(heading)
        super(_VehicleGhostMarker, self).rotate(yaw)
        self.__rotateArrow(yaw)
        self.__moveArrow(position)
        self.__updateModel()

    def cleanVehicleMarkerRef(self):
        self.__arrow.setVisible(False)
        self.__model = None
        return

    def _setupMarker(self):
        bwVehicle = BigWorld.entities.get(self.__vehID)
        if bwVehicle is not None and bwVehicle.appearance is not None:
            vehicleLength = bwVehicle.appearance.computeFullVehicleLength()
            self.__arrow = _VehicleDirectionMarker(position=self.position, yaw=self.yaw, vehicleLength=vehicleLength)
        rtsCommander = self.__sessionProvider.dynamic.rtsCommander
        proxyVehicle = rtsCommander.vehicles.get(self.__vehID)
        if proxyVehicle:
            if OverwatchSectorMarker.isSuitedForVehicle(proxyVehicle):
                self.__overwatch = OverwatchSectorMarker(position=self.position, yaw=self.yaw)
                self.__overwatch.updateVisibilityFromVehicle(proxyVehicle)
                rtsCommander.vehicles.onMannerChanged += self.__onMannerChanged
        self.__updateModel()
        self._updateVisibility()
        return

    def _onCameraChanged(self, cameraName, currentVehicleId=None):
        if cameraName is CTRL_MODE_NAME.ARCADE or cameraName is CTRL_MODE_NAME.COMMANDER:
            self._updateVisibility()

    def _onQueuePosUpdated(self):
        super(_VehicleGhostMarker, self)._onQueuePosUpdated()
        self._updateVisibility()

    def _updateVisibility(self):
        isCommanderCtrlMode = avatar_getter.isCommanderCtrlMode()
        modelAndArrowVisible = self.__isVisible and isCommanderCtrlMode and self.queuePos in self._VISIBLE_POS_STATES
        if self.__model:
            self.__model.visible = modelAndArrowVisible
        if self.__arrow:
            self.__arrow.setVisible(modelAndArrowVisible)
        if self.__overwatch:
            if modelAndArrowVisible:
                proxyVehicle = self.__sessionProvider.dynamic.rtsCommander.vehicles.get(self.__vehID)
                self.__overwatch.updateVisibilityFromVehicle(proxyVehicle)
            else:
                self.__overwatch.setVisible(False)

    def __updateModel(self):
        position = self.position
        y = max(getWaterHeight(position), position.y)
        translation = Math.Vector3(position.x, y + self.overTerrainOffset, position.z)
        matrix = Math.Matrix()
        matrix.setRotateY(self.yaw)
        matrix.translation = translation
        if self.__model:
            self.__model.matrix = matrix

    def __moveArrow(self, position, overTerrainOffset=None):
        self.__arrow.move(position, overTerrainOffset)
        if self.__overwatch:
            self.__overwatch.move(position, overTerrainOffset)

    def __rotateArrow(self, yaw):
        self.__arrow.rotate(yaw)
        if self.__overwatch:
            self.__overwatch.rotate(yaw)

    def __getYawFromHeading(self, heading):
        yaw = math.acos(math_utils.clamp(-1.0, 1.0, heading.z))
        if heading.x <= 0.0:
            yaw = self._TWO_PI - yaw
        return yaw

    def __onMannerChanged(self, vID, manner):
        if vID != self.__vehID:
            return
        if self.queuePos in self._VISIBLE_POS_STATES:
            proxyVehicle = self.__sessionProvider.dynamic.rtsCommander.vehicles.get(self.__vehID)
            isVisibilityChanged = self.__overwatch.updateVisibilityFromVehicle(proxyVehicle, definedManner=manner)
            if isVisibilityChanged and self.__overwatch.isVisible():
                self.__overwatch.update(self.position, self.yaw)


class DamageDirectionMarker(_SimplexColorMarker, IMarkerVisible):
    _HIT_VISUAL = None
    _BLOCKED_VISUAL = None
    _STATE_SHOWN = 'SHOW'
    _STATE_FADING_OUT = 'FADING_OUT'
    _STATE_FADED_OUT = 'FADED_OUT'
    _SCALE_CHANGE_MIN = 0.05
    _OVER_TERRAIN_OFFSET = 1.2
    _SIZE = Math.Vector2(1.0, 4.5)
    _FADING_OUT_DURATION = 1.0
    _MARKER_POSITION_OFFSET_SCALE = 5.0
    _CUTOFF_DELTA = 0.0
    _CUTOFF_HEIGHT = 2.0
    _DO_CUTOFF = True
    _ONLY_ON_TERRAIN = False
    _DO_RELATIVE_PROJECTION = False
    _IS_ONLY_PROJECT_UPWARDS = True
    CUTOFF_DELTA = 2.5
    CUTOFF_HEIGHT = 5.0

    @classmethod
    def _loadConfig(cls):
        if cls._HIT_VISUAL and cls._BLOCKED_VISUAL:
            return
        settingsData = ResMgr.openSection(_MARKERS_CONFIG_FILE + '/RTSMarkers/hitDirectionMarker')
        cls._HIT_VISUAL = settingsData.readString('hit').replace('.model', '.visual')
        cls._BLOCKED_VISUAL = settingsData.readString('blocked').replace('.model', '.visual')
        cls._SCALE_CHANGE_MIN = settingsData.readFloat('scaleChangeMin', cls._SCALE_CHANGE_MIN)
        cls._OVER_TERRAIN_OFFSET = settingsData.readFloat('overTerrainOffset', cls._OVER_TERRAIN_OFFSET)
        cls._SIZE = settingsData.readVector2('size', cls._SIZE)
        cls._FADING_OUT_DURATION = settingsData.readFloat('fadingOutDuration', cls._FADING_OUT_DURATION)
        cls._MARKER_POSITION_OFFSET_SCALE = settingsData.readFloat('markerPositionOffsetScale', cls._MARKER_POSITION_OFFSET_SCALE)
        cls._CUTOFF_DELTA = settingsData.readFloat('cutoffDelta', cls._CUTOFF_DELTA)
        cls._CUTOFF_HEIGHT = settingsData.readFloat('cutoffHeight', cls._CUTOFF_HEIGHT)
        cls._DO_CUTOFF = settingsData.readBool('isCutoffEnabled', cls._DO_CUTOFF)
        cls._DO_RELATIVE_PROJECTION = settingsData.readBool('isRelativeProjection', cls._DO_RELATIVE_PROJECTION)
        cls._IS_ONLY_PROJECT_UPWARDS = settingsData.readBool('isOnlyProjectUpwards', cls._IS_ONLY_PROJECT_UPWARDS)
        cls._ONLY_ON_TERRAIN = settingsData.readBool('isTerrainOnly', cls._ONLY_ON_TERRAIN)

    def __init__(self, vehicle, hitData, timeLeft, duration):
        self._loadConfig()
        self.__vehicle = weakProxy(vehicle)
        self.__hitData = hitData
        self.__damageFromArea = self.__findDamageFromArea()
        bbox = vehicle.typeDescriptor.hitTesters.hull.bbox
        delta = bbox[1] - bbox[0]
        self.__offset = delta.x / 4
        self.__timeLeft = timeLeft
        self.__totalDuration = duration
        self.__scalingFactor = None
        self.__fadingStartTime = None
        self.__cbID = None
        self.__isVisible = True
        visual = self._BLOCKED_VISUAL if hitData.isBlocked() else self._HIT_VISUAL
        position = self.__getMarkerPositionFromVehicleCenter()
        yaw = self.__getYawBasedOnHitData(hitData)
        super(DamageDirectionMarker, self).__init__(position=position, yaw=yaw, visual=visual, size=self._SIZE, overTerrainOffset=self._OVER_TERRAIN_OFFSET)
        self.__state = self._STATE_SHOWN
        if duration - self._FADING_OUT_DURATION - self.__timeLeft < 1.0:
            self.delayCallback(1.0, self.__fadeOut)
        else:
            self.delayCallback(duration - self._FADING_OUT_DURATION - self.__timeLeft, self.__fadeOut)
        return

    @property
    def vehicleProxy(self):
        return self.__vehicle

    def fini(self):
        self.__cancelFadeOutCallback()
        super(DamageDirectionMarker, self).fini()

    def isVisible(self):
        return self.__isVisible

    def setVisible(self, isVisible):
        isChanged = False
        if isVisible != self.__isVisible:
            self.__isVisible = isVisible
            self.model.visible = self.__isVisible = isVisible
            isChanged = True
        return isChanged

    def move(self, position, overTerrainOffset=None):
        position = Math.Vector3(position)
        position += self.__getOffset(self.yaw)
        return super(DamageDirectionMarker, self).move(position, overTerrainOffset)

    def redraw(self, timeLeft):
        if self.__state == self._STATE_FADED_OUT:
            return
        else:
            self.__cancelFadeOutCallback()
            self.alpha = _DEFAULT_ALPHA
            self.__state = self._STATE_SHOWN
            self.__timeLeft = timeLeft
            self.__fadingStartTime = None
            if self.__totalDuration - self._FADING_OUT_DURATION - timeLeft < 1.0:
                self.delayCallback(1.0, self.__fadeOut)
            else:
                self.delayCallback(self.__totalDuration - self._FADING_OUT_DURATION - timeLeft, self.__fadeOut)
            return

    def updateScalingFactor(self, camPos):
        scalingFactor = calculateScaleFactor(self.__getMarkerPositionFromVehicleCenter(), camPos)
        if self.__scalingFactor is not None:
            delta = abs(scalingFactor - self.__scalingFactor)
            if delta < self._SCALE_CHANGE_MIN or self.__scalingFactor == scalingFactor:
                return
        newScale = Math.Vector3(scalingFactor, scalingFactor, scalingFactor)
        self.__scalingFactor = scalingFactor
        self.scaling(newScale)
        return

    def update(self):
        position = self.__getMarkerPositionFromVehicleCenter()
        direction = position - self.__damageFromArea
        direction.normalise()
        yaw = self.__getYawBasedOnHitData(self.__hitData)
        self.rotate(yaw)
        self.move(position)
        if self.__fadingStartTime is not None:
            self.__updateFadingOutAlpha()
        return self.__state == self._STATE_FADED_OUT

    def __fadeOut(self):
        self.__state = self._STATE_FADING_OUT
        self.__fadingStartTime = BigWorld.time()

    def __updateFadingOutAlpha(self):
        deltaTime = BigWorld.time() - self.__fadingStartTime
        if deltaTime > self._FADING_OUT_DURATION:
            self.__fadingStartTime = None
            self.__state = self._STATE_FADED_OUT
            return
        else:
            alphaStep = 1.0 - math_utils.easeInOutSine(deltaTime, 1.0, self._FADING_OUT_DURATION)
            self.alpha = int(_DEFAULT_ALPHA * alphaStep)
            return

    def __findDamageFromArea(self):
        enemy = BigWorld.entity(self.__hitData.getAttackerID())
        if enemy is not None:
            return enemy.position
        else:
            start = self.__getMarkerPositionFromVehicleCenter()
            minPoint, maxPoint = BigWorld.player().arena.getArenaBB()
            mapDistance = minPoint.distTo(maxPoint)
            offset = Math.Vector3()
            offset.setPitchYaw(0.0, self.__getYawBasedOnHitData(self.__hitData))
            offset *= mapDistance
            end = start + offset
            res, position = BigWorld.player().arena.collideWithArenaBB(start, end)
            return position

    def __getOffset(self, yaw):
        offset = Math.Vector3()
        offset.setPitchYaw(0.0, yaw)
        offset *= self.__offset
        return offset

    def __cancelFadeOutCallback(self):
        if self.hasDelayedCallback(self.__fadeOut):
            self.stopCallback(self.__fadeOut)

    def __getMarkerPositionFromVehicleCenter(self):
        yawDirection = self.__hitData.getYaw() - math.pi
        hitVector = Math.Vector3()
        hitVector.setPitchYaw(0.0, yawDirection)
        return self.__vehicle.position + hitVector.scale(self._MARKER_POSITION_OFFSET_SCALE)

    def __getYawBasedOnHitData(self, hitData):
        return hitData.getYaw() - 0.5 * math.pi


class _TerrainOrderMarkerCounter(object):
    __instanceCount = 0

    def __new__(cls, *args, **kwargs):
        _TerrainOrderMarkerCounter.__instanceCount += 1
        instance = super(_TerrainOrderMarkerCounter, cls).__new__(cls, *args, **kwargs)
        return instance

    @property
    def instanceCount(self):
        return _TerrainOrderMarkerCounter.__instanceCount


class TerrainOrderMarker(_VehicleGhostMarker, _TerrainOrderMarkerCounter):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)
    _SUPPORTED_ORDERS = (RTSOrder.GO_TO_POSITION,
     RTSOrder.ATTACK_ENEMY,
     RTSOrder.CAPTURE_THE_BASE,
     RTSOrder.DEFEND_THE_BASE,
     RTSOrder.FORCE_GO_TO_POSITION,
     RTSOrder.FORCE_ATTACK_ENEMY,
     RTSOrder.RETREAT,
     RTSOrder.STOP)
    __slots__ = ('__orderType', '__markerID', '__vID')

    def __init__(self, vID, orderType, position, heading, vehicleModel, **kwargs):
        self.__orderType = orderType
        self.__markerID = self.instanceCount
        self.__vID = vID
        self._startListenOnHandleKeyEvent()
        super(TerrainOrderMarker, self).__init__(vID, position, heading, vehicleModel, **kwargs)

    def fini(self):
        rtsCommander = self.__sessionProvider.dynamic.rtsCommander
        if rtsCommander is not None:
            rtsCommander.onRTSStaticMarkerRemove(self.__markerID)
        self._stopListenOnHandleKeyEvent()
        super(TerrainOrderMarker, self).fini()
        return

    @property
    def orderType(self):
        return self.__orderType

    @property
    def markerID(self):
        return self.__markerID

    @property
    def vehicleID(self):
        return self.__vID

    @orderType.setter
    def orderType(self, oType):
        if oType is None:
            return
        else:
            if self.__orderType != oType:
                self.__orderType = oType if oType in TerrainOrderMarker._SUPPORTED_ORDERS else None
                self.__update2DMarker()
            return

    def setEnabled(self, isEnabled):
        isChanged = super(TerrainOrderMarker, self).setEnabled(isEnabled)
        if isChanged:
            self.__sessionProvider.dynamic.rtsCommander.onSetMarkerEnabled(self.__vID, isEnabled)
        return isChanged

    def setVisible(self, isVisible):
        isChanged = super(TerrainOrderMarker, self).setVisible(isVisible)
        if isChanged:
            self.__update2DMarker()
        return isChanged

    def move(self, position, overTerrainOffset=None):
        isChanged = super(TerrainOrderMarker, self).move(position)
        if isChanged:
            self.__update2DMarker()
        return isChanged

    def update(self, position, heading):
        isChanged = self.position != position
        super(TerrainOrderMarker, self).update(position, heading)
        if isChanged:
            self.__update2DMarker()

    def _updateVisibility(self):
        super(TerrainOrderMarker, self)._updateVisibility()
        self.__update2DMarker()

    def __update2DMarker(self):
        isCommanderCtrlMode = avatar_getter.isCommanderCtrlMode()
        isShowName = self.queuePos in (RTSCommandQueuePosition.SINGLE, RTSCommandQueuePosition.LAST)
        isAltDown = isShowAlternateUI()
        shouldBeVisible = self.__orderType is not None and self.isVisible() and (isCommanderCtrlMode or not isCommanderCtrlMode and isShowName or isAltDown) and self.queuePos != RTSCommandQueuePosition.PREVIEW
        vehName = self.__sessionProvider.getArenaDP().getVehicleInfo(self.__vID).vehicleType.shortName if isShowName else ''
        rtsCommander = self.__sessionProvider.dynamic.rtsCommander
        if shouldBeVisible:
            rtsCommander.onRTSStaticMarkerShow(self.__markerID, self.__vID, self.position, self.__orderType, vehName)
        else:
            rtsCommander.onRTSStaticMarkerRemove(self.__markerID)
        return

    def _handleKeyEvent(self, event):
        if event.key in (Keys.KEY_LALT, Keys.KEY_RALT):
            self.__update2DMarker()


PathMarkerStyle = namedtuple('PathMarkerStyle', ['modelPath',
 'modelIntersection',
 'scaleMarker',
 'scalePath',
 'scaleIntersection',
 'offset',
 'intervalLength',
 'rotation',
 'isStretchModel'])

class _LineMarker(_Marker):
    __slots__ = ('_style', '_lineModels', '_targetPosition', '_intersections')
    LINE_MARKER_STYLES = None

    def __init__(self, position, targetPosition, queuePos, style):
        self._loadStyles()
        self._lineModels = []
        self._intersections = []
        self._style = self.LINE_MARKER_STYLES[style]
        self._targetPosition = targetPosition
        self._rotation = self.getRotation(position, targetPosition)
        super(_LineMarker, self).__init__(position=position, yaw=self._rotation.yaw, size=Math.Vector3(), overTerrainOffset=self._style.offset, scale=self._style.scaleMarker, queuePos=queuePos)

    def fini(self):
        self._clearLine()
        super(_LineMarker, self).fini()

    @staticmethod
    def getRotation(fromPosition, toPosition):
        delta = toPosition - fromPosition
        return math_utils.createRotationMatrix(Math.Vector3(delta.yaw, delta.pitch, 0.0))

    def move(self, position, overTerrainOffset=None):
        super(_LineMarker, self).move(position, overTerrainOffset)
        self._updateLine()

    def _setupMarker(self):
        self._updateLine()

    def _getLine(self):
        return (self._position + self.overTerrainOffset, self._targetPosition + self.overTerrainOffset)

    def _updateLine(self):
        if not self._style.intervalLength:
            return
        fromPositionWithOffset, toPositionWithOffset = self._getLine()
        self._rotation = self.getRotation(fromPositionWithOffset, toPositionWithOffset)
        self._yaw = self._rotation.yaw
        distance = fromPositionWithOffset.distTo(toPositionWithOffset)
        modelCount = int(math.ceil(distance / self._style.intervalLength))
        if not modelCount:
            self._clearLine()
            return
        self.__reserveModels(modelCount)
        modelRotation = Math.Matrix(self._rotation)
        localMarkerRotation = math_utils.createRotationMatrix(self._style.rotation)
        modelRotation.postMultiply(localMarkerRotation)
        modelRotationVector = (modelRotation.yaw, modelRotation.pitch, modelRotation.roll)
        modelStretch = distance / modelCount if self._style.isStretchModel else 1.0
        modelScale = self._style.scalePath
        positionInterval = (toPositionWithOffset - fromPositionWithOffset) / modelCount
        previousPosition = fromPositionWithOffset - positionInterval * 0.5
        for idx in xrange(modelCount):
            previousPosition += positionInterval
            modelPosition = previousPosition
            _, motor = self._lineModels[idx]
            segmentScale = Math.Vector3(modelScale.x, modelScale.y, modelScale.z * modelStretch)
            motor.signal = math_utils.createSRTMatrix(segmentScale, modelRotationVector, modelPosition)

    def _addIntersection(self, position):
        if self._style.modelIntersection:
            model = BigWorld.Model(self._style.modelIntersection)
            model.position = position
            model.scale = self._style.scaleIntersection
            addModel(model)
            self._intersections.append(model)

    def _clearLine(self):
        while self._lineModels:
            self.__popLineModel()

        self._clearIntersections()

    def _clearIntersections(self):
        for model in self._intersections:
            delModel(model)

        self._intersections = []

    def _projectToTerrain(self, pos):
        spaceID = BigWorld.player().spaceID
        if spaceID:
            upPoint = Math.Vector3(pos)
            upPoint.y += 1000
            downPoint = Math.Vector3(pos)
            downPoint.y = -1000
            collideRes = BigWorld.wg_collideSegment(spaceID, upPoint, downPoint, CollisionFlags.TRIANGLE_PROJECTILENOCOLLIDE)
            if collideRes is not None:
                return collideRes.closestPoint + self.overTerrainOffset
        return pos

    @staticmethod
    def _loadStyles():
        if _LineMarker.LINE_MARKER_STYLES is None:
            settingsData = ResMgr.openSection(_MARKERS_CONFIG_FILE + '/RTSMarkers/LineStyles')
            _LineMarker.LINE_MARKER_STYLES = {}
            for section in settingsData.values():
                newStyle = PathMarkerStyle(modelPath=section.readString('lineModelPath'), modelIntersection=section.readString('intersectionModelPath'), scaleMarker=section.readVector3('markerScale'), scalePath=section.readVector3('lineScale'), scaleIntersection=section.readVector3('intersectionScale'), offset=section.readVector3('terrainOffset'), intervalLength=section.readFloat('lineIntervalLength'), rotation=section.readVector3('lineRotation'), isStretchModel=section.readBool('isStretchLine'))
                _LineMarker.LINE_MARKER_STYLES[section.name] = newStyle

        return

    def __reserveModels(self, count):
        currentCount = len(self._lineModels)
        while currentCount < count:
            self.__addModel()
            currentCount += 1

        while currentCount > count:
            self.__popLineModel()
            currentCount -= 1

    def __addModel(self):
        model = BigWorld.Model(self._style.modelPath)
        motor = BigWorld.Servo(Math.Matrix())
        model.addMotor(motor)
        addModel(model)
        self._lineModels.append((model, motor))

    def __popLineModel(self):
        model, _ = self._lineModels.pop()
        delModel(model)


class PathMarker(_LineMarker):
    __slots__ = ()
    PATH_MARKER_STYLE = 'PathMarker'

    def __init__(self, position, targetPosition, queuePos):
        self._startListenOnCameraChanged()
        self._startListenOnHandleKeyEvent()
        super(PathMarker, self).__init__(position, targetPosition, queuePos, PathMarker.PATH_MARKER_STYLE)

    def fini(self):
        self._stopListenOnCameraChanged()
        self._stopListenOnHandleKeyEvent()
        super(PathMarker, self).fini()

    def _onQueuePosUpdated(self):
        self._updateLine()

    def _updateLine(self):
        super(PathMarker, self)._updateLine()
        if avatar_getter.isCommanderCtrlMode() or isShowAlternateUI():
            self._clearIntersections()
            fromPos, toPos = self._getLine()
            self._addIntersection(fromPos)
            if self.queuePos in (RTSCommandQueuePosition.LAST, RTSCommandQueuePosition.SINGLE):
                self._addIntersection(toPos)
        else:
            self._clearLine()

    def _onCameraChanged(self, cameraName, currentVehicleId=None):
        self._updateLine()

    def _handleKeyEvent(self, event):
        if event.key in (Keys.KEY_LALT, Keys.KEY_RALT):
            self._updateLine()


class AttackMarker(_LineMarker):
    __slots__ = ('_attackerVehProxy', '_targetVehProxy')
    ATTACK_MARKER_STYLE = 'AttackMarker'

    def __init__(self, attackerVehProxy, targetVehProxy, queuePos):
        self._attackerVehProxy = weakProxy(attackerVehProxy)
        self._targetVehProxy = weakProxy(targetVehProxy)
        position = self._attackerVehProxy.position
        targetPosition = self._targetVehProxy.position
        super(AttackMarker, self).__init__(position, targetPosition, queuePos, AttackMarker.ATTACK_MARKER_STYLE)

    def update(self):
        isAltDown = isShowAlternateUI()
        isCommanderCtrlMode = avatar_getter.isCommanderCtrlMode()
        isVisible = isCommanderCtrlMode and self._attackerVehProxy.isSelected or isAltDown or isAltDown and not isCommanderCtrlMode
        if not self._attackerVehProxy.isVisible or not isVisible:
            self._clearLine()
            return
        else:
            if self._isInQueue():
                self._position = self._attackerVehProxy.lastPosition
            else:
                self._position = self._attackerVehProxy.position
            if self._targetVehProxy.isVisible:
                self._targetPosition = self._targetVehProxy.position
            elif self._targetVehProxy.lastKnownPosition is not None:
                self._targetPosition = self._targetVehProxy.lastKnownPosition
            else:
                self._clearLine()
                return
            self._updateLine()
            return

    def _isInQueue(self):
        return self.queuePos not in (RTSCommandQueuePosition.SINGLE, RTSCommandQueuePosition.CURRENT)

    def _getLine(self):
        pathMarkerStyle = self.LINE_MARKER_STYLES[PathMarker.PATH_MARKER_STYLE]
        attackerOverTerrainOffset = self.overTerrainOffset if not self._isInQueue() else pathMarkerStyle.offset
        targetOverTerrainOffset = self.overTerrainOffset if self._targetVehProxy.isVisible else pathMarkerStyle.offset
        return (self._position + attackerOverTerrainOffset, self._targetPosition + targetOverTerrainOffset)


OperationCircleConfig = namedtuple('OperationCircleConfig', ['visualPath',
 'overTerrainHeight',
 'operationRadius',
 'operationRadiusSquared'])

class OperationCircle(_SimplexColorMarker):
    __slots__ = ('_vehicle', '__isVisible')
    _CUTOFF_DELTA = 3.0
    _CUTOFF_HEIGHT = 15.0
    _DO_CUTOFF = True
    _ONLY_ON_TERRAIN = True
    _CONFIG = None
    _ALLOWED_ORDERS = MOVEMENT_ORDERS
    _ALLOWED_MANNERS = (RTSManner.DEFENSIVE, RTSManner.SCOUT)

    def __init__(self, vehicle):
        self._loadConfig()
        self.__isVisible = False
        radius = self._CONFIG.operationRadius
        super(OperationCircle, self).__init__(position=Math.Vector3(0.0, 0.0, 0.0), yaw=0, visual=self._CONFIG.visualPath, size=Math.Vector2(radius * 2, radius * 2), overTerrainOffset=self._CONFIG.overTerrainHeight)
        self._vehicle = weakProxy(vehicle)
        self.model.visible = self.__isVisible

    def update(self, *args, **kwargs):
        vehicle = self._vehicle
        lastCommandInQueue = vehicle.lastCommandInQueue
        if lastCommandInQueue is not None:
            circlePos = lastCommandInQueue.position
            order = lastCommandInQueue.order
        else:
            circlePos = vehicle.targetPosition
            order = vehicle.order
        isVisible = circlePos is not None and vehicle.isSelected and avatar_getter.isCommanderCtrlMode() and order in self._ALLOWED_ORDERS and vehicle.manner in self._ALLOWED_MANNERS and (lastCommandInQueue is not None or (vehicle.position - circlePos).lengthSquared < self._CONFIG.operationRadiusSquared)
        if self.__isVisible != isVisible:
            self.model.visible = self.__isVisible = isVisible
        if isVisible:
            self.move(circlePos)
        return

    @classmethod
    def _loadConfig(cls):
        if cls._CONFIG:
            return
        settingsData = ResMgr.openSection(_MARKERS_CONFIG_FILE)['RTSMarkers']['OperationCircle']
        radius = settingsData.readFloat('operationRadius')
        cls._CONFIG = OperationCircleConfig(visualPath=settingsData.readString('visualPath'), overTerrainHeight=settingsData.readFloat('overTerrainHeight'), operationRadius=settingsData.readFloat('operationRadius'), operationRadiusSquared=radius * radius)
