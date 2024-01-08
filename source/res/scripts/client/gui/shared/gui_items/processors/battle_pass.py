# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/gui_items/processors/battle_pass.py
import logging
from functools import partial
import BigWorld
from gui import SystemMessages
from gui.Scaleform.Waiting import Waiting
from gui.SystemMessages import SM_TYPE
from gui.impl import backport
from gui.impl.gen import R
from gui.shared import event_dispatcher
from gui.shared.formatters import getBWFormatter, text_styles
from gui.shared.gui_items.processors import Processor, makeI18nError, makeSuccess, plugins
from gui.shared.gui_items.processors.plugins import MessageConfirmator, SyncValidator
from helpers import dependency
from messenger import g_settings
from skeletons.gui.game_control import IBattlePassController
_logger = logging.getLogger(__name__)

class _BattlePassActivateChapterValidator(SyncValidator):
    __battlePassController = dependency.descriptor(IBattlePassController)

    def __init__(self, chapterID, isEnabled=True):
        super(_BattlePassActivateChapterValidator, self).__init__(isEnabled)
        self.__chapterID = chapterID

    def _validate(self):
        return plugins.makeSuccess() if self.__isValid() else plugins.makeError()

    def __isValid(self):
        return self.__chapterID in self.__battlePassController.getChapterIDs()


class _BattlePassActivateChapterConfirmator(MessageConfirmator):

    def __init__(self, chapterID, isEnabled=True):
        super(_BattlePassActivateChapterConfirmator, self).__init__(None, isEnabled)
        self.__chapterID = chapterID
        return

    def _gfMakeMeta(self):
        return partial(event_dispatcher.showBattlePassActivateChapterConfirmDialog, self.__chapterID)


class BattlePassActivateChapterProcessor(Processor):
    __battlePassController = dependency.descriptor(IBattlePassController)
    __WAITING_TEXT = 'switchChapter'

    def __init__(self, chapterID, seasonID):
        super(BattlePassActivateChapterProcessor, self).__init__()
        self.__chapterID = chapterID
        self.__seasonID = seasonID
        self.__hasActiveChapter = self.__battlePassController.hasActiveChapter()
        self.addPlugins((_BattlePassActivateChapterValidator(self.__chapterID), _BattlePassActivateChapterConfirmator(self.__chapterID)))

    def _request(self, callback):
        Waiting.show(self.__WAITING_TEXT)
        _logger.debug('Make server request to switch chapter id: %d', self.__chapterID)
        BigWorld.player().battlePass.activateChapter(self.__chapterID, self.__seasonID, lambda code: self._response(code, callback))

    def _errorHandler(self, code, errStr='', ctx=None):
        res = super(BattlePassActivateChapterProcessor, self)._errorHandler(code, errStr, ctx)
        Waiting.hide(self.__WAITING_TEXT)
        SystemMessages.pushMessage(backport.text(R.strings.system_messages.battlePass.switchChapter.error()), type=SM_TYPE.Error)
        return res

    def _successHandler(self, code, ctx=None):
        res = super(BattlePassActivateChapterProcessor, self)._successHandler(code, ctx)
        Waiting.hide(self.__WAITING_TEXT)
        self.__pushSuccessMessage()
        return res

    def __pushSuccessMessage(self):
        if self.__hasActiveChapter:
            textRes = R.strings.system_messages.battlePass.switchChapter.success()
            messageType = SM_TYPE.BattlePassSwitchChapter
        else:
            textRes = R.strings.system_messages.battlePass.activateChapter.success()
            messageType = SM_TYPE.BattlePassActivateChapter
        chapterName = backport.text(R.strings.battle_pass.chapter.fullName.num(self.__chapterID)())
        SystemMessages.pushMessage(backport.text(textRes, chapter=text_styles.credits(chapterName)), type=messageType)


class BuyBattlePass(Processor):
    __battlePass = dependency.descriptor(IBattlePassController)

    def __init__(self, seasonID, chapterID, priceID):
        super(BuyBattlePass, self).__init__()
        self.__seasonID = seasonID
        self.__chapterID = chapterID
        self.__priceID = priceID

    def _errorHandler(self, code, errStr='', ctx=None):
        return makeI18nError(sysMsgKey='battlePass_buy/server_error')

    def _successHandler(self, code, ctx=None):
        chapterName = backport.text(R.strings.battle_pass.chapter.fullName.num(self.__chapterID)())
        if self.__battlePass.isHoliday():
            description = backport.text(R.strings.messenger.serviceChannelMessages.battlePassHReward.buyWithoutRewards.text())
        else:
            description = backport.text(R.strings.messenger.serviceChannelMessages.battlePassReward.buyWithoutRewards.text(), chapter=text_styles.credits(chapterName))
        return makeSuccess(msgType=SM_TYPE.BattlePassBuy, userMsg='', auxData={'header': backport.text(R.strings.messenger.serviceChannelMessages.battlePassReward.header.buyBP()),
         'description': description,
         'additionalText': self.__makePriceString()})

    def __makePriceString(self):
        return self.__makeCurrencyString(*next(self.__battlePass.getBattlePassCost(self.__chapterID)[self.__priceID].iteritems()))

    @staticmethod
    def __makeCurrencyString(currency, amount):
        return g_settings.htmlTemplates.format('battlePassCurrency', {'currency': backport.text(R.strings.messenger.serviceChannelMessages.battlePassReward.buy.dyn(currency)()),
         'amount': getBWFormatter(currency)(amount)}) if amount else ''

    def _request(self, callback):
        _logger.debug('Make server request to buy battle pass %d for chapter %d', self.__seasonID, self.__chapterID)
        BigWorld.player().shop.buyBattlePass(self.__seasonID, self.__chapterID, self.__priceID, lambda resID, code, errStr: self._response(code, callback, errStr))


class BuyBattlePassLevels(Processor):

    def __init__(self, seasonID, chapterID, levels):
        super(BuyBattlePassLevels, self).__init__()
        self.__seasonID = seasonID
        self.__chapterID = chapterID
        self.__levels = levels

    def _errorHandler(self, code, errStr='', ctx=None):
        return makeI18nError(sysMsgKey='battlePassLevels_buy/server_error')

    def _request(self, callback):
        _logger.debug('Make server request to buy battle pass levels: %d season %d', self.__levels, self.__seasonID)
        BigWorld.player().shop.buyBattlePassLevels(self.__seasonID, self.__chapterID, self.__levels, lambda resID, code, errStr: self._response(code, callback, errStr))
