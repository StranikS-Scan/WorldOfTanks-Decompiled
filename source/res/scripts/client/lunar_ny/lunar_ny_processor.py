# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/lunar_ny/lunar_ny_processor.py
from typing import List
import BigWorld
from gui.shared.gui_items.processors import Processor
from gui.impl.gen import R
from gui.impl import backport
from gui import SystemMessages
from gui.SystemMessages import SM_TYPE

class FillAlbumSlotProcessor(Processor):
    __slots__ = ('__charmID', '__slotIdx')

    def __init__(self, charmID, slotID):
        super(FillAlbumSlotProcessor, self).__init__()
        self.__charmID = int(charmID)
        self.__slotIdx = int(slotID)

    def _request(self, callback):
        BigWorld.player().lunarNY.fillAlbumSlot(self.__slotIdx, self.__charmID, lambda _, resultID, errorStr, ctx=None: self._response(resultID, callback, errStr=errorStr, ctx=ctx))
        return

    def _errorHandler(self, code, errStr='', ctx=None):
        SystemMessages.pushMessage(backport.text(R.strings.lunar_ny.album.fillAlbumError()), type=SM_TYPE.Error)
        return super(FillAlbumSlotProcessor, self)._errorHandler(code, errStr, ctx)


class SeenAllCharmsProcessor(Processor):
    __slots__ = ('__charmIDs',)

    def __init__(self, charmIDs):
        super(SeenAllCharmsProcessor, self).__init__()
        self.__charmIDs = map(int, charmIDs)

    def _request(self, callback):
        BigWorld.player().lunarNY.markSeenAllNewCharms(self.__charmIDs, lambda _, resultID, errorStr, ctx=None: self._response(resultID, callback, ctx=ctx, errStr=errorStr))
        return
