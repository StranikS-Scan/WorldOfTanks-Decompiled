# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/gui_items/processors/loot_boxes.py
from __future__ import absolute_import
import logging
from future.utils import viewvalues
import BigWorld
from BWUtil import AsyncReturn
from debug_utils import deprecated
from gui import SystemMessages
from gui.impl import backport
from gui.shared.formatters.currency import getStyle
from helpers.time_utils import getServerUTCTime, makeLocalServerTime
from lootboxes_common import makeStopRerollTokenID
from messenger.formatters import TimeFormatter
from wg_async import wg_async, wg_await
from gui.impl.dialogs import dialogs
from gui.lootbox_system.base.awards import addCompensation, preformatRewardsInfo
from gui.lootbox_system.base.common import REROLLABLE_BOX_OPEN_COUNT, getTextResource
from gui.server_events.bonuses import getMergedBonusesFromDicts
from gui.shared.gui_items.processors import Processor, makeI18nError, makeSuccess, makeError, plugins
from gui.shared.gui_items.processors.plugins import SyncValidator
from gui.shared.notifications import NotificationPriorityLevel
from gui.shared.money import Currency, ZERO_MONEY, Money
from helpers import dependency
from messenger.formatters.service_channel import LootBoxAchievesFormatter, LootBoxSystemAchievesFormatter
from skeletons.gui.game_control import ILootBoxSystemController
from gui.impl.lobby.lootbox_system.base.reset_stats_dialog import ResetStatsDialog
_logger = logging.getLogger(__name__)
_SERVER_ERROR_TEXT_PATH = ['serviceChannelMessages', 'server_error']
_TRANSACTION_TEXT_PATH = ['serviceChannelMessages', 'financialTransaction']
_TRANSACTION_SM_TYPE_TEMPLATE = 'LootBox{}Transaction'

class _LootBoxAvailableValidator(SyncValidator):
    _lootBoxes = dependency.descriptor(ILootBoxSystemController)

    def __init__(self, eventName, category, isEnabled=True):
        super(_LootBoxAvailableValidator, self).__init__(isEnabled)
        self._eventName = eventName
        self._category = category

    def _validate(self):
        return makeError('DISABLED') if self._lootBoxes.getBox(self._eventName, self._category) is None else makeSuccess()


def _makeEventError(errStr, eventName):
    if errStr not in ('DISABLED', 'COOLDOWN'):
        errStr = 'FAILURE'
        return makeError(userMsg='', msgType=SystemMessages.SM_TYPE.ErrorHeader, msgPriority=NotificationPriorityLevel.MEDIUM, msgData={'header': backport.text(getTextResource(_SERVER_ERROR_TEXT_PATH, eventName)())})
    return makeError(userMsg=backport.text(getTextResource(_SERVER_ERROR_TEXT_PATH + [errStr], eventName)()), msgType=SystemMessages.SM_TYPE.ErrorSimple, msgPriority=NotificationPriorityLevel.MEDIUM)


def _makeBoxOpenSuccess(eventName, boxName, count, rewardsList, auxData=None):
    if count > 1:
        header = backport.text(getTextResource(['serviceChannelMessages', 'multipleOpen'], eventName)(), boxName=boxName, count=count)
    else:
        header = backport.text(getTextResource(['serviceChannelMessages', 'open'], eventName)(), boxName=boxName)
    fmt = LootBoxSystemAchievesFormatter.formatQuestAchieves(getMergedBonusesFromDicts(rewardsList), False)
    if fmt is not None:
        rewardsHeader = backport.text(getTextResource(['serviceChannelMessages', 'received'], eventName)())
        return makeSuccess(userMsg=fmt, msgType=SystemMessages.SM_TYPE.LootBoxSystemRewards, msgPriority=NotificationPriorityLevel.LOW, msgData={'header': header,
         'rewardsHeader': rewardsHeader}, auxData=auxData)
    else:
        return makeSuccess(auxData=auxData)


