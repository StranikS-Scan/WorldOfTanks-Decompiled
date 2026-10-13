# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: portal/scripts/client/portal/gui/battle_control/controllers/super_boss_transition/super_boss_transition_controller.py
import typing
import BigWorld
import Math
from aih_constants import CTRL_MODE_NAME
from frameworks.wulf import WindowLayer
from gui.battle_control.controllers.interfaces import IBattleController
from gui.impl.gen import R
from gui.Scaleform.framework.entities.View import ViewKey
from helpers import dependency
from skeletons.gui.app_loader import IAppLoader
from skeletons.gui.lobby_context import ILobbyContext
from portal.gui.portal_gui_constants import VIEW_ALIAS as PORTAL_VIEW_ALIAS
from events_core_client.gui.impl.video_with_controls.video_view import VideoPrerequisites, VideoViewWindow, VideoView
from sound_gui_manager import CommonSoundSpaceSettings
from PortalBattleStateComponent import PortalBattleStateComponent
from portal_common.portal_constants import BattleState, PORTAL_GAME_PARAMS_KEY
from portal_common_cgf.portal_helpers import SUPER_BOSS_LABEL
from portal_constants import PORTAL_BATTLE_CTRL_ID
if typing.TYPE_CHECKING:
    from typing import Dict, List, Optional
    from gui.battle_control import BattleSessionSetup

class _SuperBossVideoView(VideoView):
    _COMMON_SOUND_SPACE = CommonSoundSpaceSettings(name='GF_VIDEO_VIEW', entranceStates={}, exitStates={}, persistentSounds=(), stoppableSounds=(), priorities=(), autoStart=True, enterEvent='ev_portal_transition_to_superbossfight_play', exitEvent='ev_portal_transition_to_superbossfight_stop')


class _SuperBossVideoViewWindow(VideoViewWindow):

    def __init__(self, prerequisites, parent=None, layer=WindowLayer.OVERLAY):
        super(_SuperBossVideoViewWindow, self).__init__(prerequisites, parent=parent, layer=layer)
        self.setContent(_SuperBossVideoView(R.views.lobby.events_core_client.video_view.VideoView(), prerequisites))


def _resolveVideoPath(videoKey):
    category, name = videoKey.split('/', 1)
    accessor = getattr(R.videos, category).dyn(name)
    return accessor()


class SuperBossTransitionController(IBattleController):
    __slots__ = ('__videoWindow', '__videoStartCallback')
    __appLoader = dependency.descriptor(IAppLoader)
    __lobbyContext = dependency.descriptor(ILobbyContext)
    _DEFAULT_ARCADE_CAMERA_DISTANCE = 15

    def __init__(self, setup):
        super(SuperBossTransitionController, self).__init__()
        self.__videoWindow = None
        self.__videoStartCallback = None
        return

    def startControl(self, *args):
        PortalBattleStateComponent.onBattleStateChanged += self.__onBattleStateChanged
        PortalBattleStateComponent.onBotVehiclePreparing += self.__onBotVehiclePreparing

    def stopControl(self):
        PortalBattleStateComponent.onBattleStateChanged -= self.__onBattleStateChanged
        PortalBattleStateComponent.onBotVehiclePreparing -= self.__onBotVehiclePreparing
        self.__cancelVideoStart()
        self.__closeVideoWindow()

    def getControllerID(self):
        return PORTAL_BATTLE_CTRL_ID.SUPER_BOSS_TRANSITION_CTRL

    def __onBattleStateChanged(self, battleState):
        if battleState == BattleState.SUPER_BOSS_TRANSITION:
            self.__scheduleVideoStart()
        elif battleState == BattleState.SUPER_BOSS_FIGHT:
            self.__stopVideo()

    def __scheduleVideoStart(self):
        self.__cancelVideoStart()
        delay = self.__getTransitionSettings()['transitionVideoStartDelay']
        self.__videoStartCallback = BigWorld.callback(delay, self.__startVideo)

    def __cancelVideoStart(self):
        if self.__videoStartCallback is not None:
            BigWorld.cancelCallback(self.__videoStartCallback)
            self.__videoStartCallback = None
        return

    def __startVideo(self):
        self.__videoStartCallback = None
        self.__closeVideoWindow()
        prerequisites = VideoPrerequisites(videoPath=_resolveVideoPath(self.__getTransitionVideoKey()), isControlsVisible=False, soundSpace=None, pauseOnMinimize=False, isCloseButtonVisible=False, startFadeIn=0.3, startFadeOut=0.15, endFadeIn=0.15, endFadeOut=0.3)
        parent = self.__getParentWindow()
        self.__videoWindow = _SuperBossVideoViewWindow(prerequisites, parent=parent, layer=WindowLayer.FULLSCREEN_WINDOW)
        self.__videoWindow.load()
        return

    def __getParentWindow(self):
        app = self.__appLoader.getApp()
        containerMgr = app.containerManager
        if containerMgr is not None:
            view = containerMgr.getViewByKey(ViewKey(PORTAL_VIEW_ALIAS.PORTAL_BATTLE_PAGE))
            if view is not None:
                return view.getParentWindow()
        return

    def __stopVideo(self):
        self.__cancelVideoStart()
        if self.__videoWindow is not None:
            self.__videoWindow.startClosing()
            self.__videoWindow = None
        return

    def __getTransitionSettings(self):
        portalConfig = self.__lobbyContext.getServerSettings().getSettings()[PORTAL_GAME_PARAMS_KEY]
        return portalConfig['scenario']['superBossTransitionSettings']

    def __getTransitionVideoKey(self):
        return self.__getTransitionSettings()['transitionVideo']

    def __closeVideoWindow(self):
        if self.__videoWindow is not None:
            self.__videoWindow.destroy()
            self.__videoWindow = None
        return

    def __onBotVehiclePreparing(self, spawnData):
        botLabel = spawnData.get('extra', {}).get('label')
        if botLabel != SUPER_BOSS_LABEL:
            return
        else:
            position = spawnData.get('position', (None, None))[0]
            if position is None:
                return
            self.__aimCameraAt(Math.Vector3(*position))
            return

    def __aimCameraAt(self, targetPosition):
        avatar = BigWorld.player()
        inputHandler = getattr(avatar, 'inputHandler', None)
        if inputHandler is None or inputHandler.ctrlModeName != CTRL_MODE_NAME.ARCADE:
            return
        else:
            camera = getattr(inputHandler.ctrl, 'camera', None)
            if camera is None:
                return
            vehicle = avatar.getVehicleAttached()
            if vehicle is None:
                return
            direction = targetPosition - vehicle.position
            camera.setCameraDistance(self._DEFAULT_ARCADE_CAMERA_DISTANCE)
            camera.setYawPitch(direction.yaw, -direction.pitch)
            return


def createSuperBossTransitionController(setup):
    return SuperBossTransitionController(setup)
