# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/secret_event/action_view_with_menu.py
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.lobby.header.LobbyHeader import HeaderMenuVisibilityState
from gui.impl.lobby.secret_event.action_view_impl import ActionViewImpl
from gui.Scaleform.genConsts.APP_CONTAINERS_NAMES import APP_CONTAINERS_NAMES
from gui.impl.gen.view_models.views.lobby.secret_event.action_menu_model import ActionMenuModel
from gui.impl.gen.view_models.views.lobby.secret_event.menu_item_model import MenuItemModel
from gui.impl.lobby.secret_event import getTabs, EventViewMixin
from gui.impl.wrappers.background_blur import WGUIBackgroundBlurSupportImpl
from gui.shared import g_eventBus, events, EVENT_BUS_SCOPE, event_dispatcher
from helpers import dependency
from skeletons.gui.game_event_controller import IGameEventController
from skeletons.gui.server_events import IEventsCache

class ActionViewWithMenu(ActionViewImpl, EventViewMixin):
    _slots__ = ('_blur', '_tabs', '_nextPage')
    gameEventController = dependency.descriptor(IGameEventController)
    eventsCache = dependency.descriptor(IEventsCache)

    def __init__(self, settings):
        super(ActionViewWithMenu, self).__init__(settings)
        self._blur = WGUIBackgroundBlurSupportImpl()
        self._tabs = getTabs()
        self._nextPage = None
        return

    @property
    def viewModel(self):
        return self.getViewModel()

    def _initialize(self):
        super(ActionViewWithMenu, self)._initialize()
        self.viewModel.onClose += self.__onClose
        self.viewModel.onLoadView += self.__onLoadView
        self.viewModel.onEscPressed += self._onEscPressed
        self.eventsCache.onSyncCompleted += self._fillMenuItems
        self._eventCacheSubscribe()
        g_eventBus.handleEvent(events.LobbyHeaderMenuEvent(events.LobbyHeaderMenuEvent.TOGGLE_VISIBILITY, ctx={'state': HeaderMenuVisibilityState.NOTHING}), scope=EVENT_BUS_SCOPE.LOBBY)

    def _onLoading(self):
        super(ActionViewWithMenu, self)._onLoading()
        self._fillMenuItems()

    def _onLoaded(self, *args, **kwargs):
        super(ActionViewWithMenu, self)._onLoaded()
        currentView = self.viewModel.getCurrentView()
        settings = self._tabs[currentView]
        if settings.isBlur:
            self._blurBackGround()

    def _finalize(self):
        self.viewModel.onClose -= self.__onClose
        self.viewModel.onEscPressed -= self._onEscPressed
        self.viewModel.onLoadView -= self.__onLoadView
        self.eventsCache.onSyncCompleted -= self._fillMenuItems
        self._eventCacheUnsubscribe()
        np = self._nextPage
        if np is None:
            self._blur.disable()
        else:
            settings = self._tabs[np]
            if not settings.isBlur:
                self._blur.disable()
        super(ActionViewWithMenu, self)._finalize()
        return

    def _blurBackGround(self):
        if self._blur:
            blurLayers = [APP_CONTAINERS_NAMES.SUBVIEW, APP_CONTAINERS_NAMES.MARKER]
            self._blur.enable(APP_CONTAINERS_NAMES.SUBVIEW, blurLayers)

    def _onEscPressed(self):
        if self.viewModel.getCurrentView() == ActionMenuModel.BASE:
            g_eventBus.handleEvent(events.LoadViewEvent(VIEW_ALIAS.LOBBY_MENU), scope=EVENT_BUS_SCOPE.LOBBY)
        else:
            event_dispatcher.loadSecretEventTabMenu(ActionMenuModel.BASE)

    def __createModel(self, settings):
        menuItem = MenuItemModel()
        menuItem.setViewId(settings.id)
        menuItem.setName(settings.name)
        menuItem.setHeader(settings.tooltipHeader)
        menuItem.setDescription(settings.tooltipDesc)
        menuItem.setIsNotification(settings.isNotification)
        return menuItem

    def _fillMenuItems(self):
        self.viewModel.menuItems.clearItems()
        with self.viewModel.menuItems.transaction() as menuItems:
            for settings in self._tabs.itervalues():
                menuItems.addViewModel(self.__createModel(settings))

            menuItems.invalidate()

    def __onClose(self):
        if self.viewModel.getCurrentView() == ActionMenuModel.BASE:
            return
        event_dispatcher.loadSecretEventTabMenu(ActionMenuModel.BASE)

    def __onLoadView(self, args):
        if args is None:
            return
        else:
            menuItem = args.get('viewId')
            isFromPanel = args.get('isFromPanel', False)
            self._nextPage = menuItem
            if menuItem == ActionMenuModel.SHOP:
                event_dispatcher.goToHeroTankFromEvent()
            else:
                event_dispatcher.loadSecretEventTabMenu(menuItem, isFromPanel)
            return
