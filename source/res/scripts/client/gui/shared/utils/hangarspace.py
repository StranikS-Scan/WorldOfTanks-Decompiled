# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/utils/HangarSpace.py
from Queue import Queue
from functools import wraps
import BigWorld
import Math
import Event
import Keys
import ResMgr
import constants
from debug_utils import LOG_DEBUG, LOG_DEBUG_DEV
from gui import g_mouseEventHandlers, InputHandler
from gui.ClientHangarSpace import ClientHangarSpace, _getHangarPath
from gui.Scaleform.Waiting import Waiting
from helpers import dependency, uniprof
from helpers.statistics import HANGAR_LOADING_STATE
from shared_utils import BoundMethodWeakref
from skeletons.gui.app_loader import IAppLoader
from skeletons.gui.game_control import IGameSessionController, IIGRController
from skeletons.gui.shared.utils import IHangarSpace
from skeletons.helpers.statistics import IStatisticsCollector
from gui import g_keyEventHandlers
from gui.shared import g_eventBus, events
from constants import IS_DEVELOPMENT
import AvatarInputHandler
from AvatarInputHandler.VideoCamera import VideoCamera
from gui.app_loader import settings as app_settings
from gui import GUI_CTRL_MODE_FLAG as _CTRL_FLAG
from gui.hangar_cameras.hangar_camera_common import CameraMovementStates
from gui.prb_control.events_dispatcher import g_eventDispatcher
_Q_CHECK_DELAY = 0.0

class _execute_after_hangar_space_inited(object):
    hangarSpace = dependency.descriptor(IHangarSpace)
    __slots__ = ('__queue',)

    def __init__(self):
        self.__queue = Queue()

    def __call__(self, func):

        @wraps(func)
        def wrapped(*args, **kwargs):
            self.storeData(func, *args, **kwargs)
            self.checkConditionForExit()

        return wrapped

    def checkConditionForExit(self):
        if not self.hangarSpace.spaceInited or not self.hangarSpace.space.getVehicleEntity():
            BigWorld.callback(_Q_CHECK_DELAY, self.checkConditionForExit)
            return
        self.delayCall()

    def storeData(self, func, *args, **kwargs):
        self.__queue.put((func, args, kwargs))

    def delayCall(self):
        while not self.__queue.empty():
            f, f_args, f_kwargs = self.__queue.get()
            f(*f_args, **f_kwargs)


g_execute_after_hangar_space_inited = _execute_after_hangar_space_inited()

class HangarVideoCameraController(object):
    hangarSpace = dependency.descriptor(IHangarSpace)
    appLoader = dependency.descriptor(IAppLoader)

    def __init__(self):
        self.__videoCamera = None
        self.__enabled = False
        self.__videoCamera = None
        return

    def init(self):
        if not IS_DEVELOPMENT:
            return
        else:
            rootSection = ResMgr.openSection(AvatarInputHandler.INPUT_HANDLER_CFG)
            if rootSection is None:
                return
            videoSection = rootSection['videoMode']
            if videoSection is None:
                return
            videoCameraSection = videoSection['camera']
            self.__videoCamera = VideoCamera(videoCameraSection)
            InputHandler.g_instance.onKeyDown += self.handleKeyEvent
            InputHandler.g_instance.onKeyUp += self.handleKeyEvent
            g_mouseEventHandlers.add(self.handleMouseEvent)
            return

    def destroy(self):
        if self.__videoCamera is None:
            return
        else:
            self.__videoCamera.destroy()
            InputHandler.g_instance.onKeyDown -= self.handleKeyEvent
            InputHandler.g_instance.onKeyUp -= self.handleKeyEvent
            g_mouseEventHandlers.discard(self.handleMouseEvent)
            return

    def handleKeyEvent(self, event):
        if self.__videoCamera is None:
            return
        else:
            if BigWorld.isKeyDown(Keys.KEY_CAPSLOCK) and event.isKeyDown() and event.key == Keys.KEY_F3:
                self.__enabled = not self.__enabled
                if self.__enabled:
                    self.__enableVideoCamera()
                else:
                    self.__disableVideoCamera()
            return self.__videoCamera.handleKeyEvent(event.key, event.isKeyDown()) if self.__enabled else False

    def __enableVideoCamera(self):
        playerVehicle = self.hangarSpace.space.getVehicleEntity()
        if playerVehicle is not None and playerVehicle.state != CameraMovementStates.ON_OBJECT:
            self.__enabled = False
            return
        else:
            self.__videoCamera.enable()
            self.appLoader.detachCursor(app_settings.APP_NAME_SPACE.SF_LOBBY)
            BigWorld.player().objectsSelectionEnabled(False)
            g_eventDispatcher.loadHangar()
            return

    def __disableVideoCamera(self):
        self.__videoCamera.disable()
        BigWorld.camera(self.hangarSpace.space.camera)
        self.appLoader.attachCursor(app_settings.APP_NAME_SPACE.SF_LOBBY, _CTRL_FLAG.GUI_ENABLED)
        BigWorld.player().objectsSelectionEnabled(True)

    def handleMouseEvent(self, event):
        if self.__videoCamera is None:
            return
        else:
            return self.__videoCamera.handleMouseEvent(event.dx, event.dy, event.dz) if self.__enabled else False


