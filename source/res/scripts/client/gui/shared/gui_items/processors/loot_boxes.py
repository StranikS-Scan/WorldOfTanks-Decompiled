# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/gui_items/processors/loot_boxes.py
import logging
import BigWorld
from gui import SystemMessages
from gui.server_events.bonuses import getMergedBonusesFromDicts
from gui.shared.gui_items.processors import Processor, makeI18nError
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
        fmt = QuestAchievesFormatter.formatQuestAchieves(getMergedBonusesFromDicts(ctx['bonus']), False)
        if fmt is not None:
            SystemMessages.pushMessage(fmt, SystemMessages.SM_TYPE.LootBoxRewards)
        return super(LootBoxOpenProcessor, self)._successHandler(code, ctx)

    def _request(self, callback):
        _logger.debug('Make server request to open loot box by id: %r, count: %d', self.__lootBox, self.__count)
        BigWorld.player().tokens.openLootBox(self.__lootBox.getID(), self.__count, lambda code, errStr, ext: self._response(code, callback, ctx=ext, errStr=errStr))


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
