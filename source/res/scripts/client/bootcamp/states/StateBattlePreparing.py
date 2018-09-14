# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/bootcamp/states/StateBattlePreparing.py
import BigWorld
import BattleReplay
import SoundGroups
from PlayerEvents import g_playerEvents
from bootcamp.BootCampEvents import g_bootcampEvents
from bootcamp.BootcampHooks import BCClassHook0, BCClassHook1
from bootcamp.states import STATE
from bootcamp.states.AbstractState import AbstractState
from debug_utils_bootcamp import LOG_DEBUG_DEV_BOOTCAMP
from gui.prb_control.events_dispatcher import g_eventDispatcher
from helpers import dependency
from skeletons.gui.sounds import ISoundsController
from gui.app_loader.settings import GUI_GLOBAL_SPACE_ID as _SPACE_ID
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.shared import events, g_eventBus, EVENT_BUS_SCOPE
from gui.sounds.filters import WWISEFilteredBootcampArenaFilter as BCFilter
from bootcamp.BootcampLobbyHintsConfig import g_bootcampHintsConfig
from gui import GUI_CTRL_MODE_FLAG as _CTRL_FLAG
from gui.app_loader import g_appLoader
from gui.app_loader.settings import APP_NAME_SPACE
from gui.Scaleform.daapi.view.bootcamp.BCBattleLoadingSpaceEnv import BCBattleLoadingSpaceEnv

