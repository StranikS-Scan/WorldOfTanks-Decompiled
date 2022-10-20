# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/messenger/formatters/service_channel.py
import logging
from halloween.gui.game_control.halloween_progress_controller import PhaseTransition
from halloween.hw_constants import FIRST_PHASE_INDEX
from halloween.hw_constants import PhaseType
from gui.impl import backport
from helpers import dependency
from messenger import g_settings
from messenger.formatters.service_channel import ServiceChannelFormatter
from messenger.formatters.service_channel_helpers import MessageData
from skeletons.gui.game_control import IEventBattlesController
_logger = logging.getLogger(__name__)

class EventLifetimeFormatter(ServiceChannelFormatter):
    __eventBattlesController = dependency.descriptor(IEventBattlesController)
    _PHASE_TYPE_FORMATTERS = {PhaseType.REGULAR: {(FIRST_PHASE_INDEX, PhaseTransition.STARTED): ('HW22EventStartedSystemMessage', [])},
     PhaseType.POST: {PhaseTransition.STARTED: ('HW22PostSaleStartedSystemMessage', ['date']),
                      PhaseTransition.ENDED: ('HW22EventFinishedSystemMessage', [])}}
    _DATE_FORMATTER = '{date}, {time}'

    def format(self, data, *args):
        emptyMsgData = [MessageData(None, None)]
        if not data:
            _logger.error('Incorrect HW22 Phase transition data: %s', data)
        phaseIndex = data.get('phaseIndex')
        transition = data.get('transition')
        if not all((phaseIndex, transition)):
            _logger.error('Incorrect HW22 Phase transition data: %s', data)
        hwPhases = self.__eventBattlesController.getHWProgressCtrl().phasesHalloween
        phase = hwPhases.getPhaseByIndex(phaseIndex)
        if phase is None:
            return emptyMsgData
        else:
            data['date'] = self._getFormattedDateTime(phase.getFinishTime())
            formatters = self._PHASE_TYPE_FORMATTERS[phase.phaseType]
            state = (phaseIndex, transition) if phase.phaseType == PhaseType.REGULAR else transition
            if state not in formatters:
                return emptyMsgData
            formatter, params = formatters[state]
            ctx = {key:data[key] for key in params}
            formatted = g_settings.msgTemplates.format(formatter, ctx=ctx)
            return [MessageData(formatted, self._getGuiSettings(data, formatter))]

    def _getFormattedDateTime(self, dateTime):
        return self._DATE_FORMATTER.format(date=backport.getLongDateFormat(dateTime), time=backport.getShortTimeFormat(dateTime))
