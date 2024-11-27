# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: new_year/scripts/client/new_year/gui/shared/ny_bubble_navigation_controller.py
from Event import Event
from helpers import dependency
from skeletons.gui.impl import IGuiLoader, INewYearNavigation
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared import IItemsCache
from gui.impl.gen import R
from gui.ClientUpdateManager import g_clientUpdateManager
from frameworks.wulf import ViewStatus
from new_year.ny_constants import NyWidgetTopMenu
from new_year.skeletons.new_year import INewYearController, INewYearBubbleNavigationController
from new_year.gui.shared.ny_currency_provider import NyCurrencyProvider
from new_year_common.items.components.ny_constants import CustomizationObjects, OBJECT_MAX_LEVEL, TOKEN_VARIADIC_DISCOUNT_PREFIX
from new_year.gui.shared.ny_level_helper import NewYearAtmospherePresenter
from new_year.gui.impl.gen.view_models.common.ny_currency_type_model import NyCurrencyType
from new_year.gui.impl.lobby.new_year.quests.ny_quest_helper import getDaysFromQuestsUpdate, updateQuestsUpdatedAt
from new_year_account_settings import getShowBubbleNavigation, setShowBubbleNavigation, getCanBuyCustomizationZone, setCanBuyCustomizationZone
from new_year.gui.impl.lobby.new_year.ny_menu_component import NAVIGATION_ALIAS_VIEWS

def replaceMenuName(value):

    def outer(fn):

        def wrapper(self, *args, **kwargs):
            if 'menuName' in kwargs:
                return fn(self, *args, **kwargs)
            kwargs['menuName'] = value
            return fn(self, *args, **kwargs)

        return wrapper

    return outer


