# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/helpers/statistics.py
import BigWorld
import ResMgr
import Settings
from constants import ARENA_PERIOD, INVALID_CLIENT_STATS
from account_helpers.settings_core.settings_constants import GRAPHICS
from gui.shared.utils import monitor_settings
from debug_utils import LOG_DEBUG, LOG_NOTE
from helpers import dependency, isPlayerAvatar
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.connection_mgr import IConnectionManager
from skeletons.gui.battle_session import IBattleSessionProvider
from skeletons.gui.shared.utils import IHangarSpace
from skeletons.helpers.statistics import IStatisticsCollector
STATISTICS_VERSION = '0.0.2'

class _STATISTICS_STATE(object):
    STARTED = 0
    IN_PROGRESS = 1
    STOPPED = 2


class HARDWARE_SCORE_PARAMS(object):
    PARAM_GPU_MEMORY = 0
    PARAM_GPU_SCORE = 1
    PARAM_CPU_SCORE = 2
    PARAM_CPU_CORES = 3
    PARAM_RAM = 4
    PARAM_VIRTUAL_MEMORY = 5
    MAX_PARAMS = 6


class HANGAR_LOADING_STATE(object):
    LOGIN = 0
    CONNECTED = 1
    SHOW_GUI = 2
    QUESTS_SYNC = 3
    USER_SERVER_SETTINGS_SYNC = 4
    START_LOADING_SPACE = 5
    START_LOADING_VEHICLE = 6
    FINISH_LOADING_VEHICLE = 7
    FINISH_LOADING_SPACE = 8
    HANGAR_UI_READY = 9
    TRAINING_UI_READY = 10
    HANGAR_READY = 11
    START_LOADING_TUTORIAL = 12
    FINISH_LOADING_TUTORIAL = 13
    DISCONNECTED = 14
    COUNT = 15


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
 'HANGAR UI READY',
 'TRAINING UI READY',
 'HANGAR READY',
 'TUTORIAL LOADING START',
 'TUTORIAL LOADING END',
 'DISCONNECTED']
_HANGAR_LOADING_STATES_IDS = [HANGAR_LOADING_STATE.FINISH_LOADING_VEHICLE,
 HANGAR_LOADING_STATE.FINISH_LOADING_SPACE,
 HANGAR_LOADING_STATE.FINISH_LOADING_TUTORIAL,
 HANGAR_LOADING_STATE.HANGAR_READY]
_IMPORTANT_GRAPHICS_SETTINGS_SET = {'TEXTURE_QUALITY',
 'LIGHTING_QUALITY',
 'SHADOWS_QUALITY',
 'EFFECTS_QUALITY',
 'SNIPER_MODE_EFFECTS_QUALITY',
 'FLORA_QUALITY',
 'POST_PROCESSING_QUALITY',
 'SNIPER_MODE_GRASS_ENABLED',
 'VEHICLE_DUST_ENABLED',
 'DRR_AUTOSCALER_ENABLED'}
_OTHER_GRAPHICS_SETTINGS_SET = {'TERRAIN_QUALITY',
 'WATER_QUALITY',
 'DECALS_QUALITY',
 'OBJECT_LOD',
 'SPEEDTREE_QUALITY',
 'FAR_PLANE',
 'MOTION_BLUR_QUALITY',
 'SEMITRANSPARENT_LEAVES_ENABLED',
 'VEHICLE_TRACES_ENABLED',
 'FPS_PERFOMANCER'}
_VIDEO_MODE_SIZE_CHANGE_SET = {GRAPHICS.WINDOW_SIZE, GRAPHICS.RESOLUTION, GRAPHICS.BORDERLESS_SIZE}

