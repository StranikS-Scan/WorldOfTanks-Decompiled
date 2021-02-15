# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/gui_items/processors/blueprints_convert_sale.py
import BigWorld
from gui.shared.gui_items.processors import Processor

class ProcessExchangeBlueprintsProcessor(Processor):

    def __init__(self, offerID, count=1):
        super(ProcessExchangeBlueprintsProcessor, self).__init__()
        self.offerID = offerID
        self.count = count

    def _request(self, callback):
        BigWorld.player().exchangeBlueprintsSale(self.offerID, self.count, lambda code, errStr: self._response(code, callback, errStr=errStr))
