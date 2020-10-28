# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/hangar/event/event_style_shop_preview.py
import logging
import BigWorld
from CurrentVehicle import g_currentPreviewVehicle
from WeakMethod import WeakMethodProxy
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.lobby.hangar.event.event_confirmation import EventConfirmationCloser
from gui.Scaleform.framework.managers.loaders import SFViewLoadParams
from gui.server_events.awards_formatters import getEventShopConfirmFormatter, getEventAwardFormatter, AWARDS_SIZES, formatShopConfirmBonus
from gui.shared import g_eventBus, events, EVENT_BUS_SCOPE
from gui.shared.gui_items import GUI_ITEM_TYPE
from helpers import dependency
from gui.Scaleform.daapi.view.lobby.hangar.event.event_styles_preview_base import EventStylesTradeBase
from adisp import process
from items.vehicles import VehicleDescriptor
from skeletons.gui.game_event_controller import IGameEventController
from gui.impl.gen import R
from gui.impl import backport
from gui.server_events.events_dispatcher import showRecruitWindow
_logger = logging.getLogger(__name__)

class EventStylesShopPreview(EventStylesTradeBase, EventConfirmationCloser):
    gameEventController = dependency.descriptor(IGameEventController)
    _DEACTIVATABLE_BUY_BUTTON = True
    _EVENT_COIN_CURRENCY = 'eventCoin'

    def __init__(self, ctx=None):
        super(EventStylesShopPreview, self).__init__(ctx)
        self._highlightHangarVehicle = True

    def onBuyClick(self):
        item = self.getSelectedItem()
        if item is None:
            return
        else:
            styleID = self._getStyleIDFromItem(item)
            vehicleDescr = VehicleDescriptor(typeName=self._getVehicleTypeFromItem(item))
            vehicleType = vehicleDescr.type
            styleItem = self.c11nService.getItemByID(GUI_ITEM_TYPE.STYLE, styleID)
            descr = ''
            vehiclesInInventory = self._getVehiclesInInventory()
            if vehicleType.compactDescr not in vehiclesInInventory:
                descr = backport.text(R.strings.event.tradeStyles.warning(), name=vehicleType.shortUserString)
            giftBonus = item.getTankmanBonus()
            bonuses = [ b for b in item.getBonuses() if b.getName() != giftBonus.getName() ]
            formattedBonuses = getEventShopConfirmFormatter().format(bonuses)
            rewards = [ formatShopConfirmBonus(bonus, styleItem.icon) for bonus in formattedBonuses ]
            formattedGiftBonus = getEventShopConfirmFormatter().format([giftBonus])
            gift = formatShopConfirmBonus(formattedGiftBonus[0])
            g_eventBus.handleEvent(events.LoadViewEvent(SFViewLoadParams(VIEW_ALIAS.EVENT_CONFIRMATION), ctx={'title': backport.text(R.strings.event.shop.styleBuy.title(), styleName=styleItem.userName, vehName=vehicleType.shortUserString),
             'descr': descr,
             'rewards': rewards,
             'giftTitle': backport.text(R.strings.event.shop.styleBuy.giftTitle()),
             'giftDescr': backport.text(R.strings.event.shop.styleBuy.giftDescr()),
             'gift': gift,
             'currency': self._EVENT_COIN_CURRENCY,
             'price': item.price,
             'purchaseConfirmedCallback': WeakMethodProxy(self._purchaseCallback),
             'closeCallback': WeakMethodProxy(self._confirmationClosedCallback)}), EVENT_BUS_SCOPE.LOBBY)
            self.as_setVisibleS(False)
            self.showBlur()
            return

    def getSelectedItem(self):
        shop = self.gameEventController.getShop()
        items = shop.getStyleItems()
        return items[self._selectedTank] if self._selectedTank < len(items) else None

    def _purchaseCallback(self):
        item = self.getSelectedItem()
        if item is None:
            return
        else:
            self._buyStyle(item)
            return

    def _confirmationClosedCallback(self):
        self.as_setVisibleS(True)
        self.hideBlur()

    @process
    def _buyStyle(self, item):
        result = yield item.buy()
        if result.success:
            tankmanBonusTokenID = item.getTankmanBonusTokenID()
            if tankmanBonusTokenID is not None:
                showRecruitWindow(tankmanBonusTokenID)
        return

    def _populate(self):
        super(EventStylesShopPreview, self)._populate()
        self.gameEventController.getShop().onShopUpdated += self._onShopUpdated
        if BigWorld.player() is not None:
            BigWorld.player().objectsSelectionEnabled(False)
        self.hideMarkers()
        self._changeStyle(self._selectedTank)
        self.hangarSpace.setVehicleSelectable(False)
        return

    def _dispose(self):
        self.gameEventController.getShop().onShopUpdated -= self._onShopUpdated
        g_currentPreviewVehicle.selectNoVehicle()
        if BigWorld.player() is not None:
            BigWorld.player().objectsSelectionEnabled(True)
        self.showMarkers()
        super(EventStylesShopPreview, self)._dispose()
        return

    def _onShopUpdated(self):
        self._updateData()

    def _getStyles(self):
        shop = self.gameEventController.getShop()
        return [ {'vehicle': self._getVehicleTypeFromItem(item),
         'price': item.price,
         'styleID': self._getStyleIDFromItem(item),
         'currency': self._EVENT_COIN_CURRENCY} for item in shop.getStyleItems() ]

    def _getCurrencyAmount(self, _):
        shop = self.gameEventController.getShop()
        return shop.getCoins()

    def _getSkinVO(self, style):
        vo = super(EventStylesShopPreview, self)._getSkinVO(style)
        shop = self.gameEventController.getShop()
        item = [ i for i in shop.getStyleItems() if self._getStyleIDFromItem(i) == style['styleID'] ].pop()
        bonusFormatted = getEventAwardFormatter().format([item.getTankmanBonus()])[0]
        vo.update({'hasReward': True,
         'rewardIcon': bonusFormatted.getImage(AWARDS_SIZES.SMALL),
         'rewardTooltip': {'tooltip': bonusFormatted.tooltip,
                           'isSpecial': bonusFormatted.isSpecial,
                           'specialAlias': bonusFormatted.specialAlias,
                           'specialArgs': bonusFormatted.specialArgs}})
        return vo

    def _getStyleIDFromItem(self, item):
        return item.getCustomizationsBonus().getCustomizations()[0].get('id')

    @staticmethod
    def _getVehicleTypeFromItem(item):
        return item.getID().split('::')[-1]
