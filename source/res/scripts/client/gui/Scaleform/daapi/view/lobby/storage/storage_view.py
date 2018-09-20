# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/storage/storage_view.py
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.Scaleform.daapi import LobbySubView
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.lobby.storage.sound_constants import STORAGE_SOUND_SPACE
from gui.Scaleform.daapi.view.lobby.storage.storage_helpers import getStorageShellsData
from gui.Scaleform.daapi.view.lobby.store.browser.ingameshop_helpers import isIngameShopEnabled
from gui.Scaleform.daapi.view.meta.StorageViewMeta import StorageViewMeta
from gui.Scaleform.genConsts.STORAGE_CONSTANTS import STORAGE_CONSTANTS
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.shared import events, EVENT_BUS_SCOPE
from gui.shared.event_dispatcher import showHangar
from helpers import dependency
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
from gui.shared.utils.requesters.ItemsRequester import REQ_CRITERIA
from gui.shared.gui_items import GUI_ITEM_TYPE

class StorageView(LobbySubView, StorageViewMeta):
    __background_alpha__ = 1.0
    lobbyContext = dependency.descriptor(ILobbyContext)
    itemsCache = dependency.descriptor(IItemsCache)
    _COMMON_SOUND_SPACE = STORAGE_SOUND_SPACE

    def __init__(self, ctx=None):
        super(StorageView, self).__init__(ctx)
        self.sections = [{'id': STORAGE_CONSTANTS.FOR_SELL,
          'linkage': STORAGE_CONSTANTS.FOR_SELL_VIEW,
          'tooltip': TOOLTIPS.STORAGE_MAINMENU_FOR_SELL},
         {'id': STORAGE_CONSTANTS.STORAGE,
          'linkage': STORAGE_CONSTANTS.STORAGE_VIEW,
          'tooltip': TOOLTIPS.STORAGE_MAINMENU_STORAGE},
         {'id': STORAGE_CONSTANTS.IN_HANGAR,
          'linkage': STORAGE_CONSTANTS.IN_HANGAR_VIEW,
          'tooltip': TOOLTIPS.STORAGE_MAINMENU_IN_HANGAR},
         {'id': STORAGE_CONSTANTS.PERSONAL_RESERVES,
          'linkage': STORAGE_CONSTANTS.PERSONAL_RESERVES_VIEW,
          'tooltip': TOOLTIPS.STORAGE_MAINMENU_PERSONAL_RESERVES}]
        self.__showDummyScreen = False
        self.__isItemsForSellEmpty = self.__getItemsForSellEmpty()
        self.__activeSectionIdx = 0
        self.__activeTab = None
        self.__switchSection(sectionName=(ctx or {}).get('defaultSection', STORAGE_CONSTANTS.FOR_SELL), sectionTab=(ctx or {}).get('defaultTab'), skipRefresh=True)
        self.__addHandlers()
        return

    def _onRegisterFlashComponent(self, viewPy, alias):
        super(StorageView, self)._onRegisterFlashComponent(viewPy, alias)
        if alias == STORAGE_CONSTANTS.IN_HANGAR_VIEW:
            viewPy.setActiveTab(self.__activeTab)

    def onClose(self):
        self.fireEvent(events.LoadViewEvent(VIEW_ALIAS.LOBBY_HANGAR), scope=EVENT_BUS_SCOPE.LOBBY)

    def navigateToHangar(self):
        showHangar()

    def _populate(self):
        super(StorageView, self)._populate()
        self.__showDummyScreen = not self.lobbyContext.getServerSettings().isIngameStorageEnabled()
        self.__initialize()

    def _invalidate(self, *args, **kwargs):
        super(StorageView, self)._invalidate(args, kwargs)
        self.__switchSection(sectionName=(args[0] or {}).get('defaultSection', STORAGE_CONSTANTS.FOR_SELL))

    def _dispose(self):
        self.__removeHandlers()
        super(StorageView, self)._dispose()

    def __addHandlers(self):
        serverSettings = self.lobbyContext.getServerSettings()
        serverSettings.onServerSettingsChange += self.__onServerSettingChanged
        g_clientUpdateManager.addCallbacks({'inventory': self.__onInventoryUpdated})

    def __removeHandlers(self):
        g_clientUpdateManager.removeObjectCallbacks(self)
        serverSettings = self.lobbyContext.getServerSettings()
        serverSettings.onServerSettingsChange -= self.__onServerSettingChanged

    def __onServerSettingChanged(self, diff):
        if 'ingameShop' in diff:
            storageEnabled = self.lobbyContext.getServerSettings().isIngameStorageEnabled()
            if isIngameShopEnabled():
                if not storageEnabled and not self.__showDummyScreen:
                    showHangar()
                if storageEnabled and self.__showDummyScreen:
                    self.__showDummyScreen = False
                    self.__initialize()
            else:
                showHangar()

    def __onInventoryUpdated(self, diff):
        if diff:
            self.__isItemsForSellEmpty = self.__getItemsForSellEmpty()

    def __switchSection(self, sectionName, sectionTab=None, skipRefresh=False):
        if sectionName == STORAGE_CONSTANTS.FOR_SELL and self.__isItemsForSellEmpty:
            sectionName = STORAGE_CONSTANTS.STORAGE
        for i, section in enumerate(self.sections):
            if section['id'] == sectionName:
                self.__activeSectionIdx = i
                break

        if not skipRefresh:
            self.as_selectSectionS(self.__activeSectionIdx)
        self.__activeTab = sectionTab

    def __getItemsForSellEmpty(self):
        invVehicles = self.itemsCache.items.getVehicles(REQ_CRITERIA.INVENTORY).values()
        requestTypeIds = GUI_ITEM_TYPE.VEHICLE_MODULES
        criteria = ~REQ_CRITERIA.VEHICLE.SUITABLE(invVehicles, requestTypeIds)
        criteria |= REQ_CRITERIA.INVENTORY
        items = self.itemsCache.items.getItems(requestTypeIds, criteria, nationID=None)
        shellItems = getStorageShellsData(invVehicles, False)
        return not items and not shellItems

    def __initialize(self):
        self.as_setDataS({'bgSource': RES_ICONS.MAPS_ICONS_STORAGE_BACKGROUND,
         'sections': self.sections,
         'showDummyScreen': self.__showDummyScreen})
        self.as_selectSectionS(self.__activeSectionIdx)
