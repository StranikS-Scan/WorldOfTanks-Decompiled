# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/shop_sales/entry_point.py
import WWISE
from account_helpers.settings_core import settings_constants
from constants import EventPhase
from frameworks.wulf import ViewSettings
from frameworks.wulf.gui_constants import ViewFlags
from gui.Scaleform.framework.entities.inject_component_adaptor import InjectComponentAdaptor
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.impl import backport
from gui.impl.backport import BackportTooltipWindow, createTooltipData
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.shop_sales.shop_sales_entry_point_model import ShopSalesEntryPointModel
from gui.impl.gen.view_models.views.lobby.shop_sales.shop_sales_entry_point_states import ShopSalesEntryPointStates
from gui.impl.pub import ViewImpl
from gui.shared.utils.scheduled_notifications import Notifiable, TimerNotifier
from helpers import dependency
from helpers.time_utils import getServerUTCTime
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.game_control import IShopSalesEventController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
from gui.shared import g_eventBus
from gui.shared.events import CarouselEvent
from account_helpers.settings_core.options import CarouselTypeSetting
_EVENT_PHASE = {EventPhase.NOT_STARTED: ShopSalesEntryPointStates.STATE_LOCKED,
 EventPhase.IN_PROGRESS: ShopSalesEntryPointStates.STATE_ACTIVE,
 EventPhase.FINISHED: ShopSalesEntryPointStates.STATE_ENDED}

def _getState(isEnabled, isInEvent, eventPhase):
    return _EVENT_PHASE.get(eventPhase, ShopSalesEntryPointStates.STATE_LOCKED) if isEnabled and isInEvent else ShopSalesEntryPointStates.STATE_LOCKED


class _Notifiable(Notifiable):

    def updateNotifiers(self, *notifiers):
        self.clearNotification()
        self.addNotificators(*notifiers)
        self.startNotification()


class ShopSalesEntryPointInject(InjectComponentAdaptor):

    def _makeInjectView(self):
        return ShopSalesEntryPoint()


class ShopSalesEntryPoint(ViewImpl, _Notifiable):
    __settingsCore = dependency.descriptor(ISettingsCore)
    __lobbyContext = dependency.descriptor(ILobbyContext)
    __itemsCache = dependency.descriptor(IItemsCache)
    __shopSales = dependency.descriptor(IShopSalesEventController)
    __slots__ = ()

    def __init__(self):
        settings = ViewSettings(R.views.lobby.shop_sales.shop_sales_entry_point.ShopSalesEntryPoint())
        settings.flags = ViewFlags.COMPONENT
        settings.model = ShopSalesEntryPointModel()
        super(ShopSalesEntryPoint, self).__init__(settings)

    @property
    def viewModel(self):
        return super(ShopSalesEntryPoint, self).getViewModel()

    def createToolTip(self, event):
        if event.contentID == R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent():
            tooltipId = event.getArgument('tooltipId')
            if tooltipId != TOOLTIPS_CONSTANTS.SHOP_SALES_ENTRY_POINT:
                return
            tooltipData = createTooltipData(isSpecial=True, specialAlias=tooltipId)
            if tooltipData is None:
                return
            window = BackportTooltipWindow(tooltipData, self.getParentWindow())
            if window is not None:
                window.load()
            return window
        else:
            return super(ShopSalesEntryPoint, self).createToolTip(event)

    def _initialize(self):
        super(ShopSalesEntryPoint, self)._initialize()
        self.viewModel.onClick += self.__onClickHandler
        self.__shopSales.onStateChanged += self.__onUpdate
        self.__shopSales.onPhaseChanged += self.__onPhaseChanged
        self.__shopSales.onFavoritesChanged += self.__onUpdate
        g_eventBus.addListener(CarouselEvent.CAROUSEL_TYPE_WAS_CHANGED, self.__onCarouselTypeChanged)

    def _finalize(self):
        self.clearNotification()
        self.__shopSales.onFavoritesChanged -= self.__onUpdate
        self.__shopSales.onPhaseChanged -= self.__onPhaseChanged
        self.__shopSales.onStateChanged -= self.__onUpdate
        self.viewModel.onClick -= self.__onClickHandler
        g_eventBus.removeListener(CarouselEvent.CAROUSEL_TYPE_WAS_CHANGED, self.__onCarouselTypeChanged)
        super(ShopSalesEntryPoint, self)._finalize()

    def _onLoading(self, *args, **kwargs):
        super(ShopSalesEntryPoint, self)._onLoading(*args, **kwargs)
        self.__update()

    def __onCarouselTypeChanged(self, event):
        caruselType = event.ctx[CarouselEvent.CAROUSEL_TYPE_ARG]
        self.viewModel.setIsDoubleRowsCarousel(caruselType == CarouselTypeSetting.OPTIONS.DOUBLE)

    def __onClickHandler(self, _=None):
        self.__shopSales.openMainView()

    def __onPhaseChanged(self):
        if self.__shopSales.currentEventPhase == EventPhase.IN_PROGRESS:
            WWISE.WW_eventGlobal(backport.sound(R.sounds.double_eleven_unlock_ui()))
        self.__onUpdate()

    def __onUpdate(self, *_):
        self.__update()

    def __update(self):
        self.updateNotifiers(TimerNotifier(self.__getCooldown, self.__updateCooldown))
        setting = self.__settingsCore.options.getSetting(settings_constants.GAME.CAROUSEL_TYPE)
        isDoubleRowsCarousel = setting.getRowCount() > 1
        setting = self.__settingsCore.options.getSetting(settings_constants.GAME.DOUBLE_CAROUSEL_TYPE)
        isSmallDoubleCarouselEnable = setting.enableSmallCarousel()
        with self.viewModel.transaction() as tx:
            tx.setIsDoubleRowsCarousel(isDoubleRowsCarousel)
            tx.setIsSmallDoubleCarouselEnable(isSmallDoubleCarouselEnable)
            tx.setState(_getState(self.__shopSales.isEnabled, self.__shopSales.isInEvent, self.__shopSales.currentEventPhase))
            tx.setIsDisabled(not (self.__shopSales.isEnabled and self.__shopSales.isInEvent and self.__shopSales.currentEventPhase != EventPhase.NOT_STARTED))
            tx.setItemsCount(self.__shopSales.favoritesCount)
            self.__updateCooldown(tx)

    def __updateCooldown(self, viewModel=None):
        (viewModel or self.viewModel).setCooldownTime(backport.getTillTimeStringByRClass(self.__getCooldown(preventNegative=True), R.strings.menu.headerButtons.battle.types.ranked.availability))

    def __getCooldown(self, preventNegative=False):
        _, endTimestamp = self.__shopSales.currentEventPhaseTimeRange
        cooldown = endTimestamp - getServerUTCTime()
        return 0 if cooldown < 0 and preventNegative else cooldown
