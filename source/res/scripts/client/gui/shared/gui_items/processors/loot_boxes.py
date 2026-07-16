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
from wg_async import wg_async, wg_await
from gui.impl.dialogs import dialogs
from gui.lootbox_system.base.awards import preformatRewardsInfo
from gui.lootbox_system.base.common import getTextResource
from gui.server_events.bonuses import getMergedBonusesFromDicts
from gui.shared import EVENT_BUS_SCOPE, events, g_eventBus
from gui.shared.gui_items.processors import Processor, makeI18nError, makeSuccess, makeError, plugins
from gui.shared.notifications import NotificationPriorityLevel
from gui.shared.money import Currency, ZERO_MONEY, Money
from helpers import dependency
from messenger.formatters.service_channel import LootBoxAchievesFormatter, LootBoxSystemAchievesFormatter
from skeletons.gui.game_control import ILootBoxSystemController
from gui.impl.lobby.lootbox_system.base.reset_stats_dialog import ResetStatsDialog
_logger = logging.getLogger(__name__)

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
        pathParts = ['serviceChannelMessages', 'server_error']
        eventName = self._getLootBox().getType()
        if errStr not in ('DISABLED', 'COOLDOWN'):
            errStr = 'FAILURE'
            SystemMessages.pushMessage(text='', type=SystemMessages.SM_TYPE.ErrorHeader, priority=NotificationPriorityLevel.MEDIUM, messageData={'header': backport.text(getTextResource(pathParts, eventName)())})
        else:
            SystemMessages.pushMessage(text=backport.text(getTextResource(pathParts + [errStr], eventName)()), type=SystemMessages.SM_TYPE.ErrorSimple, priority=NotificationPriorityLevel.MEDIUM)
        g_eventBus.handleEvent(events.LootBoxSystemEvent(events.LootBoxSystemEvent.OPENING_ERROR), scope=EVENT_BUS_SCOPE.LOBBY)
        return super(LootBoxSystemOpenProcessor, self)._errorHandler(code, errStr, ctx)

    def _successHandler(self, code, ctx=None):
        eventName = self._getLootBox().getType()
        count = self._getCount()
        boxName = self._getLootBox().getUserName()
        if count > 1:
            header = backport.text(getTextResource(['serviceChannelMessages', 'multipleOpen'], eventName)(), boxName=boxName, count=count)
        else:
            header = backport.text(getTextResource(['serviceChannelMessages', 'open'], eventName)(), boxName=boxName)
        rewardsList = ctx.get('bonus', [])
        for rewards in rewardsList:
            preformatRewardsInfo(rewards)

        fmt = LootBoxSystemAchievesFormatter.formatQuestAchieves(getMergedBonusesFromDicts(rewardsList), False)
        if fmt is not None:
            rewardsHeader = backport.text(getTextResource(['serviceChannelMessages', 'received'], eventName)())
            SystemMessages.pushMessage(text=fmt, type=SystemMessages.SM_TYPE.LootBoxSystemRewards, priority=NotificationPriorityLevel.LOW, messageData={'header': header,
             'rewardsHeader': rewardsHeader})
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
