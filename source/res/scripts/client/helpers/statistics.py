# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/helpers/statistics.py
import math
import BigWorld
import ResMgr
import Settings
from constants import ARENA_PERIOD, INVALID_CLIENT_STATS
from account_helpers.settings_core import SettingsCore
from account_helpers.settings_core.settings_constants import GRAPHICS
from gui.shared.utils import graphics
from debug_utils import LOG_DEBUG, LOG_NOTE
STATISTICS_VERSION = '0.0.2'

class _STATISTICS_STATE:
    STARTED = 0
    IN_PROGRESS = 1
    STOPPED = 2


class _HARDWARE_SCORE_PARAMS:
    PARAM_GPU_SCORE = 1
    PARAM_CPU_SCORE = 4


class HANGAR_LOADING_STATE:
    LOGIN = 0
    CONNECTED = 1
    SHOW_GUI = 2
    QUESTS_SYNC = 3
    USER_SERVER_SETTINGS_SYNC = 4
    START_LOADING_SPACE = 5
    START_LOADING_VEHICLE = 6
    FINISH_LOADING_VEHICLE = 7
    FINISH_LOADING_SPACE = 8
    HANGAR_READY = 9
    START_LOADING_TUTORIAL = 10
    FINISH_LOADING_TUTORIAL = 11
    DISCONNECTED = 12
    COUNT = 13


_HANGAR_LOADING_STATES_PREFIX = 'HANGAR LOADING STATE'
_HANGAR_LOADING_STATES = ['LOGIN',
 'CONNECTED',
 'SHOW GUI',
 'QUESTS SYNC',
 'USS SYNC',
 'SPACE LOADING START',
 'VEHICLE LOADING START',
 'VEHICLE LOADING END',
 'SPACE LOADING END',
 'HANGAR READY',
 'TUTORIAL LOADING START',
 'TUTORIAL LOADING END',
 'DISCONNECTED']
_HANGAR_LOADING_STATES_IDS = [HANGAR_LOADING_STATE.FINISH_LOADING_VEHICLE,
 HANGAR_LOADING_STATE.FINISH_LOADING_SPACE,
 HANGAR_LOADING_STATE.FINISH_LOADING_TUTORIAL,
 HANGAR_LOADING_STATE.HANGAR_READY]

