# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/game_control/perfomance_analyzer_controller.py
import BigWorld
from backports.functools_lru_cache import lru_cache
from helpers import dependency
from account_helpers.settings_core.settings_constants import GRAPHICS
from helpers.statistics import HARDWARE_SCORE_PARAMS
from skeletons.account_helpers.settings_core import ISettingsCore

class WTLimitType(object):
    SYSTEM_DATA = 0
    HARDWARE_PARAMS = 1


class WTPerformance(object):
    HIGH_RISK = 1
    MEDIUM_RISK = 2
    LOW_RISK = 3
    PERFORMANCE_MAP = {HIGH_RISK: 'highRisk',
     MEDIUM_RISK: 'mediumRisk',
     LOW_RISK: 'lowRisk'}

    @staticmethod
    def getPerformanceRiskMap(risk):
        return WTPerformance.PERFORMANCE_MAP.get(risk, WTPerformance.LOW_RISK)


PERFORMANCE_GROUP_LIMITS = {WTPerformance.HIGH_RISK: [{WTLimitType.SYSTEM_DATA: {'clientBit': 1}},
                           {WTLimitType.SYSTEM_DATA: {'osBit': 1,
                                                      'graphicsEngine': 0}},
                           {WTLimitType.HARDWARE_PARAMS: {HARDWARE_SCORE_PARAMS.PARAM_GPU_MEMORY: 490}},
                           {WTLimitType.SYSTEM_DATA: {'graphicsEngine': 0},
                            WTLimitType.HARDWARE_PARAMS: {HARDWARE_SCORE_PARAMS.PARAM_RAM: 2900}}],
 WTPerformance.MEDIUM_RISK: [{WTLimitType.HARDWARE_PARAMS: {HARDWARE_SCORE_PARAMS.PARAM_GPU_SCORE: 150}}, {WTLimitType.HARDWARE_PARAMS: {HARDWARE_SCORE_PARAMS.PARAM_CPU_SCORE: 50000}}]}

class PerformanceAnalyzer(object):
    __settingsCore = dependency.descriptor(ISettingsCore)

    @lru_cache()
    def analyzeClientSystem(self):
        stats = BigWorld.wg_getClientStatistics()
        stats['graphicsEngine'] = self.__settingsCore.getSetting(GRAPHICS.RENDER_PIPELINE)
        for groupName, conditions in PERFORMANCE_GROUP_LIMITS.iteritems():
            for currentLimit in conditions:
                condValid = True
                systemStats = currentLimit.get(WTLimitType.SYSTEM_DATA, {})
                for key, limit in systemStats.iteritems():
                    currValue = stats.get(key, None)
                    if currValue is None or currValue != limit:
                        condValid = False

                hardwareParams = currentLimit.get(WTLimitType.HARDWARE_PARAMS, {})
                for key, limit in hardwareParams.iteritems():
                    currValue = BigWorld.getAutoDetectGraphicsSettingsScore(key)
                    if currValue >= limit:
                        condValid = False

                if condValid:
                    return groupName

        return WTPerformance.LOW_RISK
