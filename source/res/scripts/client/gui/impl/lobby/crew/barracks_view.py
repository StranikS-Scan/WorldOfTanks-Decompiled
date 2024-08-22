# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/crew/barracks_view.py
import nations
from PlayerEvents import g_playerEvents
from frameworks.wulf import ViewFlags, ViewSettings
from gui.Scaleform.genConsts.BARRACKS_CONSTANTS import BARRACKS_CONSTANTS
from gui.Scaleform.genConsts.CONTEXT_MENU_HANDLER_TYPE import CONTEXT_MENU_HANDLER_TYPE
from gui.game_control import restore_contoller
from gui.impl import backport
from gui.impl.backport import createContextMenuData, BackportContextMenuWindow
from gui.impl.dialogs import dialogs
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.crew.barracks_view_model import BarracksViewModel
from gui.impl.gen.view_models.views.lobby.crew.filter_panel_widget_model import FilterPanelType
from gui.impl.gen.view_models.views.lobby.crew.tankman_model import TankmanModel, TankmanKind
from gui.impl.gui_decorators import args2params
from gui.impl.lobby.crew.base_tankman_list_view import BaseTankmanListView
from gui.impl.lobby.crew.crew_helpers.model_setters import setTankmanModel, setTmanSkillsModel, setRecruitTankmanModel
from gui.impl.lobby.crew.crew_helpers.tankman_helpers import getBethsSlotsCount, getPerksResetGracePeriod
from gui.impl.lobby.crew.filter import getTankmanKindSettings, getNationSettings, getTankmanRoleSettings, getVehicleTypeSettings, getVehicleTierSettings, getVehicleGradeSettings, SEARCH_MAX_LENGTH
from gui.impl.lobby.crew.filter.data_providers import CompoundDataProvider, TankmenDataProvider, RecruitsDataProvider
from gui.impl.lobby.crew.filter.filter_panel_widget import FilterPanelWidget
from gui.impl.lobby.crew.widget.crew_banner_widget import CrewBannerWidget
from gui.impl.lobby.crew.filter.state import FilterState
from gui.impl.lobby.crew.tooltips.bunks_confirm_discount_tooltip import BunksConfirmDiscountTooltip
from gui.server_events import recruit_helper
from gui.server_events.events_dispatcher import showRecruitWindow
from gui.shared.event_dispatcher import showPersonalCase, showHangar
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.money import Currency
from helpers import dependency
from skeletons.gui.game_control import IRestoreController
from skeletons.gui.game_control import ISpecialSoundCtrl
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared import IItemsCache
from uilogging.crew.loggers import CrewViewLogger
from uilogging.crew.logging_constants import CrewViewKeys, CrewNavigationButtons, CrewBarracksKeys, CrewMemberAdditionalInfo
from wg_async import wg_await, wg_async