class LootBoxOpenProcessor(Processor):

    def __init__(self, lootBoxItem, count=1):
        super(LootBoxOpenProcessor, self).__init__()
        self.__lootBox = lootBoxItem
        self.__count = count

    def _getCount(self):
        return self.__count

    def _getLootBox(self):
        return self.__lootBox

    def _errorHandler(self, code, errStr='', ctx=None):
        defaultKey = 'lootboxes/open/server_error'
        return makeI18nError('/'.join((defaultKey, errStr)), defaultKey)

    def _successHandler(self, code, ctx=None):
        bonus = ctx.get('bonus', [])
        self._preformatCompensationValue(bonus)
        fmt = LootBoxAchievesFormatter.formatQuestAchieves(getMergedBonusesFromDicts(bonus), False)
        if fmt is not None:
            SystemMessages.pushMessage(fmt, SystemMessages.SM_TYPE.LootBoxRewards)
        return super(LootBoxOpenProcessor, self)._successHandler(code, ctx)

    def _request(self, callback):
        _logger.debug('Make server request to open loot box by id: %r, count: %d', self.__lootBox, self.__count)
        BigWorld.player().tokens.openLootBox(self.__lootBox.getID(), self.__count, lambda code, errStr, ext: self._response(code, callback, ctx=ext, errStr=errStr))

    def _preformatCompensationValue(self, rewardsList):
        for rewards in rewardsList:
            vehiclesList = rewards.get('vehicles', [])
            compValue = self.__getCompensationValue(vehiclesList)
            for currency in Currency.ALL:
                if compValue.get(currency, 0) > 0:
                    currencyValue = rewards.pop(currency, None)
                    if currency is not None:
                        newCurrencyValue = currencyValue - compValue.get(currency, 0)
                        if newCurrencyValue:
                            rewards[currency] = newCurrencyValue

        return

    def __getCompensationValue(self, vehicles):
        comp = ZERO_MONEY
        for vehicleDict in vehicles:
            for vehData in viewvalues(vehicleDict):
                if 'rentCompensation' in vehData:
                    comp += Money.makeFromMoneyTuple(vehData['rentCompensation'])
                if 'customCompensation' in vehData:
                    comp += Money.makeFromMoneyTuple(vehData['customCompensation'])

        return comp


class LootBoxSystemOpenProcessor(LootBoxOpenProcessor):
    __lootBoxes = dependency.descriptor(ILootBoxSystemController)

    def _errorHandler(self, code, errStr='', ctx=None):
        errorRes = _makeEventError(errStr, self._getLootBox().getType())
        SystemMessages.pushMessage(errorRes.userMsg, type=errorRes.sysMsgType, priority=errorRes.msgPriority, messageData=errorRes.msgData)
        return super(LootBoxSystemOpenProcessor, self)._errorHandler(code, errStr, ctx)

    def _successHandler(self, code, ctx=None):
        rewardsList = ctx.get('bonus', [])
        for rewards in rewardsList:
            preformatRewardsInfo(rewards)

        box = self._getLootBox()
        result = _makeBoxOpenSuccess(box.getType(), box.getUserName(), self._getCount(), rewardsList, ctx)
        SystemMessages.pushMessagesFromResult(result)
        return makeSuccess(auxData=ctx)


class LootBoxGetInfoProcessor(Processor):

    def __init__(self, lootBoxes):
        super(LootBoxGetInfoProcessor, self).__init__()
        self.__lootBoxes = lootBoxes

    @deprecated
    def _request(self, callback):
        lootboxIDs = [ item.getID() for item in self.__lootBoxes ]
        _logger.debug('Make server request to get info about loot boxes by ids %r', lootboxIDs)
        BigWorld.player().tokens.getInfoLootBox(lootboxIDs, lambda code, errStr, ext: self._response(code, callback, ctx=ext, errStr=errStr))


class ResetLootBoxSystemStatisticsProcessor(Processor):

    def __init__(self, boxIDs):
        self.__boxIDs = boxIDs
        super(ResetLootBoxSystemStatisticsProcessor, self).__init__([self.__dialogConfirmator()])

    def _errorHandler(self, code, errStr='', ctx=None):
        return makeError('#lootbox_system:serviceChannelMessages/statisticReset/server_error/text', msgType=SystemMessages.SM_TYPE.ErrorSimple)

    def _request(self, callback):
        BigWorld.player().tokens.resetLootBoxStatistics(self.__boxIDs, lambda code, errStr, ext: self._response(code, callback, ctx=ext, errStr=errStr))

    @wg_async
    def __showResetStatsDialog(self):
        layoutID = ResetStatsDialog.LAYOUT_ID
        eventName = self.itemsCache.items.tokens.getLootBoxByID(self.__boxIDs[0]).getType()
        result = yield wg_await(dialogs.showSingleDialog(layoutID=layoutID, wrappedViewClass=ResetStatsDialog, eventName=eventName))
        raise AsyncReturn(result.result)

    def __dialogConfirmator(self):
        return plugins.AsyncDialogConfirmator(self.__showResetStatsDialog)