class HangarSpace(IHangarSpace):
    isPremium = property(lambda self: self.__isSpacePremium if self.__spaceInited else self.__delayedIsPremium)
    gameSession = dependency.descriptor(IGameSessionController)
    igrCtrl = dependency.descriptor(IIGRController)
    statsCollector = dependency.descriptor(IStatisticsCollector)

    def __init__(self):
        self.__space = None
        self.__videoCameraController = HangarVideoCameraController()
        self.__inited = False
        self.__spaceInited = False
        self.__isModelLoaded = False
        self.__isSpacePremium = False
        self.__igrSpaceType = constants.IGR_TYPE.NONE
        self.__delayedIsPremium = False
        self.__delayedForceRefresh = False
        self.__delayedRefreshCallback = None
        self.__spaceDestroyedDuringLoad = False
        self.__lastUpdatedVehicle = None
        self.onSpaceRefresh = Event.Event()
        self.onSpaceRefreshCompleted = Event.Event()
        self.onSpaceCreating = Event.Event()
        self.onSpaceCreate = Event.Event()
        self.onSpaceDestroy = Event.Event()
        self.onSpaceChanged = Event.Event()
        self.onMouseEnter = Event.Event()
        self.onMouseExit = Event.Event()
        self.onMouseDown = Event.Event()
        self.onMouseUp = Event.Event()
        self.onHeroTankReady = Event.Event()
        self.onVehicleChanged = Event.Event()
        self.onVehicleChangeStarted = Event.Event()
        self.onSpaceChangedByAction = Event.Event()
        self.onNotifyCursorOver3dScene = Event.Event()
        self.__isCursorOver3DScene = False
        return

    @property
    def space(self):
        return self.__space if self.spaceInited else None

    @property
    def spaceID(self):
        return self.__space.getSpaceID() if self.__space else None

    @property
    def inited(self):
        return self.__inited

    @property
    def spaceInited(self):
        return self.__spaceInited

    @property
    def isCursorOver3DScene(self):
        return self.__isCursorOver3DScene

    @property
    def isModelLoaded(self):
        return self.__isModelLoaded

    @property
    def spacePath(self):
        return None if self.__space is None else self.__space.spacePath

    @property
    def visibilityMask(self):
        return None if self.__space is None else self.__space.visibilityMask

    def spaceLoading(self):
        return self.__space.spaceLoading() if self.__space is not None else False

    def getAnchorParams(self, slotId, areaId, regionId):
        return self.__space.getAnchorParams(slotId, areaId, regionId)

    def updateAnchorsParams(self, *args):
        self.__space.updateAnchorsParams(*args)

    def __onNotifyCursorOver3dScene(self, event):
        self.__isCursorOver3DScene = event.ctx.get('isOver3dScene', False)
        self.onNotifyCursorOver3dScene(self.__isCursorOver3DScene)

    @uniprof.regionDecorator(label='hangar.space.loading', scope='enter')
    def init(self, isPremium):
        if self.__space is None:
            self.__space = ClientHangarSpace(BoundMethodWeakref(self._changeDone))
        self.statsCollector.noteHangarLoadingState(HANGAR_LOADING_STATE.START_LOADING_SPACE)
        self.__videoCameraController.init()
        self.__spaceDestroyedDuringLoad = False
        if not self.__spaceInited:
            LOG_DEBUG('HangarSpace::init')
            Waiting.show('loadHangarSpace')
            self.__inited = True
            self.__isSpacePremium = isPremium
            self.__igrSpaceType = self.igrCtrl.getRoomType()
            self.__space.create(isPremium, self.__spaceDone)
            self.onSpaceCreating()
            if self.__lastUpdatedVehicle is not None:
                self.startToUpdateVehicle(self.__lastUpdatedVehicle)
            self.gameSession.onPremiumNotify += self.onPremiumChanged
            g_keyEventHandlers.add(self.__handleKeyEvent)
            g_eventBus.addListener(events.LobbySimpleEvent.NOTIFY_CURSOR_OVER_3DSCENE, self.__onNotifyCursorOver3dScene)
        return

    def refreshSpace(self, isPremium, forceRefresh=False):
        igrType = self.igrCtrl.getRoomType()
        if self.__isSpacePremium == isPremium and self.__igrSpaceType == igrType and not forceRefresh:
            return
        else:
            self.onSpaceRefresh()
            if not self.__spaceInited and self.__space.spaceLoading():
                LOG_DEBUG('HangarSpace::refreshSpace(isPremium={0!r:s}) - is delayed until space load is done'.format(isPremium))
                if self.__delayedRefreshCallback is None:
                    self.__delayedRefreshCallback = BigWorld.callback(0.1, self.__delayedRefresh)
                self.__delayedIsPremium = isPremium
                self.__delayedForceRefresh = forceRefresh
                return
            LOG_DEBUG('HangarSpace::refreshSpace(isPremium={0!r:s})'.format(isPremium))
            self.destroy()
            self.init(isPremium)
            self.__isSpacePremium = isPremium
            self.__igrSpaceType = igrType
            self.onSpaceRefreshCompleted()
            return

    def destroy(self):
        if self.__inited:
            g_keyEventHandlers.remove(self.__handleKeyEvent)
            g_eventBus.removeListener(events.LobbySimpleEvent.NOTIFY_CURSOR_OVER_3DSCENE, self.__onNotifyCursorOver3dScene)
        self.onSpaceDestroy(self.__spaceInited and not self.__spaceDestroyedDuringLoad)
        self.__videoCameraController.destroy()
        self.__isModelLoaded = False
        self.__isCursorOver3DScene = False
        if self.__spaceInited:
            LOG_DEBUG('HangarSpace::destroy')
            self.__inited = False
            self.__spaceInited = False
            self.__space.destroy()
        elif self.spaceLoading():
            LOG_DEBUG('HangarSpace::destroy - delayed until space load done')
            self.__spaceDestroyedDuringLoad = True
            self.__space.destroy()
            self.__inited = False
            self.__spaceInited = False
        if self.__delayedRefreshCallback is not None:
            BigWorld.cancelCallback(self.__delayedRefreshCallback)
            self.__delayedRefreshCallback = None
        self.gameSession.onPremiumNotify -= self.onPremiumChanged
        return

    @g_execute_after_hangar_space_inited
    @uniprof.regionDecorator(label='hangar.vehicle.loading', scope='enter')
    def updateVehicle(self, vehicle, outfit=None):
        if self.__inited:
            self.__isModelLoaded = False
            self.onVehicleChangeStarted()
            self.statsCollector.noteHangarLoadingState(HANGAR_LOADING_STATE.START_LOADING_VEHICLE)
            self.__space.recreateVehicle(vehicle.descriptor, vehicle.modelState, outfit=outfit)
            self.__lastUpdatedVehicle = vehicle
        else:
            Waiting.hide('loadHangarSpaceVehicle')

    def startToUpdateVehicle(self, vehicle, outfit=None):
        Waiting.show('loadHangarSpaceVehicle', isSingle=True)
        self.updateVehicle(vehicle, outfit)

    def updateVehicleDescriptor(self, descr):
        if self.__inited:
            self.__space.updateVehicleDescriptor(descr)

    def __handleKeyEvent(self, event):
        if event.key == Keys.KEY_LEFTMOUSE:
            if event.isKeyDown():
                self.onMouseDown()
            else:
                self.onMouseUp()

    @g_execute_after_hangar_space_inited
    def updatePreviewVehicle(self, vehicle, outfit=None):
        if self.__inited:
            self.__isModelLoaded = False
            self.onVehicleChangeStarted()
            Waiting.show('loadHangarSpaceVehicle', isSingle=True)
            self.__space.recreateVehicle(vehicle.descriptor, vehicle.modelState, outfit=outfit)
            self.__lastUpdatedVehicle = vehicle

    def getVehicleEntity(self):
        return self.__space.getVehicleEntity() if self.__inited else None

    def getVehicleEntityAppearance(self):
        entity = self.getVehicleEntity()
        return entity.appearance if entity is not None else None

    def updateVehicleOutfit(self, outfit):
        if self.__inited:
            self.__space.updateVehicleCustomization(outfit)

    def getCentralPointForArea(self, areaId):
        return self.__space.getCentralPointForArea(areaId) if self.__inited else Math.Vector3(0.0)

    @g_execute_after_hangar_space_inited
    def removeVehicle(self):
        if self.__inited:
            self.__isModelLoaded = False
            self.onVehicleChangeStarted()
            Waiting.show('loadHangarSpaceVehicle', isSingle=True)
            if self.__space is not None:
                self.__space.removeVehicle()
            Waiting.hide('loadHangarSpaceVehicle')
            self.__isModelLoaded = True
            self.onVehicleChanged()
            self.__lastUpdatedVehicle = None
        return

    def setVehicleSelectable(self, flag):
        self.__space.setVehicleSelectable(flag)

    def onPremiumChanged(self, isPremium, attrs, premiumExpiryTime):
        premiumHangar = _getHangarPath(True, self.__igrSpaceType)
        defaultHangar = _getHangarPath(False, self.__igrSpaceType)
        if premiumHangar != defaultHangar:
            self.refreshSpace(isPremium)
        self.__isSpacePremium = isPremium

    def resetLastUpdatedVehicle(self):
        self.__lastUpdatedVehicle = None
        return

    @uniprof.regionDecorator(label='hangar.space.loading', scope='exit')
    def __spaceDone(self):
        self.__spaceInited = True
        if self.__spaceDestroyedDuringLoad:
            self.destroy()
            self.__spaceDestroyedDuringLoad = False
        self.onSpaceCreate()
        Waiting.hide('loadHangarSpace')
        self.statsCollector.noteHangarLoadingState(HANGAR_LOADING_STATE.FINISH_LOADING_SPACE)
        self.statsCollector.noteHangarLoadingState(HANGAR_LOADING_STATE.HANGAR_READY)
        stats = self.statsCollector.getStatistics()
        player = BigWorld.player()
        if player is not None:
            LOG_DEBUG_DEV(stats)
            if stats['system'] and hasattr(player, 'logClientSystem'):
                BigWorld.player().logClientSystem(stats['system'])
            if stats['session'] and hasattr(player, 'logClientSessionStats'):
                BigWorld.player().logClientSessionStats(stats['session'])
        self.onHeroTankReady()
        return

    @uniprof.regionDecorator(label='hangar.vehicle.loading', scope='exit')
    def _changeDone(self):
        Waiting.hide('loadHangarSpaceVehicle')
        self.__isModelLoaded = True
        self.onVehicleChanged()
        self.statsCollector.noteHangarLoadingState(HANGAR_LOADING_STATE.FINISH_LOADING_VEHICLE)

    def __delayedRefresh(self):
        self.__delayedRefreshCallback = None
        if not self.__spaceInited:
            self.__delayedRefreshCallback = BigWorld.callback(0.1, self.__delayedRefresh)
            return
        else:
            self.refreshSpace(self.__delayedIsPremium, self.__delayedForceRefresh)
            return
