# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/storage/storage_view.py
from account_helpers import AccountSettings
from account_helpers.AccountSettings import LAST_STORAGE_VISITED_TIMESTAMP
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.Scaleform.daapi import LobbySubView
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.lobby.storage import getSectionsList
from gui.Scaleform.daapi.view.lobby.storage.sound_constants import STORAGE_SOUND_SPACE
from gui.Scaleform.daapi.view.lobby.storage.storage_helpers import getStorageShellsData
from gui.Scaleform.daapi.view.meta.StorageViewMeta import StorageViewMeta
from gui.Scaleform.framework.managers.loaders import SFViewLoadParams
from gui.Scaleform.genConsts.STORAGE_CONSTANTS import STORAGE_CONSTANTS
from gui.impl import backport
from gui.impl.gen import R
from gui.shared import events, EVENT_BUS_SCOPE
from gui.shared.event_dispatcher import showHangar
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.utils.requesters.ItemsRequester import REQ_CRITERIA
from helpers import dependency
from helpers.time_utils import getCurrentTimestamp
from skeletons.gui.demount_kit import IDemountKitNovelty
from skeletons.gui.offers import IOffersNovelty, IOffersDataProvider
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache

class StorageView(LobbySubView, StorageViewMeta):
    __background_alpha__ = 1.0
    __lobbyContext = dependency.descriptor(ILobbyContext)
    __itemsCache = dependency.descriptor(IItemsCache)
    __offersProvider = dependency.descriptor(IOffersDataProvider)
    __demountKitNovelty = dependency.descriptor(IDemountKitNovelty)
    __offersNovelty = dependency.descriptor(IOffersNovelty)
    _COMMON_SOUND_SPACE = STORAGE_SOUND_SPACE
    _AUTO_TAB_SELECT_ENABLE = [STORAGE_CONSTANTS.IN_HANGAR_VIEW, STORAGE_CONSTANTS.STORAGE_VIEW]

    def __init__(self, ctx=None):
        super(StorageView, self).__init__(ctx)
        self.__sections = self.__createSections()
        self.__showDummyScreen = False
        self.__isItemsForSellEmpty = self.__getItemsForSellEmpty()
        self.__activeSectionIdx = 0
        self.__activeTab = None
        self.__switchSection(sectionName=(ctx or {}).get('defaultSection', STORAGE_CONSTANTS.FOR_SELL), sectionTab=(ctx or {}).get('defaultTab'), skipRefresh=True)
        return

    def onClose(self):
        self.fireEvent(events.LoadViewEvent(SFViewLoadParams(VIEW_ALIAS.LOBBY_HANGAR)), scope=EVENT_BUS_SCOPE.LOBBY)

    def navigateToHangar(self):
        showHangar()

    def _populate(self):
        super(StorageView, self)._populate()
        self.__showDummyScreen = not self.__lobbyContext.getServerSettings().isStorageEnabled()
        self.__initialize()
        self.__addHandlers()

    def _invalidate(self, *args, **kwargs):
        super(StorageView, self)._invalidate(args, kwargs)
        self.__switchSection(sectionName=(args[0] or {}).get('defaultSection', STORAGE_CONSTANTS.FOR_SELL))

    def _dispose(self):
        self.__removeHandlers()
        self.__saveLastTimestamp()
        super(StorageView, self)._dispose()

    def _onRegisterFlashComponent(self, viewPy, alias):
        super(StorageView, self)._onRegisterFlashComponent(viewPy, alias)
        if alias in self._AUTO_TAB_SELECT_ENABLE:
            viewPy.setActiveTab(self.__activeTab)

    def __initialize(self):
        self.as_setDataS({'bgSource': backport.image(R.images.gui.maps.icons.storage.background()),
         'sections': self.__sections,
         'showDummyScreen': self.__showDummyScreen})
        self.as_selectSectionS(self.__activeSectionIdx)
        self.__onDemountKitNoveltyUpdated()
        self.__onOffersNoveltyUpdated()

    def __saveLastTimestamp(self):
        AccountSettings.setSessionSettings(LAST_STORAGE_VISITED_TIMESTAMP, getCurrentTimestamp())

    def __addHandlers(self):
        serverSettings = self.__lobbyContext.getServerSettings()
        serverSettings.onServerSettingsChange += self.__onServerSettingChanged
        g_clientUpdateManager.addCallbacks({'inventory': self.__onInventoryUpdated,
         'serverSettings.blueprints_config': self.__onBlueprintsModeChanged})
        self.__offersProvider.onOffersUpdated += self.__onOffersChanged
        self.__demountKitNovelty.onUpdated += self.__onDemountKitNoveltyUpdated
        self.__offersNovelty.onUpdated += self.__onOffersNoveltyUpdated

    def __removeHandlers(self):
        g_clientUpdateManager.removeObjectCallbacks(self)
        serverSettings = self.__lobbyContext.getServerSettings()
        serverSettings.onServerSettingsChange -= self.__onServerSettingChanged
        self.__offersProvider.onOffersUpdated -= self.__onOffersChanged
        self.__demountKitNovelty.onUpdated -= self.__onDemountKitNoveltyUpdated
        self.__offersNovelty.onUpdated -= self.__onOffersNoveltyUpdated

    def __onServerSettingChanged(self, diff):
        if 'shop' in diff:
            storageEnabled = self.__lobbyContext.getServerSettings().isStorageEnabled()
            if not storageEnabled and not self.__showDummyScreen:
                self.navigateToHangar()
            if storageEnabled and self.__showDummyScreen:
                self.__showDummyScreen = False
                self.__initialize()
        self.__onOffersChanged()

    def __rebuildSections(self):
        if not self.__showDummyScreen:
            activeSectionAlias, activeTab = self.__findActiveSectionAndTab()
            self.__sections = self.__createSections()
            self.__setActiveSectionIdx(activeSectionAlias)
            self.__initialize()
            self.__activeTab = activeTab

    def __updateWindowForHiddenSection(self, hiddenSectionAlias):
        if not self.__showDummyScreen:
            activeSectionAlias, _ = self.__findActiveSectionAndTab()
            if activeSectionAlias == hiddenSectionAlias:
                self.navigateToHangar()
            else:
                self.__rebuildSections()

    def __onBlueprintsModeChanged(self, _):
        blueprintsEnabled = self.__lobbyContext.getServerSettings().blueprintsConfig.isBlueprintsAvailable()
        if not blueprintsEnabled:
            self.__updateWindowForHiddenSection(STORAGE_CONSTANTS.BLUEPRINTS_VIEW)
        else:
            self.__rebuildSections()

    def __onOffersChanged(self):
        isSectionExist = self.__isSectionExist(STORAGE_CONSTANTS.OFFERS)
        availableOffers = self.__offersProvider.getAvailableOffers()
        offersEnabled = self.__lobbyContext.getServerSettings().isOffersEnabled()
        isOffers = availableOffers and offersEnabled
        if not isSectionExist and isOffers:
            self.__rebuildSections()
        elif isSectionExist and not isOffers:
            self.__updateWindowForHiddenSection(STORAGE_CONSTANTS.OFFERS_VIEW)

    def __onInventoryUpdated(self, diff):
        if diff:
            self.__isItemsForSellEmpty = self.__getItemsForSellEmpty()

    def __switchSection(self, sectionName, sectionTab=None, skipRefresh=False):
        if sectionName == STORAGE_CONSTANTS.FOR_SELL and self.__isItemsForSellEmpty:
            sectionName = STORAGE_CONSTANTS.STORAGE
        for i, section in enumerate(self.__sections):
            if section['id'] == sectionName:
                self.__activeSectionIdx = i
                break

        if not skipRefresh:
            self.as_selectSectionS(self.__activeSectionIdx)
        self.__activeTab = sectionTab

    def __findActiveSectionAndTab(self):
        for alias, section in self.components.iteritems():
            if section.getActive():
                if section.components:
                    for tabAlias, tab in section.components.iteritems():
                        if tab.getActive():
                            return (alias, tabAlias)

                return (alias, None)

        return None

    def __getItemsForSellEmpty(self):
        invVehicles = self.__itemsCache.items.getVehicles(REQ_CRITERIA.INVENTORY).values()
        requestTypeIds = GUI_ITEM_TYPE.VEHICLE_MODULES
        criteria = ~REQ_CRITERIA.VEHICLE.SUITABLE(invVehicles, requestTypeIds)
        criteria |= REQ_CRITERIA.INVENTORY
        items = self.__itemsCache.items.getItems(requestTypeIds, criteria, nationID=None)
        shellItems = getStorageShellsData(invVehicles, False)
        return not items and not shellItems

    def __createSections(self):
        notActiveSection = []
        if not self.__lobbyContext.getServerSettings().blueprintsConfig.isBlueprintsAvailable():
            notActiveSection.append(STORAGE_CONSTANTS.BLUEPRINTS)
        if not self.__offersProvider.getAvailableOffers() or not self.__lobbyContext.getServerSettings().isOffersEnabled():
            notActiveSection.append(STORAGE_CONSTANTS.OFFERS)
        return [ section for section in getSectionsList() if section['id'] not in notActiveSection ]

    def __setActiveSectionIdx(self, sectionAlias):
        for idx, section in enumerate(self.__sections):
            if section['linkage'] == sectionAlias:
                self.__activeSectionIdx = idx

    def __onDemountKitNoveltyUpdated(self):
        self.__setTabCounter(STORAGE_CONSTANTS.STORAGE, self.__demountKitNovelty.noveltyCount)

    def __onOffersNoveltyUpdated(self):
        if self.__isSectionExist(STORAGE_CONSTANTS.OFFERS):
            self.__setTabCounter(STORAGE_CONSTANTS.OFFERS, self.__offersNovelty.noveltyCount)

    def __setTabCounter(self, tabId, value):
        if not self.__showDummyScreen:
            for i, section in enumerate(self.__sections):
                if section['id'] == tabId:
                    self.as_setButtonCounterS(i, value)
                    break

    def __isSectionExist(self, tabId):
        return tabId in [ s['id'] for s in self.__sections ]
