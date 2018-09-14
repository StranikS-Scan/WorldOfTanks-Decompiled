# Embedded file name: scripts/client/helpers/statistics.py
import math
import BigWorld
import ResMgr
from constants import ARENA_PERIOD, INVALID_CLIENT_STATS
from account_helpers.settings_core import SettingsCore
from account_helpers.settings_core.settings_constants import GRAPHICS
from gui.shared.utils import graphics
STATISTICS_VERSION = '0.0.2'

class _STATISTICS_STATE:
    STARTED = 0
    IN_PROGRESS = 1
    STOPPED = 2


class _HARDWARE_SCORE_PARAMS:
    PARAM_GPU_SCORE = 1
    PARAM_CPU_SCORE = 4


class StatisticsCollector:
    avrPing = property(lambda self: (0 if self.__framesTotal is 0 else self.__avrPing / self.__framesTotal))
    lagPercentage = property(lambda self: (0 if self.__framesTotal is 0 else self.__framesWithLags * 100 / self.__framesTotal))
    update = property(lambda self: self.__updateFunc)

    def __init__(self):
        self.__state = _STATISTICS_STATE.STOPPED
        self.__hangarLoaded = False
        self.__invalidStats = 0
        self.reset()
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
            g_sessionProvider.getDrrScaleCtrl().onDRRChanged -= self.__onDRRChanged

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
            g_sessionProvider.getDrrScaleCtrl().onDRRChanged += self.__onDRRChanged
            self.__state = _STATISTICS_STATE.IN_PROGRESS
            self.__updateFunc = self.__updateBattle
            self.__updateFunc(fpsInfo, ping, isLagging)

    def __updateBattle(self, fpsInfo, ping, isLagging):
        if self.__state == _STATISTICS_STATE.IN_PROGRESS:
            self.__avrPing += ping
            self.__framesTotal += 1
            self.__framesWithLags += 1 if isLagging else 0

    def subscribeToHangarSpaceCreate(self, event):
        event += self.__onHangarSpaceLoaded

    def getStatistics(self, andStop = True):
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


g_statistics = StatisticsCollector()
