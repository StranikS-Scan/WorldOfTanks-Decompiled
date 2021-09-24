# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/gui_items/processors/wt_event.py
import logging
import BigWorld
from gui.shared.gui_items.processors import Processor
from helpers import dependency, isPlayerAccount
from skeletons.gui.game_control import IGameEventController
_logger = logging.getLogger(__name__)

class WtEventVehicleExchange(Processor):
    __eventCtrl = dependency.descriptor(IGameEventController)

    def _request(self, callback):
        _logger.debug('Make server request to exchange lootBoxes on the vehicle')
        if isPlayerAccount():
            exchangeConfig = self.__eventCtrl.getConfig().exchange
            token = exchangeConfig['token']
            BigWorld.player().requestSingleToken(token, lambda code, errStr, ext: self._response(code, callback, ctx=ext, errStr=errStr))
