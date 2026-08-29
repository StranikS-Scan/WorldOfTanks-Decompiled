# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/uilogging/prebattle_highlights/loggers.py
from __future__ import absolute_import
import json
import logging
from typing import TYPE_CHECKING, NamedTuple, Tuple
from uilogging.base.logger import MetricsLogger
from uilogging.prebattle_highlights.constants import FEATURE, PrebattleHighlightsLogAction, PrebattleHighlightsLogKeys
if TYPE_CHECKING:
    from typing import Dict, Any, Optional
_logger = logging.getLogger(__name__)
PBHViewingLogInfo = NamedTuple('PBHViewingLogInfo', [('sequence_layer', Tuple[str, int]), ('historical_level', int), ('was_historical_compliance', bool)])

class PrebattleHighlightsEventLogger(MetricsLogger):

    def __init__(self):
        super(PrebattleHighlightsEventLogger, self).__init__(FEATURE)
        self.__viewingLogInfo = None
        return

    def reset(self):
        self.__viewingLogInfo = None
        super(PrebattleHighlightsEventLogger, self).reset()
        return

    def logStartViewingAction(self, info):
        if self.__viewingLogInfo is not None:
            _logger.debug('Log info is already stored and will be rewrote. Current: %s; New: %s', self.__viewingLogInfo, info)
        self.__viewingLogInfo = info
        self.startAction(PrebattleHighlightsLogAction.VIEWED)
        return

    def logStopViewingAction(self, viewStatus):
        if self.__viewingLogInfo is None:
            _logger.debug('Log info not found.')
            return
        else:
            layerName, layerDuration = self.__viewingLogInfo.sequence_layer
            infoStr = json.dumps({'view_status': viewStatus.value,
             'sequence_type': layerName,
             'sequence_duration': int(layerDuration),
             'historical_level': self.__viewingLogInfo.historical_level,
             'was_historical_warning_shown': self.__viewingLogInfo.was_historical_compliance})
            self.__viewingLogInfo = None
            self.stopAction(PrebattleHighlightsLogAction.VIEWED, PrebattleHighlightsLogKeys.PBH, info=infoStr)
            return

    def logSkipViewingEvent(self, info):
        infoStr = json.dumps(info)
        self._log(PrebattleHighlightsLogAction.VIEWED, item=PrebattleHighlightsLogKeys.PBH, parent_screen=None, item_state=None, additional_info=infoStr, partnerID=None, timeSpent=0.0)
        return

    def logUnfocusClientEvent(self):
        self.logOnce(PrebattleHighlightsLogAction.COLLAPSE, PrebattleHighlightsLogKeys.PBH_OUT_OF_FOCUS)
