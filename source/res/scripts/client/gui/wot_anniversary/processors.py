# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/wot_anniversary/processors.py
import BigWorld
from gui.shared.gui_items.processors import Processor
from helpers import dependency
from skeletons.gui.wot_anniversary import IWotAnniversaryController

class WotAnniversaryOpenEnvelopeProcessor(Processor):
    __wotAnniversaryController = dependency.descriptor(IWotAnniversaryController)

    def _request(self, callback):
        BigWorld.player().wotAnniversary.openEnvelope(lambda code, errorStr, ext: self._response(code, callback, errStr=errorStr, ctx=ext))
