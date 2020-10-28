# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/hangar/event/event_simple_item_confirmation.py
import GUI
from adisp import process
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.framework.managers.loaders import SFViewLoadParams
from gui.server_events.awards_formatters import getSimpleItemsFormatter, EventItemsSizes, AWARDS_SIZES
from gui.shared.utils.functions import makeTooltip
from helpers import dependency
from gui.impl.gen import R
from gui.impl import backport
from gui.Scaleform.daapi.view.meta.EventItemsTradeMeta import EventItemsTradeMeta
from gui.shared import events, EVENT_BUS_SCOPE, g_eventBus
from skeletons.gui.game_event_controller import IGameEventController
from skeletons.gui.game_control import IEventTokenController
from shared_utils import first

class EventSimpleItemTab(EventItemsTradeMeta):
    gameEventController = dependency.descriptor(IGameEventController)
    eventToken = dependency.descriptor(IEventTokenController)

    def __init__(self, ctx=None, *args, **kwargs):
        super(EventSimpleItemTab, self).__init__(*args, **kwargs)
        self.__shop = self.gameEventController.getShop()
        self.__blur = GUI.WGUIBackgroundBlur()
        self._ctx = ctx
        self._item = self.__shop.getSimpleItemByTypeAndIndex(self._ctx.get('itemTypeValue'), self._ctx.get('itemIndex'))

    def closeView(self):
        g_eventBus.handleEvent(events.LoadViewEvent(SFViewLoadParams(VIEW_ALIAS.EVENT_ITEMS_FOR_TOKENS)), scope=EVENT_BUS_SCOPE.LOBBY)

    def backView(self):
        self.closeView()

    @process
    def onButtonPaymentPanelClick(self, count):
        result = yield self._item.buy(count=count)
        if result.success:
            g_eventBus.handleEvent(events.LoadViewEvent(SFViewLoadParams(VIEW_ALIAS.EVENT_SIMPLE_ITEM_CONGRATULATION), ctx={'item': self._item}), scope=EVENT_BUS_SCOPE.LOBBY)

    def _populate(self):
        super(EventSimpleItemTab, self)._populate()
        self.eventToken.onEventMoneyUpdated += self._update
        self.__shop.onShopUpdated += self._update
        self.fireEvent(events.HangarVehicleEvent(events.HangarVehicleEvent.HERO_TANK_MARKER, ctx={'isDisable': True}), EVENT_BUS_SCOPE.LOBBY)
        self.__blur.enable = True
        self._update()

    def _dispose(self):
        self.fireEvent(events.HangarVehicleEvent(events.HangarVehicleEvent.HERO_TANK_MARKER, ctx={'isDisable': False}), EVENT_BUS_SCOPE.LOBBY)
        self.__blur.enable = False
        self.eventToken.onEventMoneyUpdated -= self._update
        self.__shop.onShopUpdated -= self._update
        super(EventSimpleItemTab, self)._dispose()

    def _update(self):
        coinsAmount = self.__shop.getCoins()
        bonuses = self._item.getBonuses()
        formattedBonus = first(getSimpleItemsFormatter().format(bonuses))
        if self._item.canBuy():
            availableForPurchase = backport.text(R.strings.event.shop.simpleItem.availableForPurchase())
            btnTooltip = ''
        else:
            availableForPurchase = backport.text(R.strings.event.shop.simpleItem.outOfStock())
            btnTooltip = makeTooltip(body=backport.text(R.strings.event.shop.simpleItem.outOfStockMsg()))
        data = {'header': formattedBonus.userName,
         'title': backport.text(R.strings.event.shop.simpleItem.title()),
         'description': formattedBonus.description,
         'btnLabel': backport.text(R.strings.event.shop.simpleItem.btnLabel()),
         'backDescription': backport.text(R.strings.event.shop.simpleItem.backDescription()),
         'item': formattedBonus.images.get(EventItemsSizes.HUGE),
         'inStock': backport.text(R.strings.event.shop.simpleItem.inStock()),
         'availableForPurchase': availableForPurchase,
         'value': self._item.price,
         'count': self._item.getBonusCount(),
         'tokens': coinsAmount,
         'multiplier': formattedBonus.label,
         'btnTooltip': btnTooltip,
         'sign': formattedBonus.getOverlayIcon(AWARDS_SIZES.BIG)}
        self.as_setDataS(data)
        self.as_updateTokensS(coinsAmount)
