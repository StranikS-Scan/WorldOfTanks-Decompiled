# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/boosters/BoostersWindow.py
from account_helpers.AccountSettings import AccountSettings, BOOSTERS_FILTER
from goodies.goodie_constants import GOODIE_RESOURCE_TYPE
from gui.Scaleform.daapi.view.lobby.boosters.booster_tabs import TabsContainer, TABS_IDS, getGuiCount
from gui.Scaleform.daapi.view.lobby.store.browser.ingameshop_helpers import isIngameShopEnabled
from gui.Scaleform.genConsts.TEXT_ALIGN import TEXT_ALIGN
from helpers import dependency
from helpers.i18n import makeString as _ms
from gui.Scaleform.daapi.view.meta.BoostersWindowMeta import BoostersWindowMeta
from gui.goodies.goodie_items import MAX_ACTIVE_BOOSTERS_COUNT, BOOSTER_QUALITY_NAMES
from gui.shared import event_bus_handlers, events, EVENT_BUS_SCOPE
from gui.shared.formatters import text_styles
from gui.Scaleform.locale.MENU import MENU
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.shared.utils.functions import makeTooltip
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from shared_utils import BitmaskHelper
from skeletons.gui.lobby_context import ILobbyContext

class FILTER_STATE(BitmaskHelper):
    ALL = 0
    SMALL = 1
    MEDIUM = 2
    BIG = 4
    XP = 8
    CREW_XP = 16
    FREE_XP = 32
    CREDITS = 64
    BOOSTER_QUALITIES = ((SMALL, BOOSTER_QUALITY_NAMES.SMALL), (MEDIUM, BOOSTER_QUALITY_NAMES.MEDIUM), (BIG, BOOSTER_QUALITY_NAMES.BIG))
    BOOSTER_TYPES = ((XP, GOODIE_RESOURCE_TYPE.XP),
     (CREW_XP, GOODIE_RESOURCE_TYPE.CREW_XP),
     (FREE_XP, GOODIE_RESOURCE_TYPE.FREE_XP),
     (CREDITS, GOODIE_RESOURCE_TYPE.CREDITS))


