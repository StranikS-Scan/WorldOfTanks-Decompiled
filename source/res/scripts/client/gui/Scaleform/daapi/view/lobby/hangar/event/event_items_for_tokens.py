# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/hangar/event/event_items_for_tokens.py
import Keys
from frameworks.wulf import ViewSettings, ViewFlags
from gui import InputHandler
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.framework.managers.loaders import SFViewLoadParams
from gui.Scaleform.genConsts.LAYER_NAMES import LAYER_NAMES
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.impl import backport
from gui.impl.backport import BackportTooltipWindow, createTooltipData
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.event.event_items_for_tokens_model import EventItemsForTokensModel
from gui.impl.gen.view_models.views.lobby.event.ift_item_group_model import IftItemGroupModel
from gui.impl.gen.view_models.views.lobby.event.ift_item_model import IftItemModel
from gui.impl.pub import ViewImpl
from gui.server_events.awards_formatters import EventItemsSizes, AWARDS_SIZES, getEventShopItemListFormatter
from gui.server_events.events_dispatcher import showEventShop
from gui.server_events.game_event.shop import ShopItems
from gui.shared import g_eventBus, events, EVENT_BUS_SCOPE
from gui.shared.view_helpers.blur_manager import CachedBlur
from helpers import dependency
from shared_utils import first
from skeletons.gui.game_control import IEventTokenController
from skeletons.gui.game_event_controller import IGameEventController
_BONUS_NAME = 'battleToken'
_ICON_PATH = '../maps/icons/missions/tokens/80x80/token_he19_money.png'

class EventItemsForTokensWindow(ViewImpl):
    gameEventController = dependency.descriptor(IGameEventController)
    eventToken = dependency.descriptor(IEventTokenController)
    itemTypes = [ShopItems.Boosters, ShopItems.Goodies, ShopItems.CrewBooks]

    def __init__(self):
        settings = ViewSettings(layoutID=R.views.lobby.halloween.ItemsForTokensWindow(), flags=ViewFlags.COMPONENT, model=EventItemsForTokensModel())
        self.__blur = CachedBlur(enabled=True, ownLayer=LAYER_NAMES.SUBVIEW)
        self.__shop = self.gameEventController.getShop()
        super(EventItemsForTokensWindow, self).__init__(settings)

    @property
    def _viewModel(self):
        return self.getViewModel()

    def _initialize(self, *args, **kwargs):
        super(EventItemsForTokensWindow, self)._initialize()
        self.__shop.onShopUpdated += self._onLoading
        self._viewModel.onClose += self._onClose
        self._viewModel.onBack += self._onBack
        self._viewModel.onItemClicked += self._onItemClicked
        self.eventToken.onEventMoneyUpdated += self._onLoading

    def _onLoaded(self, *args, **kwargs):
        InputHandler.g_instance.onKeyDown += self.__handleKeyEvent

    def _finalize(self):
        super(EventItemsForTokensWindow, self)._finalize()
        self.__blur.fini()
        self.__shop.onShopUpdated -= self._onLoading
        self._viewModel.onClose -= self._onClose
        self._viewModel.onBack -= self._onBack
        self._viewModel.onItemClicked -= self._onItemClicked
        self.eventToken.onEventMoneyUpdated -= self._onLoading
        InputHandler.g_instance.onKeyDown -= self.__handleKeyEvent

    def _onLoading(self, *args, **kwargs):
        super(EventItemsForTokensWindow, self)._onLoading(*args, **kwargs)
        with self._viewModel.transaction() as model:
            model.setTokens(self.__shop.getCoins())
            groupsContainer = model.groups.getItems()
            for itemType in self.itemTypes:
                group = IftItemGroupModel()
                group.setTitle(backport.text(R.strings.event.ift.titles.dyn(itemType.value)()))
                group.setType(itemType.value)
                itemsContainer = group.items.getItems()
                groupsContainer.addViewModel(group)
                for simpleItem in self.__shop.getSimpleItemsByType(itemType.value):
                    formattedBonus = first(getEventShopItemListFormatter().format(simpleItem.getBonuses()))
                    item = IftItemModel()
                    item.setTitle(formattedBonus.userName)
                    item.setAmount(formattedBonus.label)
                    item.setIcon(formattedBonus.images.get(EventItemsSizes.SMALL))
                    item.setAvailable(simpleItem.getBonusCount())
                    item.setPrice(simpleItem.price)
                    item.setHighlight(formattedBonus.getHighlightType(AWARDS_SIZES.SMALL))
                    itemsContainer.addViewModel(item)
                    item.setDescription(formattedBonus.description)

            groupsContainer.invalidate()

    def _onItemClicked(self, args):
        itemTypeValue = args.get('type')
        itemIndex = int(args.get('index'))
        g_eventBus.handleEvent(events.LoadViewEvent(SFViewLoadParams(VIEW_ALIAS.EVENT_SIMPLE_ITEM_CONFIRMATION), ctx={'itemTypeValue': itemTypeValue,
         'itemIndex': itemIndex}), scope=EVENT_BUS_SCOPE.LOBBY)

    def _onBack(self):
        self._onClose()

    def _onClose(self):
        self.destroyWindow()
        showEventShop()

    def __handleKeyEvent(self, event):
        if event.key == Keys.KEY_ESCAPE:
            self._onBack()

    def createToolTip(self, event):
        if event.contentID == R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent():
            tooltipID = event.getArgument('tooltipId', '')
            if tooltipID == EventItemsForTokensModel.TOKEN_TOOLTIP_ID:
                window = BackportTooltipWindow(createTooltipData(isSpecial=True, specialAlias=TOOLTIPS_CONSTANTS.EVENT_BONUSES_INFO, specialArgs=[None, _BONUS_NAME, _ICON_PATH]), self.getParentWindow())
                window.load()
                return window
        return super(EventItemsForTokensWindow, self).createToolTip(event)