class StatisticsCollector(IStatisticsCollector):
    update = property(lambda self: self.__updateFunc)
    sessionProvider = dependency.descriptor(IBattleSessionProvider)
    settingsCore = dependency.descriptor(ISettingsCore)
    connectionMgr = dependency.descriptor(IConnectionManager)
    hangarSpace = dependency.descriptor(IHangarSpace)

    def __init__(self):
        self.__state = _STATISTICS_STATE.STOPPED
        self.__hangarLoaded = False
        self.__invalidStats = 0
        self.__dynEvents = []
        self.reset()
        self.__needCollectSystemData = False
        self.__needCollectSessionData = False
        self.__hangarWasLoadedOnce = False
        self.__sendFullStat = False
        self.__loadingStates = [0.0] * HANGAR_LOADING_STATE.COUNT
        self.__loadingInitialState = HANGAR_LOADING_STATE.LOGIN
        self.__hangarLoadingTime = 0.0
        self.__lastArenaUniqueID = 0
        self.__lastArenaTypeID = 0
        self.__lastArenaTeam = 0

    def init(self):
        self.connectionMgr.onDisconnected += self.__onClientDisconnected
        self.hangarSpace.onSpaceCreate += self.__onHangarSpaceLoaded

    def fini(self):
        self.settingsCore.onSettingsChanged -= self.__onSettingsChanged
        self.connectionMgr.onDisconnected -= self.__onClientDisconnected
        self.hangarSpace.onSpaceCreate -= self.__onHangarSpaceLoaded
        self.__updateFunc = None
        return

    def start(self):
        self.stop()
        self.reset()
        self.__state = _STATISTICS_STATE.STARTED

    def stop(self):
        if self.__state != _STATISTICS_STATE.STOPPED:
            self.__state = _STATISTICS_STATE.STOPPED
            BigWorld.enableBattleStatisticCollector(False)
            self.settingsCore.onSettingsChanged -= self.__onSettingsChanged
            ctrl = self.sessionProvider.shared.drrScale
            if ctrl is not None:
                ctrl.onDRRChanged -= self.__onDRRChanged
        return

    def reset(self):
        self.__invalidStats = 0
        self.__updateFunc = self.__updateIdle

    def needCollectSystemData(self, value):
        self.__needCollectSystemData = value

    def needCollectSessionData(self, value):
        self.__needCollectSessionData = value

    def getSessionData(self):
        stat = BigWorld.wg_getClientStatistics()
        return self.__getSessionData(stat) if stat else None

    def getStatistics(self, andStop=True):
        result = {'system': None,
         'session': None}
        stat = BigWorld.wg_getClientStatistics()
        BigWorld.wg_clearCrashedState()
        if not stat:
            return result
        else:
            if self.__sendFullStat:
                self.__sendFullStat = False
                self.__needCollectSystemData = False
                self.__needCollectSessionData = False
                result['system'] = self.__getSystemData(stat)
                result['session'] = self.__getSessionData(stat)
            if self.__needCollectSystemData:
                self.__needCollectSystemData = False
                result['system'] = self.__getSystemData(stat)
            if self.__needCollectSessionData:
                self.__needCollectSessionData = False
                result['session'] = self.__getSessionData(stat)
            if andStop is True:
                self.stop()
            return result

    def noteLastArenaData(self, arenaTypeID, arenaUniqueID, arenaTeam):
        self.__lastArenaTypeID = arenaTypeID
        self.__lastArenaUniqueID = arenaUniqueID
        self.__lastArenaTeam = arenaTeam
        if not self.__hangarWasLoadedOnce:
            self.__invalidStats |= INVALID_CLIENT_STATS.CLIENT_STRAIGHT_INTO_BATTLE
            self.__sendFullStat = True

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
            if self.__loadingStates[HANGAR_LOADING_STATE.FINISH_LOADING_TUTORIAL] != 0.0:
                reportHeader += ' (With Tutorial stage) '
            self.__hangarLoadingTime = self.__loadingStates[state] - self.__loadingStates[self.__loadingInitialState]
            LOG_NOTE(reportHeader + ' TOTAL = ' + str(self.__hangarLoadingTime))

    def __getSessionData(self, stat):
        stat['graphicsPreset'] = self.settingsCore.getSetting(GRAPHICS.PRESETS)
        windowMode = BigWorld.getWindowMode()
        windowModeLUT = {BigWorld.WindowModeWindowed: 0,
         BigWorld.WindowModeExclusiveFullscreen: 1,
         BigWorld.WindowModeBorderless: 2}
        stat['windowMode'] = windowModeLUT.get(windowMode, 0)
        monitorSettings = monitor_settings.g_monitorSettings
        resolutionContainer = monitorSettings.currentWindowSize
        if windowMode == BigWorld.WindowModeExclusiveFullscreen:
            resolutionContainer = monitorSettings.currentVideoMode
        elif windowMode == BigWorld.WindowModeBorderless:
            resolutionContainer = monitorSettings.currentBorderlessSize
        stat['screenResWidth'] = resolutionContainer.width
        stat['screenResHeight'] = resolutionContainer.height
        stat['drrScale'] = int(round(BigWorld.getDRRScale() * 100))
        stat['dynamicDRR'] = BigWorld.isDRRAutoscalingEnabled()
        stat['invalidStats'] |= self.__invalidStats
        stat['soundQuality'] = Settings.g_instance.userPrefs[Settings.KEY_SOUND_PREFERENCES].readInt('LQ_render', 0)
        stat['hangarLoadingTime'] = self.__hangarLoadingTime
        stat['lastArenaUniqueID'] = self.__lastArenaUniqueID
        stat['lastArenaTypeID'] = self.__lastArenaTypeID
        stat['lastArenaTeam'] = self.__lastArenaTeam
        return stat

    def __getSystemData(self, statisticsDict):
        return {'isLaptop': statisticsDict['isLaptop'],
         'cpuVendor': statisticsDict['cpuVendor'],
         'cpuCores': statisticsDict['cpuCores'],
         'cpuFreq': statisticsDict['cpuFreq'],
         'gpuVendor': statisticsDict['gpuVendor'],
         'gpuMemory': statisticsDict['gpuMemory'],
         'mainMemory': statisticsDict['mainMemory'],
         'os': statisticsDict['os'],
         'graphicsEngine': self.settingsCore.getSetting(GRAPHICS.RENDER_PIPELINE),
         'cpuScore': BigWorld.getAutoDetectGraphicsSettingsScore(HARDWARE_SCORE_PARAMS.PARAM_CPU_SCORE),
         'gpuScore': BigWorld.getAutoDetectGraphicsSettingsScore(HARDWARE_SCORE_PARAMS.PARAM_GPU_SCORE),
         'osBit': statisticsDict['osBit'],
         'hasMods': statisticsDict['hasMods'],
         'reason32bit': statisticsDict['reason32bit'],
         'cpuFamily': statisticsDict['cpuFamily'],
         'gpuFamily': statisticsDict['gpuFamily'],
         'crashed': statisticsDict['crashed'],
         'contentType': ResMgr.activeContentType(),
         'gpuDriverVersion': statisticsDict['gpuDriverVersion'],
         'graphicsAPIID': statisticsDict['graphicsAPIID'],
         'multiGPU': statisticsDict['multiGPU'],
         'cpuName': statisticsDict['cpuName'],
         'hangarFirstLoadingTime': self.__hangarLoadingTime,
         'clientBit': statisticsDict['clientBit']}

    def __onSettingsChanged(self, diff):
        keys = set(diff.keys())
        if _VIDEO_MODE_SIZE_CHANGE_SET & keys:
            self.__invalidStats |= INVALID_CLIENT_STATS.CLIENT_RESOLUTION_CHANGED
        if GRAPHICS.VIDEO_MODE in keys:
            self.__invalidStats |= INVALID_CLIENT_STATS.CLIENT_WM_CHANGED
        if GRAPHICS.DYNAMIC_RENDERER in keys:
            self.__invalidStats |= INVALID_CLIENT_STATS.CLIENT_DRR_SCALE_CHANGED
        if _IMPORTANT_GRAPHICS_SETTINGS_SET & keys:
            self.__invalidStats |= INVALID_CLIENT_STATS.CLIENT_GS_MAJOR_CHANGED
        if _OTHER_GRAPHICS_SETTINGS_SET & keys:
            self.__invalidStats |= INVALID_CLIENT_STATS.CLIENT_GS_MINOR_CHANGED

    def __onHangarSpaceLoaded(self):
        self.__hangarLoaded = True
        self.__hangarWasLoadedOnce = True

    def __onClientDisconnected(self):
        self.__hangarLoaded = False

    def __onDRRChanged(self):
        self.__invalidStats |= INVALID_CLIENT_STATS.CLIENT_DRR_SCALE_CHANGED

    def __updateIdle(self):
        if isPlayerAvatar() and BigWorld.player().arena.period > ARENA_PERIOD.IDLE:
            self.__updateFunc = self.__updatePrebattle
            self.__updateFunc()

    def __updatePrebattle(self):
        if isPlayerAvatar() and BigWorld.player().arena.period == ARENA_PERIOD.BATTLE and self.__state == _STATISTICS_STATE.STARTED:
            BigWorld.enableBattleStatisticCollector(True)
            self.settingsCore.onSettingsChanged += self.__onSettingsChanged
            ctrl = self.sessionProvider.shared.drrScale
            if ctrl is not None:
                ctrl.onDRRChanged += self.__onDRRChanged
            self.__state = _STATISTICS_STATE.IN_PROGRESS
            self.__updateFunc = self.__updateBattle
            self.__updateFunc()
        return

    def __updateBattle(self):
        pass
