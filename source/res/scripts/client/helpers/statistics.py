# Embedded file name: scripts/client/helpers/statistics.py
import math
import BigWorld
from constants import ARENA_PERIOD
from account_helpers.settings_core import SettingsCore
from account_helpers.settings_core.settings_constants import GRAPHICS
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

    def __init__(self):
        self.__state = _STATISTICS_STATE.STOPPED
        self.reset()

    def start(self):
        self.stop()
        self.reset()
        self.__state = _STATISTICS_STATE.STARTED

    def stop(self):
        if self.__state != _STATISTICS_STATE.STOPPED:
            self.__state = _STATISTICS_STATE.STOPPED
            BigWorld.enableBattleFPSCounter(False)

    def reset(self):
        self.__framesTotal = 0
        self.__framesWithLags = 0
        self.__avrPing = 0
        self.__graphicsPreset = 0

    def update(self, fpsInfo, ping, isLagging):
        if BigWorld.player().arena.period == ARENA_PERIOD.BATTLE:
            if self.__state == _STATISTICS_STATE.STARTED:
                self.__graphicsPreset = -1 if BigWorld.graphicsSettingsNeedRestart() else SettingsCore.g_settingsCore.getSetting(GRAPHICS.PRESETS)
                BigWorld.enableBattleFPSCounter(True)
                self.__state = _STATISTICS_STATE.IN_PROGRESS
            if self.__state == _STATISTICS_STATE.IN_PROGRESS:
                self.__avrPing += ping
                self.__framesTotal += 1
                self.__framesWithLags += 1 if isLagging else 0

    def getStatistics(self, andStop = True):
        proceed = self.__state == _STATISTICS_STATE.IN_PROGRESS
        ret = {}
        if proceed:
            ret = BigWorld.wg_getClientStatistics()
            proceed = ret is not None
            if proceed:
                ret['cpuScore'] = BigWorld.getAutoDetectGraphicsSettingsScore(_HARDWARE_SCORE_PARAMS.PARAM_CPU_SCORE)
                ret['gpuScore'] = BigWorld.getAutoDetectGraphicsSettingsScore(_HARDWARE_SCORE_PARAMS.PARAM_GPU_SCORE)
                ret['drrScale'] = int(round(BigWorld.getDRRScale() * 100))
                ret['ping'] = int(math.ceil(self.avrPing))
                ret['lag'] = self.lagPercentage
                ret['graphicsEngine'] = SettingsCore.g_settingsCore.getSetting(GRAPHICS.RENDER_PIPELINE)
                from gui.shared.utils import graphics
                graphicsPreset = SettingsCore.g_settingsCore.getSetting(GRAPHICS.PRESETS)
                if self.__graphicsPreset != graphicsPreset or BigWorld.graphicsSettingsNeedRestart():
                    ret['graphicsPreset'] = graphics.getGraphicsPresetsIndices().__len__()
                else:
                    ret['graphicsPreset'] = graphicsPreset
                if SettingsCore.g_settingsCore.getSetting(GRAPHICS.FULLSCREEN):
                    ret['screenResWidth'] = graphics.g_monitorSettings.currentVideoMode.width
                    ret['screenResHeight'] = graphics.g_monitorSettings.currentVideoMode.height
                    ret['windowMode'] = 1
                else:
                    ret['screenResWidth'] = graphics.g_monitorSettings.currentWindowSize.width
                    ret['screenResHeight'] = graphics.g_monitorSettings.currentWindowSize.height
                    ret['windowMode'] = 0
        if andStop is True or not proceed:
            self.stop()
        return ret


g_statistics = StatisticsCollector()
