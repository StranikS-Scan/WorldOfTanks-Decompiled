# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/gui_items/processors/advent_calendar_v2_processor.py
import BigWorld
import logging
from gui.shared.gui_items.processors import Processor
_logger = logging.getLogger(__name__)

class AdventCalendarDoorsProcessor(Processor):

    def __init__(self, dayID, currencyName):
        super(AdventCalendarDoorsProcessor, self).__init__()
        self.__dayID = dayID
        self.__currencyName = currencyName

    def _errorHandler(self, code, errStr='', ctx=None):
        _logger.error('Failed to open door=%d, errorCode=%d, errorMsg=%s', self.__dayID, code, errStr)
        return super(AdventCalendarDoorsProcessor, self)._errorHandler(code, errStr, ctx)

    def _request(self, callback):
        _logger.debug('Make server request to open Adent door number: %d, currency %s', self.__dayID, self.__currencyName)
        BigWorld.player().adventCalendarV2.openAdventCalendarDoor(self.__dayID, self.__currencyName, lambda code, errStr: self._response(code, callback, errStr))
