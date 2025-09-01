# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/gui/shared/utils/performance_analyzer.py
import logging
import typing
from enum import IntEnum
from helpers.statistics import HARDWARE_SCORE_PARAMS
import BigWorld
from gui.shared.utils.graphics import getGraphicsEngineValue
if typing.TYPE_CHECKING:
    from typing import Optional, Dict
_logger = logging.getLogger(__name__)

class LimitType(IntEnum):
    SYSTEM_DATA = 0
    HARDWARE_PARAMS = 1


class PerformanceGroup(object):
    LOW_RISK = 0
    MEDIUM_RISK = 1
    HIGH_RISK = 2


DEFAULT_PERFORMANCE_GROUP_LIMITS = {PerformanceGroup.HIGH_RISK: [{LimitType.SYSTEM_DATA: {'osBit': 1,
                                                       'graphicsEngine': 0}}, {LimitType.HARDWARE_PARAMS: {HARDWARE_SCORE_PARAMS.PARAM_GPU_MEMORY: 490}}, {LimitType.SYSTEM_DATA: {'graphicsEngine': 0},
                               LimitType.HARDWARE_PARAMS: {HARDWARE_SCORE_PARAMS.PARAM_RAM: 2900}}],
 PerformanceGroup.MEDIUM_RISK: [{LimitType.HARDWARE_PARAMS: {HARDWARE_SCORE_PARAMS.PARAM_GPU_SCORE: 300}}, {LimitType.HARDWARE_PARAMS: {HARDWARE_SCORE_PARAMS.PARAM_CPU_SCORE: 50000}}]}

class PerformanceAnalyzerMixin(object):
    __performanceGroup = None

    def __init__(self, *args, **kwargs):
        super(PerformanceAnalyzerMixin, self).__init__(*args, **kwargs)
        self.__performanceGroup = None
        self.__lastLimitMap = None
        return

    def getPerformanceGroup(self, groupLimitMap=None, defaultGroup=PerformanceGroup.LOW_RISK):
        limitMap = groupLimitMap or DEFAULT_PERFORMANCE_GROUP_LIMITS
        if limitMap != self.__lastLimitMap:
            self.__lastLimitMap = limitMap
            self.__performanceGroup = None
        if not self.__performanceGroup:
            self.__analyzeClientSystem(limitMap, defaultGroup)
            _logger.debug('Current performance group %s, self=%s', self.__performanceGroup, self)
        return self.__performanceGroup

    def __analyzeClientSystem(self, groupLimitMap, defaultGroup):
        stats = BigWorld.wg_getClientStatistics()
        stats['graphicsEngine'] = getGraphicsEngineValue()
        self.__performanceGroup = defaultGroup
        for groupName, conditions in groupLimitMap.iteritems():
            for currentLimit in conditions:
                condValid = True
                systemStats = currentLimit.get(LimitType.SYSTEM_DATA, {})
                for key, limit in systemStats.iteritems():
                    currValue = stats.get(key, None)
                    if currValue is None or currValue != limit:
                        condValid = False

                hardwareParams = currentLimit.get(LimitType.HARDWARE_PARAMS, {})
                for key, limit in hardwareParams.iteritems():
                    currValue = BigWorld.getAutoDetectGraphicsSettingsScore(key)
                    if currValue >= limit:
                        condValid = False

                if condValid:
                    self.__performanceGroup = groupName

        return
