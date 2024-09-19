# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/gui_items/processors/loot_boxes.py
import logging
import BigWorld
from gui import SystemMessages
from gui.server_events.bonuses import getMergedBonusesFromDicts
from gui.shared.gui_items.processors import Processor, makeI18nError
from gui.shared.money import Currency, ZERO_MONEY, Money
from messenger.formatters.service_channel import QuestAchievesFormatter
_logger = logging.getLogger(__name__)
_DEFAULT_ERROR_KEY = 'lootboxes/open/server_error'

class LootBoxOpenProcessor(Processor):

    def __init__(self, lootBoxItem, count=1):
        super(LootBoxOpenProcessor, self).__init__()
        self.__lootBox = lootBoxItem
        self.__count = count

    def _errorHandler(self, code, errStr='', ctx=None):
        return makeI18nError('/'.join((_DEFAULT_ERROR_KEY, errStr)), _DEFAULT_ERROR_KEY)

    def _successHandler(self, code, ctx=None):
        bonus = ctx.get('bonus', [])
        self.__preformatCompensationValue(bonus)
        fmt = QuestAchievesFormatter.formatQuestAchieves(getMergedBonusesFromDicts(bonus), False)
        if fmt is not None:
            SystemMessages.pushMessage(fmt, SystemMessages.SM_TYPE.LootBoxRewards)
        return super(LootBoxOpenProcessor, self)._successHandler(code, ctx)

    def _request(self, callback):
        _logger.debug('Make server request to open loot box by id: %r, count: %d', self.__lootBox, self.__count)
        BigWorld.player().tokens.openLootBox(self.__lootBox.getID(), self.__count, lambda code, errStr, ext: self._response(code, callback, ctx=ext, errStr=errStr))

    def __preformatCompensationValue(self, rewardsList):
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
            for _, vehData in vehicleDict.iteritems():
                if 'rentCompensation' in vehData:
                    comp += Money.makeFromMoneyTuple(vehData['rentCompensation'])
                if 'customCompensation' in vehData:
                    comp += Money.makeFromMoneyTuple(vehData['customCompensation'])

        return comp


class LootBoxGetInfoProcessor(Processor):

    def __init__(self, lootBoxes):
        super(LootBoxGetInfoProcessor, self).__init__()
        self.__lootBoxes = lootBoxes

    def _request(self, callback):
        lootboxIDs = [ item.getID() for item in self.__lootBoxes ]
        _logger.debug('Make server request to get info about loot boxes by ids %r', lootboxIDs)
        BigWorld.player().tokens.getInfoLootBox(lootboxIDs, lambda code, errStr, ext: self._response(code, callback, ctx=ext, errStr=errStr))


class LootBoxReRollHistoryProcessor(Processor):

    def _errorHandler(self, code, errStr='', ctx=None):
        return makeI18nError('/'.join((_DEFAULT_ERROR_KEY, errStr)), _DEFAULT_ERROR_KEY)

    def _request(self, callback):
        _logger.debug('Make server request to re-roll history')
        BigWorld.player().tokens.getLootBoxReRollRecords(lambda code, errStr, ext: self._response(code, callback, ctx=ext, errStr=errStr))


class LootBoxReRollProcessor(Processor):

    def __init__(self, lootBoxItem):
        super(LootBoxReRollProcessor, self).__init__()
        self.__lootBox = lootBoxItem

    def _errorHandler(self, code, errStr='', ctx=None):
        return makeI18nError('/'.join((_DEFAULT_ERROR_KEY, errStr)), _DEFAULT_ERROR_KEY)

    def _request(self, callback):
        _logger.debug('Make server request to re-roll loot box by id: %r', self.__lootBox)
        BigWorld.player().tokens.reRollLootBox(self.__lootBox.getID(), lambda code, errStr, ext: self._response(code, callback, ctx=ext, errStr=errStr))
