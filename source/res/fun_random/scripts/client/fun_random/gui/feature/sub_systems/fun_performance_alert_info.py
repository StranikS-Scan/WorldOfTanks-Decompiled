# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/gui/feature/sub_systems/fun_performance_alert_info.py
from __future__ import absolute_import
import logging
from fun_random.gui.feature.sub_systems.fun_performance_analyzers import GraphicsPresetAnalyzerHandler, RenderPipelineAnalyzerHandler, PerformanceGroup, MediumPerformanceGroupHandler, HighPerformanceGroupHandler
from fun_random_common.fun_constants import FunPerformanceParameter
_logger = logging.getLogger(__name__)
_ALERT_HANDLERS = {FunPerformanceParameter.RECOMMENDED_GRAPHICS_PRESET: GraphicsPresetAnalyzerHandler(),
 FunPerformanceParameter.RENDER_PIPELINE: RenderPipelineAnalyzerHandler(),
 FunPerformanceParameter.MEDIUM_RISK: MediumPerformanceGroupHandler(),
 FunPerformanceParameter.HIGH_RISK: HighPerformanceGroupHandler()}

class PerformanceAlertInfo(object):
    _DEFAULT_ALERT_GROUP = PerformanceGroup.LOW_RISK

    def __init__(self, alertType=None):
        self._performanceGroup = self._analyzeClientSystem(alertType)

    @property
    def performanceGroup(self):
        return self._performanceGroup

    def _analyzeClientSystem(self, alertType):
        if not alertType:
            return self._DEFAULT_ALERT_GROUP
        handler = _ALERT_HANDLERS.get(alertType)
        if not handler:
            _logger.debug('Handler for alert type %s not found', alertType)
            return self._DEFAULT_ALERT_GROUP
        return handler.analyze()