class StateBattlePreparing(AbstractState):
    soundController = dependency.instance(ISoundsController)

    def __init__(self, lessonNum, account):
        super(StateBattlePreparing, self).__init__(STATE.BATTLE_PREPARING)
        self.__lessonId = lessonNum
        self.__account = account
        self.__hookOnBecomePlayer = None
        self.__hookOnEnterWorld = None
        self.__hookOnSpaceLoaded = None
        self.__hookOnShowBattle = None
        self.__hookVehicleOnEnterWorld = False
        self.__isIntroVideoFinished = False
        self.__onEnterWorldVehicles = []
        self._soundFilter = BCFilter()
        self.__oldSpaceEnv = None
        return

    def activate(self):
        from Avatar import PlayerAvatar
        g_playerEvents.onAvatarReady += self.onAvatarReady
        g_playerEvents.onAvatarBecomePlayer += self.onAvatarBecomePlayer
        g_bootcampEvents.onIntroVideoStop += self.__onBCIntroVideoStop
        g_bootcampEvents.onIntroVideoGoNext += self.__onIntroVideoGoNext
        g_bootcampEvents.onArenaLoadCompleted += self.onArenaLoadCompleted
        if self.__lessonId == 0:
            self.__isIntroVideoFinished = False
            self.__hookOnEnterWorld = BCClassHook1(PlayerAvatar, 'onEnterWorld', self.onEnterWorld)
            self.__hookOnEnterWorld.called = False
            BigWorld.delaySpaceLoad(True)
            self.__hookVehicleOnEnterWorld = True
            self.__oldSpaceEnv = self.soundController.setEnvForSpace(_SPACE_ID.BATTLE_LOADING, BCBattleLoadingSpaceEnv)
        self.__hookOnSpaceLoaded = BCClassHook0(PlayerAvatar, 'onSpaceLoaded', self.onSpaceLoadCompleted)

    def deactivate(self):
        LOG_DEBUG_DEV_BOOTCAMP('StateBattlePreparing.deactivate')
        g_playerEvents.onAvatarReady -= self.onAvatarReady
        g_playerEvents.onAvatarBecomePlayer -= self.onAvatarBecomePlayer
        g_bootcampEvents.onIntroVideoStop -= self.__onBCIntroVideoStop
        g_bootcampEvents.onIntroVideoGoNext -= self.__onIntroVideoGoNext
        g_bootcampEvents.onArenaLoadCompleted -= self.onArenaLoadCompleted
        if self.__hookOnSpaceLoaded is not None:
            self.__hookOnSpaceLoaded.dispose()
            self.__hookOnSpaceLoaded = None
        if self.__hookOnBecomePlayer is not None:
            self.__hookOnBecomePlayer.dispose()
            self.__hookOnBecomePlayer = None
        if self.__hookOnEnterWorld is not None:
            self.__hookOnEnterWorld.dispose()
            self.__hookOnEnterWorld = None
        if self.__lessonId == 0 and self.__oldSpaceEnv is not None:
            self.soundController.setEnvForSpace(_SPACE_ID.BATTLE_LOADING, self.__oldSpaceEnv)
        self.onAvatarBecomeNonPlayer()
        return

    def onAvatarBecomeNonPlayer(self):
        BigWorld.finishDelayedLoading()

    def handleKeyEvent(self, event):
        pass

    def hookVehicleOnEnterWorld(self):
        return self.__hookVehicleOnEnterWorld

    def onAvatarBecomePlayer(self):
        LOG_DEBUG_DEV_BOOTCAMP('onAvatarBecomePlayer called')
        self.onBecomePlayer()

    def onAvatarReady(self):
        LOG_DEBUG_DEV_BOOTCAMP('onAvatarReady called')

    def __onIntroVideoGoNext(self):
        LOG_DEBUG_DEV_BOOTCAMP('__onIntroVideoGoNext')
        self.__hookOnSpaceLoaded.callOriginalInstance(BigWorld.player())
        app = g_appLoader.getDefBattleApp()
        app.cursorMgr.resetMousePosition()
        return None

    def onArenaLoadCompleted(self):
        g_bootcampEvents.onBattleLoaded(self.__lessonId)
        g_eventBus.handleEvent(events.LoadViewEvent(VIEW_ALIAS.BOOTCAMP_INTRO_FADEOUT, None, {'duration': 1000}), EVENT_BUS_SCOPE.BATTLE)
        return

    def __onBCIntroVideoStop(self):
        from bootcamp.Bootcamp import g_bootcamp
        self._soundFilter.start()
        LOG_DEBUG_DEV_BOOTCAMP('__onBCIntroVideoStop called')
        self.__isIntroVideoFinished = True
        g_bootcamp.setIntroVideoPlayed()
        if self.__lessonId == 0:
            BigWorld.delaySpaceLoad(False)
            BigWorld.finishDelayedLoading()
        if len(self.__onEnterWorldVehicles) > 0:
            for vehicle in self.__onEnterWorldVehicles:
                self.runVehicleOnEnterWorld(BigWorld.player(), vehicle)

            self.__onEnterWorldVehicles = []
        if self.__hookOnEnterWorld is not None and self.__hookOnEnterWorld.called:
            self.__hookOnEnterWorld.callOriginalInstance(BigWorld.player(), 0)
        g_appLoader.attachCursor(APP_NAME_SPACE.SF_BATTLE, _CTRL_FLAG.GUI_ENABLED)
        return

    def onBecomePlayer(self):
        g_eventBus.handleEvent(events.LoadViewEvent(VIEW_ALIAS.BOOTCAMP_BATTLE_HIGHLIGHTS, None, {'descriptors': g_bootcampHintsConfig.getItems()}), EVENT_BUS_SCOPE.BATTLE)
        return

    def getIntroVideoData(self):
        from bootcamp.Bootcamp import g_bootcamp
        video = ''
        background = ''
        if self.__lessonId == 0:
            if not g_bootcamp.isIntroVideoPlayed():
                video = 'video/_tutorialInitial.usm'
            background = '../maps/bootcamp/loading/introLoading.png'
        autoStart = False
        bootcampParameters = g_bootcamp.getParameters()
        if bootcampParameters.has_key('introAutoStart'):
            autoStart = bootcampParameters['introAutoStart']
        if BattleReplay.isPlaying():
            autoStart = True
        introVideoData = {'backgroundImage': background,
         'video': video,
         'autoStart': autoStart,
         'lessonNumber': self.__lessonId,
         'tutorialPages': g_bootcamp.getBattleLoadingPages()}
        return introVideoData

    def onEnterWorld(self, prereqs):
        LOG_DEBUG_DEV_BOOTCAMP('onEnterWorld called')
        self.__hookOnEnterWorld.called = True
        if self.__isIntroVideoFinished:
            self.__hookOnEnterWorld.callOriginalInstance(BigWorld.player(), 0)

    def onSpaceLoadCompleted(self):
        LOG_DEBUG_DEV_BOOTCAMP('onSpaceLoadCompleted called')
        g_eventDispatcher.unloadBootcampQueue()
        bb = BigWorld.player().arena.arenaType.boundingBox
        BigWorld.wgUpdateTerrainBorders((bb[0][0],
         bb[0][1],
         bb[1][0],
         bb[1][1]))
        g_bootcampEvents.onIntroVideoLoaded()
        noSounds = BattleReplay.g_replayCtrl.isTimeWarpInProgress
        if not noSounds:
            SoundGroups.g_instance.playSound2D('bc_loading_tips')
        if self.__lessonId == 0 and not noSounds:
            SoundGroups.g_instance.playSound2D('vo_bc_welcome')

    def vehicleOnEnterWorld(self, avatar, vehicle):
        LOG_DEBUG_DEV_BOOTCAMP('vehicleOnEnterWorld called')
        if self.__isIntroVideoFinished:
            self.runVehicleOnEnterWorld(avatar, vehicle)
            return
        self.__onEnterWorldVehicles.append(vehicle)

    def runVehicleOnEnterWorld(self, avatar, vehicle):
        LOG_DEBUG_DEV_BOOTCAMP('runVehicleOnEnterWorld')
        self.__hookVehicleOnEnterWorld = False
        avatar.vehicle_onEnterWorld(vehicle)
        self.__hookVehicleOnEnterWorld = True

    def onBattleAction(self, actionId, actionArgs):
        pass