class BarracksView(BaseTankmanListView):
    itemsCache = dependency.descriptor(IItemsCache)
    restore = dependency.descriptor(IRestoreController)
    specialSounds = dependency.descriptor(ISpecialSoundCtrl)
    eventsCache = dependency.descriptor(IEventsCache)
    __slots__ = ('__dataProviders', '__filterState', '__hasFilters', '__filterPanelWidget', '__berthPrice', '__berthsInPack', '__defaultBerthPrice', '__uiLogger')

    def __init__(self, layoutID=R.views.lobby.crew.BarracksView(), *args, **kwargs):
        settings = ViewSettings(layoutID, flags=ViewFlags.LOBBY_SUB_VIEW, model=BarracksViewModel(), args=args, kwargs=kwargs)
        location = kwargs.get('ctx', {}).get('location')
        berths = self.itemsCache.items.stats.tankmenBerthsCount
        self.__berthPrice, self.__berthsInPack = self.itemsCache.items.shop.getTankmanBerthPrice(berths)
        self.__defaultBerthPrice, _ = self.itemsCache.items.shop.defaults.getTankmanBerthPrice(berths)
        self.__hasFilters = location == BARRACKS_CONSTANTS.LOCATION_FILTER_NOT_RECRUITED
        self.__filterState = FilterState({FilterState.GROUPS.TANKMANKIND.value: TankmanKind.RECRUIT.value if self.__hasFilters else TankmanKind.TANKMAN.value})
        self.__filterPanelWidget = self.__initFilterPanelWidget()
        self.__bannerWidget = CrewBannerWidget()
        self.__dataProviders = CompoundDataProvider(tankmen=TankmenDataProvider(self.__filterState), recruits=RecruitsDataProvider(self.__filterState))
        self.__uiLogger = CrewViewLogger(self, CrewViewKeys.BARRACKS)
        super(BarracksView, self).__init__(settings)

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.lobby.crew.tooltips.BunksConfirmDiscountTooltip():
            money = int(self.itemsCache.items.stats.money.getSignValue(Currency.GOLD))
            return BunksConfirmDiscountTooltip(bunksCount=self.__berthsInPack, oldCost=self.__defaultBerthPrice.gold, newCost=self.__berthPrice.gold, isEnough=self.__berthPrice.gold <= money)
        return super(BarracksView, self).createToolTipContent(event, contentID)

    @property
    def viewModel(self):
        return super(BarracksView, self).getViewModel()

    def createContextMenu(self, event):
        if event.contentID == R.views.common.BackportContextMenu():
            menuType = event.getArgument('type')
            if menuType == CONTEXT_MENU_HANDLER_TYPE.CREW_TANKMAN:
                contextMenuArgs = {'tankmanID': event.getArgument('tankmanID'),
                 'slotIdx': 0,
                 'parentLayoutID': self.layoutID}
                contextMenuData = createContextMenuData(CONTEXT_MENU_HANDLER_TYPE.CREW_TANKMAN, contextMenuArgs)
                if contextMenuData:
                    window = BackportContextMenuWindow(contextMenuData, self.getParentWindow())
                    window.load()
                    return window
        return None

    def __updateWidget(self, tx):
        timeLeft = getPerksResetGracePeriod()
        isVisible = timeLeft > 0
        tx.setIsBannerVisible(isVisible)
        if isVisible:
            self.__bannerWidget.fillModel()

    def _onLoading(self, *args, **kwargs):
        super(BarracksView, self)._onLoading(*args, **kwargs)
        self.__uiLogger.initialize()
        self.setChildView(FilterPanelWidget.LAYOUT_ID(), self.__filterPanelWidget)
        self.setChildView(CrewBannerWidget.LAYOUT_ID(), self.__bannerWidget)
        with self.viewModel.transaction() as tx:
            berths = self.itemsCache.items.stats.tankmenBerthsCount
            berthPrice, _ = self.itemsCache.items.shop.getTankmanBerthPrice(berths)
            defaultBerthPrice, _ = self.itemsCache.items.shop.defaults.getTankmanBerthPrice(berths)
            tx.setIsBerthsOnSale(berthPrice != defaultBerthPrice)
            self.__updateWidget(tx)
        self.__dataProviders.subscribe()
        self.__dataProviders.update()

    def _onLoaded(self, *args, **kwargs):
        super(BarracksView, self)._onLoaded(*args, **kwargs)
        self.restore.onTankmenBufferUpdated += self.__onTankmenBufferUpdated

    def _finalize(self):
        self.restore.onTankmenBufferUpdated -= self.__onTankmenBufferUpdated
        self.__dataProviders.unsubscribe()
        super(BarracksView, self)._finalize()
        self.__uiLogger.finalize()
        self.__filterState = None
        self.__dataProviders = None
        self.__filterPanelWidget = None
        self.__bannerWidget = None
        return

    def _onVehicleLockChanged(self, _, __):
        self.__onFilterStateUpdated()

    def _getEvents(self):
        eventsTuple = super(BarracksView, self)._getEvents()
        return eventsTuple + ((self.viewModel.onResetFilters, self.__onResetFilters),
         (self.viewModel.onBuyBerth, self.__onClickBuyBerth),
         (self.viewModel.onTankmanSelected, self.__onTankmanSelected),
         (self.viewModel.onTankmanRecruit, self.__onTankmanRecruit),
         (self.viewModel.onTankmanDismiss, self.__onTankmanDismiss),
         (self.viewModel.onPlayTankmanVoiceover, self.__onPlayTankmanVoiceover),
         (self.viewModel.onTankmanRestore, self._onTankmanRestore),
         (self.viewModel.showHangar, self.__showHangar),
         (self.viewModel.onLoadCards, self._onLoadCards),
         (self.__filterState.onStateChanged, self.__onFilterStateUpdated),
         (self.__dataProviders.onDataChanged, self.__fillCardList),
         (self.itemsCache.onSyncCompleted, self.__onBerthsPricesChanged),
         (g_playerEvents.onVehicleLockChanged, self._onVehicleLockChanged),
         (self.eventsCache.onProgressUpdated, self.__onNewRecruits))

    @property
    def _tankmenProvider(self):
        return self.__dataProviders['tankmen']

    @property
    def _recruitsProvider(self):
        return self.__dataProviders['recruits']

    @property
    def _filterState(self):
        return self.__filterState

    @property
    def _uiLoggingKey(self):
        return CrewViewKeys.BARRACKS

    def _getCallbacks(self):
        return (('inventory', self.__onInventoryUpdate),
         ('stats.berths', self.__onTankmenBerthsCountUpdate),
         ('tokens', self.__onNewRecruits),
         ('potapovQuests', self.__onNewRecruits))

    def _fillTankmanCard(self, cardsList, tankman):
        tm = TankmanModel()
        setTankmanModel(tm, tankman, tmanNativeVeh=self.itemsCache.items.getItemByCD(tankman.vehicleNativeDescr.type.compactDescr), tmanVeh=self.itemsCache.items.getVehicle(tankman.vehicleInvID))
        setTmanSkillsModel(tm.skills, tankman, fillBonusSkills=False)
        tm.setNation(nations.NAMES[tankman.nationID])
        tm.setHasVoiceover(False)
        if tankman.isDismissed:
            _, time = restore_contoller.getTankmenRestoreInfo(tankman)
            tm.setTimeToDismiss(time)
        cardsList.addViewModel(tm)

    def _fillRecruitCard(self, cardsList, recruitInfo):
        tm = TankmanModel()
        if len(recruitInfo.getNations()) == 1:
            tm.setNation(recruitInfo.getNations()[0])
        setRecruitTankmanModel(tm, recruitInfo, useOnlyFullSkills=False)
        cardsList.addViewModel(tm)

    def __onInventoryUpdate(self, invDiff):
        if GUI_ITEM_TYPE.TANKMAN in invDiff or GUI_ITEM_TYPE.CREW_SKINS in invDiff:
            self.__dataProviders.reinit()
            self.__dataProviders.update()

    def __onNewRecruits(self, *_):
        self.__dataProviders.reinit()
        self.__dataProviders.update()

    def __onTankmenBufferUpdated(self):
        self.__dataProviders.reinit()
        self.__dataProviders.update()

    def __onTankmenBerthsCountUpdate(self, *_):
        slotsCount, freeBerthsCount = getBethsSlotsCount()
        if slotsCount != self.viewModel.berthsAmount.getTo():
            with self.viewModel.transaction() as tx:
                tx.berthsAmount.setFrom(freeBerthsCount)
                tx.berthsAmount.setTo(slotsCount)

    def __onBerthsPricesChanged(self, *_):
        berths = self.itemsCache.items.stats.tankmenBerthsCount
        self.__berthPrice, _ = self.itemsCache.items.shop.getTankmanBerthPrice(berths)
        defaultBerthPrice, _ = self.itemsCache.items.shop.defaults.getTankmanBerthPrice(berths)
        isNowBerthsOnSale = self.__berthPrice != defaultBerthPrice
        if isNowBerthsOnSale != self.viewModel.getIsBerthsOnSale():
            with self.viewModel.transaction() as tx:
                tx.setIsBerthsOnSale(isNowBerthsOnSale)

    def __onFilterStateUpdated(self):
        self.__dataProviders.update()
        self.__hasFilters = self.__filterPanelWidget.hasAppliedFilters()

    def __onResetFilters(self):
        self.__filterPanelWidget.resetState()
        self.__filterPanelWidget.applyStateToModel()

    @wg_async
    def __onClickBuyBerth(self):
        yield wg_await(dialogs.showEnlargeBarracksDialog())

    @args2params(int)
    def __onTankmanSelected(self, tankmanID):
        self.__uiLogger.logClick(CrewBarracksKeys.CARD, info=CrewMemberAdditionalInfo.TANKMAN)
        showPersonalCase(tankmanID, previousViewID=self.layoutID)

    @args2params(str)
    def __onTankmanRecruit(self, recruitID):
        self.__uiLogger.logClick(CrewBarracksKeys.CARD, info=CrewMemberAdditionalInfo.RECRUIT)
        showRecruitWindow(recruitID, parentViewKey=CrewViewKeys.BARRACKS)

    @args2params(int)
    def __onTankmanDismiss(self, tankmanID):
        self.__uiLogger.logClick(CrewBarracksKeys.CARD_DISMISS_BUTTON)
        dialogs.showDismissTankmanDialog(tankmanID, parentViewKey=CrewViewKeys.BARRACKS)

    @args2params(str)
    def __onPlayTankmanVoiceover(self, recruitID):
        self._onPlayVoiceover(recruitID)
        self.__uiLogger.logClick(CrewBarracksKeys.CARD_VOICEOVER_BUTTON)

    def __initFilterPanelWidget(self):
        widget = FilterPanelWidget(getTankmanKindSettings(), (getVehicleGradeSettings(withLocation=True, labelResId=R.strings.crew.filter.group.details.title(), tooltipDynAccessor=R.strings.crew.filter.tooltip.crewMemberVehicleGrade),
         getVehicleTypeSettings(customTooltipBody=R.strings.crew.filter.tooltip.crewMemberVehicleType.body()),
         getNationSettings(R.strings.crew.filter.tooltip.nation.crewMember.body()),
         getTankmanRoleSettings(),
         getVehicleTierSettings()), R.strings.crew.filter.popup.default.title(), self.__filterState, title=R.strings.crew.tankmanList.filter.title(), isSearchEnabled=True, hasVehicleFilter=True, panelType=FilterPanelType.BARRACKS, popoverTooltipHeader=R.strings.crew.tankmanList.tooltip.popover.header(), popoverTooltipBody=R.strings.crew.tankmanList.tooltip.popover.body(), searchTooltipBody=backport.text(R.strings.crew.tankmanList.tooltip.searchInput.body(), maxLength=SEARCH_MAX_LENGTH))
        return widget

    def __fillCardList(self):
        with self.viewModel.transaction() as tx:
            self.__updateWidget(tx)
            tx.setHasFilters(self.__filterPanelWidget.hasAppliedFilters())
            self.__filterPanelWidget.updateAmountInfo(self.__dataProviders.itemsCount, self.__dataProviders.initialItemsCount)
            tx.setItemsAmount(self.__dataProviders.itemsCount)
            tx.setItemsOffset(self._itemsOffset)
            self.__filterPanelWidget.applyStateToModel()
            newRecruitCount = self._recruitsProvider.newItemsCount
            if newRecruitCount:
                self.__filterPanelWidget.updateFilterToggleCounter(TankmanKind.RECRUIT.value, newRecruitCount)
            self._fillVisibleCards(tx.getTankmanList())
            slotsCount, freeBerthsCount = getBethsSlotsCount()
            tx.berthsAmount.setFrom(freeBerthsCount)
            tx.berthsAmount.setTo(slotsCount)
            if self._recruitsProvider.itemsCount:
                self.__setNewRecruitVisited()

    def __showHangar(self):
        self.__uiLogger.logNavigationButtonClick(CrewNavigationButtons.ESC)
        showHangar()

    def __setNewRecruitVisited(self):
        recruit_helper.setNewRecruitsVisited()
        self.__filterPanelWidget.updateFilterToggleCounter(TankmanKind.RECRUIT.value, 0)
