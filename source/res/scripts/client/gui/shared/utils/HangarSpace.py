# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/utils/HangarSpace.py
import BigWorld
import Event
import Keys
import ResMgr
import constants
from debug_utils import LOG_DEBUG
from gui import g_mouseEventHandlers, InputHandler
from gui.ClientHangarSpace import ClientHangarSpace
from gui.Scaleform.Waiting import Waiting
from helpers import dependency
from helpers.statistics import HANGAR_LOADING_STATE
from skeletons.gui.game_control import IGameSessionController, IIGRController
from skeletons.helpers.statistics import IStatisticsCollector

class HangarVideoCameraController:
    import AvatarInputHandler
    from AvatarInputHandler.VideoCamera import VideoCamera

    def __init__(self):
        self.__videoCamera = None
        self.__enabled = False
        self.__overriddenCamera = None
        self.__videoCamera = None
        return

    def init(self):
        rootSection = ResMgr.openSection(HangarVideoCameraController.AvatarInputHandler._INPUT_HANDLER_CFG)
        if rootSection is None:
            return
        else:
            videoSection = rootSection['videoMode']
            if videoSection is None:
                return
            if not videoSection.readBool('enableInHangar', False):
                return
            videoCameraSection = videoSection['camera']
            self.__videoCamera = HangarVideoCameraController.VideoCamera(videoCameraSection)
            self.__overriddenCamera = BigWorld.camera()
            InputHandler.g_instance.onKeyDown += self.handleKeyEvent
            InputHandler.g_instance.onKeyUp += self.handleKeyEvent
            g_mouseEventHandlers.add(self.handleMouseEvent)
            return

    def destroy(self):
        if self.__videoCamera is None:
            return
        else:
            self.__videoCamera.destroy()
            BigWorld.camera(self.__overriddenCamera)
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
                    self.__overriddenCamera = BigWorld.camera()
                    self.__videoCamera.enable()
                else:
                    self.__videoCamera.disable()
                    BigWorld.camera(self.__overriddenCamera)
            return self.__videoCamera.handleKeyEvent(event.key, event.isKeyDown()) if self.__enabled else False

    def handleMouseEvent(self, event):
        if self.__videoCamera is None:
            return
        else:
            return self.__videoCamera.handleMouseEvent(event.dx, event.dy, event.dz) if self.__enabled else False