class NewYearBubbleNavigationController(INewYearBubbleNavigationController):
    __slots__ = ('__currencyProvider', '__currency', 'onUpdateBubble')
    __nyController = dependency.descriptor(INewYearController)
    __guiLoader = dependency.descriptor(IGuiLoader)
    __eventsCache = dependency.descriptor(IEventsCache)
    __newYearNavigation = dependency.descriptor(INewYearNavigation)
    __itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, *args, **kwargs):
        self.__currencyProvider = NyCurrencyProvider()
        self.__currency = NyCurrencyType.MANDARIN
        self.onUpdateBubble = Event()
        super(NewYearBubbleNavigationController, self).__init__(*args, **kwargs)

    def onLobbyStarted(self, *_):
        self.__currencyProvider.initialize()
        self.__subscribe()
        self.__updateQuestsMenu()

    def fini(self):
        self.__unsubscribe()
        self.__currencyProvider.finalize()

    def onAccountBecomeNonPlayer(self):
        self.__unsubscribe()

    def __subscribe(self):
        if self.__guiLoader.windowsManager is not None:
            self.__guiLoader.windowsManager.onViewStatusChanged += self.__onViewStatusChanged
        self.__nyController.onCustomizationObjectUpdated += self.__onCustomizationObjectUpdated
        self.__currencyProvider.onCurrencyUpdated += self.__onCurrencyUpdated
        self.__eventsCache.onSyncCompleted += self.__onSyncCompleted
        g_clientUpdateManager.addCallback('tokens', self.__onTokensUpdate)
        return

    def __unsubscribe(self):
        if self.__guiLoader.windowsManager is not None:
            self.__guiLoader.windowsManager.onViewStatusChanged -= self.__onViewStatusChanged
        self.__nyController.onCustomizationObjectUpdated -= self.__onCustomizationObjectUpdated
        self.__currencyProvider.onCurrencyUpdated -= self.__onCurrencyUpdated
        self.__eventsCache.onSyncCompleted -= self.__onSyncCompleted
        g_clientUpdateManager.removeObjectCallbacks(self, True)
        return

    def __onTokensUpdate(self, tokens):
        self.__updateRewardsMenu(tokens=tokens)

    def __checkIfCurrentView(self, widgetNavigationName):
        viewAlias = NAVIGATION_ALIAS_VIEWS[widgetNavigationName]
        return self.__newYearNavigation.isCurrentView(viewAlias)

    def __onCurrencyUpdated(self, currency, diff):
        if currency == self.__currency:
            self.__updateCityMenu()
        elif currency == NyCurrencyType.NYGIFTMACHINETOKEN:
            self.__updateSurpriseMachineMenu()

    def __onCustomizationObjectUpdated(self, *args):
        self.__updateCityMenu()

    def __onViewStatusChanged(self, uniqueID, newStatus):
        mainView = R.views.new_year.lobby.new_year.MainView()
        view = self.__guiLoader.windowsManager.getView(uniqueID)
        if view and view.layoutID == mainView:
            if newStatus == ViewStatus.CREATED:
                view.onNewYearViewInitialized += self.__onNewYearViewInitialized
            if newStatus == ViewStatus.DESTROYING:
                view.onNewYearViewInitialized -= self.__onNewYearViewInitialized

    def __onNewYearViewInitialized(self, menuName):
        if menuName not in NyWidgetTopMenu.BUBBLE_NAVIGATION:
            return
        self.__setShowBubbleNavigation(menuName, False)

    def __onSyncCompleted(self, *args):
        self.__updateQuestsMenu()

    def __setShowBubbleNavigation(self, navigationName, value):
        if getShowBubbleNavigation(navigationName) != value:
            setShowBubbleNavigation(navigationName, value)
            self.onUpdateBubble()

    @replaceMenuName(NyWidgetTopMenu.CITY)
    def __updateCityMenu(self, menuName):
        currencyCount = self.__currencyProvider.getCurrencyCount(self.__currency)
        self.__setShowBubbleNavigation(menuName, False)
        for objectName in CustomizationObjects.ALL:
            level = NewYearAtmospherePresenter.getLevelItem(objectName)
            if level < OBJECT_MAX_LEVEL:
                updateLevelPrice = NewYearAtmospherePresenter.getLevelPrice(objectName, level + 1)
                if updateLevelPrice <= currencyCount:
                    if not getCanBuyCustomizationZone(objectName) and not self.__checkIfCurrentView(menuName):
                        self.__setShowBubbleNavigation(menuName, True)
                    setCanBuyCustomizationZone(objectName, True)
                elif getCanBuyCustomizationZone(objectName):
                    setCanBuyCustomizationZone(objectName, False)

    @replaceMenuName(NyWidgetTopMenu.SURPRISE_MACHINE)
    def __updateSurpriseMachineMenu(self, menuName):
        if not self.__checkIfCurrentView(menuName):
            self.__setShowBubbleNavigation(menuName, True)

    @replaceMenuName(NyWidgetTopMenu.QUESTS)
    def __updateQuestsMenu(self, menuName):
        if getDaysFromQuestsUpdate() >= 1:
            updateQuestsUpdatedAt()
            if not self.__checkIfCurrentView(menuName):
                self.__setShowBubbleNavigation(menuName, True)

    @replaceMenuName(NyWidgetTopMenu.REWARDS)
    def __updateRewardsMenu(self, menuName, tokens):
        if not self.__checkIfCurrentView(menuName):
            for key, value in tokens.items():
                if key.startswith(TOKEN_VARIADIC_DISCOUNT_PREFIX):
                    if value:
                        self.__setShowBubbleNavigation(menuName, True)
                    else:
                        cacheTokens = self.__itemsCache.items.tokens.getTokens()
                        for cacheKey, _ in cacheTokens.items():
                            if cacheKey.startswith(TOKEN_VARIADIC_DISCOUNT_PREFIX):
                                return

                        self.__setShowBubbleNavigation(menuName, False)

    @classmethod
    def checkIfHasNavigationBubble(cls, navigationName):
        return getShowBubbleNavigation(navigationName)
