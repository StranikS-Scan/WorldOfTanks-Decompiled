# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: grinch/scripts/client/grinch/messenger/formatters/service_channel.py
import logging
from grinch_progression.skeletons.game_controller import IGrinchProgressionController
from gui.impl import backport
from gui.impl.gen import R
from helpers import dependency
from messenger import g_settings
from messenger.formatters.service_channel import BattleResultsFormatter, ServiceChannelFormatter
from grinch_common.grinch_constants import EventStates
from messenger.formatters.service_channel_helpers import MessageData
_logger = logging.getLogger(__name__)

class GrinchBattleResultsFormatter(BattleResultsFormatter):

    def _prepareFormatData(self, message):
        _, ctx = super(GrinchBattleResultsFormatter, self)._prepareFormatData(message)
        ctx['progressionPoints'] = self.__makeTotalPointsString(message)
        return ('GrinchBattleResults', ctx)

    @staticmethod
    def __makeTotalPointsString(message):
        tokens = message.data.get('tokens', {})
        gp = dependency.instance(IGrinchProgressionController)
        grinchProgressionTokens = tokens.get(gp.token, {})
        totalValue = message.data.get('grinch/progressionPoints', 0) + grinchProgressionTokens.get('count', 0)
        return backport.getIntegralFormat(totalValue)


class GrinchEventStateMessageFormatter(ServiceChannelFormatter):
    _grinchProgressionCtrl = dependency.descriptor(IGrinchProgressionController)
    __TEMPLATES = {EventStates.SUSPEND: 'GrinchEventSuspendedMessage',
     EventStates.RESUME: 'GrinchEventResumedMessage',
     EventStates.BATTLES_FINISH: 'GrinchBattlesFinishMessage',
     EventStates.BATTLES_CHAPTER_BEGIN: 'GrinchBattlesBeginChapterMessage',
     EventStates.BATTLES_CHAPTER_FINISH: 'GrinchBattlesFinishChapterMessage'}

    def format(self, message, *args):
        state = message.get('state', None)
        if state is None:
            _logger.error('[GrinchEventStateMessageFormatter] message.state is missing')
            return []
        else:
            template = self.__TEMPLATES.get(state, None)
            if template is None:
                _logger.error('[GrinchEventStateMessageFormatter] Missing template for state %s', state)
                return []
            ctx = {}
            periodInfo = message.get('periodInfo', None)
            if state == EventStates.BATTLES_FINISH:
                dateValue = self._grinchProgressionCtrl.getEndEventDate()
                ctx.update({'date': backport.getShortDateFormat(dateValue)})
            if state == EventStates.BATTLES_CHAPTER_BEGIN:
                if periodInfo is None:
                    _logger.error('[GrinchEventStateMessageFormatter] message.periodInfo is missing')
                    return []
                chapNum = int(periodInfo.seasonBorderLeft.userName)
                header = backport.text(R.strings.grinch_messenger.serviceChannelMessages.grinchBattlesBeginChapterMessage.header(), chapNum=chapNum)
                ctx.update({'header': header,
                 'chapNum': chapNum,
                 'date': backport.getShortDateFormat(periodInfo.seasonBorderRight.timestamp)})
            if state == EventStates.BATTLES_CHAPTER_FINISH:
                if periodInfo is None:
                    _logger.error('[GrinchEventStateMessageFormatter] message.periodInfo is missing')
                    return []
                chapNum = int(periodInfo.seasonBorderLeft.userName)
                header = backport.text(R.strings.grinch_messenger.serviceChannelMessages.grinchBattlesFinishChapterMessage.header(), chapNum=chapNum)
                nextchapNum = int(periodInfo.seasonBorderRight.userName)
                ctx.update({'date': backport.getShortDateFormat(periodInfo.seasonBorderRight.timestamp),
                 'header': header,
                 'chapNum': nextchapNum})
            formatted = g_settings.msgTemplates.format(template, ctx=ctx)
            return [MessageData(formatted, self._getGuiSettings(message, template))]