class _HangarSpace(object):
    isPremium = property(lambda self: self.__isSpacePremium if self.__spaceInited else self.__delayedIsPremium)
    gameSession = dependency.descriptor(IGameSessionController)
    igrCtrl = dependency.descriptor(IIGRController)
    statsCollector = dependency.descriptor(IStatisticsCollector)

    def __init__(self):
        self.__space = ClientHangarSpace()
        self.__videoCameraController = HangarVideoCameraController()
        self.__inited = False
        self.__spaceInited = False
        self.__isSpacePremium = False
        self.__igrSpaceType = constants.IGR_TYPE.NONE
        self.__delayedIsPremium = False
        self.__delayedForceRefresh = False
        self.__delayedRefreshCallback = None
        self.__spaceDestroyedDuringLoad = False
        self.__lastUpdatedVehicle = None
        self.onSpaceCreate = Event.Event()
        self.onObjectSelected = Event.Event()
        self.onObjectUnselected = Event.Event()
        self.onObjectClicked = Event.Event()
        self.onRequestOpenWindowsUpdate = Event.Event()
        return

    @property
    def space(self):
        return self.__space if self.spaceInited else None

    @property
    def inited(self):
        return self.__inited

    @property
    def spaceInited(self):
        return self.__spaceInited

    def spaceLoading(self):
        return self.__space.spaceLoading()

    def init(self, isPremium):
        self.statsCollector.noteHangarLoadingState(HANGAR_LOADING_STATE.START_LOADING_SPACE)
        self.__videoCameraController.init()
        self.__spaceDestroyedDuringLoad = False
        if not self.__spaceInited:
            LOG_DEBUG('_HangarSpace::init')
            Waiting.show('loadHangarSpace')
            self.__inited = True
            self.__isSpacePremium = isPremium
            self.__igrSpaceType = self.igrCtrl.getRoomType()
            self.__space.create(isPremium, self.__spaceDone)
            if self.__lastUpdatedVehicle is not None:
                self.updateVehicle(self.__lastUpdatedVehicle)
            self.gameSession.onPremiumNotify += self.onPremiumChanged
        return

    def refreshSpace(self, isPremium, forceRefresh=False):
        igrType = self.igrCtrl.getRoomType()
        if self.__isSpacePremium == isPremium and self.__igrSpaceType == igrType and not forceRefresh:
            return
        elif not self.__spaceInited and self.__space.spaceLoading():
            LOG_DEBUG('_HangarSpace::refreshSpace(isPremium={0!r:s}) - is delayed until space load is done'.format(isPremium))
            if self.__delayedRefreshCallback is None:
                self.__delayedRefreshCallback = BigWorld.callback(0.1, self.__delayedRefresh)
            self.__delayedIsPremium = isPremium
            self.__delayedForceRefresh = forceRefresh
            return
        else:
            LOG_DEBUG('_HangarSpace::refreshSpace(isPremium={0!r:s})'.format(isPremium))
            self.destroy()
            self.init(isPremium)
            self.__isSpacePremium = isPremium
            self.__igrSpaceType = igrType
            return

    def destroy(self):
        self.__videoCameraController.destroy()
        if self.__spaceInited:
            LOG_DEBUG('_HangarSpace::destroy')
            self.__inited = False
            self.__spaceInited = False
            self.__space.destroy()
        elif self.spaceLoading():
            LOG_DEBUG('_HangarSpace::destroy - delayed until space load done')
            self.__spaceDestroyedDuringLoad = True
            self.__space.destroy()
            self.__inited = False
            self.__spaceInited = False
        if self.__delayedRefreshCallback is not None:
            BigWorld.cancelCallback(self.__delayedRefreshCallback)
            self.__delayedRefreshCallback = None
        self.gameSession.onPremiumNotify -= self.onPremiumChanged
        return

    def updateVehicle(self, vehicle):
        if self.__inited:
            Waiting.show('loadHangarSpaceVehicle', True)
            self.statsCollector.noteHangarLoadingState(HANGAR_LOADING_STATE.START_LOADING_VEHICLE)
            self.__space.recreateVehicle(vehicle.getCustomizedDescriptor(), vehicle.modelState, self.__changeDone)
            self.__lastUpdatedVehicle = vehicle

    def updatePreviewVehicle(self, vehicle):
        if self.__inited:
            Waiting.show('loadHangarSpaceVehicle', True)
            self.__space.recreateVehicle(vehicle.descriptor, vehicle.modelState, self.__changeDone)
            self.__lastUpdatedVehicle = vehicle

    def removeVehicle(self):
        if self.__inited:
            Waiting.show('loadHangarSpaceVehicle')
            if self.__space is not None:
                self.__space.removeVehicle()
            Waiting.hide('loadHangarSpaceVehicle')
            self.__lastUpdatedVehicle = None
        return

    def onPremiumChanged(self, isPremium, attrs, premiumExpiryTime):
        self.refreshSpace(isPremium)

    def __spaceDone(self):
        self.__spaceInited = True
        if self.__spaceDestroyedDuringLoad:
            self.__spaceDestroyedDuringLoad = False
            self.destroy()
        self.onSpaceCreate()
        Waiting.hide('loadHangarSpace')
        self.statsCollector.noteHangarLoadingState(HANGAR_LOADING_STATE.FINISH_LOADING_SPACE)
        self.statsCollector.noteHangarLoadingState(HANGAR_LOADING_STATE.HANGAR_READY, showSummaryNow=True)

    def __changeDone(self):
        Waiting.hide('loadHangarSpaceVehicle')
        self.statsCollector.noteHangarLoadingState(HANGAR_LOADING_STATE.FINISH_LOADING_VEHICLE)

    def __delayedRefresh(self):
        self.__delayedRefreshCallback = None
        if not self.__spaceInited:
            self.__delayedRefreshCallback = BigWorld.callback(0.1, self.__delayedRefresh)
            return
        else:
            self.refreshSpace(self.__delayedIsPremium, self.__delayedForceRefresh)
            return

    def leftButtonClicked(self):
        self.onObjectClicked()


g_hangarSpace = _HangarSpace()
