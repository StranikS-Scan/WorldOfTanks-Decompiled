# Embedded file name: scripts/client/gui/shared/utils/HangarSpace.py
import BigWorld
import Event
import Keys
import ResMgr
from account_shared import getCustomizedVehCompDescr
from gui.shared import g_itemsCache
from items import vehicles
import constants
from gui import game_control, g_mouseEventHandlers, InputHandler
from gui.ClientHangarSpace import ClientHangarSpace
from gui.Scaleform.Waiting import Waiting
from gui.LobbyContext import g_lobbyContext
from debug_utils import LOG_DEBUG

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
            if self.__enabled:
                return self.__videoCamera.handleKeyEvent(event.key, event.isKeyDown())
            return False

    def handleMouseEvent(self, event):
        if self.__videoCamera is None:
            return
        elif self.__enabled:
            return self.__videoCamera.handleMouseEvent(event.dx, event.dy, event.dz)
        else:
            return False


class _HangarSpace(object):
    isPremium = property(lambda self: (self.__isSpacePremium if self.__spaceInited else self.__delayedIsPremium))

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
        from helpers.statistics import g_statistics
        g_statistics.subscribeToHangarSpaceCreate(self.onSpaceCreate)
        return

    @property
    def space(self):
        if self.spaceInited:
            return self.__space
        else:
            return None

    @property
    def inited(self):
        return self.__inited

    @property
    def spaceInited(self):
        return self.__spaceInited

    def spaceLoading(self):
        return self.__space.spaceLoading()

    def init(self, isPremium):
        self.__videoCameraController.init()
        self.__spaceDestroyedDuringLoad = False
        if not self.__spaceInited:
            LOG_DEBUG('_HangarSpace::init')
            Waiting.show('loadHangarSpace')
            self.__inited = True
            self.__isSpacePremium = isPremium
            self.__igrSpaceType = game_control.g_instance.igr.getRoomType()
            self.__space.create(isPremium, self.__spaceDone)
            if self.__lastUpdatedVehicle is not None:
                self.updateVehicle(self.__lastUpdatedVehicle)
            game_control.g_instance.gameSession.onPremiumNotify += self.onPremiumChanged
        self.playHangarMusic()
        return

    def refreshSpace(self, isPremium, forceRefresh = False):
        igrType = game_control.g_instance.igr.getRoomType()
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
        game_control.g_instance.gameSession.onPremiumNotify -= self.onPremiumChanged
        return

    def _stripVehCompDescrIfRoaming(self, vehCompDescr):
        serverSettings = g_lobbyContext.getServerSettings()
        if serverSettings is not None and serverSettings.roaming.isInRoaming():
            vehCompDescr = vehicles.stripCustomizationFromVehicleCompactDescr(vehCompDescr, True, True, False)[0]
        return vehicles.VehicleDescr(compactDescr=vehCompDescr)

    def updateVehicle(self, vehicle):
        if self.__inited:
            Waiting.show('loadHangarSpaceVehicle', True)
            igrRoomType = game_control.g_instance.igr.getRoomType()
            igrLayout = g_itemsCache.items.inventory.getIgrCustomizationsLayout()
            updatedVehCompactDescr = getCustomizedVehCompDescr(igrLayout, vehicle.invID, igrRoomType, vehicle.descriptor.makeCompactDescr())
            self.__space.recreateVehicle(self._stripVehCompDescrIfRoaming(updatedVehCompactDescr), vehicle.modelState, self.__changeDone)
            self.__lastUpdatedVehicle = vehicle

    def removeVehicle(self):
        if self.__inited:
            Waiting.show('loadHangarSpaceVehicle')
            if self.__space is not None:
                self.__space.removeVehicle()
            self.__changeDone()
            self.__lastUpdatedVehicle = None
        return

    def playHangarMusic(self, restart = False):
        if self.__space is not None:
            self.__space.playHangarMusic(restart)
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

    def __changeDone(self):
        Waiting.hide('loadHangarSpaceVehicle')

    def __delayedRefresh(self):
        self.__delayedRefreshCallback = None
        if not self.__spaceInited:
            self.__delayedRefreshCallback = BigWorld.callback(0.1, self.__delayedRefresh)
            return
        else:
            self.refreshSpace(self.__delayedIsPremium, self.__delayedForceRefresh)
            return


g_hangarSpace = _HangarSpace()
