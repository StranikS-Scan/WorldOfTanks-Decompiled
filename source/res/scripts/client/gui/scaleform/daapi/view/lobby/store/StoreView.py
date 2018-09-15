# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/store/StoreView.py
from account_helpers import AccountSettings
from gui.Scaleform.daapi.view.lobby.store.actions_formatters import getActiveActions, getNewActiveActions
from gui.Scaleform.daapi.view.meta.StoreViewMeta import StoreViewMeta
from gui.Scaleform.locale.MENU import MENU
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.shared import events, g_eventBus, EVENT_BUS_SCOPE
from gui.sounds.ambients import ShopEnv
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.genConsts.STORE_CONSTANTS import STORE_CONSTANTS
from helpers import dependency
from helpers.i18n import makeString
from shared_utils import findFirst
from skeletons.gui.server_events import IEventsCache
_TABS = ({'id': STORE_CONSTANTS.STORE_ACTIONS,
  'label': makeString(MENU.STORETAB_ACTIONS),
  'linkage': STORE_CONSTANTS.STORE_ACTIONS_LINKAGE}, {'id': STORE_CONSTANTS.SHOP,
  'label': makeString(MENU.STORETAB_SHOP),
  'linkage': STORE_CONSTANTS.SHOP_LINKAGE}, {'id': STORE_CONSTANTS.INVENTORY,
  'label': makeString(MENU.STORETAB_INVENTORY),
  'linkage': STORE_CONSTANTS.INVENTORY_LINKAGE})

def _getTabIndex(tabId):
    index, _ = findFirst(lambda (i, e): e['id'] == tabId, enumerate(_TABS), (0, None))
    return index


class StoreView(StoreViewMeta):
    __sound_env__ = ShopEnv
    eventsCache = dependency.descriptor(IEventsCache)

    def __init__(self, ctx=None):
        super(StoreView, self).__init__(ctx)
        self.__currentTabIdx = None
        self.__currentTabId = None
        self.__showBackButton = False
        self.__addHandlers()
        self._initialize(ctx)
        return

    def _populate(self):
        super(StoreView, self)._populate()
        self.as_initS({'currentViewIdx': self.__currentTabIdx,
         'buttonBarData': _TABS,
         'bgImageSrc': RES_ICONS.MAPS_ICONS_MISSIONS_BACKGROUNDS_SHOP})
        self.__updateActionsCounter()

    def _invalidate(self, ctx=None):
        super(StoreView, self)._invalidate(ctx)
        tabId = ctx.get('tabId')
        prevTabID = self.__currentTabIdx
        self._initialize(ctx)
        self.__updateActionsCounter()
        if prevTabID != self.__currentTabIdx and tabId is not None:
            self.as_showStorePageS(tabId)
            self.components.get(self.__currentTabId).updateFilters()
        return

    def __addHandlers(self):
        g_eventBus.addListener(events.LobbySimpleEvent.EVENTS_UPDATED, self.__onActionVisitedChange, scope=EVENT_BUS_SCOPE.DEFAULT)

    def __removeHandlers(self):
        g_eventBus.removeListener(events.LobbySimpleEvent.EVENTS_UPDATED, self.__onActionVisitedChange, scope=EVENT_BUS_SCOPE.DEFAULT)

    def __onActionVisitedChange(self, event):
        self.__updateActionsCounter()

    def __updateActionsCounter(self):
        newActions = getNewActiveActions(self.eventsCache)
        if newActions:
            self.as_setBtnTabCountersS(({'componentId': STORE_CONSTANTS.STORE_ACTIONS,
              'count': str(len(newActions))},))
        else:
            self.as_removeBtnTabCountersS((STORE_CONSTANTS.STORE_ACTIONS,))

    def _initialize(self, ctx=None):
        ctx = ctx or {}
        tabId = ctx.get('tabId')
        component = ctx.get('component')
        itemCD = ctx.get('itemCD')
        self.__showBackButton = ctx.get('showBackButton', False)
        if tabId is not None:
            self.__currentTabIdx = _getTabIndex(tabId)
        elif self.__currentTabIdx is None:
            if getActiveActions(self.eventsCache):
                self.__currentTabIdx = _getTabIndex(STORE_CONSTANTS.STORE_ACTIONS)
            else:
                self.__currentTabIdx = _getTabIndex(STORE_CONSTANTS.SHOP)
        if component is not None:
            nation, _, actionsSelected = AccountSettings.getFilter('shop_current')
            AccountSettings.setFilter('shop_current', (nation, component, actionsSelected))
        if all((itemCD, component, tabId)):
            AccountSettings.setFilter('scroll_to_item', itemCD)
            section = '{}_{}'.format(tabId, component)
            _, component, _ = AccountSettings.getFilter('shop_current')
            defaults = AccountSettings.getFilterDefault(section)
            AccountSettings.setFilter('shop_current', (-1, component, False))
            AccountSettings.setFilter(section, defaults)
        return

    def onTabChange(self, tabId):
        isBackBtnShow = bool(self.__currentTabId == STORE_CONSTANTS.STORE_ACTIONS and tabId == STORE_CONSTANTS.SHOP)
        self.__updateBackButton(isBackBtnShow)
        self.__currentTabId = tabId
        self.__currentTabIdx = _getTabIndex(tabId)

    def onClose(self):
        self.fireEvent(events.LoadViewEvent(VIEW_ALIAS.LOBBY_HANGAR), scope=EVENT_BUS_SCOPE.LOBBY)

    def onBackButtonClick(self):
        self.as_showStorePageS(STORE_CONSTANTS.STORE_ACTIONS)

    def __updateBackButton(self, isShow):
        if isShow and self.__showBackButton:
            self.as_showBackButtonS(MENU.STORE_BACKBUTTON_LABEL, MENU.STORE_BACKBUTTON_DESCRIPTION)
        else:
            self.as_hideBackButtonS()
        self.__showBackButton = False

    def _dispose(self):
        self.__removeHandlers()
        super(StoreView, self)._dispose()