class BoostersWindow(BoostersWindowMeta):
    lobbyContext = dependency.descriptor(ILobbyContext)
    __metaclass__ = event_bus_handlers.EventBusListener

    def __init__(self, ctx=None):
        super(BoostersWindow, self).__init__()
        self.__tabsContainer = TabsContainer()
        self.__defaultTabIdx = ctx.get('tabID')
        self.__qualities = []
        self.__boosterTypes = []

    def onWindowClose(self):
        self.destroy()

    def requestBoostersArray(self, tabIndex):
        self.__tabsContainer.setCurrentTabIdx(tabIndex)
        self.__setCommonData()
        self.as_setListDataS(self.__tabsContainer.currentTab.getBoostersVOs(), False)

    def onBoosterActionBtnClick(self, boosterID, questID):
        self.__tabsContainer.currentTab.doAction(boosterID, questID)

    def onFiltersChange(self, filters):
        self.__setFilters(filters)
        self.__update()

    def onResetFilters(self):
        self.__setFilters(FILTER_STATE.ALL)
        self.__update(FILTER_STATE.ALL)

    def _populate(self):
        super(BoostersWindow, self)._populate()
        serverSettings = self.lobbyContext.getServerSettings()
        serverSettings.onServerSettingsChange += self.__onServerSettingsChanged
        self.__tabsContainer.init()
        self.__tabsContainer.onTabsUpdate += self.__onTabsUpdate
        self.__setFilters(AccountSettings.getFilter(BOOSTERS_FILTER))
        self.__setStaticData()
        if self.__defaultTabIdx is None:
            self.__defaultTabIdx = self.__getDefaultTabIdx()
        self.__tabsContainer.setCurrentTabIdx(self.__defaultTabIdx)
        self.__update()
        return

    def _dispose(self):
        self.__tabsContainer.onTabsUpdate -= self.__onTabsUpdate
        self.__tabsContainer.fini()
        self.__tabsContainer = None
        self.__qualities = None
        self.__boosterTypes = None
        serverSettings = self.lobbyContext.getServerSettings()
        serverSettings.onServerSettingsChange -= self.__onServerSettingsChanged
        super(BoostersWindow, self)._dispose()
        return

    def __getDefaultTabIdx(self):
        for tab in self.__tabsContainer.getTabs().itervalues():
            if tab.getTotalCount() > 0:
                return tab.getID()

        return TABS_IDS.INVENTORY

    def __onTabsUpdate(self):
        self.__update()

    def __update(self, filterState=-1):
        self.__setCommonData(filterState)
        self.as_setListDataS(self.__tabsContainer.currentTab.getBoostersVOs(), False)

    def __setStaticData(self):
        self.as_setStaticDataS({'windowTitle': _ms(MENU.BOOSTERSWINDOW_TITLE),
         'closeBtnLabel': _ms(MENU.BOOSTERSWINDOW_CLOSEBTN_LABEL),
         'noInfoBgSource': RES_ICONS.MAPS_ICONS_BOOSTERS_NOINFOBG,
         'filtersData': {'qualityFiltersLabel': text_styles.main(MENU.BOOSTERSWINDOW_LEVELFILTERS_LABEL),
                         'typeFiltersLabel': text_styles.main(MENU.BOOSTERSWINDOW_TYPEFILTERS_LABEL),
                         'qualityFilters': self.__packFiltersData(self.__packQualityFiltersItems()),
                         'typeFilters': self.__packFiltersData(self.__packTypeFiltersItems())}})

    def __packNoInfo(self):
        return {'title': text_styles.middleTitle(MENU.BOOSTERSWINDOW_BOOSTERSTABLE_NOINFO_NOTFOUND_TITLE),
         'message': text_styles.main(MENU.BOOSTERSWINDOW_BOOSTERSTABLE_NOINFO_NOTFOUND_MESSAGE),
         'returnBtnLabel': _ms(MENU.BOOSTERSWINDOW_RETURNBTN_LABEL)} if self.__tabsContainer.currentTab.getTotalCount() > 0 else {'title': '',
         'returnBtnLabel': '',
         'message': text_styles.alignStandartText(MENU.BOOSTERSWINDOW_BOOSTERSTABLE_NOINFO_EMPTY_MESSAGE, TEXT_ALIGN.CENTER)}

    @staticmethod
    def __packFiltersData(items):
        return {'items': items,
         'minSelectedItems': 0}

    @staticmethod
    def __packFilterItem(icon, value, tooltip, selected):
        return {'icon': icon,
         'filterValue': value,
         'selected': selected,
         'tooltip': makeTooltip(None, _ms(tooltip))}

    def __packQualityFiltersItems(self):
        return [self.__packFilterItem(RES_ICONS.MAPS_ICONS_FILTERS_LEVELS_LEVEL_1, FILTER_STATE.SMALL, TOOLTIPS.BOOSTER_FILTERS_QUALITYSMALL_BODY, BOOSTER_QUALITY_NAMES.SMALL in self.__qualities), self.__packFilterItem(RES_ICONS.MAPS_ICONS_FILTERS_LEVELS_LEVEL_2, FILTER_STATE.MEDIUM, TOOLTIPS.BOOSTER_FILTERS_QUALITYMEDIUM_BODY, BOOSTER_QUALITY_NAMES.MEDIUM in self.__qualities), self.__packFilterItem(RES_ICONS.MAPS_ICONS_FILTERS_LEVELS_LEVEL_3, FILTER_STATE.BIG, TOOLTIPS.BOOSTER_FILTERS_QUALITYBIG_BODY, BOOSTER_QUALITY_NAMES.BIG in self.__qualities)]

    def __packTypeFiltersItems(self):
        return [self.__packFilterItem(RES_ICONS.MAPS_ICONS_BOOSTERS_BOOSTER_XP_SMALL_BW, FILTER_STATE.XP, TOOLTIPS.BOOSTER_FILTERS_TYPEXP_BODY, GOODIE_RESOURCE_TYPE.XP in self.__boosterTypes),
         self.__packFilterItem(RES_ICONS.MAPS_ICONS_BOOSTERS_BOOSTER_CREW_XP_SMALL_BW, FILTER_STATE.CREW_XP, TOOLTIPS.BOOSTER_FILTERS_TYPECREWXP_BODY, GOODIE_RESOURCE_TYPE.CREW_XP in self.__boosterTypes),
         self.__packFilterItem(RES_ICONS.MAPS_ICONS_BOOSTERS_BOOSTER_FREE_XP_SMALL_BW, FILTER_STATE.FREE_XP, TOOLTIPS.BOOSTER_FILTERS_TYPEFREEXP_BODY, GOODIE_RESOURCE_TYPE.FREE_XP in self.__boosterTypes),
         self.__packFilterItem(RES_ICONS.MAPS_ICONS_BOOSTERS_BOOSTER_CREDITS_SMALL_BW, FILTER_STATE.CREDITS, TOOLTIPS.BOOSTER_FILTERS_TYPECREDITS_BODY, GOODIE_RESOURCE_TYPE.CREDITS in self.__boosterTypes)]

    def __setCommonData(self, filterState=-1):
        currentTab = self.__tabsContainer.currentTab
        self.as_setDataS({'isHaveNotInfo': currentTab.getCount() == 0,
         'noInfoData': self.__packNoInfo(),
         'tabsLabels': [self.__getInventoryTabLabel(), self.__getShopTabLabel()],
         'activeText': self.__getActiveText(),
         'filterState': filterState,
         'tabIndex': currentTab.getID()})

    def __getInventoryTabLabel(self):
        inventory = self.__tabsContainer.inventoryTab
        return _ms(MENU.BOOSTERSWINDOW_TABS_AVAILABLELABEL, count=self.__getFormattedCount(inventory))

    def __getShopTabLabel(self):
        shop = self.__tabsContainer.shopTab
        return _ms(MENU.BOOSTERSWINDOW_TABS_BUYLABEL, count=self.__getFormattedCount(shop))

    def __getActiveText(self):
        return text_styles.highTitle(_ms(MENU.BOOSTERSWINDOW_ACTIVEBOOSTERS, activeNo=self.__tabsContainer.getActiveBoostersCount(), allNo=MAX_ACTIVE_BOOSTERS_COUNT))

    def __setFilters(self, filterState):
        self.__qualities = []
        self.__boosterTypes = []
        for quality, param in FILTER_STATE.BOOSTER_QUALITIES:
            if filterState & quality:
                self.__qualities.append(param)

        for bType, param in FILTER_STATE.BOOSTER_TYPES:
            if filterState & bType:
                self.__boosterTypes.append(param)

        AccountSettings.setFilter(BOOSTERS_FILTER, filterState)
        self.__tabsContainer.setFilters(self.__qualities, self.__boosterTypes)

    def __getFormattedCount(self, tab):
        current = getGuiCount(tab.getCount())
        total = getGuiCount(tab.getTotalCount())
        return '%s/%s' % (current, total) if self.__qualities or self.__boosterTypes else '%s' % current

    @event_bus_handlers.eventBusHandler(events.HideWindowEvent.HIDE_BOOSTERS_WINDOW, EVENT_BUS_SCOPE.LOBBY)
    def __handleBoostersWindowClose(self, _):
        self.destroy()

    def __onServerSettingsChanged(self, diff):
        if 'ingameShop' in diff and isIngameShopEnabled():
            self.destroy()
