# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: winback/scripts/client/winback/gui/shared/gui_items/processors/winback.py
import BigWorld
from gui.shared.gui_items.processors import Processor

class WinbackDrawSelectorHintTokenProcessor(Processor):

    def _request(self, callback):
        BigWorld.player().winback.drawWinbackSelectorHintToken(lambda code, errStr: self._response(code, callback, errStr=errStr))
