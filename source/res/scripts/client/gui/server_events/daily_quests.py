# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/server_events/daily_quests.py
import logging
import BigWorld
import AccountCommands
import async
from helpers import dependency, time_utils
from skeletons.gui.server_events import IEventsCache
from gui.shared.utils.requesters import REQ_CRITERIA
from gui.shared.gui_items.processors.plugins import SyncValidator, makeSuccess, makeError
from gui.shared.gui_items.processors.plugins import AwaitConfirmator
from gui.shared.gui_items.processors import Processor, makeI18nError, makeI18nSuccess
from gui.server_events.events_helpers import isRerollEnabled, getRerollTimeout
from gui.impl import backport
from gui.impl.dialogs import dialogs
from gui.impl.gen import R
from gui.impl.dialogs.builders import WarningDialogBuilder, ResSimpleDialogBuilder
from gui.impl.wrappers.user_format_string_arg_model import UserFormatStringArgModel as FmtArgs
_logger = logging.getLogger(__name__)

class DQRerollEnabledValidator(SyncValidator):

    def _validate(self):
        return makeError('reroll_disabled') if not isRerollEnabled() else makeSuccess()


class DQRerollCooldown(SyncValidator):
    eventsCache = dependency.descriptor(IEventsCache)

    def _validate(self):
        naxtRerollAvailableTimestamp = self.eventsCache.dailyQuests.getNextAvailableRerollTimestamp()
        return makeError('reroll_in_cooldown') if naxtRerollAvailableTimestamp > time_utils.getCurrentLocalServerTimestamp() else makeSuccess()


class DQNotCompletedValidator(SyncValidator):

    def __init__(self, quest, isEnabled=True):
        super(DQNotCompletedValidator, self).__init__(isEnabled)
        self.__quest = quest

    def _validate(self):
        return makeError('quest_is_already_completed') if self.__quest.isCompleted() else makeSuccess()


class DQRerollConfirmator(AwaitConfirmator):

    @async.async
    def _confirm(self, callback):
        criteria = REQ_CRITERIA.IN_OWNERSHIP | REQ_CRITERIA.VEHICLE.IS_IN_BATTLE
        numTanksInBattle = len(self.itemsCache.items.getVehicles(criteria=criteria))
        rerollTimeoutHours = int(getRerollTimeout() / time_utils.ONE_MINUTE / time_utils.MINUTES_IN_HOUR)
        rerollTimeoutMins = int(getRerollTimeout() % (time_utils.ONE_MINUTE * time_utils.MINUTES_IN_HOUR) / time_utils.ONE_MINUTE)
        if rerollTimeoutHours > 0:
            if rerollTimeoutMins > 0:
                timeLimitMsg = backport.text(R.strings.dialogs.dailyQuests.dialogConfirmReroll.timeLimitMsgHoursMins(), hours=str(rerollTimeoutHours), mins=str(rerollTimeoutMins))
            else:
                timeLimitMsg = backport.text(R.strings.dialogs.dailyQuests.dialogConfirmReroll.timeLimitMsgHours(), hours=str(rerollTimeoutHours))
        else:
            timeLimitMsg = backport.text(R.strings.dialogs.dailyQuests.dialogConfirmReroll.timeLimitMsgMins(), mins=str(rerollTimeoutMins))
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
        result = yield async.await(dialogs.showSimple(builder.build()))
        callback(makeSuccess() if result else makeError())


class DailyQuestReroll(Processor):
    eventsCache = dependency.descriptor(IEventsCache)

    def __init__(self, quest):
        super(DailyQuestReroll, self).__init__(plugins=(DQRerollEnabledValidator(),
         DQRerollCooldown(),
         DQNotCompletedValidator(quest),
         DQRerollConfirmator()))
        self._quest = quest
        self._callback = None
        return

    def _errorHandler(self, code, errStr='', ctx=None):
        return makeI18nError('daily_quests/reroll/%s' % errStr, defaultSysMsgKey='daily_quests/reroll/unknown_error')

    def _successHandler(self, code, ctx=None):
        return makeI18nSuccess('daily_quests/reroll/success')

    def _request(self, callback):
        _logger.debug('Make server request to reroll quest: %s', self._quest)
        self._startListeningForResponse(callback)
        BigWorld.player().stats.rerollDailyQuest(self._quest.getID(), self._onRerolCmdResponseReceived)

    def _onRerolCmdResponseReceived(self, resID):
        if not AccountCommands.isCodeValid(resID):
            self.__response(resID)

    def _startListeningForResponse(self, callback):
        self._callback = callback
        self.eventsCache.onSyncCompleted += self._onEventsSyncCompleted

    def _stopListeningForResponse(self):
        self._callback = None
        self.eventsCache.onSyncCompleted -= self._onEventsSyncCompleted
        return

    def _onEventsSyncCompleted(self):
        if self._quest.getID() not in self.eventsCache.getDailyQuests():
            self.__response(AccountCommands.RES_SUCCESS)

    def __response(self, resID):
        self._response(resID, self._callback or (lambda *args: None), errStr=self.__resID2ErrStr(resID))
        self._stopListeningForResponse()

    def __resID2ErrStr(self, resID):
        return 'reroll_in_cooldown' if resID == AccountCommands.RES_COOLDOWN else ''
