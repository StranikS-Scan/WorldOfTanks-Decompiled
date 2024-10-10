# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/gui_items/processors/loot_boxes.py
import logging
from functools import partial
import BigWorld
from AccountCommands import RES_COOLDOWN
from constants import REQUEST_COOLDOWN
from gui.shared.gui_items.processors import Processor, makeI18nError
from helpers import uniprof
_logger = logging.getLogger(__name__)
_DEFAULT_ERROR_KEY = 'lootboxes/open/server_error'
_REQUEST_ATTEMPTS = 2
_COOLDOWN_DELAY = 0.5

class LootBoxOpenProcessor(Processor):
    __slots__ = ('__lootBox', '__count', '__keyID', '__requestAttempts')

    def __init__(self, lootBoxItem, count=1, keyID=0):
        super(LootBoxOpenProcessor, self).__init__()
        self.__lootBox = lootBoxItem
        self.__count = count
        self.__keyID = keyID
        self.__requestAttempts = _REQUEST_ATTEMPTS

    def _errorHandler(self, code, errStr='', ctx=None):
        return makeI18nError('/'.join((_DEFAULT_ERROR_KEY, errStr)), _DEFAULT_ERROR_KEY)

    def _request(self, callback):
        uniprof.enterToRegion('LootBoxOpenProcessor.request')
        if self.__keyID == 0:
            _logger.debug('Make server request to open loot box by id: %r, count: %d', self.__lootBox, self.__count)
            BigWorld.player().tokens.openLootBox(self.__lootBox.getID(), self.__count, lambda code, errStr, ext: self._response(code, callback, ctx=ext, errStr=errStr))
        else:
            _logger.debug('Make server request to open loot box by key by id: %r, count: %d keyID: %d', self.__lootBox, self.__count, self.__keyID)
            BigWorld.player().tokens.openLootBoxByKey(self.__lootBox.getID(), self.__count, self.__keyID, lambda code, errStr, ext: self._response(code, callback, ctx=ext, errStr=errStr))
        self.__requestAttempts -= 1

    def _response(self, code, callback, errStr='', ctx=None):
        uniprof.exitFromRegion('LootBoxOpenProcessor.request')
        if code == RES_COOLDOWN and self.__requestAttempts:
            _logger.debug('Server cooldown response: code=%r, error=%r, ctx=%r', code, errStr, ctx)
            BigWorld.callback(REQUEST_COOLDOWN.LOOTBOX + _COOLDOWN_DELAY, partial(self._request, callback))
            return None
        else:
            return super(LootBoxOpenProcessor, self)._response(code, callback, errStr, ctx)


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
