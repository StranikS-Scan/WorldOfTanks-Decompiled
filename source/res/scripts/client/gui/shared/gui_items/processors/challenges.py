# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/gui_items/processors/challenges.py
from __future__ import absolute_import
import BigWorld
from functools import partial
from gui.impl import backport
from gui import SystemMessages
from gui.impl.gen import R
from gui.shared.gui_items.processors import Processor, makeError, makeSuccess
from gui.shared.gui_items.processors.plugins import MessageConfirmator
from gui.shared.money import Money
from gui.shared.notifications import NotificationPriorityLevel
from helpers import dependency
from helpers.time_utils import getServerUTCTime, makeLocalServerTime
from messenger import g_settings
from messenger.formatters import TimeFormatter
from skeletons.gui.challenges import IChallengesController

class _ChallengesActionConfirmator(MessageConfirmator):

    def __init__(self, challengeID, actionType, isFree=False):
        super(_ChallengesActionConfirmator, self).__init__(None, True)
        self.__challengeID = challengeID
        self.__actionType = actionType
        self.__isFree = isFree
        return

    def _gfMakeMeta(self):
        from gui.shared.event_dispatcher import showChallengesActionConfirmDialog
        return partial(showChallengesActionConfirmDialog, self.__challengeID, self.__actionType, self.__isFree)


class _ChallengesProcessor(Processor):
    _challengesCtrl = dependency.descriptor(IChallengesController)

    def _errorHandler(self, code, errStr='', ctx=None):
        return self._makeError(errStr)

    def _getMessageKey(self):
        raise NotImplementedError

    def _makeError(self, errStr):
        errorKey = R.strings.system_messages.challenges.serverError.dyn(errStr)
        text = backport.text(errorKey()) if errorKey.exists() else backport.text(self._getMessageKey().serverError())
        return makeError(userMsg=text, msgType=SystemMessages.SM_TYPE.ErrorSimple, msgPriority=NotificationPriorityLevel.MEDIUM)


class ActivateChallengeProcessor(_ChallengesProcessor):
    __ACTION_TYPE = 'activate'

    def __init__(self, challengeId):
        super(ActivateChallengeProcessor, self).__init__()
        self.__challengeId = challengeId
        self.addPlugins([_ChallengesActionConfirmator(self.__challengeId, self.__ACTION_TYPE)])

    def _request(self, callback):
        BigWorld.player().challenges.activateChallenge(self.__challengeId, lambda code, errStr, ext: self._response(code, callback, ctx=ext, errStr=errStr))

    def _getMessageKey(self):
        return R.strings.system_messages.challenges.activate

    def _successHandler(self, code, ctx=None):
        msgKey = self._getMessageKey()
        challenge = self._challengesCtrl.getChallenge(self.__challengeId)
        return makeSuccess(userMsg=backport.text(msgKey.success.text()), msgType=SystemMessages.SM_TYPE.ChallengesActivation, msgData={'title': backport.text(msgKey.success.title(), challengeName=challenge.name)}) if challenge is not None else makeSuccess()


class RestartChallengeProcessor(_ChallengesProcessor):
    __ACTION_TYPE = 'restart'

    def __init__(self, challengeId, isFree):
        super(RestartChallengeProcessor, self).__init__()
        self.__challengeId = challengeId
        self.__isFree = isFree
        self.addPlugins([_ChallengesActionConfirmator(self.__challengeId, self.__ACTION_TYPE, self.__isFree)])

    def _request(self, callback):
        BigWorld.player().challenges.restartChallenge(self.__challengeId, self.__isFree, lambda code, errStr, ext: self._response(code, callback, ctx=ext, errStr=errStr))

    def _getMessageKey(self):
        return R.strings.system_messages.challenges.restart

    def _successHandler(self, code, ctx=None):
        msgKey = self._getMessageKey()
        challenge = self._challengesCtrl.getChallenge(self.__challengeId)
        if challenge is None:
            return makeSuccess()
        elif self.__isFree:
            return makeSuccess(userMsg=backport.text(msgKey.free.text()), msgType=SystemMessages.SM_TYPE.ChallengesFreeRestart, msgData={'title': backport.text(msgKey.free.title(), challengeName=challenge.name)})
        else:
            money = Money.makeMoney(challenge.restartPrice)
            currency = money.getCurrency()
            fmt = g_settings.htmlTemplates.format('challengesSpent{}'.format(currency[0].upper() + currency[1:]), {'amount': backport.getIntegralFormat(money.get(currency))})
            return makeSuccess(userMsg=fmt, msgType=SystemMessages.SM_TYPE.ChallengesPaidRestart, msgData={'title': backport.text(msgKey.paid.title(), challengeName=challenge.name),
             'time': TimeFormatter.getLongDatetimeFormat(makeLocalServerTime(getServerUTCTime()))})


class SurrenderChallengeProcessor(_ChallengesProcessor):
    __ACTION_TYPE = 'surrender'

    def __init__(self, challengeId):
        super(SurrenderChallengeProcessor, self).__init__()
        self.__challengeId = challengeId
        self.addPlugins([_ChallengesActionConfirmator(self.__challengeId, self.__ACTION_TYPE)])

    def _request(self, callback):
        BigWorld.player().challenges.surrenderChallenge(self.__challengeId, lambda code, errStr, ext: self._response(code, callback, ctx=ext, errStr=errStr))

    def _getMessageKey(self):
        return R.strings.system_messages.challenges.surrender

    def _successHandler(self, code, ctx=None):
        msgKey = self._getMessageKey()
        challenge = self._challengesCtrl.getChallenge(self.__challengeId)
        return makeSuccess(userMsg=backport.text(msgKey.success.text(), challengeName=challenge.name), msgType=SystemMessages.SM_TYPE.Information, msgPriority=NotificationPriorityLevel.MEDIUM) if challenge is not None else makeSuccess()
