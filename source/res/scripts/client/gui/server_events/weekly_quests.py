# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/server_events/weekly_quests.py
import logging
import BigWorld
import wg_async
from helpers import dependency, time_utils
from skeletons.gui.server_events import IEventsCache
from gui.shared.utils.requesters import REQ_CRITERIA
from gui.shared.gui_items.processors.plugins import SyncValidator, makeSuccess, makeError
from gui.shared.gui_items.processors.plugins import AwaitConfirmator
from gui.shared.gui_items.processors import Processor, makeI18nError, makeI18nSuccess
from gui.server_events.events_helpers import getWeeklyRerollTimeout
from gui.impl import backport
from gui.impl.dialogs import dialogs
from gui.impl.gen import R
from gui.impl.dialogs.builders import WarningDialogBuilder, ResSimpleDialogBuilder
from gui.impl.wrappers.user_format_string_arg_model import UserFormatStringArgModel as FmtArgs
_logger = logging.getLogger(__name__)

class WQRerollCooldown(SyncValidator):
    eventsCache = dependency.descriptor(IEventsCache)

    def __init__(self, quest, isEnabled=True):
        super(WQRerollCooldown, self).__init__(isEnabled)
        self.__quest = quest

    def _validate(self):
        weeklyQuestsData = self.eventsCache.weeklyQuests
        qId = self.__quest.getInfo().id
        nextRerollAvailableTimestamp = weeklyQuestsData.getNextAvailableRerollTimestamp(qId)
        return makeError('WQ_REROLL_TIMEOUT') if nextRerollAvailableTimestamp > time_utils.getCurrentLocalServerTimestamp() else makeSuccess()


class WQNotCompletedValidator(SyncValidator):

    def __init__(self, quest, isEnabled=True):
        super(WQNotCompletedValidator, self).__init__(isEnabled)
        self.__quest = quest

    def _validate(self):
        return makeError('WQ_QUEST_COMPLETED') if self.__quest.isCompleted() else makeSuccess()


class WQRerollConfirmator(AwaitConfirmator):

    @wg_async.wg_async
    def _confirm(self, callback):
        criteria = REQ_CRITERIA.IN_OWNERSHIP | REQ_CRITERIA.VEHICLE.IS_IN_BATTLE
        numTanksInBattle = len(self.itemsCache.items.getVehicles(criteria=criteria))
        rerollTimeout = getWeeklyRerollTimeout()
        rerollTimeoutDays = time_utils.secondsToDays(rerollTimeout)
        rerollTimeoutHours = time_utils.secondsToHoursNoDays(rerollTimeout)
        rerollTimeoutMins = time_utils.secondsToMinutesNoHours(rerollTimeout)
        dialogConfirmReroll = R.strings.dialogs.dailyQuests.dialogConfirmReroll
        if rerollTimeoutDays > 0:
            if rerollTimeoutHours > 0:
                timeLimitMsg = backport.text(dialogConfirmReroll.timeLimitMsgDaysHours(), days=str(rerollTimeoutDays), hours=str(rerollTimeoutHours))
            else:
                timeLimitMsg = backport.text(dialogConfirmReroll.timeLimitMsgDays(), days=str(rerollTimeoutDays))
        elif rerollTimeoutHours > 0:
            if rerollTimeoutMins > 0:
                timeLimitMsg = backport.text(dialogConfirmReroll.timeLimitMsgHoursMins(), hours=str(rerollTimeoutHours), mins=str(rerollTimeoutMins))
            else:
                timeLimitMsg = backport.text(dialogConfirmReroll.timeLimitMsgHours(), hours=str(rerollTimeoutHours))
        else:
            timeLimitMsg = backport.text(dialogConfirmReroll.timeLimitMsgMins(), mins=str(rerollTimeoutMins))
        if numTanksInBattle > 0:
            dialogParams = R.strings.dialogs.dailyQuests.dialogWarningConfirmReroll
            warningString = backport.text(R.strings.dialogs.dailyQuests.dialogWarningConfirmReroll.warning())
            builder = WarningDialogBuilder()
            builder.setMessagesAndButtons(dialogParams)
            builder.setMessageArgs(fmtArgs=[FmtArgs(warningString, 'warning', R.styles.NeutralTextBigStyle()), FmtArgs(timeLimitMsg, 'timeLimitMsg', R.styles.NeutralTextBigStyle())])
        else:
            dialogParams = R.strings.dialogs.dailyQuests.dialogInfoConfirmReroll
            builder = ResSimpleDialogBuilder()
            builder.setMessagesAndButtons(dialogParams)
            builder.setMessageArgs(fmtArgs=[FmtArgs(timeLimitMsg, 'timeLimitMsg', R.styles.NeutralTextBigStyle())])
        result = yield wg_async.wg_await(dialogs.showSimple(builder.build()))
        callback(makeSuccess() if result else makeError())


class WeeklyQuestReroll(Processor):
    eventsCache = dependency.descriptor(IEventsCache)

    def __init__(self, quest):
        super(WeeklyQuestReroll, self).__init__(plugins=(WQRerollCooldown(quest), WQNotCompletedValidator(quest), WQRerollConfirmator()))
        self._quest = quest
        self._callback = None
        return

    def _errorHandler(self, code, errStr='', ctx=None):
        return makeI18nError('weekly_quests/reroll/%s' % errStr, defaultSysMsgKey='weekly_quests/reroll/unknown_error')

    def _successHandler(self, code, ctx=None):
        return makeI18nSuccess('weekly_quests/reroll/success')

    def _request(self, callback):
        _logger.debug('Make server request to reroll quest: %s', self._quest)
        self._callback = callback
        BigWorld.player().stats.rerollWeeklyQuest(self._quest.getID(), self._onRerolCmdResponseReceived)

    def _onRerolCmdResponseReceived(self, resID, errorStr):
        self._response(resID, self._callback or (lambda *args: None), errStr=errorStr)
        self._callback = None
        return
