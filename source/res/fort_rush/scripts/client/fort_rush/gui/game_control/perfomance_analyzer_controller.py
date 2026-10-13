# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fort_rush/scripts/client/fort_rush/gui/game_control/perfomance_analyzer_controller.py
from __future__ import absolute_import
import BigWorld
from backports.functools_lru_cache import lru_cache
from future.utils import viewitems
from helpers import dependency
from account_helpers.settings_core.settings_constants import GRAPHICS
from helpers.statistics import HARDWARE_SCORE_PARAMS
from skeletons.account_helpers.settings_core import ISettingsCore

class LimitType(object):
    SYSTEM_DATA = 0
    HARDWARE_PARAMS = 1


class PerformanceGroup(object):
    HIGH_RISK = 1
    MEDIUM_RISK = 2
    LOW_RISK = 3
    PERFORMANCE_MAP = {HIGH_RISK: 'highRisk',
     MEDIUM_RISK: 'mediumRisk',
     LOW_RISK: 'lowRisk'}

    @staticmethod
    def getPerformanceRiskMap(risk):
        return PerformanceGroup.PERFORMANCE_MAP.get(risk, PerformanceGroup.LOW_RISK)


PERFORMANCE_GROUP_LIMITS = {PerformanceGroup.HIGH_RISK: [{LimitType.SYSTEM_DATA: {'clientBit': 1}},
                              {LimitType.SYSTEM_DATA: {'osBit': 1,
                                                       'graphicsEngine': 0}},
                              {LimitType.HARDWARE_PARAMS: {HARDWARE_SCORE_PARAMS.PARAM_GPU_MEMORY: 490}},
                              {LimitType.SYSTEM_DATA: {'graphicsEngine': 0},
                               LimitType.HARDWARE_PARAMS: {HARDWARE_SCORE_PARAMS.PARAM_RAM: 2900}}],
 PerformanceGroup.MEDIUM_RISK: [{LimitType.HARDWARE_PARAMS: {HARDWARE_SCORE_PARAMS.PARAM_GPU_SCORE: 150}}, {LimitType.HARDWARE_PARAMS: {HARDWARE_SCORE_PARAMS.PARAM_CPU_SCORE: 50000}}]}

class PerformanceAnalyzer(object):
    __settingsCore = dependency.descriptor(ISettingsCore)

    @lru_cache()
    def getPerformanceGroup(self):
        stats = BigWorld.wg_getClientStatistics()
        stats['graphicsEngine'] = self.__settingsCore.getSetting(GRAPHICS.RENDER_PIPELINE)
        for groupName, conditions in viewitems(PERFORMANCE_GROUP_LIMITS):
            for currentLimit in conditions:
                condValid = True
                systemStats = currentLimit.get(LimitType.SYSTEM_DATA, {})
                for key, limit in viewitems(systemStats):
                    currValue = stats.get(key, None)
                    if currValue is None or currValue != limit:
                        condValid = False

                hardwareParams = currentLimit.get(LimitType.HARDWARE_PARAMS, {})
                for key, limit in viewitems(hardwareParams):
                    currValue = BigWorld.getAutoDetectGraphicsSettingsScore(key)
                    if currValue >= limit:
                        condValid = False

                if condValid:
                    return groupName

        return PerformanceGroup.LOW_RISK
