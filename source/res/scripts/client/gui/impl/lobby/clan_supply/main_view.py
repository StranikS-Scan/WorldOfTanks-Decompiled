# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/clan_supply/main_view.py
import logging
import weakref
from functools import partial
import typing
from account_helpers import AccountSettings
from account_helpers.AccountSettings import GUI_START_BEHAVIOR
from account_helpers.settings_core.ServerSettingsManager import SETTINGS_SECTIONS
from account_helpers.settings_core.settings_constants import GuiSettingsBehavior
from frameworks.wulf import ViewFlags, ViewSettings
from frameworks.wulf.view.submodel_presenter import SubModelPresenter
from gui import GUI_SETTINGS
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.impl.gen.view_models.views.lobby.clan_supply.clan_supply_model import ClanSupplyModel, ClanSupplyViews
from gui.impl.gen.view_models.views.lobby.clan_supply.tab_model import TabModel
from gui.impl.gui_decorators import args2params
from gui.impl.lobby.clan_supply.pages.progression_page import ProgressionPage
from gui.impl.lobby.clan_supply.pages.quests_page import QuestsPage
from gui.impl.lobby.clan_supply.sound_helper import getMainSoundSpace
from gui.impl.pub import ViewImpl
from gui.impl.wrappers.function_helpers import replaceNoneKwargsModel
from gui.shared.event_dispatcher import showStrongholds, showBrowserOverlayView
from gui.shared.money import Currency
from helpers import dependency
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.game_control import IWalletController
from skeletons.gui.shared import IItemsCache
from uilogging.clan_supply.constants import ClanSupplyLogKeys
from uilogging.clan_supply.loggers import ClanSupplyEventLogger
if typing.TYPE_CHECKING:
    from typing import Optional
_logger = logging.getLogger(__name__)
_SubModelInfo = typing.NamedTuple('_SubModelInfo', [('ID', ClanSupplyViews), ('presenter', SubModelPresenter)])

