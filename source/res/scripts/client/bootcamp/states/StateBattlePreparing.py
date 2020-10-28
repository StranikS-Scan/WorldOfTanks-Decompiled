# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/bootcamp/states/StateBattlePreparing.py
import BattleReplay
import BigWorld
import Settings
import SoundGroups
from PlayerEvents import g_playerEvents
from aih_constants import CTRL_MODE_NAME
from bootcamp.BootCampEvents import g_bootcampEvents
from bootcamp.BootcampConstants import CAMERA_START_DISTANCE
from bootcamp.BootcampLobbyHintsConfig import g_bootcampHintsConfig
from bootcamp.aop.battle_preparing import weave
from bootcamp.states import STATE
from bootcamp.states.AbstractState import AbstractState
from debug_utils_bootcamp import LOG_DEBUG_DEV_BOOTCAMP
from gui import GUI_CTRL_MODE_FLAG as _CTRL_FLAG
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.bootcamp.BCBattleLoadingSpaceEnv import BCBattleLoadingSpaceEnv
from gui.Scaleform.framework.managers.loaders import SFViewLoadParams
from gui.app_loader import settings as app_settings
from gui.prb_control.events_dispatcher import g_eventDispatcher
from gui.shared import events, g_eventBus, EVENT_BUS_SCOPE
from gui.sounds.filters import WWISEFilteredBootcampArenaFilter as BCFilter
from helpers import dependency, aop
from skeletons.gui.app_loader import IAppLoader, GuiGlobalSpaceID
from skeletons.gui.sounds import ISoundsController
from soft_exception import SoftException
_INTRO_VIDEO_PATH = 'videos/_tutorialInitial.usm'
_INTRO_VIDEO_LOOP_PATH = 'videos/_tutorialInitialLoop.usm'
_INTRO_VIDEO_MUSIC_START_EVENT = 'bc_music_video_intro_start'
_INTRO_VIDEO_MUSIC_STOP_EVENT = 'bc_music_video_intro_stop'
_INTRO_VIDEO_MUSIC_PAUSE_EVENT = 'bc_music_video_intro_pause'
_INTRO_VIDEO_MUSIC_RESUME_EVENT = 'bc_music_video_intro_resume'
_INTRO_VIDEO_MUSIC_TO_LOOP_EVENT = 'bc_music_transition_to_loop'
_DEFAULT_VIDEO_BUFFERING_TIME = 0.5
_BUTTON_HINT_SOUND_DELAY = 5

