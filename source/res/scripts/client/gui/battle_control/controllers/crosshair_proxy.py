# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/controllers/crosshair_proxy.py
import Event
import GUI
from AvatarInputHandler import aih_global_binding, aih_constants
from gui.battle_control.battle_constants import BATTLE_CTRL_ID, CROSSHAIR_VIEW_ID, STRATEGIC_CAMERA_ID
from gui.battle_control.controllers.interfaces import IBattleController
from helpers import dependency
from skeletons.account_helpers.settings_core import ISettingsCore
_BINDING_ID = aih_global_binding.BINDING_ID
_CTRL_MODE = aih_constants.CTRL_MODE_NAME
_MARKER_TYPE = aih_constants.GUN_MARKER_TYPE
_MARKER_FLAG = aih_constants.GUN_MARKER_FLAG
_STRATEGIC_CAMERA = aih_constants.STRATEGIC_CAMERA
_CTRL_MODE_TO_VIEW_ID = {_CTRL_MODE.ARCADE: CROSSHAIR_VIEW_ID.ARCADE,
 _CTRL_MODE.STRATEGIC: CROSSHAIR_VIEW_ID.STRATEGIC,
 _CTRL_MODE.ARTY: CROSSHAIR_VIEW_ID.STRATEGIC,
 _CTRL_MODE.SNIPER: CROSSHAIR_VIEW_ID.SNIPER,
 _CTRL_MODE.POSTMORTEM: CROSSHAIR_VIEW_ID.POSTMORTEM,
 _CTRL_MODE.FALLOUT_DEATH: CROSSHAIR_VIEW_ID.POSTMORTEM}
_GUN_MARKERS_SET_IDS = (_BINDING_ID.GUN_MARKERS_FLAGS,
 _BINDING_ID.CLIENT_GUN_MARKER_DATA_PROVIDER,
 _BINDING_ID.SERVER_GUN_MARKER_DATA_PROVIDER,
 _BINDING_ID.CLIENT_SPG_GUN_MARKER_DATA_PROVIDER,
 _BINDING_ID.SERVER_SPG_GUN_MARKER_DATA_PROVIDER,
 _BINDING_ID.CLIENT_SUB_GUN_MARKER_DATA_PROVIDER)
_STRATEGIC_CAMERA_TO_ID = {_STRATEGIC_CAMERA.AERIAL: STRATEGIC_CAMERA_ID.AERIAL,
 _STRATEGIC_CAMERA.TRAJECTORY: STRATEGIC_CAMERA_ID.TRAJECTORY}

def getCrosshairViewIDByCtrlMode(ctrlMode):
    """Gets viewID by avatar control mode.
    If control mode has not UI, that function return CROSSHAIR_VIEW_ID.UNDEFINED
    :param ctrlMode: string containing one of CTRL_MODE_NAME.
    :return: integer containing one of CROSSHAIR_VIEW_ID.
    """
    if ctrlMode in _CTRL_MODE_TO_VIEW_ID:
        viewID = _CTRL_MODE_TO_VIEW_ID[ctrlMode]
    else:
        viewID = CROSSHAIR_VIEW_ID.UNDEFINED
    return viewID


class GunMarkersSetInfo(object):
    clientMarkerDataProvider = aih_global_binding.bindRO(_BINDING_ID.CLIENT_GUN_MARKER_DATA_PROVIDER)
    clientSubMarkerDataProvider = aih_global_binding.bindRO(_BINDING_ID.CLIENT_SUB_GUN_MARKER_DATA_PROVIDER)
    clientSPGMarkerDataProvider = aih_global_binding.bindRO(_BINDING_ID.CLIENT_SPG_GUN_MARKER_DATA_PROVIDER)
    serverMarkerDataProvider = aih_global_binding.bindRO(_BINDING_ID.SERVER_GUN_MARKER_DATA_PROVIDER)
    serverSPGMarkerDataProvider = aih_global_binding.bindRO(_BINDING_ID.SERVER_SPG_GUN_MARKER_DATA_PROVIDER)
    __gunMarkersFlags = aih_global_binding.bindRO(_BINDING_ID.GUN_MARKERS_FLAGS)

    @property
    def isClientMarkerActivated(self):
        return self.__isFlagActivated(_MARKER_FLAG.CLIENT_MODE_ENABLED)

    @property
    def isServerMarkerActivated(self):
        return self.__isFlagActivated(_MARKER_FLAG.SERVER_MODE_ENABLED)

    @property
    def isEnabledInVideoMode(self):
        return self.__isFlagActivated(_MARKER_FLAG.VIDEO_MODE_ENABLED)

    @property
    def isArtyHitActivated(self):
        return self.__isFlagActivated(_MARKER_FLAG.ARTY_HIT_ENABLED)

    def __isFlagActivated(self, flag):
        return self.__gunMarkersFlags & _MARKER_FLAG.CONTROL_ENABLED > 0 and self.__gunMarkersFlags & flag > 0