class MainView(ViewImpl):
    __slots__ = ('__tabId', '__presenterLoader', '__isClosingBySelf', '__uiLogger')
    _COMMON_SOUND_SPACE = getMainSoundSpace()
    __itemsCache = dependency.descriptor(IItemsCache)
    __wallet = dependency.descriptor(IWalletController)
    __settingsCore = dependency.descriptor(ISettingsCore)
    __tabID2ScreenEventLog = {ClanSupplyViews.PROGRESSION: ClanSupplyLogKeys.PROGRESSION_SCREEN,
     ClanSupplyViews.QUESTS: ClanSupplyLogKeys.QUESTS_SCREEN}
    __tabID2SidebarLog = {ClanSupplyViews.PROGRESSION: ClanSupplyLogKeys.SIDEBAR_PROGRESSION,
     ClanSupplyViews.QUESTS: ClanSupplyLogKeys.SIDEBAR_QUEST}

    def __init__(self, layoutID, *args, **kwargs):
        settings = ViewSettings(layoutID, flags=ViewFlags.LOBBY_SUB_VIEW, model=ClanSupplyModel(), args=args, kwargs=kwargs)
        super(MainView, self).__init__(settings, *args, **kwargs)
        self.__presenterLoader = None
        self.__tabId = ClanSupplyViews.PROGRESSION
        self.__isClosingBySelf = False
        self.__uiLogger = ClanSupplyEventLogger()
        return

    @property
    def viewModel(self):
        return super(MainView, self).getViewModel()

    def createToolTipContent(self, event, contentID):
        return self.__currentPage.createToolTipContent(event, contentID)

    def createToolTip(self, event):
        return self.__currentPage.createToolTip(event) or super(MainView, self).createToolTip(event)

    def switchPage(self, tabId, *args, **kwargs):
        if self.__currentPage.isLoaded:
            self.__uiLogger.logCloseEvent(self.__tabID2ScreenEventLog.get(self.__tabId), self.__tabID2SidebarLog.get(tabId))
            self.__uiLogger.logOpenEvent(self.__tabID2ScreenEventLog.get(tabId), self.__tabID2ScreenEventLog.get(self.__tabId))
            self.__currentPage.finalize()
        subModelInfo = self.__presenterLoader[tabId]
        subModelInfo.presenter.initialize(*args, **kwargs)
        self.viewModel.setPageViewId(subModelInfo.ID)
        self.__tabId = tabId

    def _onLoading(self, tabId=None, parentScreenLog=None, *args, **kwargs):
        self.__initPages()
        if tabId is not None:
            if tabId in self.__presenterLoader:
                self.__tabId = tabId
            else:
                _logger.error('Wrong tabId: %s', tabId)
        self.__uiLogger.logOpenEvent(self.__tabID2ScreenEventLog.get(self.__tabId), parentScreenLog)
        self.__updateTabs()
        self.__updateBalance()
        self.switchPage(self.__tabId, *args, **kwargs)
        super(MainView, self)._onLoading(*args, **kwargs)
        return

    def _initialize(self, *args, **kwargs):
        super(MainView, self)._initialize(*args, **kwargs)
        self.__tryShowInfoPage()

    def _finalize(self):
        self.__clearPages()
        if not self.__isClosingBySelf:
            self.__uiLogger.logCloseEvent(self.__tabID2ScreenEventLog.get(self.__tabId), ClanSupplyLogKeys.HANGAR_HEADER)
        super(MainView, self)._finalize()

    def _getEvents(self):
        return super(MainView, self)._getEvents() + ((self.viewModel.onClose, self.__onClose), (self.viewModel.onInfoPageOpen, self.__onInfoPageOpen), (self.viewModel.sidebar.onSideBarTabChange, self.__onSideBarTabChanged))

    def _getCallbacks(self):
        return (('cache.dynamicCurrencies.tourcoin', self.__updateBalance),)

    @property
    def __currentPage(self):
        return self.__presenterLoader[self.__tabId].presenter

    def __initPages(self):
        self.__presenterLoader = PresenterLazyLoader(self)

    def __clearPages(self):
        if self.__currentPage.isLoaded:
            self.__currentPage.finalize()
        self.__presenterLoader.clear()
        self.__presenterLoader = None
        return

    def __updateTabs(self):
        with self.viewModel.transaction() as tx:
            tabs = tx.sidebar.getItems()
            tabs.clear()
            for tab in tuple(ClanSupplyViews):
                tabModel = TabModel()
                tabModel.setId(tab)
                tabs.addViewModel(tabModel)

            tabs.invalidate()

    def __onClose(self):
        self.__isClosingBySelf = True
        self.__uiLogger.logCloseEvent(self.__tabID2ScreenEventLog.get(self.__tabId), ClanSupplyLogKeys.BACK_BUTTON)
        showStrongholds()

    @args2params(int)
    def __onSideBarTabChanged(self, tabId):
        if tabId == self.__tabId:
            return
        if tabId not in self.__presenterLoader:
            _logger.error('Wrong tabId: %s', tabId)
            return
        self.switchPage(tabId)

    def __onInfoPageOpen(self):
        self.__openInfoPage()

    def __tryShowInfoPage(self):
        defaults = AccountSettings.getFilterDefault(GUI_START_BEHAVIOR)
        settings = self.__settingsCore.serverSettings.getSection(SETTINGS_SECTIONS.GUI_START_BEHAVIOR, defaults)
        if not settings.get(GuiSettingsBehavior.CLAN_SUPPLY_INTRO_SHOWN, False):
            self.__openInfoPage()
            settings[GuiSettingsBehavior.CLAN_SUPPLY_INTRO_SHOWN] = True
            self.__settingsCore.serverSettings.setSectionSettings(SETTINGS_SECTIONS.GUI_START_BEHAVIOR, settings)

    def __openInfoPage(self):
        url = GUI_SETTINGS.clanSupply.get('baseURL')
        if url is None:
            _logger.error('clanSupply.baseURL is missed')
        showBrowserOverlayView(url, alias=VIEW_ALIAS.CLAN_SUPPLY_INFO_VIEW, parent=self.getParentWindow())
        return

    @replaceNoneKwargsModel
    def __updateBalance(self, value=None, model=None):
        balance = -1
        if self.__wallet.isAvailable:
            balance = self.__itemsCache.items.stats.dynamicCurrencies.get(Currency.TOUR_COIN, -1)
        model.setCurrencyValue(balance)


class PresenterLazyLoader(object):

    def __init__(self, mainView):
        self.__presentersCache = {}
        self.__mainView = weakref.proxy(mainView)
        self.__loadersMap = {ClanSupplyViews.PROGRESSION: partial(self.__makeSubModel, ClanSupplyViews.PROGRESSION, self.__loadProgression),
         ClanSupplyViews.QUESTS: partial(self.__makeSubModel, ClanSupplyViews.QUESTS, self.__loadQuests)}

    def clear(self):
        self.__loadersMap.clear()
        for subModelInfo in self.__presentersCache.values():
            subModelInfo.presenter.clear()

        self.__presentersCache.clear()
        self.__mainView = None
        return

    def __getitem__(self, item):
        if item not in self.__presentersCache:
            self.__tryToLoadPresenter(item)
        return self.__presentersCache.get(item, None)

    def __contains__(self, item):
        return item in self.__loadersMap

    def __tryToLoadPresenter(self, key):
        if key in self.__loadersMap:
            self.__presentersCache[key] = self.__loadersMap[key]()

    def __loadProgression(self):
        return ProgressionPage(self.__mainView.viewModel.progressionModel, self.__mainView)

    def __loadQuests(self):
        return QuestsPage(self.__mainView.viewModel.questsModel, self.__mainView)

    @staticmethod
    def __makeSubModel(viewAlias, loader):
        return _SubModelInfo(viewAlias, loader())