class RerollLootBoxProcessor(Processor):
    __lootBoxes = dependency.descriptor(ILootBoxSystemController)

    def __init__(self, eventName, category):
        self.__eventName = eventName
        self.__category = category
        super(RerollLootBoxProcessor, self).__init__(plugins=(_LootBoxAvailableValidator(eventName, category),))

    def _request(self, callback):
        BigWorld.player().tokens.rerollBox(self.__lootBoxes.getBox(self.__eventName, self.__category).getID(), lambda code, errStr, ext: self._response(code, callback, ctx=ext, errStr=errStr))

    def _errorHandler(self, code, errStr='', ctx=None):
        return _makeEventError(errStr, self.__eventName)

    def _successHandler(self, code, ctx=None):
        rewards = ctx.get('rewards', {})
        if rewards:
            preformatRewardsInfo(rewards)
        box = self.__lootBoxes.getBox(self.__eventName, self.__category)
        if box is None:
            _logger.error('No box for event: %s, category: %s', self.__eventName, self.__category)
            return makeSuccess(auxData=ctx)
        else:
            if makeStopRerollTokenID(box.getID()) in rewards.get('tokens', {}):
                ctx['rewardsResult'] = _makeBoxOpenSuccess(box.getType(), box.getUserName(), REROLLABLE_BOX_OPEN_COUNT, [rewards])
            else:
                addCompensation(rewards)
            rerollIndex = ctx.get('rerollIndex')
            rerollPrices = box.getRerollPrices()
            if rerollIndex is None or rerollIndex >= len(rerollPrices):
                _logger.error('Invalid rerollIndex: %s for prices: %s', rerollIndex, rerollPrices)
                return makeSuccess(auxData=ctx)
            price = rerollPrices[rerollIndex]
            if price == 0:
                return makeSuccess(auxData=ctx)
            currency = box.getRerollCurrency()
            return makeSuccess(userMsg=backport.text(getTextResource(_TRANSACTION_TEXT_PATH + [currency], self.__eventName)(), amount=getStyle(currency)(price)), msgType=SystemMessages.SM_TYPE.lookup(_TRANSACTION_SM_TYPE_TEMPLATE.format(currency.capitalize())), msgData={'date': backport.text(getTextResource(_TRANSACTION_TEXT_PATH + ['date'], self.__eventName)(), date=TimeFormatter.getLongDatetimeFormat(makeLocalServerTime(getServerUTCTime())))}, auxData=ctx)


class AcceptLootBoxRerollProcessor(Processor):
    __lootBoxes = dependency.descriptor(ILootBoxSystemController)

    def __init__(self, eventName, category):
        self.__eventName = eventName
        self.__category = category
        super(AcceptLootBoxRerollProcessor, self).__init__(plugins=(_LootBoxAvailableValidator(eventName, category),))

    def _request(self, callback):
        BigWorld.player().tokens.acceptBoxRerollRewards(self.__lootBoxes.getBox(self.__eventName, self.__category).getID(), lambda code, errStr, ext: self._response(code, callback, ctx=ext, errStr=errStr))

    def _errorHandler(self, code, errStr='', ctx=None):
        return _makeEventError(errStr, self.__eventName)

    def _successHandler(self, code, ctx=None):
        rewardsList = ctx.get('bonus', [])
        for rewards in rewardsList:
            preformatRewardsInfo(rewards)

        box = self.__lootBoxes.getBox(self.__eventName, self.__category)
        if box is None:
            _logger.error('No box for event: %s, category: %s', self.__eventName, self.__category)
            return makeSuccess(auxData=ctx)
        else:
            return _makeBoxOpenSuccess(box.getType(), box.getUserName(), REROLLABLE_BOX_OPEN_COUNT, rewardsList, ctx)
