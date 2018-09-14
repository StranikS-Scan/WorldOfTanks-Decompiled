# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/controllers/crosshair_proxy.py
import Event
import GUI
from account_helpers.settings_core import g_settingsCore
from avatar_helpers import aim_global_binding
from gui.battle_control.battle_constants import getCrosshairViewIDByCtrlMode
from gui.battle_control.battle_constants import BATTLE_CTRL_ID, CROSSHAIR_VIEW_ID
from gui.battle_control.controllers.interfaces import IBattleController
_BINDING_ID = aim_global_binding.BINDING_ID

class CrosshairDataProxy(IBattleController):
    """This class is proxy of descriptors from aim_global_binding.
    It listens changes of descriptors, calculates/converts to required values
    or just transferred values via event."""
    __slots__ = ('__width', '__height', '__positionX', '__positionY', '__scale', '__viewID', '__eManager', 'onCrosshairViewChanged', 'onCrosshairOffsetChanged', 'onCrosshairSizeChanged', 'onCrosshairPositionChanged', 'onCrosshairScaleChanged', 'onCrosshairZoomFactorChanged', 'onGunMarkerPositionChanged')
    __ctrlMode = aim_global_binding.bind(aim_global_binding.BINDING_ID.CTRL_MODE_NAME)
    __offset = aim_global_binding.bind(aim_global_binding.BINDING_ID.AIM_OFFSET)
    __zoomFactor = aim_global_binding.bind(aim_global_binding.BINDING_ID.ZOOM_FACTOR)

    def __init__(self):
        super(CrosshairDataProxy, self).__init__()
        self.__width = 0
        self.__height = 0
        self.__positionX = 0
        self.__positionY = 0
        self.__scale = 1.0
        self.__viewID = CROSSHAIR_VIEW_ID.UNDEFINED
        self.__eManager = Event.EventManager()
        self.onCrosshairViewChanged = Event.Event(self.__eManager)
        self.onCrosshairOffsetChanged = Event.Event(self.__eManager)
        self.onCrosshairSizeChanged = Event.Event(self.__eManager)
        self.onCrosshairPositionChanged = Event.Event(self.__eManager)
        self.onCrosshairScaleChanged = Event.Event(self.__eManager)
        self.onCrosshairZoomFactorChanged = Event.Event(self.__eManager)
        self.onGunMarkerPositionChanged = Event.Event(self.__eManager)

    def getControllerID(self):
        """Gets unique ID of controller.
        :return: integer containing value of BATTLE_CTRL_ID.CROSSHAIR.
        """
        return BATTLE_CTRL_ID.CROSSHAIR

    def startControl(self, *args):
        """ Starts to control."""
        g_settingsCore.interfaceScale.onScaleChanged += self.__onScaleFactorChanged
        aim_global_binding.subscribe(_BINDING_ID.CTRL_MODE_NAME, self.__onAvatarControlModeChanged)
        aim_global_binding.subscribe(_BINDING_ID.AIM_OFFSET, self.__onAimOffsetChanged)
        aim_global_binding.subscribe(_BINDING_ID.GUN_MARKER_POSITION, self.__onGunMarkerPositionChanged)
        aim_global_binding.subscribe(_BINDING_ID.ZOOM_FACTOR, self.__onZoomFactorChanged)
        self.__viewID = getCrosshairViewIDByCtrlMode(self.__ctrlMode)
        self.__scale = round(g_settingsCore.interfaceScale.get(), 1)
        self.__calculateSize(nofity=False)
        self.__calculatePosition(nofity=False)

    def stopControl(self):
        """ Stops to control."""
        self.__eManager.clear()
        g_settingsCore.interfaceScale.onScaleChanged -= self.__onScaleFactorChanged
        aim_global_binding.unsubscribe(_BINDING_ID.CTRL_MODE_NAME, self.__onAvatarControlModeChanged)
        aim_global_binding.unsubscribe(_BINDING_ID.AIM_OFFSET, self.__onAimOffsetChanged)
        aim_global_binding.unsubscribe(_BINDING_ID.GUN_MARKER_POSITION, self.__onGunMarkerPositionChanged)
        aim_global_binding.unsubscribe(_BINDING_ID.ZOOM_FACTOR, self.__onZoomFactorChanged)

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

    def __calculateSize(self, nofity=True):
        width, height = GUI.screenResolution()[:2]
        if self.__width != width or self.__height != height:
            self.__width = width
            self.__height = height
            if nofity:
                self.onCrosshairSizeChanged(self.__width, self.__height)

    def __calculatePosition(self, nofity=True):
        posX = 0.5 * self.__width * (1.0 + self.__offset.x)
        posY = 0.5 * self.__height * (1.0 - self.__offset.y)
        if self.__scale > 1.0:
            posX = int(posX / self.__scale)
            posY = int(posY / self.__scale)
        else:
            posX = int(posX)
            posY = int(posY)
        if self.__positionX != posX or self.__positionY != posY:
            self.__positionX = posX
            self.__positionY = posY
            if nofity:
                self.onCrosshairPositionChanged(posX, posY)

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

    def __onGunMarkerPositionChanged(self, value):
        assert len(value) == 2
        position, relaxTime = value
        self.onGunMarkerPositionChanged(position, relaxTime)

    def __onZoomFactorChanged(self, zoomFactor):
        self.onCrosshairZoomFactorChanged(zoomFactor)