class CrosshairDataProxy(IBattleController):
    """This class is proxy of descriptors from aim_global_binding.
    It listens changes of descriptors, calculates/converts to required values
    or just transferred values via event."""
    __slots__ = ('__width', '__height', '__positionX', '__positionY', '__scale', '__viewID', '__eManager', '__isArenaStarted', '__strategicCameraID', 'onCrosshairViewChanged', 'onCrosshairOffsetChanged', 'onCrosshairSizeChanged', 'onCrosshairPositionChanged', 'onCrosshairScaleChanged', 'onCrosshairZoomFactorChanged', 'onGunMarkerStateChanged', 'onGunMarkersSetChanged', 'onStrategicCameraChanged')
    settingsCore = dependency.descriptor(ISettingsCore)
    __ctrlMode = aih_global_binding.bindRO(_BINDING_ID.CTRL_MODE_NAME)
    __offset = aih_global_binding.bindRO(_BINDING_ID.AIM_OFFSET)
    __zoomFactor = aih_global_binding.bindRO(_BINDING_ID.ZOOM_FACTOR)

    def __init__(self):
        super(CrosshairDataProxy, self).__init__()
        self.__width = 0
        self.__height = 0
        self.__positionX = 0
        self.__positionY = 0
        self.__scale = 1.0
        self.__viewID = CROSSHAIR_VIEW_ID.UNDEFINED
        self.__strategicCameraID = STRATEGIC_CAMERA_ID.UNDEFINED
        self.__eManager = Event.EventManager()
        self.onCrosshairViewChanged = Event.Event(self.__eManager)
        self.onCrosshairOffsetChanged = Event.Event(self.__eManager)
        self.onCrosshairSizeChanged = Event.Event(self.__eManager)
        self.onCrosshairPositionChanged = Event.Event(self.__eManager)
        self.onCrosshairScaleChanged = Event.Event(self.__eManager)
        self.onCrosshairZoomFactorChanged = Event.Event(self.__eManager)
        self.onGunMarkerStateChanged = Event.Event(self.__eManager)
        self.onGunMarkersSetChanged = Event.Event(self.__eManager)
        self.onStrategicCameraChanged = Event.Event(self.__eManager)

    def getControllerID(self):
        """Gets unique ID of controller.
        :return: integer containing value of BATTLE_CTRL_ID.CROSSHAIR.
        """
        return BATTLE_CTRL_ID.CROSSHAIR

    def startControl(self, *args):
        """ Starts to control."""
        self.settingsCore.interfaceScale.onScaleChanged += self.__onScaleFactorChanged
        aih_global_binding.subscribe(_BINDING_ID.CTRL_MODE_NAME, self.__onAvatarControlModeChanged)
        aih_global_binding.subscribe(_BINDING_ID.AIM_OFFSET, self.__onAimOffsetChanged)
        aih_global_binding.subscribe(_BINDING_ID.CLIENT_GUN_MARKER_STATE, self.__onClientGunMarkerStateChanged)
        aih_global_binding.subscribe(_BINDING_ID.SUB_GUN_MARKER_STATE, self.__onSubGunMarkerStateChanged)
        aih_global_binding.subscribe(_BINDING_ID.SERVER_GUN_MARKER_STATE, self.__onServerGunMarkerStateChanged)
        aih_global_binding.subscribe(_BINDING_ID.ZOOM_FACTOR, self.__onZoomFactorChanged)
        aih_global_binding.subscribe(_BINDING_ID.STRATEGIC_CAMERA, self.__onStrategicCameraChanged)
        for bindingID in _GUN_MARKERS_SET_IDS:
            aih_global_binding.subscribe(bindingID, self.__onGunMarkersSetChanged)

        self.__viewID = getCrosshairViewIDByCtrlMode(self.__ctrlMode)
        self.__scale = round(self.settingsCore.interfaceScale.get(), 1)
        self.__calculateSize(notify=False)
        self.__calculatePosition(notify=False)

    def stopControl(self):
        """ Stops to control."""
        self.__eManager.clear()
        self.settingsCore.interfaceScale.onScaleChanged -= self.__onScaleFactorChanged
        aih_global_binding.unsubscribe(_BINDING_ID.CTRL_MODE_NAME, self.__onAvatarControlModeChanged)
        aih_global_binding.unsubscribe(_BINDING_ID.AIM_OFFSET, self.__onAimOffsetChanged)
        aih_global_binding.unsubscribe(_BINDING_ID.CLIENT_GUN_MARKER_STATE, self.__onClientGunMarkerStateChanged)
        aih_global_binding.unsubscribe(_BINDING_ID.SUB_GUN_MARKER_STATE, self.__onSubGunMarkerStateChanged)
        aih_global_binding.unsubscribe(_BINDING_ID.SERVER_GUN_MARKER_STATE, self.__onServerGunMarkerStateChanged)
        aih_global_binding.unsubscribe(_BINDING_ID.ZOOM_FACTOR, self.__onZoomFactorChanged)
        aih_global_binding.unsubscribe(_BINDING_ID.STRATEGIC_CAMERA, self.__onStrategicCameraChanged)
        for bindingID in _GUN_MARKERS_SET_IDS:
            aih_global_binding.unsubscribe(bindingID, self.__onGunMarkersSetChanged)

    def getViewID(self):
        """Gets current unique ID of crosshair view.
        :return: integer containing one of CROSSHAIR_VIEW_ID.
        """
        return self.__viewID

    def getSize(self):
        """Gets size of crosshair view.
        :return: tuple(width, height).
        """
        return (self.__width, self.__height)

    def getPosition(self):
        """Gets position of crosshair view.
        :return: tuple(x, y).
        """
        return (self.__positionX, self.__positionY)

    def getScaledPosition(self):
        """Gets position of crosshair view that is divided by the scale.
        :return: tuple(x, y).
        """
        if self.__scale > 1.0:
            posX = int(self.__positionX / self.__scale)
            posY = int(self.__positionY / self.__scale)
        else:
            posX = int(self.__positionX)
            posY = int(self.__positionY)
        return (posX, posY)

    def getDisaredPosition(self):
        """ This method invokes 'getScaledPosition' in usual cases.
        Special case, when player switches on to arty mode, when camera is moved with interpolation,
        this method returns center of screen with scale. Because of we do not have mechanics
        to predict when camera will be in desired position without reducing of performance,
        see WOTD-83447."""
        if self.__ctrlMode == _CTRL_MODE.ARTY:
            if self.__scale > 1.0:
                posX = int(0.5 * self.__width / self.__scale)
                posY = int(0.5 * self.__height / self.__scale)
            else:
                posX = int(0.5 * self.__width)
                posY = int(0.5 * self.__height)
            return (posX, posY)
        return self.getScaledPosition()

    def getScaleFactor(self):
        """Gets scale of crosshair view.
        :return: float containing scale factor.
        """
        return self.__scale

    def getOffset(self):
        """Gets offset of crosshair view.
        :return: tuple(x, y).
        """
        return (self.__offset.x, self.__offset.y)

    def getZoomFactor(self):
        """Gets zoom factor.
        :return: float containing zoom factor.
        """
        return self.__zoomFactor

    def getStrategicCameraID(self):
        """
        Gets current strategic camera id for Strategic mode
        @return: integer containing one of STRATEGIC_CAMERA_ID.
        """
        return self.__strategicCameraID

    @staticmethod
    def getGunMarkersSetInfo():
        return GunMarkersSetInfo()

    def __calculateSize(self, notify=True):
        width, height = GUI.screenResolution()[:2]
        if self.__width != width or self.__height != height:
            self.__width = width
            self.__height = height
            if notify:
                self.onCrosshairSizeChanged(self.__width, self.__height)

    def __calculatePosition(self, notify=True):
        """Calculates position of panel's center. Screen size is in pixel.
        Offset is in clip metric (from -1 to 1, 0 - center of screen).
        :param notify: bool.
        """
        posX = int(0.5 * self.__width * (1.0 + self.__offset.x))
        posY = int(0.5 * self.__height * (1.0 - self.__offset.y))
        if self.__positionX != posX or self.__positionY != posY:
            self.__positionX = posX
            self.__positionY = posY
            if notify:
                self.onCrosshairPositionChanged(posX, posY)

    def __setGunMarkerState(self, markerType, value):
        assert len(value) == 3
        position, dir, collision = value
        self.onGunMarkerStateChanged(markerType, position, dir, collision)

    def __onAvatarControlModeChanged(self, ctrlMode):
        viewID = getCrosshairViewIDByCtrlMode(ctrlMode)
        if self.__viewID != viewID:
            self.__viewID = viewID
            self.onCrosshairViewChanged(viewID)

    def __onAimOffsetChanged(self, offset):
        self.onCrosshairOffsetChanged(offset.x, offset.y)
        self.__calculatePosition()

    def __onScaleFactorChanged(self, scale):
        scale = round(scale, 1)
        if self.__scale != scale:
            self.__scale = scale
            self.onCrosshairScaleChanged(scale)
        self.__calculateSize()
        self.__calculatePosition()

    def __onClientGunMarkerStateChanged(self, value):
        self.__setGunMarkerState(_MARKER_TYPE.CLIENT, value)

    def __onSubGunMarkerStateChanged(self, value):
        self.__setGunMarkerState(_MARKER_TYPE.SUB, value)

    def __onServerGunMarkerStateChanged(self, value):
        self.__setGunMarkerState(_MARKER_TYPE.SERVER, value)

    def __onZoomFactorChanged(self, zoomFactor):
        self.onCrosshairZoomFactorChanged(zoomFactor)

    def __onGunMarkersSetChanged(self, _):
        self.onGunMarkersSetChanged(self.getGunMarkersSetInfo())

    def __onStrategicCameraChanged(self, camera):
        if camera in _STRATEGIC_CAMERA_TO_ID:
            cameraID = _STRATEGIC_CAMERA_TO_ID[camera]
        else:
            cameraID = STRATEGIC_CAMERA_ID.UNDEFINED
        if self.__strategicCameraID != cameraID:
            self.__strategicCameraID = cameraID
            self.onStrategicCameraChanged(cameraID)
