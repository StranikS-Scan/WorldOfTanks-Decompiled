# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/hangar/event/event_pack_confirmation.py
import logging
import GUI
from adisp import process
from gui.Scaleform.daapi.view.meta.EventItemPackTradeMeta import EventItemPackTradeMeta
from gui.Scaleform.daapi.view.meta.EventPlayerPackTradeMeta import EventPlayerPackTradeMeta
from gui.Scaleform.genConsts.CURRENCIES_CONSTANTS import CURRENCIES_CONSTANTS
from gui.server_events.awards_formatters import AWARDS_SIZES, getEventShopPackConfirmFormatter
from gui.server_events.events_dispatcher import showEventShop
from gui.shared.utils.functions import makeTooltip
from gui.shop import showBuyGoldForBundle
from helpers import dependency
from gui.impl.gen import R
from gui.impl import backport
from gui.shared import events, EVENT_BUS_SCOPE, event_dispatcher
from skeletons.gui.game_event_controller import IGameEventController
from skeletons.gui.game_control import IEventTokenController
from skeletons.gui.shared import IItemsCache
_logger = logging.getLogger(__name__)

class EventPackConfirmationMixin(object):
    gameEventController = dependency.descriptor(IGameEventController)
    eventToken = dependency.descriptor(IEventTokenController)
    itemsCache = dependency.descriptor(IItemsCache)
    _BONUSES_ORDER = ('customizations', 'battleToken', 'premium_plus', 'goodies', 'items', 'crewBooks', 'customizations', 'tmanToken')

    def init(self, ctx):
        self._shop = self.gameEventController.getShop()
        self._blur = GUI.WGUIBackgroundBlur()
        self._index = ctx.get('index')
        self._item = self._shop.getPackItemByType(self._index)

    def closeView(self):
        showEventShop()

    def backView(self):
        self.closeView()

    @process
    def _onButtonPaymentSetPanelClick(self):
        currency, price = self._item.currency, self._item.price
        stats = self.itemsCache.items.stats
        curAmount = stats.money.get(currency, 0)
        isGold = currency == CURRENCIES_CONSTANTS.GOLD
        notEnough = curAmount < price and isGold
        if notEnough:
            showBuyGoldForBundle(price, {})
        else:
            isOk = yield self._item.buy()
            if isOk.success:
                self.destroy()
                event_dispatcher.showCongratulationWindow(self._index)

    def _onPopulate(self):
        self._blur.enable = True
        self.fireEvent(events.HangarVehicleEvent(events.HangarVehicleEvent.HERO_TANK_MARKER, ctx={'isDisable': True}), EVENT_BUS_SCOPE.LOBBY)
        self._shop.onShopUpdated += self._update
        self._update()

    def _onDispose(self):
        self._shop.onShopUpdated -= self._update
        self.fireEvent(events.HangarVehicleEvent(events.HangarVehicleEvent.HERO_TANK_MARKER, ctx={'isDisable': False}), EVENT_BUS_SCOPE.LOBBY)
        self._blur.enable = False

    def _getKeySortOrder(self, key):
        return self._BONUSES_ORDER.index(key) if key in self._BONUSES_ORDER else -1

    def _sortFunc(self, b1, b2):
        return cmp(self._getKeySortOrder(b1.bonusName), self._getKeySortOrder(b2.bonusName))

    def _getGeneralData(self):
        if self._item.canBuy():
            btnLabel = backport.text(R.strings.event.shop.bestDeal.buyButtonLabel())
        else:
            btnLabel = backport.text(R.strings.event.shop.bestDeal.bought())
        return {'header': backport.text(R.strings.event.shop.bestDeal.num(self._index)()),
         'backDescription': backport.text(R.strings.event.shop.bestDeal.backDescription()),
         'inStock': backport.text(R.strings.event.shop.simpleItem.inStock()),
         'tokens': self._shop.getCoins(),
         'oldPrice': self._item.oldPrice,
         'newPrice': self._item.price,
         'percent': self._item.discount,
         'btnLabel': btnLabel,
         'btnEnabled': self._item.canBuy(),
         'infoTitle': backport.text(R.strings.event.shop.bestDeal.free()),
         'infoDescription': backport.text(R.strings.event.shop.bestDeal.num(self._index).freeDescription()),
         'infoTooltip': makeTooltip(body=backport.text(R.strings.event.shop.bestDeal.tooltip.info.num(self._index)()))}

    def _getItemData(self, bonus, iconSize=AWARDS_SIZES.BIG):
        return {'name': bonus.getImage(iconSize),
         'value': bonus.label,
         'tooltip': bonus.tooltip,
         'specialAlias': bonus.specialAlias,
         'specialArgs': bonus.specialArgs}

    def _getRewardsData(self):
        raise NotImplementedError

    def _update(self):
        if not self._shop.isEnabled():
            self.closeView()
            return
        data = self._getGeneralData()
        data.update(self._getRewardsData())
        self.as_setDataS(data)


class EventPlayerPackConfirmation(EventPackConfirmationMixin, EventPlayerPackTradeMeta):

    def __init__(self, ctx=None, *args, **kwargs):
        super(EventPlayerPackConfirmation, self).__init__(*args, **kwargs)
        self.init(ctx)

    def onButtonPaymentSetPanelClick(self, count):
        self._onButtonPaymentSetPanelClick()

    def _populate(self):
        super(EventPlayerPackConfirmation, self)._populate()
        self._onPopulate()

    def _dispose(self):
        self._onDispose()
        super(EventPlayerPackConfirmation, self)._dispose()

    def _getItemData(self, bonus, iconSize=AWARDS_SIZES.BIG):
        data = super(EventPlayerPackConfirmation, self)._getItemData(bonus, iconSize=AWARDS_SIZES.BIG)
        data.update({'description': bonus.userName})
        return data

    def _getRewardsData(self):
        formatter = getEventShopPackConfirmFormatter()
        bonuses = sorted(formatter.format(self._item.getBonuses()), cmp=self._sortFunc)
        extraBonuses = sorted(formatter.format(self._item.extraBonuses), cmp=self._sortFunc)
        return {'item1': self._getItemData(bonuses[0]),
         'item2': self._getItemData(bonuses[1]),
         'item3': self._getItemData(bonuses[2]),
         'vehicle1': self._getItemData(extraBonuses[0]),
         'vehicle2': self._getItemData(extraBonuses[1]),
         'description': backport.text(R.strings.event.shop.bestDeal.premiumVehiclesDescription())}


class EventItemPackConfirmation(EventPackConfirmationMixin, EventItemPackTradeMeta):

    def __init__(self, ctx=None, *args, **kwargs):
        super(EventItemPackConfirmation, self).__init__(*args, **kwargs)
        self.init(ctx)

    def onButtonPaymentSetPanelClick(self, count):
        self._onButtonPaymentSetPanelClick()

    def _populate(self):
        super(EventItemPackConfirmation, self)._populate()
        self._onPopulate()

    def _dispose(self):
        self._onDispose()
        super(EventItemPackConfirmation, self)._dispose()

    def _getRewardsData(self):
        formatter = getEventShopPackConfirmFormatter()
        bonuses = sorted(formatter.format(self._item.getBonuses()), cmp=self._sortFunc)
        extraBonuses = sorted(formatter.format(self._item.extraBonuses), cmp=self._sortFunc)
        return {'items': [ self._getItemData(bonus) for bonus in bonuses ],
         'styles': [ self._getItemData(bonus) for bonus in extraBonuses ]}
