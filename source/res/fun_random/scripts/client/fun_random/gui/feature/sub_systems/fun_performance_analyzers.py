# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/gui/feature/sub_systems/fun_performance_analyzers.py
from __future__ import absolute_import
import BigWorld
from gui.shared.utils.graphics import isLowPreset

class PerformanceGroup(object):
    LOW_RISK = 0
    MEDIUM_RISK = 1
    HIGH_RISK = 2


class IPerformanceAlertHandler(object):

    def analyze(self):
        raise NotImplementedError


class GraphicsPresetAnalyzerHandler(IPerformanceAlertHandler):
    __ALERT_LEVELS_KEYS = {PerformanceGroup.HIGH_RISK: ['LOW'],
     PerformanceGroup.MEDIUM_RISK: ['MEDIUM']}

    def analyze(self):
        recommendedPresetIndex = BigWorld.detectGraphicsPresetFromSystemSettings()
        presetId = BigWorld.getSystemPerformancePresetIdFromName
        currentLevel = PerformanceGroup.LOW_RISK
        for level, alertNames in self.__ALERT_LEVELS_KEYS.items():
            if alertNames and any((recommendedPresetIndex == presetId(pName) for pName in alertNames)) and level > currentLevel:
                currentLevel = level

        return currentLevel


class RenderPipelineAnalyzerHandler(IPerformanceAlertHandler):

    def analyze(self):
        return PerformanceGroup.MEDIUM_RISK if isLowPreset() else PerformanceGroup.LOW_RISK


class HighPerformanceGroupHandler(IPerformanceAlertHandler):

    def analyze(self):
        return PerformanceGroup.HIGH_RISK


class MediumPerformanceGroupHandler(IPerformanceAlertHandler):

    def analyze(self):
        return PerformanceGroup.MEDIUM_RISK