class StateBattlePreparing(AbstractState):
    soundController = dependency.descriptor(ISoundsController)
    appLoader = dependency.descriptor(IAppLoader)

    def __init__(self, lessonNum, account):
        super(StateBattlePreparing, self).__init__(STATE.BATTLE_PREPARING)
        self.__lessonId = lessonNum
        self.__account = account
        self.__weaver = aop.Weaver()
        self.__spaceLoadDelayed = False
        self.__prereqs = None
        self.__isIntroVideoFinished = False
        self.__onEnterWorldVehicles = []
        self._soundFilter = BCFilter()
        self.__oldSpaceEnv = None
        self.__skipBootcamp = False
        self.__btnHintSoundCallbackId = None
        return

    @property
    def skipBootcamp(self):
        return self.__skipBootcamp

    def activate(self):
        g_playerEvents.onAvatarReady += self.onAvatarReady
        g_playerEvents.onAvatarBecomePlayer += self.onAvatarBecomePlayer
        g_bootcampEvents.onIntroVideoStop += self.__onBCIntroVideoStop
        g_bootcampEvents.onBootcampGoNext += self.__onBootcampGoNext
        g_bootcampEvents.onArenaLoadCompleted += self.onArenaLoadCompleted
        self.__spaceLoadDelayed = False
        weave(self.__weaver, self)
        if self.isVideoPlayingLesson:
            self.__isIntroVideoFinished = False
            self.__oldSpaceEnv = self.soundController.setEnvForSpace(GuiGlobalSpaceID.BATTLE_LOADING, BCBattleLoadingSpaceEnv)
        self._soundFilter.start()

    def deactivate(self):
        LOG_DEBUG_DEV_BOOTCAMP('StateBattlePreparing.deactivate')
        g_playerEvents.onAvatarReady -= self.onAvatarReady
        g_playerEvents.onAvatarBecomePlayer -= self.onAvatarBecomePlayer
        g_bootcampEvents.onIntroVideoStop -= self.__onBCIntroVideoStop
        g_bootcampEvents.onBootcampGoNext -= self.__onBootcampGoNext
        g_bootcampEvents.onArenaLoadCompleted -= self.onArenaLoadCompleted
        if self.isVideoPlayingLesson and self.__oldSpaceEnv is not None:
            self.soundController.setEnvForSpace(GuiGlobalSpaceID.BATTLE_LOADING, self.__oldSpaceEnv)
        self.onAvatarBecomeNonPlayer()
        self.__weaver.clear()
        self.__cancelHintSoundCallback()
        self._soundFilter.stop()
        return

    @property
    def isVideoPlayingLesson(self):
        return False if BattleReplay.g_replayCtrl.isTimeWarpInProgress else self.__lessonId == 0

    def handleKeyEvent(self, event):
        pass

    def onAvatarBecomePlayer(self):
        LOG_DEBUG_DEV_BOOTCAMP('onAvatarBecomePlayer called')
        self.onBecomePlayer()

    def onAvatarReady(self):
        LOG_DEBUG_DEV_BOOTCAMP('onAvatarReady called')
        player = BigWorld.player()
        if player is not None and player.inputHandler is not None:
            inputHandler = player.inputHandler
            ctrlName = inputHandler.ctrlModeName
            if ctrlName == CTRL_MODE_NAME.ARCADE:
                yaw, pitch = inputHandler.ctrl.camera.angles
                inputHandler.ctrl.camera.setCameraDistance(CAMERA_START_DISTANCE)
                inputHandler.ctrl.camera.setYawPitch(yaw, pitch)
        return

    def onArenaLoadCompleted(self):
        g_bootcampEvents.onBattleLoaded(self.__lessonId)
        g_eventBus.handleEvent(events.LoadViewEvent(SFViewLoadParams(VIEW_ALIAS.BOOTCAMP_INTRO_FADEOUT), ctx={'duration': 1000}), EVENT_BUS_SCOPE.BATTLE)

    def onBecomePlayer(self):
        g_eventBus.handleEvent(events.LoadViewEvent(SFViewLoadParams(VIEW_ALIAS.BOOTCAMP_BATTLE_HIGHLIGHTS), ctx={'descriptors': g_bootcampHintsConfig.getItems()}), EVENT_BUS_SCOPE.BATTLE)

    def getIntroVideoData(self):
        introVideoData = {'showSkipOption': False}
        if self.isVideoPlayingLesson:
            introVideoData.update({'video': _INTRO_VIDEO_PATH,
             'backgroundVideo': _INTRO_VIDEO_LOOP_PATH,
             'backgroundMusicStartEvent': _INTRO_VIDEO_MUSIC_START_EVENT,
             'backgroundMusicStopEvent': _INTRO_VIDEO_MUSIC_STOP_EVENT,
             'backgroundMusicPauseEvent': _INTRO_VIDEO_MUSIC_PAUSE_EVENT,
             'backgroundMusicResumeEvent': _INTRO_VIDEO_MUSIC_RESUME_EVENT,
             'backgroundMusicToLoopEvent': _INTRO_VIDEO_MUSIC_TO_LOOP_EVENT,
             'bufferTime': Settings.g_instance.userPrefs.readFloat(Settings.VIDEO_BUFFERING_TIME, _DEFAULT_VIDEO_BUFFERING_TIME)})
        return introVideoData

    def onSpaceLoaded(self):
        LOG_DEBUG_DEV_BOOTCAMP('onSpaceLoaded called')
        if self.__spaceLoadDelayed:
            return False
        self.__spaceLoadDelayed = True
        g_eventDispatcher.unloadBootcampQueue()
        bb = BigWorld.player().arena.arenaType.boundingBox
        BigWorld.updateTerrainBorders((bb[0][0],
         bb[0][1],
         bb[1][0],
         bb[1][1]))
        g_bootcampEvents.onBootcampSpaceLoaded()
        return True

    def onVehicleOnEnterWorld(self, vehicle):
        LOG_DEBUG_DEV_BOOTCAMP('onVehicleOnEnterWorld called')
        if not self.isVideoPlayingLesson or self.__isIntroVideoFinished:
            return False
        self.__onEnterWorldVehicles.append(vehicle)
        return True

    def onAvatarOnEnterWorld(self, prereqs):
        LOG_DEBUG_DEV_BOOTCAMP('onAvatarOnEnterWorld called')
        if not self.isVideoPlayingLesson or self.__isIntroVideoFinished:
            return False
        self.__prereqs = prereqs
        return True

    def onBattleAction(self, actionId, actionArgs):
        pass

    def _doDeactivate(self):
        raise SoftException('This method should not be reached in this context')

    def _doActivate(self):
        raise SoftException('This method should not be reached in this context')

    def __onBootcampGoNext(self):
        LOG_DEBUG_DEV_BOOTCAMP('__onBootcampGoNext')
        self.__cancelHintSoundCallback()
        BigWorld.player().onSpaceLoaded()
        app = self.appLoader.getDefBattleApp()
        app.cursorMgr.resetMousePosition()

    def __onBCIntroVideoStop(self):
        from bootcamp.Bootcamp import g_bootcamp
        noSounds = BattleReplay.g_replayCtrl.isTimeWarpInProgress
        if not noSounds and self.isVideoPlayingLesson:
            self.__btnHintSoundCallbackId = BigWorld.callback(_BUTTON_HINT_SOUND_DELAY, self.__playHintSound)
            SoundGroups.g_instance.playSound2D('vo_bc_welcome')
        LOG_DEBUG_DEV_BOOTCAMP('__onBCIntroVideoStop called')
        self.__isIntroVideoFinished = True
        g_bootcamp.setIntroVideoPlayed()
        for vehicle in self.__onEnterWorldVehicles:
            BigWorld.player().vehicle_onEnterWorld(vehicle)

        del self.__onEnterWorldVehicles[:]
        if self.__prereqs is not None:
            BigWorld.player().onEnterWorld(self.__prereqs)
            self.__prereqs = None
        self.appLoader.attachCursor(app_settings.APP_NAME_SPACE.SF_BATTLE, _CTRL_FLAG.GUI_ENABLED)
        return

    def __playHintSound(self):
        self.__cancelHintSoundCallback()
        SoundGroups.g_instance.playSound2D('bc_loading_tips')

    def __cancelHintSoundCallback(self):
        if self.__btnHintSoundCallbackId is not None:
            BigWorld.cancelCallback(self.__btnHintSoundCallbackId)
            self.__btnHintSoundCallbackId = None
        return
