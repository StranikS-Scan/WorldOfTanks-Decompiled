# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/crew/barracks_view.py
import nations
from frameworks.wulf import ViewFlags, ViewSettings
from frameworks.wulf.view.array import fillIntsArray
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
from gui.impl.lobby.crew.filter import getTankmanKindSettings, getNationSettings, getTankmanRoleSettings, getVehicleTypeSettings, getVehicleTierSettings, getVehicleGradeSettings, SEARCH_MAX_LENGTH
from gui.impl.lobby.crew.filter.data_providers import CompoundDataProvider, BarracksDataProvider
from gui.shared.gui_items.Tankman import NO_SLOT
from gui.impl.lobby.crew.filter.filter_panel_widget import FilterPanelWidget
from gui.impl.lobby.crew.filter.state import FilterState
from gui.impl.lobby.crew.tooltips.bunks_confirm_discount_tooltip import BunksConfirmDiscountTooltip
from gui.server_events import recruit_helper
from gui.server_events.events_dispatcher import showRecruitWindow
from gui.shared.event_dispatcher import showPersonalCase, showHangar
from gui.shared.gui_items import GUI_ITEM_TYPE
from helpers import dependency
from skeletons.gui.game_control import IRestoreController
from skeletons.gui.game_control import ISpecialSoundCtrl
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared import IItemsCache
from uilogging.crew.loggers import CrewViewLogger
from uilogging.crew.logging_constants import CrewViewKeys, CrewNavigationButtons, CrewBarracksKeys, CrewMemberAdditionalInfo
from th_async import th_await, th_async
from PlayerEvents import g_playerEvents
from gui.shared.gui_items.Vehicle import NO_VEHICLE_ID
_SELECTION_CARDS_LIMIT = 200

