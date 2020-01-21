# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/gui_items/processors/loot_boxes.py
import logging
import BigWorld
from gui import SystemMessages
from gui.impl.lobby.loot_box.loot_box_helper import getMergedLootBoxBonuses
from gui.shared.gui_items.processors import Processor, makeI18nError
from messenger.formatters.service_channel import TokenQuestsFormatter
_logger = logging.getLogger(__name__)

class LootBoxOpenProcessor(Processor):

    def __init__(self, lootBoxItem, count=1):
        super(LootBoxOpenProcessor, self).__init__()
        self.__lootBox = lootBoxItem
        self.__count = count

    def _errorHandler(self, code, errStr='', ctx=None):
        defaultKey = 'lootboxes/open/server_error'
        return makeI18nError('/'.join((defaultKey, errStr)), defaultKey)

    def _successHandler(self, code, ctx=None):
        fmt = TokenQuestsFormatter.formatQuestAchieves(getMergedLootBoxBonuses(ctx), False)
        if fmt is not None:
            SystemMessages.pushMessage(fmt, SystemMessages.SM_TYPE.LootBoxRewards)
        return super(LootBoxOpenProcessor, self)._successHandler(code, ctx)

    def _request(self, callback):
        _logger.debug('Make server request to open loot box by id: %r, count: %d', self.__lootBox, self.__count)
        BigWorld.player().tokens.openLootBox(self.__lootBox.getID(), self.__count, lambda code, errStr, ext: self._response(code, callback, ctx=ext, errStr=errStr))


class LootBoxGetInfoProcessor(Processor):

    def __init__(self, lootBoxes, fullInfo=True):
        super(LootBoxGetInfoProcessor, self).__init__()
        self.__lootBoxes = lootBoxes
        self.__fullInfo = fullInfo

    def _request(self, callback):
        lootboxIDs = [ item.getID() for item in self.__lootBoxes ]
        _logger.debug('Make server request to get info about loot boxes by ids %r', lootboxIDs)
        BigWorld.player().tokens.getInfoLootBox(lootboxIDs, self.__fullInfo, lambda code, errStr, ext: self._response(code, callback, ctx=ext, errStr=errStr))
