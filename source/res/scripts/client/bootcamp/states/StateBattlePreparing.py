# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/bootcamp/states/StateBattlePreparing.py
import BigWorld
import BattleReplay
import SoundGroups
from AvatarInputHandler.aih_constants import CTRL_MODE_NAME
from PlayerEvents import g_playerEvents
from bootcamp.BootCampEvents import g_bootcampEvents
from bootcamp.BootcampConstants import CAMERA_START_DISTANCE
from bootcamp.states import STATE
from bootcamp.states.AbstractState import AbstractState
from bootcamp.aop.battle_preparing import weave
from debug_utils_bootcamp import LOG_DEBUG_DEV_BOOTCAMP
from gui.prb_control.events_dispatcher import g_eventDispatcher
from helpers import dependency, aop
from skeletons.gui.sounds import ISoundsController
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.shared import events, g_eventBus, EVENT_BUS_SCOPE
from gui.sounds.filters import WWISEFilteredBootcampArenaFilter as BCFilter
from bootcamp.BootcampLobbyHintsConfig import g_bootcampHintsConfig
from gui import GUI_CTRL_MODE_FLAG as _CTRL_FLAG
from gui.app_loader import g_appLoader, settings as app_settings
from gui.Scaleform.daapi.view.bootcamp.BCBattleLoadingSpaceEnv import BCBattleLoadingSpaceEnv
from gui.Scaleform.locale.RES_ICONS import RES_ICONS

class StateBattlePreparing(AbstractState):
    soundController = dependency.instance(ISoundsController)

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
            BigWorld.delaySpaceLoad(True)
            self.__oldSpaceEnv = self.soundController.setEnvForSpace(app_settings.GUI_GLOBAL_SPACE_ID.BATTLE_LOADING, BCBattleLoadingSpaceEnv)

    def deactivate(self):
        LOG_DEBUG_DEV_BOOTCAMP('StateBattlePreparing.deactivate')
        g_playerEvents.onAvatarReady -= self.onAvatarReady
        g_playerEvents.onAvatarBecomePlayer -= self.onAvatarBecomePlayer
        g_bootcampEvents.onIntroVideoStop -= self.__onBCIntroVideoStop
        g_bootcampEvents.onBootcampGoNext -= self.__onBootcampGoNext
        g_bootcampEvents.onArenaLoadCompleted -= self.onArenaLoadCompleted
        if self.isVideoPlayingLesson and self.__oldSpaceEnv is not None:
            self.soundController.setEnvForSpace(app_settings.GUI_GLOBAL_SPACE_ID.BATTLE_LOADING, self.__oldSpaceEnv)
        self.onAvatarBecomeNonPlayer()
        self.__weaver.clear()
        return

    @property
    def isVideoPlayingLesson(self):
        return False if BattleReplay.g_replayCtrl.isTimeWarpInProgress else self.__lessonId == 0

    def onAvatarBecomeNonPlayer(self):
        BigWorld.finishDelayedLoading()

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
        g_eventBus.handleEvent(events.LoadViewEvent(VIEW_ALIAS.BOOTCAMP_INTRO_FADEOUT, None, {'duration': 1000}), EVENT_BUS_SCOPE.BATTLE)
        return

    def onBecomePlayer(self):
        g_eventBus.handleEvent(events.LoadViewEvent(VIEW_ALIAS.BOOTCAMP_BATTLE_HIGHLIGHTS, None, {'descriptors': g_bootcampHintsConfig.getItems()}), EVENT_BUS_SCOPE.BATTLE)
        return

    def getIntroVideoData(self):
        video = ''
        background = ''
        if self.isVideoPlayingLesson:
            video = 'video/_tutorialInitial.usm'
            background = RES_ICONS.MAPS_ICONS_BOOTCAMP_LOADING_INTROLOADING
        introVideoData = {'backgroundImage': background,
         'video': video,
         'showSkipOption': False}
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
        g_bootcampEvents.onIntroVideoLoaded()
        noSounds = BattleReplay.g_replayCtrl.isTimeWarpInProgress
        if not noSounds:
            SoundGroups.g_instance.playSound2D('bc_loading_tips')
        if self.isVideoPlayingLesson and not noSounds:
            SoundGroups.g_instance.playSound2D('vo_bc_welcome')
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
        raise UserWarning('This method should not be reached in this context')

    def _doActivate(self):
        raise UserWarning('This method should not be reached in this context')

    def __onBootcampGoNext(self):
        LOG_DEBUG_DEV_BOOTCAMP('__onBootcampGoNext')
        BigWorld.player().onSpaceLoaded()
        app = g_appLoader.getDefBattleApp()
        app.cursorMgr.resetMousePosition()

    def __onBCIntroVideoStop(self):
        from bootcamp.Bootcamp import g_bootcamp
        self._soundFilter.start()
        LOG_DEBUG_DEV_BOOTCAMP('__onBCIntroVideoStop called')
        self.__isIntroVideoFinished = True
        g_bootcamp.setIntroVideoPlayed()
        if self.isVideoPlayingLesson:
            BigWorld.delaySpaceLoad(False)
            BigWorld.finishDelayedLoading()
        for vehicle in self.__onEnterWorldVehicles:
            BigWorld.player().vehicle_onEnterWorld(vehicle)

        del self.__onEnterWorldVehicles[:]
        if self.__prereqs is not None:
            BigWorld.player().onEnterWorld(self.__prereqs)
            self.__prereqs = None
        g_appLoader.attachCursor(app_settings.APP_NAME_SPACE.SF_BATTLE, _CTRL_FLAG.GUI_ENABLED)
        return