class BarracksView(BaseTankmanListView):
    itemsCache = dependency.descriptor(IItemsCache)
    restore = dependency.descriptor(IRestoreController)
    specialSounds = dependency.descriptor(ISpecialSoundCtrl)
    eventsCache = dependency.descriptor(IEventsCache)
    __slots__ = ('__dataProviders', '__filterState', '__hasFilters', '__filterPanelWidget', '__berthPrice', '__berthsInPack', '__defaultBerthPrice', '__uiLogger', '__selectMode', '__selectedTankmans', '__selectionLimitOver')

    def __init__(self, layoutID=R.views.lobby.crew.BarracksView(), *args, **kwargs):
        settings = ViewSettings(layoutID, flags=ViewFlags.LOBBY_SUB_VIEW, model=BarracksViewModel(), args=args, kwargs=kwargs)
        location = kwargs.get('ctx', {}).get('location')
        berths = self.itemsCache.items.stats.tankmenBerthsCount
        self.__berthPrice, self.__berthsInPack = self.itemsCache.items.shop.getTankmanBerthPrice(berths)
        self.__defaultBerthPrice, _ = self.itemsCache.items.shop.defaults.getTankmanBerthPrice(berths)
        self.__hasFilters = location == BARRACKS_CONSTANTS.LOCATION_FILTER_NOT_RECRUITED
        self.__filterState = FilterState({FilterState.GROUPS.TANKMANKIND.value: TankmanKind.RECRUIT.value if self.__hasFilters else TankmanKind.TANKMAN.value})
        self.__filterPanelWidget = self.__initFilterPanelWidget()
        self.__dataProviders = CompoundDataProvider(barracks=BarracksDataProvider(self.__filterState))
        self.__uiLogger = CrewViewLogger(self, CrewViewKeys.BARRACKS)
        self.__selectedTankmans = []
        self.__selectionLimitOver = False
        super(BarracksView, self).__init__(settings)

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.lobby.crew.tooltips.BunksConfirmDiscountTooltip():
            currency = self.__berthPrice.getCurrency()
            money = int(self.itemsCache.items.stats.money.getSignValue(currency))
            return BunksConfirmDiscountTooltip(bunksCount=self.__berthsInPack, oldCost=self.__defaultBerthPrice.get(currency, 0), newCost=self.__berthPrice.get(currency, 0), isEnough=self.__berthPrice.get(currency, 0) <= money, currencyType=currency)
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

    def _onLoading(self, *args, **kwargs):
        super(BarracksView, self)._onLoading(*args, **kwargs)
        self.__uiLogger.initialize()
        self.setChildView(FilterPanelWidget.LAYOUT_ID(), self.__filterPanelWidget)
        with self.viewModel.transaction() as tx:
            berths = self.itemsCache.items.stats.tankmenBerthsCount
            berthPrice, _ = self.itemsCache.items.shop.getTankmanBerthPrice(berths)
            defaultBerthPrice, _ = self.itemsCache.items.shop.defaults.getTankmanBerthPrice(berths)
            tx.setIsBerthsOnSale(berthPrice != defaultBerthPrice)
        self.__dataProviders.subscribe()
        self.__dataProviders.update()

    def _onLoaded(self, *args, **kwargs):
        super(BarracksView, self)._onLoaded(*args, **kwargs)
        self.restore.onTankmenBufferUpdated += self.__onTankmenBufferUpdated

    def _finalize(self):
        self.restore.onTankmenBufferUpdated -= self.__onTankmenBufferUpdated
        super(BarracksView, self)._finalize()
        self.__dataProviders.unsubscribe()
        self.__dataProviders.clear()
        self.__uiLogger.finalize()
        self.__filterState = None
        self.__dataProviders = None
        self.__filterPanelWidget = None
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
         (self.__filterPanelWidget.viewModel.onDismissOrRestore, self.__onDismissOrRestore),
         (self.__filterPanelWidget.onSelectedModeChange, self.__onSelectedModeChange),
         (self.__filterPanelWidget.onResetSelection, self.__resetSelectedTankmanList),
         (self.__filterPanelWidget.onUpdateToggle, self.__onUpdateToggle),
         (self.__dataProviders.onDataChanged, self.__fillCardList),
         (self.itemsCache.onSyncCompleted, self.__onBerthsPricesChanged),
         (g_playerEvents.onVehicleLockChanged, self._onVehicleLockChanged),
         (self.viewModel.onTankmanSelectedChange, self.__onTankmanSelectedChange))

    @property
    def _viewProvider(self):
        return self.__dataProviders['barracks']

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
         ('personalMissionQuests', self.__onNewRecruits))

    def _fillTankmanCard(self, cardsList, tankman):
        tm = TankmanModel()
        tmanVehicle = self.itemsCache.items.getVehicle(tankman.vehicleInvID)
        setTankmanModel(tm, tankman, tmanNativeVeh=self.itemsCache.items.getItemByCD(tankman.vehicleNativeDescr.type.compactDescr), tmanVeh=tmanVehicle, compVeh=tmanVehicle)
        setTmanSkillsModel(tm.getSkills(), tankman)
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
        setRecruitTankmanModel(tm, recruitInfo)
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
        with self.viewModel.transaction() as tx:
            tx.berthsAmount.setFrom(self._viewProvider.tankmanInBarracksCount())
            tx.berthsAmount.setTo(self.itemsCache.items.stats.tankmenBerthsCount)

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
        self.__filterPanelWidget.resetPopoverFilter()

    def __onSelectedModeChange(self, enable):
        self.__setCardToggleEnabled(enable)
        self.__fillAmountInfo(enable)

    def __setCardToggleEnabled(self, enable):
        if enable:
            self.__selectionLimitOver = self._viewProvider.initialItemsCount > _SELECTION_CARDS_LIMIT
        with self.viewModel.transaction() as tx:
            tx.setIsSelectedMode(enable)
            tx.setIsSelectedLimitReached(False)

    @th_async
    def __onClickBuyBerth(self):
        yield th_await(dialogs.showEnlargeBarracksDialog())

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
        self.__uiLogger.logClick(CrewBarracksKeys.CARD_VOICEOVER_BUTTON)
        self._onPlayVoiceover(recruitID)

    @args2params(int)
    def _onTankmanRestore(self, tankmanID):
        self.__uiLogger.logClick(CrewBarracksKeys.CARD_RESTORE_BUTTON)
        dialogs.showRestoreTankmanDialog(tankmanID, NO_VEHICLE_ID, NO_SLOT, parentViewKey=self._uiLoggingKey)

    def __initFilterPanelWidget(self):
        widget = FilterPanelWidget(getTankmanKindSettings(), (getVehicleGradeSettings(withLocation=True, labelResId=R.strings.crew.filter.group.details.title(), tooltipDynAccessor=R.strings.crew.filter.tooltip.crewMemberVehicleGrade),
         getVehicleTypeSettings(customTooltipBody=R.strings.crew.filter.tooltip.crewMemberVehicleType.body()),
         getNationSettings(R.strings.crew.filter.tooltip.nation.crewMember.body()),
         getTankmanRoleSettings(),
         getVehicleTierSettings()), R.strings.crew.filter.popup.default.title(), self.__filterState, title=R.strings.crew.tankmanList.filter.title(), isSearchEnabled=True, hasVehicleFilter=True, panelType=FilterPanelType.BARRACKS, popoverTooltipHeader=R.strings.crew.tankmanList.tooltip.popover.header(), popoverTooltipBody=R.strings.crew.tankmanList.tooltip.popover.body(), searchTooltipBody=backport.text(R.strings.crew.tankmanList.tooltip.searchInput.body(), maxLength=SEARCH_MAX_LENGTH))
        return widget

    def __fillCardList(self):
        with self.viewModel.transaction() as tx:
            tx.setHeaderTitle(self.__filterPanelWidget.getActiveFilterTitle())
            tx.setHasFilters(self.__filterPanelWidget.hasAppliedFilters())
            fillIntsArray(self._viewProvider.getHeaderIndexes(), tx.getHeadersIndexes())
            self.__filterPanelWidget.applyStateToModel()
            self.__fillAmountInfo(self.__filterPanelWidget.isSelectedMode())
            tx.setItemsAmount(self._viewProvider.getActualItemsAmount())
            tx.setItemsOffset(self._itemsOffset)
            newRecruitCount = self._viewProvider.newItemsCount
            if newRecruitCount:
                self.__filterPanelWidget.updateFilterToggleCounter(TankmanKind.RECRUIT.value, newRecruitCount)
            self._fillVisibleCards(tx.getTankmanList())
            self.__onTankmenBerthsCountUpdate()
            if self._viewProvider.recruitTankmanCount():
                self.__setNewRecruitVisited()

    def __fillAmountInfo(self, selectable):
        if selectable:
            self.__updateSelectedTankmanAmountInfo()
        else:
            self.__resetSelectedTankmanList()
            self.__filterPanelWidget.updateAmountInfo(self._viewProvider.itemsCount, self._viewProvider.initialItemsCount)

    def __showHangar(self):
        self.__uiLogger.logNavigationButtonClick(CrewNavigationButtons.ESC)
        showHangar()

    def __setNewRecruitVisited(self):
        recruit_helper.setNewRecruitsVisited()
        self.__filterPanelWidget.updateFilterToggleCounter(TankmanKind.RECRUIT.value, 0)

    def _getSortedTankmanList(self):
        tmanKind = self._viewProvider.stateValue
        if tmanKind in (TankmanKind.RECRUIT.value, TankmanKind.DISMISSED.value):
            return self._viewProvider.items()
        return self._viewProvider.getTankmanSortedList() if tmanKind in (TankmanKind.TANKMAN.value, TankmanKind.UNIQUE.value) else []

    def __onUpdateToggle(self, isTankmanFilter):
        with self.viewModel.transaction() as tx:
            tx.setIsAllTankmanFilter(isTankmanFilter)

    @args2params(int)
    def __onTankmanSelectedChange(self, tankmanID):
        if tankmanID in self.__selectedTankmans:
            self.__selectedTankmans.remove(tankmanID)
        else:
            self.__selectedTankmans.append(tankmanID)
        self.__updateSelectedTankmanAmount()

    def __updateSelectedTankmanAmount(self):
        self.__fillModelSelectedTankmanList()
        self.__updateSelectedTankmanAmountInfo()

    def __updateSelectedTankmanAmountInfo(self):
        tmanLen = len(self.__selectedTankmans)
        selectionLimit = _SELECTION_CARDS_LIMIT if self.__selectionLimitOver else tmanLen
        self.__filterPanelWidget.updateAmountInfo(tmanLen, selectionLimit)

    def __resetSelectedTankmanList(self):
        self.__selectedTankmans = []
        self.__updateSelectedTankmanAmount()

    def __fillModelSelectedTankmanList(self):
        with self.viewModel.transaction() as tx:
            fillIntsArray(self.__selectedTankmans, tx.getSelectedTankmanList())
            selectedTankmanCount = len(self.__selectedTankmans)
            self.__filterPanelWidget.enableSelectionButton(selectedTankmanCount > 0)
            limitReached = selectedTankmanCount == _SELECTION_CARDS_LIMIT
            tx.setIsSelectedLimitReached(limitReached)
            self.__filterPanelWidget.setSelectedLimitReached(limitReached)

    @th_async()
    def __onDismissOrRestore(self):
        isRestore = TankmanKind.DISMISSED.value in self._viewProvider.stateValue
        isSingle = len(self.__selectedTankmans) == 1
        logKey = CrewBarracksKeys.CARD_SELECTED_RESTORE_BUTTON if isRestore else CrewBarracksKeys.CARD_SELECTED_DISMISS_BUTTON
        self.__uiLogger.logClick(logKey)
        dialog = self.__getDialog(isRestore, isSingle)
        result = yield th_await(dialog)
        if result.result:
            self.__resetSelectedTankmanList()
            self.__filterPanelWidget.disableSelectedMode()
            self.__setCardToggleEnabled(False)

    def __getDialog(self, isRestore, isSingle):
        if isSingle:
            tmanID = self.__selectedTankmans[0]
            if isRestore:
                return dialogs.showRestoreTankmanDialog(tmanID, NO_VEHICLE_ID, NO_SLOT, parentViewKey=self._uiLoggingKey)
            return dialogs.showDismissTankmanDialog(tmanID, parentViewKey=CrewViewKeys.BARRACKS)
        return dialogs.showRestoreSelectedTankmansDialog(self.__selectedTankmans, CrewViewKeys.BARRACKS) if isRestore else dialogs.showDismissSelectedTankmansDialog(self.__selectedTankmans, CrewViewKeys.BARRACKS)
