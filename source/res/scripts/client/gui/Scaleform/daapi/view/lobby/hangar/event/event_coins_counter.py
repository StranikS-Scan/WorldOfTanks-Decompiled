# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/hangar/event/event_coins_counter.py
from gui.Scaleform.daapi.view.meta.EventCoinsCounterMeta import EventCoinsCounterMeta
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from helpers import dependency
from skeletons.gui.game_event_controller import IGameEventController

class EventCoinsCounter(EventCoinsCounterMeta):
    _gameEventController = dependency.descriptor(IGameEventController)
    _BONUS_NAME = 'battleToken'
    _ICON_PATH = '../maps/icons/missions/tokens/80x80/token_he19_money.png'

    @property
    def _shop(self):
        return self._gameEventController.getShop()

    def _populate(self):
        super(EventCoinsCounter, self)._populate()
        self._shop.onShopUpdated += self.__update
        self.__update()

    def _dispose(self):
        self._shop.onShopUpdated -= self.__update
        super(EventCoinsCounter, self)._dispose()

    def __update(self):
        tooltipData = {'tooltip': '',
         'specialArgs': [None, self._BONUS_NAME, self._ICON_PATH],
         'specialAlias': TOOLTIPS_CONSTANTS.EVENT_BONUSES_INFO,
         'isSpecial': True}
        self.as_setCoinsTooltipS(tooltipData)
        self.as_setCoinsCountS(self._shop.getCoins())
        return