class StatisticsCollector:
    avrPing = property(lambda self: 0 if self.__framesTotal is 0 else self.__avrPing / self.__framesTotal)
    lagPercentage = property(lambda self: 0 if self.__framesTotal is 0 else self.__framesWithLags * 100 / self.__framesTotal)
    update = property(lambda self: self.__updateFunc)

    def __init__(self):
        self.__state = _STATISTICS_STATE.STOPPED
        self.__hangarLoaded = False
        self.__invalidStats = 0
        self.reset()
        self.__loadingStates = [0.0] * HANGAR_LOADING_STATE.COUNT
        self.__loadingInitialState = HANGAR_LOADING_STATE.LOGIN
        self.__hangarLoadingTime = 0.0
        from ConnectionManager import connectionManager
        connectionManager.onDisconnected += self.__onClientDisconnected

    def start(self):
        self.stop()
        self.reset()
        self.__state = _STATISTICS_STATE.STARTED

    def stop(self):
        if self.__state != _STATISTICS_STATE.STOPPED:
            self.__state = _STATISTICS_STATE.STOPPED
            BigWorld.enableBattleFPSCounter(False)
            SettingsCore.g_settingsCore.onSettingsChanged -= self.__onSettingsChanged
            from gui.battle_control import g_sessionProvider
            ctrl = g_sessionProvider.shared.drrScale
            if ctrl is not None:
                ctrl.onDRRChanged -= self.__onDRRChanged
        return

    def reset(self):
        self.__invalidStats = 0
        self.__framesTotal = 0
        self.__framesWithLags = 0
        self.__avrPing = 0
        self.__updateFunc = self.__updateIdle

    def __updateIdle(self, fpsInfo, ping, isLagging):
        if BigWorld.player().arena.period > ARENA_PERIOD.IDLE:
            self.__updateFunc = self.__updatePrebattle
            self.__updateFunc(fpsInfo, ping, isLagging)

    def __updatePrebattle(self, fpsInfo, ping, isLagging):
        if BigWorld.player().arena.period == ARENA_PERIOD.BATTLE and self.__state == _STATISTICS_STATE.STARTED:
            BigWorld.enableBattleFPSCounter(True)
            SettingsCore.g_settingsCore.onSettingsChanged += self.__onSettingsChanged
            from gui.battle_control import g_sessionProvider
            ctrl = g_sessionProvider.shared.drrScale
            if ctrl is not None:
                ctrl.onDRRChanged += self.__onDRRChanged
            self.__state = _STATISTICS_STATE.IN_PROGRESS
            self.__updateFunc = self.__updateBattle
            self.__updateFunc(fpsInfo, ping, isLagging)
        return

    def __updateBattle(self, fpsInfo, ping, isLagging):
        if self.__state == _STATISTICS_STATE.IN_PROGRESS:
            self.__avrPing += ping
            self.__framesTotal += 1
            self.__framesWithLags += 1 if isLagging else 0

    def subscribeToHangarSpaceCreate(self, event):
        event += self.__onHangarSpaceLoaded

    def getStatistics(self, andStop=True):
        proceed = self.__state == _STATISTICS_STATE.IN_PROGRESS
        ret = {}
        if proceed:
            ret = BigWorld.wg_getClientStatistics()
            proceed = ret is not None
            if proceed:
                ret['cpuScore'] = BigWorld.getAutoDetectGraphicsSettingsScore(_HARDWARE_SCORE_PARAMS.PARAM_CPU_SCORE)
                ret['gpuScore'] = BigWorld.getAutoDetectGraphicsSettingsScore(_HARDWARE_SCORE_PARAMS.PARAM_GPU_SCORE)
                ret['ping'] = int(math.ceil(self.avrPing))
                ret['lag'] = self.lagPercentage
                ret['graphicsEngine'] = SettingsCore.g_settingsCore.getSetting(GRAPHICS.RENDER_PIPELINE)
                if not self.__hangarLoaded:
                    self.__invalidStats |= INVALID_CLIENT_STATS.CLIENT_STRAIGHT_INTO_BATTLE
                ret['graphicsPreset'] = SettingsCore.g_settingsCore.getSetting(GRAPHICS.PRESETS)
                windowMode = SettingsCore.g_settingsCore.getSetting(GRAPHICS.FULLSCREEN)
                ret['windowMode'] = 1 if windowMode else 0
                resolutionContainer = graphics.g_monitorSettings.currentVideoMode if windowMode else graphics.g_monitorSettings.currentWindowSize
                ret['screenResWidth'] = resolutionContainer.width
                ret['screenResHeight'] = resolutionContainer.height
                ret['drrScale'] = int(round(BigWorld.getDRRScale() * 100))
                ret['dynamicDRR'] = BigWorld.isDRRAutoscalingEnabled()
                ret['invalidStats'] |= self.__invalidStats
                ret['contentType'] = ResMgr.activeContentType()
                ret['soundQuality'] = Settings.g_instance.userPrefs[Settings.KEY_SOUND_PREFERENCES].readInt('LQ_render', 0)
                ret['hangarLoadingTime'] = self.__hangarLoadingTime
        if andStop is True or not proceed:
            self.stop()
        return ret

    def __onSettingsChanged(self, diff):
        if GRAPHICS.DYNAMIC_RENDERER in diff:
            self.__invalidStats |= INVALID_CLIENT_STATS.CLIENT_DRR_SCALE_CHANGED
        importantSettings = set([GRAPHICS.TEXTURE_QUALITY,
         GRAPHICS.LIGHTING_QUALITY,
         GRAPHICS.SHADOWS_QUALITY,
         GRAPHICS.EFFECTS_QUALITY,
         GRAPHICS.SNIPER_MODE_EFFECTS_QUALITY,
         GRAPHICS.FLORA_QUALITY,
         GRAPHICS.POST_PROCESSING_QUALITY,
         GRAPHICS.SNIPER_MODE_GRASS_ENABLED,
         GRAPHICS.VEHICLE_DUST_ENABLED,
         GRAPHICS.DRR_AUTOSCALER_ENABLED])
        keys = set(diff.keys())
        if importantSettings & keys:
            self.__invalidStats |= INVALID_CLIENT_STATS.CLIENT_GS_MAJOR_CHANGED
        otherSettings = set([GRAPHICS.TERRAIN_QUALITY,
         GRAPHICS.WATER_QUALITY,
         GRAPHICS.DECALS_QUALITY,
         GRAPHICS.OBJECT_LOD,
         GRAPHICS.SPEEDTREE_QUALITY,
         GRAPHICS.FAR_PLANE,
         GRAPHICS.MOTION_BLUR_QUALITY,
         GRAPHICS.SEMITRANSPARENT_LEAVES_ENABLED,
         GRAPHICS.VEHICLE_TRACES_ENABLED,
         GRAPHICS.FPS_PERFOMANCER])
        if otherSettings & keys:
            self.__invalidStats |= INVALID_CLIENT_STATS.CLIENT_GS_MINOR_CHANGED

    def __onHangarSpaceLoaded(self):
        self.__hangarLoaded = True

    def __onClientDisconnected(self):
        self.__hangarLoaded = False

    def __onDRRChanged(self):
        self.__invalidStats |= INVALID_CLIENT_STATS.CLIENT_DRR_SCALE_CHANGED

    def noteHangarLoadingState(self, state, initialState=False, showSummaryNow=False):
        if state < 0 or state > HANGAR_LOADING_STATE.COUNT:
            LOG_DEBUG('Unknown hangar loading state: {0}'.format(state))
            return
        if initialState:
            self.__loadingStates = [0] * HANGAR_LOADING_STATE.COUNT
            self.__loadingInitialState = state
        if self.__loadingStates[state] != 0.0:
            return
        exactTime = BigWorld.timeExact()
        stateName = '{0}: {1}'.format(_HANGAR_LOADING_STATES_PREFIX, _HANGAR_LOADING_STATES[state])
        LOG_NOTE('{0} - {1}'.format(stateName, exactTime))
        self.__loadingStates[state] = exactTime
        BigWorld.addUPLMessage(stateName)
        if showSummaryNow:
            reportHeader = _HANGAR_LOADING_STATES_PREFIX + ': SUMMARY'
            stopWatch = HANGAR_LOADING_STATE.HANGAR_READY
            if self.__loadingStates[HANGAR_LOADING_STATE.FINISH_LOADING_TUTORIAL] != 0.0:
                stopWatch = HANGAR_LOADING_STATE.FINISH_LOADING_TUTORIAL
                reportHeader += ' (With Tutorial stage) '
            self.__hangarLoadingTime = self.__loadingStates[stopWatch] - self.__loadingStates[self.__loadingInitialState]
            LOG_NOTE(reportHeader + ' TOTAL = ' + str(self.__hangarLoadingTime))


g_statistics = StatisticsCollector()
