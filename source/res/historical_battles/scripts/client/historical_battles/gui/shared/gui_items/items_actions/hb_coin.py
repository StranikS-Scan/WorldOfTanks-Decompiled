# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/shared/gui_items/items_actions/hb_coin.py
import typing
from adisp import adisp_process
from wg_async import wg_async
from gui.Scaleform.Waiting import Waiting
from gui.impl.gen import R
from gui.shared.gui_items.items_actions.actions import AsyncGUIItemAction
from historical_battles.gui.shared.gui_items.processors.hb_coin import HBCoinsExchangeProcessor
if typing.TYPE_CHECKING:
    from gui.SystemMessages import ResultMsg

class ExchangeHBCoinsAction(AsyncGUIItemAction):
    __slots__ = ('_coinsToGive', '_coinsToGet', '_count')

    def __init__(self, coinsToGive, coinsToGet, count):
        super(ExchangeHBCoinsAction, self).__init__()
        self._coinsToGive = coinsToGive
        self._coinsToGet = coinsToGet
        self._count = count

    @wg_async
    @adisp_process
    def doAction(self, callback):
        Waiting.show(R.invalid)
        result = yield HBCoinsExchangeProcessor(self._coinsToGive, self._coinsToGet, self._count).request()
        Waiting.hide(R.invalid)
        self._showResult(result)
        callback(result.success)
