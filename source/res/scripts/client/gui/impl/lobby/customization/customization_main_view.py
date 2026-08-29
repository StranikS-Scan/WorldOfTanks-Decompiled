# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/customization/customization_main_view.py
import logging
from BWUtil import AsyncReturn
from typing import TYPE_CHECKING
import BigWorld
import SoundGroups
import adisp
from CurrentVehicle import g_currentVehicle
from Math import Matrix
from account_helpers.settings_core.settings_constants import OnceOnlyHints
from frameworks.wulf import ViewFlags, ViewSettings
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.lobby.header.LobbyHeader import HeaderMenuVisibilityState
from gui.Scaleform.framework.entities.EventSystemEntity import EventSystemEntity
from gui.Scaleform.framework.managers.loaders import SFViewLoadParams
from gui.Scaleform.genConsts.CONTEXT_MENU_HANDLER_TYPE import CONTEXT_MENU_HANDLER_TYPE
from gui.Scaleform.genConsts.CUSTOMIZATION_ALIASES import CUSTOMIZATION_ALIASES
from gui.customization.constants import CustomizationModeSource, CustomizationModes, INVALID_ID
from gui.customization.shared import C11nId, SEASON_NAME_TO_TYPE, SEASON_TYPE_TO_NAME, appliedToFromSlotsIds, chooseMode, isVehicleCanBeCustomized
from gui.hangar_cameras.hangar_camera_common import CameraRelatedEvents
from gui.impl import backport
from gui.impl.backport import createContextMenuData
from gui.impl.dialogs.sub_views.top_right.money_balance import MoneyBalance
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.customization.customization_carousel_arrow_model import CustomizationCarouselArrowModel
from gui.impl.gen.view_models.views.lobby.customization.customization_carousel_bookmark_model import CustomizationCarouselBookmarkModel
from gui.impl.gen.view_models.views.lobby.customization.customization_carousel_model import CustomizationCarouselModel
from gui.impl.gen.view_models.views.lobby.customization.customization_header_vehicle_info_model import CustomizationHeaderVehicleInfoModel
from gui.impl.gen.view_models.views.lobby.customization.customization_main_view_model import CustomizationMainViewModel
from gui.impl.gen.view_models.views.lobby.customization.customization_money_balance_model import CustomizationMoneyBalanceModel
from gui.impl.gui_decorators import args2params
from gui.impl.lobby.common.vehicle_model_helpers import fillVehicleModel
from gui.impl.lobby.common.view_wrappers import createBackportContextMenuDecorator, createBackportTooltipDecorator
from gui.impl.lobby.customization.customization_bill_data_packer import isCreditPriceEnough, isVehicleEmpty, packBottomPanelBillData
from gui.impl.lobby.customization.customization_bin.customization_bin_subview import CustomizationBinSubview
from gui.impl.lobby.customization.customization_carousel_helpers import CustomizationCarouselDataProvider, FilterTypes
from gui.impl.lobby.customization.customization_item_data_packer import fillMagneticTool, packCustomizationItemData, packEmptyCustomizationItemData
from gui.impl.lobby.customization.customization_seasons_data_packer import fillSeasonsModel
from gui.impl.lobby.customization.customization_style_info.customization_style_info_view import CustomizationStyleInfoView
from gui.impl.lobby.customization.customization_tabs_packer import fillTabsModel
from gui.impl.lobby.customization.customization_toolbar_provider import CustomizationToolbarProvider
from gui.impl.lobby.customization.customization_window_events import showFilterPopoverWindow, showProgressiveItemsView
from gui.impl.lobby.customization.decorators import sharedCustomizationTooltipData
from gui.impl.lobby.customization.dialogs import showCloseConfirmWithoutApplyingChangesDialog
from gui.impl.lobby.customization.filter_types import getStructureList
from gui.impl.lobby.customization.progression_styles.stage_switcher_provider import StageSwitcherProvider
from gui.impl.lobby.customization.settings_constants import CAROUSEL_ARROWS_HINT_SHOWN_FIELD, CUSTOMIZATION_STYLE_ITEMS_VISITED, CustomizationFilter, CustomizationSettingsSerializable, IS_CUSTOMIZATION_INTRO_VIEWED
from gui.impl.lobby.customization.shared import CustomizationTabs, checkSlotsFilling, getEmptyRegions, getTabByItem, isItemUsedUp
from gui.impl.lobby.customization.sound_constants import SOUNDS
from gui.impl.lobby.customization.vehicle_slot_selector import VehicleSlotSelector
from gui.impl.pub import ViewImpl
from gui.shared import EVENT_BUS_SCOPE, events
from gui.shared.close_confiramtor_helper import CloseConfirmatorsHelper
from gui.shared.event_dispatcher import showOnboardingView
from gui.shared.events import LobbySimpleEvent
from gui.shared.gui_items import GUI_ITEM_TYPE, GUI_ITEM_TYPE_NAMES
from gui.shared.money import Currency
from gui.shared.utils.requesters import REQ_CRITERIA
from helpers import dependency
from items.components.c11n_constants import ApplyArea, CustomizationDisplayType, ItemTags, SeasonType
from shared_utils import findFirst, first, safeCall
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.customization import ICustomizationService
from skeletons.gui.impl import IGuiLoader
from skeletons.gui.shared.utils import IHangarSpace
from th_async import th_async, th_await
from tutorial.hints_manager import HINT_SHOWN_STATUS
from vehicle_outfit.outfit import Area
if TYPE_CHECKING:
    from typing import Dict, Optional
    from gui.impl.lobby.customization.context.context import CustomizationContext
    from gui.impl.lobby.customization.customization_carousel_helpers import CarouselData
    from gui.impl.gen.view_models.views.lobby.customization.customization_carousel_item_model import CustomizationCarouselItemModel
    from gui.impl.gen.view_models.views.lobby.customization.customization_types_model import CustomizationTypesModel
_logger = logging.getLogger(__name__)

class _CustomizationCloseConfirmationsHelper(CloseConfirmatorsHelper):

    def getRestrictedSfViews(self):
        return super(_CustomizationCloseConfirmationsHelper, self).getRestrictedSfViews() + [VIEW_ALIAS.LOBBY_HANGAR]

    def getRestrictedGuiImplViews(self):
        return super(_CustomizationCloseConfirmationsHelper, self).getRestrictedGuiImplViews() + [R.views.lobby.common.BrowserView(), R.views.lobby.personal_reserves.ReservesActivationView(), R.views.lobby.personal_reserves.ReservesIntroView()]

    def start(self, closeConfirmator):
        super(_CustomizationCloseConfirmationsHelper, self).start(closeConfirmator)
        self._addPlatoonCreationConfirmator()

    def stop(self):
        self._deletePlatoonCreationConfirmator()
        super(_CustomizationCloseConfirmationsHelper, self).stop()


@sharedCustomizationTooltipData
class CustomizationMainView(ViewImpl, EventSystemEntity, CustomizationSettingsSerializable):
    __slots__ = ('__ctx', '__carouselDP', '__slotSelector', '__selectedItem', '__isHistoric', '__isNonHistoric', '__isFantastical', '__initAnchorsPositionsCallback', '__toolbarProvider', '__stageSwitcherProvider', '__carouselArrowsHintShown', '__closeConfirmationsHelper', '__isOnLoading', '__forceClose', '__progressiveItemCD')
    __service = dependency.descriptor(ICustomizationService)
    __settingsCore = dependency.descriptor(ISettingsCore)
    __guiLoader = dependency.descriptor(IGuiLoader)
    __hangarSpace = dependency.descriptor(IHangarSpace)
    __BIN_VIEW_ID = R.views.lobby.customization.CustomizationBinSubview()
    __STYLE_INFO_VIEW_ID = R.views.lobby.customization.CustomizationStyleInfoView()
    __ZOOM_ON_EMBLEM = 0.1
    __ZOOM_ON_INSCRIPTION = 0.1

    def __init__(self, layoutID, ctx):
        settings = ViewSettings(layoutID)
        settings.flags = ViewFlags.LOBBY_SUB_VIEW
        settings.model = CustomizationMainViewModel()
        safeCall(ctx.get('callback'))
        self.__progressiveItemCD = ctx.get('progressiveItemCD')
        self.__ctx = None
        self.__carouselDP = None
        self.__slotSelector = VehicleSlotSelector()
        self.__selectedItem = None
        self.__isHistoric = False
        self.__isNonHistoric = False
        self.__isFantastical = False
        self.__initAnchorsPositionsCallback = None
        self.__toolbarProvider = None
        self.__stageSwitcherProvider = None
        self.__carouselArrowsHintShown = False
        self.__closeConfirmationsHelper = _CustomizationCloseConfirmationsHelper()
        self.__isOnLoading = False
        self.__forceClose = False
        BigWorld.EnvironmentSwitcher.instance().activateTempEnvironment('Customization')
        super(CustomizationMainView, self).__init__(settings)
        return

    @property
    def viewModel(self):
        return super(CustomizationMainView, self).getViewModel()

    @property
    def _binSubView(self):
        return self.getChildView(self.__BIN_VIEW_ID)

    @createBackportTooltipDecorator()
    def createToolTip(self, event):
        return super(CustomizationMainView, self).createToolTip(event)

    def createPopOver(self, event):
        return showFilterPopoverWindow(event, self.__carouselDP) if event.contentID == R.views.lobby.customization.popovers.CustomizationFilterPopoverView() else super(CustomizationMainView, self).createPopOver(event)

    @createBackportContextMenuDecorator()
    def createContextMenu(self, event):
        return super(CustomizationMainView, self).createContextMenu(event)

    def getContextMenuData(self, event):
        menuType = event.getArgument('type')
        if menuType == CONTEXT_MENU_HANDLER_TYPE.CUSTOMIZATION_ITEM:
            contextMenuArgs = {'itemID': int(event.getArgument('intCD'))}
            return createContextMenuData(CONTEXT_MENU_HANDLER_TYPE.CUSTOMIZATION_ITEM, contextMenuArgs)
        else:
            return None

    def progressiveItemsViewShowed(self):
        self.__ctx.mode.unselectItem()
        self.__ctx.mode.unselectSlot()

    def resetCustomizationCamera(self, resetRotation=False):
        if self.__ctx.c11nCameraManager is None:
            return
        else:
            self.__ctx.c11nCameraManager.resetCustomizationCamera(resetRotation)
            if self.__toolbarProvider is not None:
                self.__toolbarProvider.locateToCustomizationPreview()
            self.__ctx.vehicleAnchorsUpdater.onCameraLocated()
            return

    @adisp.adisp_async
    @adisp.adisp_process
    def applyItems(self, purchaseItems, force=False, callback=None):
        self.__service.stopHighlighter()
        yield self.__ctx.applyItems(purchaseItems)
        self.__forceClose = force
        self.__close()
        callback(None)
        return

    def updateIsBinSubViewActive(self, isBinSubViewActive):
        if self._binSubView:
            self.viewModel.setIsBuyViewActive(isBinSubViewActive)
            self.viewModel.billModel.setIsApplyButton(isBinSubViewActive)
            self.viewModel.billModel.setBuyButtonEnabled(isCreditPriceEnough(isBinSubViewActive))
            if isBinSubViewActive:
                self.__service.stopHighlighter()
            else:
                if self.__ctx.modeId == CustomizationModes.EDITABLE_STYLE:
                    self.__ctx.changeMode(self.__ctx.prevModeId)
                self.__service.restartHighlighter()

    def _initialize(self, *args, **kwargs):
        super(CustomizationMainView, self)._initialize(*args, **kwargs)
        self.soundManager.playInstantSound(SOUNDS.ENTER)
        self.soundManager.setState(SOUNDS.STATE_PLACE, SOUNDS.STATE_PLACE_C11N)
        self.__closeConfirmationsHelper.start(self.__closeConfirmator)
        self.fireEvent(CameraRelatedEvents(CameraRelatedEvents.FORCE_DISABLE_IDLE_PARALAX_MOVEMENT, ctx={'isDisable': True,
         'setIdle': True,
         'setParallax': True}), scope=EVENT_BUS_SCOPE.LOBBY)
        self.fireEvent(events.LobbyHeaderMenuEvent(events.LobbyHeaderMenuEvent.TOGGLE_VISIBILITY, ctx={'state': HeaderMenuVisibilityState.ONLINE_COUNTER}), EVENT_BUS_SCOPE.LOBBY)
        self.fireEvent(events.LobbyInterfaceEvent(events.LobbyInterfaceEvent.TOGGLE_VISIBILITY, ctx={'headerIsVisible': True,
         'ignoreTopOffset': True}), EVENT_BUS_SCOPE.LOBBY)
        BigWorld.callback(0.0, self.__initAnchorsPositions)

    def _finalize(self):
        self.soundManager.playInstantSound(SOUNDS.EXIT)
        self.soundManager.setState(SOUNDS.STATE_PLACE, SOUNDS.STATE_PLACE_GARAGE)
        self.fireEvent(events.HangarCustomizationEvent(events.HangarCustomizationEvent.RESET_VEHICLE_MODEL_TRANSFORM), scope=EVENT_BUS_SCOPE.LOBBY)
        self.fireEvent(events.LobbyHeaderMenuEvent(events.LobbyHeaderMenuEvent.TOGGLE_VISIBILITY, ctx={'state': HeaderMenuVisibilityState.ALL}), EVENT_BUS_SCOPE.LOBBY)
        self.fireEvent(events.LobbyInterfaceEvent(events.LobbyInterfaceEvent.TOGGLE_VISIBILITY, ctx={'headerIsVisible': True}), EVENT_BUS_SCOPE.LOBBY)
        self.fireEvent(CameraRelatedEvents(CameraRelatedEvents.FORCE_DISABLE_IDLE_PARALAX_MOVEMENT, ctx={'isDisable': False,
         'setIdle': True,
         'setParallax': True}), scope=EVENT_BUS_SCOPE.LOBBY)
        BigWorld.EnvironmentSwitcher.instance().activateMainEnvironment()
        self.__service.stopHighlighter()
        self.__toolbarProvider.fini()
        if self.__initAnchorsPositionsCallback is not None:
            BigWorld.cancelCallback(self.__initAnchorsPositionsCallback)
            self.__initAnchorsPositionsCallback = None
        entity = self.__hangarSpace.getVehicleEntity()
        if entity and entity.appearance:
            entity.appearance.loadState.unsubscribe(self.__onVehicleLoadFinished, self.__onVehicleLoadStarted)
            entity.appearance.turretRotator.onTurretRotated -= self.__onTurretAndGunRotated
        self._dumpSettings()
        if not self.__forceClose:
            self.__closeConfirmationsHelper.stop()
        self.soundManager.playInstantSound(SOUNDS.BACK_TO_HANGAR)
        super(CustomizationMainView, self)._finalize()
        self.__carouselDP.fini()
        self.__service.closeCustomization()
        self.__ctx = None
        return

    def _getEvents(self):
        return ((self.viewModel.changeFilter, self.__changeFilter),
         (self.viewModel.clearFilter, self.__clearFilter),
         (self.viewModel.onClose, self.__closeConfirmator),
         (self.viewModel.onCloseBinEsc, self.__onCloseBinEsc),
         (self.viewModel.onCloseStyleInfoEsc, self.onCloseStyleInfo),
         (self.viewModel.onExpandCarousel, self.__onExpandCarousel),
         (self.viewModel.onSceneOverChange, self.__onSceneOverChange),
         (self.viewModel.onSceneDraggingChange, self.__onSceneDraggingChange),
         (self.viewModel.onSceneClick, self.__onSceneClick),
         (self.viewModel.onMoveSpace, self.__onMoveSpace),
         (self.viewModel.onSelectItem, self.__onSelectItem),
         (self.viewModel.onUnselectItem, self.__onUnselectItem),
         (self.viewModel.onSelectTab, self.__onSelectTab),
         (self.viewModel.onHoverItem, self.__onHoverItem),
         (self.viewModel.onApplyToAllSeasonsChange, self.__onApplyToAllSeasonsChange),
         (self.viewModel.onEditItem, self.__onEditItem),
         (self.viewModel.onCloseEditItem, self.__onCloseEditItem),
         (self.viewModel.onClickDecalsBanner, self.__onProgressionDecalsBannerClick),
         (self.viewModel.onSelectSeason, self.__onSelectSeason),
         (self.viewModel.onBuyItems, self.__onBuyItems),
         (self.viewModel.onProgressiveInfoButtonClick, self.__showProgressiveInfoView),
         (self.viewModel.billModel.onAutoRentHintClose, self.__onAutoRentHintClose),
         (self.viewModel.billModel.onAutoRentChange, self.__onAutoRentChange),
         (self.viewModel.billModel.onClearBasket, self.__onRemoveAll),
         (self.viewModel.billModel.onCancelChanges, self.__onCancelChanges),
         (self.viewModel.billModel.onShowBuyWindow, self.showBuyWindow),
         (self.viewModel.markersModel.onSelectAnchor, self.__onSelectAnchor),
         (self.viewModel.markersModel.onHoverAnchor, self.__onHoverAnchor),
         (self.viewModel.markersModel.onDragAnchor, self.__onDragAnchor),
         (self.viewModel.onPressSelectNextItem, self.__onPressSelectNextItem),
         (self.viewModel.onRequestItems, self.__onRequestItems),
         (self.__ctx.events.onItemInstalled, self.__onItemsInstalled),
         (self.__ctx.events.onItemSelected, self.__onItemSelected),
         (self.__ctx.events.onTabChanged, self.__onTabChanged),
         (self.__ctx.events.onSeasonChanged, self.__onSeasonChanged),
         (self.__ctx.events.onItemUnselected, self.__onItemUnselected),
         (self.__ctx.events.onSlotSelected, self.__onSlotSelected),
         (self.__ctx.events.onSlotUnselected, self.__onSlotUnselected),
         (self.__ctx.events.onChangesCanceled, self.__onChangesCanceled),
         (self.__ctx.events.onItemsRemoved, self.__onItemsRemoved),
         (self.__ctx.events.onModeChanged, self.__onModeChanged),
         (self.__ctx.events.onProlongStyleRent, self.__onProlongStyleRent),
         (self.__ctx.events.onAnchorsStateChanged, self.__onAnchorsStatesChanged),
         (self.__ctx.events.onCacheResync, self.__onCacheResync),
         (self.__ctx.events.onCarouselFiltered, self.__updateData),
         (self.__ctx.events.onEditModeEnabled, self.__onEditModeEnabled),
         (self.__ctx.events.onGetItemBackToHand, self.__onGetItemBackToHand),
         (self.__ctx.events.onPropertySheetHidden, self.__onPropertySheetHidden),
         (self.__ctx.events.onShowStyleInfo, self.__onShowStyleInfo),
         (self.__ctx.events.onUpdateSwitchers, self.__onUpdateSwitchers),
         (self.__ctx.events.onPropertySheetShown, self.__onPropertySheetShown),
         (self.__ctx.events.onComponentChanged, self.__onComponentChanged),
         (self.__ctx.events.onFilterPopover, self.__onFilterPopover),
         (self.__ctx.events.onOnboardingView, self.__onOnboardingView),
         (self.__service.onRegionHighlighted, self.__onRegionHighlighted),
         (self.__toolbarProvider.onApplyToAllSeasonsSelectedChanged, self.__onApplyToAllSeasonsSelectedChanged),
         (self.__settingsCore.onSettingsChanged, self.__onSettingsChanged),
         (g_currentVehicle.onChanged, self.__onVehicleChanged),
         (g_currentVehicle.onChangeStarted, self.__onVehicleChangeStarted))

    def _getCallbacks(self):
        return (('stats.{}'.format(c), self.__updateMoney) for c in Currency.ALL)

    def _onLoading(self, *args, **kwargs):
        self.__isOnLoading = True
        self.__ctx = self.__service.getCtx()
        self.__toolbarProvider = CustomizationToolbarProvider(self)
        self.__toolbarProvider.init()
        self.__stageSwitcherProvider = StageSwitcherProvider(self)
        super(CustomizationMainView, self)._onLoading(*args, **kwargs)
        self._loadSettings()
        entity = self.__hangarSpace.getVehicleEntity()
        if entity and entity.appearance:
            entity.appearance.loadState.subscribe(self.__onVehicleLoadFinished, self.__onVehicleLoadStarted)
            entity.appearance.turretRotator.onTurretRotated += self.__onTurretAndGunRotated
        self.__carouselDP = CustomizationCarouselDataProvider()
        self.__carouselDP.init()
        self.__selectInitialTab()
        self.__updateData()
        if self.__ctx.mode.isRegion:
            highlightingMode = chooseMode(self.__ctx.mode.slotType, self.__ctx.modeId, g_currentVehicle.item)
            self.__service.startHighlighter(highlightingMode)
        self.setChildView(self.__BIN_VIEW_ID, view=CustomizationBinSubview({'c11nView': self}))
        self.setChildView(self.__STYLE_INFO_VIEW_ID, view=CustomizationStyleInfoView())
        layoutID = R.views.lobby.customization.CustomizationMoneyBalance()
        self.setChildView(R.views.lobby.customization.CustomizationMoneyBalance(), MoneyBalance(layoutID, CustomizationMoneyBalanceModel()))
        self.__isOnLoading = False

    def _onLoaded(self, *args, **kwargs):
        super(CustomizationMainView, self)._onLoaded(*args, **kwargs)
        if not self.getSetting(IS_CUSTOMIZATION_INTRO_VIEWED, False):
            questProgressionStyles = self.__service.getStyles(criteria=REQ_CRITERIA.CUSTOMIZATION.ON_ACCOUNT | REQ_CRITERIA.CUSTOMIZATION.HAS_TAGS([ItemTags.QUESTS_PROGRESSION]))
            if questProgressionStyles:
                showOnboardingView(first(questProgressionStyles), True)
                self.setSetting(IS_CUSTOMIZATION_INTRO_VIEWED, True)
        if self.__progressiveItemCD is not None:
            showProgressiveItemsView(self.__progressiveItemCD, customizationView=self)
        return

    def __onPropertySheetHidden(self):
        if self.__ctx.mode.isRegion:
            self.__service.resetHighlighting()

    def __onPropertySheetShown(self, slotId):
        if not self.getSetting(CAROUSEL_ARROWS_HINT_SHOWN_FIELD, False) and not self.__toolbarProvider.inEditMode:
            self.viewModel.carouselModel.setIsCarouselArrowsHintVisible(True)
            self.__carouselArrowsHintShown = True

    def __tryHideCarouselArrowsHint(self):
        if self.__carouselArrowsHintShown:
            self.viewModel.carouselModel.setIsCarouselArrowsHintVisible(False)
            self.__carouselArrowsHintShown = False
            self.setSetting(CAROUSEL_ARROWS_HINT_SHOWN_FIELD, True)

    def __onShowStyleInfo(self, style=None):
        self.__ctx.mode.unselectSlot()
        self.soundManager.setState(SOUNDS.STATE_STYLEINFO, SOUNDS.STATE_STYLEINFO_SHOW)
        self.soundManager.setRTPC(SOUNDS.RTPC_STYLEINFO, 1)
        self.__service.stopHighlighter()
        entity = self.__hangarSpace.getVehicleEntity()
        if entity and entity.appearance and entity.appearance.isLoaded():
            self.__ctx.c11nCameraManager.locateCameraToStyleInfoPreview()
        with self.viewModel.transaction() as model:
            model.setIsStyleInfoViewActive(True)

    def __onTurretAndGunRotated(self):
        if self.__ctx.mode.isRegion:
            self.__service.restartHighlighter()

    def __onSettingsChanged(self, diff):
        if self.__ctx.mode.isRegion and 'OBJECT_LOD' in diff:
            BigWorld.callback(0.0, self.__service.restartHighlighter)

    def __updateBaseData(self, model):
        self.__carouselDP.updateCarouselDPData()
        filteredItemsCounter, itemsCounter, newHiddenItemsCount = self.__carouselDP.getCountersForCtx()
        model.setIsEditable(self.__ctx.modeId == CustomizationModes.EDITABLE_STYLE)
        model.setIsApplyToAllSeasonsAvailable(self.__toolbarProvider.isApplyToAllSeasonsAvailable)
        model.setIsApplyToAllSeasonsSelected(self.__toolbarProvider.isApplyToAllSeasonsSelected)
        model.filterModel.setFavorite(self.__carouselDP.isFilterApplied(FilterTypes.FAVORITE))
        model.filterModel.setAvailability(self.__carouselDP.getAvailabilityFilter())
        model.filterModel.setAllItemsCounter(itemsCounter)
        model.filterModel.setFilteredItemsCounter(filteredItemsCounter)
        model.filterModel.setNewHiddenItemsCounter(newHiddenItemsCount)
        model.filterModel.setIsFilteringActive(self.__carouselDP.hasAppliedFilter())
        structure = getStructureList(self.__ctx, self.__carouselDP)
        structureList = model.filterModel.getStructure()
        structureList.clear()
        for el in structure:
            structureList.addString(el.value)

        structureList.invalidate()
        self.__fillVehicleInfo(model.headerVehicleInfoModel)

    def __updateData(self):
        self.__updateSelection()
        with self.viewModel.transaction() as model:
            self.__updateBaseData(model)
            carouselDataItems = self.__carouselDP.getCarouselData()
            fillSeasonsModel(model.seasonsModel, self.__ctx)
            fillTabsModel(model.tabsModel, self.__ctx, self.__carouselDP)
            self.__fillCarouselModel(model.carouselModel, carouselDataItems)
            packBottomPanelBillData(model.billModel, model.getIsBuyViewActive())
            self.__fillTypesModel(model.markersModel.customizationTypes)
            model.setIsShowProgressionInfoButton(self.__ctx.modeId == CustomizationModes.EDITABLE_STYLE and any((self.__service.getItemByCD(itemCD).isQuestsProgression for itemCD in carouselDataItems.items)))

    def __changeFilter(self, args):
        self.__carouselDP.updateFilterCarousel({args['key']: args['value']})

    def __clearFilter(self):
        self.__carouselDP.resetFilter()

    def __onGetItemBackToHand(self, item, progressionLevel=-1, scrollToItem=False):
        self.__ctx.mode.selectItem(item.intCD, progressionLevel)

    def __onEditModeEnabled(self, enabled, slotId):
        if enabled and self.__ctx.mode.selectedSlot:
            self.__locateCameraOnAnchor(self.__ctx.mode.selectedSlot, forceRotate=True)

    def __showBinSubview(self):
        if self._binSubView:
            self._binSubView.updateModel()
            self.updateIsBinSubViewActive(True)
            self.__ctx.c11nCameraManager.moveToBinCamera()
            self.__ctx.mode.unselectItem()
            self.__ctx.mode.unselectSlot()
            self.viewModel.billModel.setIsAutoRentSelected(self.__ctx.mode.isAutoRentEnabled())

    def __showProgressiveInfoView(self):
        showOnboardingView()

    def __onCacheResync(self, reason, items):
        if not g_currentVehicle.isPresent():
            return
        typesForUpdate = {GUI_ITEM_TYPE.CUSTOMIZATION, GUI_ITEM_TYPE.CUSTOMIZATIONS}
        if not typesForUpdate & set(items):
            return
        self.__carouselDP.invalidateItems()
        self.__updateData()

    def __onVehicleChanged(self):
        entity = self.__hangarSpace.getVehicleEntity()
        if entity and entity.appearance:
            entity.appearance.loadState.subscribe(self.__onVehicleLoadFinished, self.__onVehicleLoadStarted)
        self.__ctx.mode.unselectItem()
        self.__ctx.mode.unselectSlot()
        self.__carouselDP.invalidateItems()
        self.__updateData()

    def __onProgressionDecalsBannerClick(self):
        showProgressiveItemsView(customizationView=self)

    def __updateMoney(self, *_):
        with self.viewModel.transaction() as model:
            packBottomPanelBillData(model.billModel, model.getIsBuyViewActive())

    def __onItemsRemoved(self, *_, **__):
        self.__updateData()

    def __onModeChanged(self, modeId, prevModeId):
        self.__carouselDP.modeChanged(modeId, prevModeId)
        if prevModeId == CustomizationModes.EDITABLE_STYLE:
            self.__checkHighlighter()

    @args2params(int)
    def __onEditItem(self, itemId):
        self.__ctx.editStyle(itemId, source=CustomizationModeSource.CAROUSEL)

    def __onCloseEditItem(self):
        if self.__ctx.mode.modeId == CustomizationModes.EDITABLE_STYLE:
            self.__ctx.changeMode(self.__ctx.prevModeId)
        if self.__ctx.mode.tabId == CustomizationTabs.INSCRIPTIONS and self.__toolbarProvider.isShownToolbar:
            SoundGroups.g_instance.playSound2D(SOUNDS.CUST_CHOICE_ESC)

    def __onCancelChanges(self):
        if self.__ctx.mode.tabId == CustomizationTabs.INSCRIPTIONS and self.__toolbarProvider.isShownToolbar:
            SoundGroups.g_instance.playSound2D(SOUNDS.CUST_CHOICE_ESC)
        self.__ctx.mode.cancelChanges()
        if self.__ctx.modeId in CustomizationModes.ALL_STYLES:
            self.__ctx.changeMode(self.__ctx.prevModeId, tabId=self.__ctx.prevTabId)
            self.__ctx.mode.cancelChanges()

    @adisp.adisp_process
    def showBuyWindow(self, ctx=None):
        isEmpty = isVehicleEmpty()
        if self.__ctx.modeId in CustomizationModes.STYLED:
            currentOutfit = self.__ctx.mode.currentOutfit
            if currentOutfit and currentOutfit.style and currentOutfit.style.isEditable:
                itemId = self.__ctx.mode.currentOutfit.style.compactDescr
                self.__ctx.editStyle(itemId, source=CustomizationModeSource.CAROUSEL)
        if self.__toolbarProvider.handleLobbyClick():
            return
        self.__toolbarProvider.hide()
        purchaseItems = self.__ctx.mode.getPurchaseItems()
        if isEmpty:
            yield self.applyItems(purchaseItems)
        else:
            self.__showBinSubview()

    def __locateCameraOnAnchor(self, slotId, forceRotate=False):
        if self.__ctx.c11nCameraManager is None:
            return
        else:
            anchorParams = self.__ctx.mode.getAnchorParams(slotId)
            if anchorParams is None:
                _logger.warning('Anchor params not found for slot: %s', slotId)
                return
            if slotId.slotType in (GUI_ITEM_TYPE.EMBLEM, GUI_ITEM_TYPE.INSCRIPTION):
                if slotId.slotType == GUI_ITEM_TYPE.EMBLEM:
                    relativeSize = self.__ZOOM_ON_EMBLEM
                else:
                    relativeSize = self.__ZOOM_ON_INSCRIPTION
                located = self.__ctx.c11nCameraManager.locateCameraOnDecal(location=anchorParams.location, width=anchorParams.descriptor.size, slotId=anchorParams.id, relativeSize=relativeSize, forceRotate=forceRotate)
            elif slotId.slotType in (GUI_ITEM_TYPE.STYLE, GUI_ITEM_TYPE.MODIFICATION):
                located = self.__ctx.c11nCameraManager.locateCameraOnAnchor(position=None, normal=None, up=anchorParams.location.up, slotId=anchorParams.id, forceRotate=forceRotate)
            elif slotId.slotType == GUI_ITEM_TYPE.PAINT:
                located = self.__ctx.c11nCameraManager.locateCameraOnAnchor(position=anchorParams.location.position, normal=None, up=anchorParams.location.up, slotId=anchorParams.id, forceRotate=forceRotate)
            else:
                if slotId.slotType == GUI_ITEM_TYPE.PROJECTION_DECAL:
                    normal = anchorParams.location.normal
                    if normal.dot((0.0, 1.0, 0.0)) > 0.99:
                        localPYR = anchorParams.descriptor.rotation
                        worldRotation = Matrix()
                        worldRotation.setRotateYPR((localPYR.y, localPYR.x, localPYR.z))
                        vehicleMatrix = self.__hangarSpace.getVehicleEntity().model.matrix
                        worldRotation.postMultiply(vehicleMatrix)
                        normal.setPitchYaw(anchorParams.location.normal.pitch, worldRotation.yaw)
                else:
                    normal = None
                located = self.__ctx.c11nCameraManager.locateCameraOnAnchor(position=anchorParams.location.position, normal=normal, up=anchorParams.location.up, slotId=anchorParams.id, forceRotate=forceRotate, customConstraints=True)
            if located and not forceRotate:
                self.__toolbarProvider.locateOnAnchor(slotId)
                self.__ctx.vehicleAnchorsUpdater.onCameraLocated(self.__ctx.mode.selectedSlot)
            return

    def __onBuyItems(self):
        if self._binSubView:
            self._binSubView.processBuy()

    def __onProlongStyleRent(self):
        self.showBuyWindow(ctx={'prolongStyleRent': True})

    def __onChangesCanceled(self):
        self.__carouselDP.invalidateFilteredItems()
        self.__updateData()
        self.__fillAnchorsData(True)
        self.__ctx.mode.unselectItem()
        self.__ctx.mode.unselectSlot()
        if self._binSubView:
            self._binSubView.updateModel()

    def __fillVehicleInfo(self, vehicleInfoModel):
        vehicle = g_currentVehicle.item
        vModel = vehicleInfoModel.vehicle
        fillVehicleModel(vModel, vehicle)
        ctxMode = self.__ctx.mode
        if self.__ctx.modeId == CustomizationModes.EDITABLE_STYLE:
            vehicleInfoModel.setIsQuestProgressionInfoBtnVisible(ctxMode.style.isQuestsProgression)
        description, isStyleBonusPreviewText = self.__getHeaderDescriptionData()
        vehicleInfoModel.setDescription(description)
        vehicleInfoModel.setIsStyleBonusPreviewText(isStyleBonusPreviewText)

    def __getHeaderDescriptionData(self):
        slotType = self.__ctx.mode.slotType
        description = ''
        isStyleBonusPreviewText = False
        modeId = self.__ctx.modeId
        rDescription = R.strings.vehicle_customization.customization.header.counter
        if modeId == CustomizationModes.STYLED_2D:
            if self.__ctx.mode.modifiedStyle is not None:
                isStyleBonusPreviewText = True
                description = backport.text(rDescription.c_2Dstyle.installed())
            else:
                description = backport.text(rDescription.c_2Dstyle.notInstalled())
        elif modeId == CustomizationModes.STYLED_3D:
            if self.__ctx.mode.modifiedStyle is not None:
                isStyleBonusPreviewText = True
                description = backport.text(rDescription.c_3Dstyle.installed())
            else:
                description = backport.text(rDescription.c_3Dstyle.notInstalled())
        elif modeId == CustomizationModes.EDITABLE_STYLE:
            isStyleBonusPreviewText = True
            description = backport.text(rDescription.editablestyle.installed(), name=self.__ctx.mode.style.userName)
        elif isVehicleCanBeCustomized(g_currentVehicle.item, slotType):
            typeName = GUI_ITEM_TYPE_NAMES[slotType]
            outfit = self.__ctx.mode.currentOutfit
            slotsCount, filledSlotsCount = checkSlotsFilling(outfit, slotType)
            if slotsCount == filledSlotsCount:
                isStyleBonusPreviewText = True
            description = '' if not rDescription.dyn(typeName).exists() else backport.text(rDescription.dyn(typeName)(), filled=filledSlotsCount, available=slotsCount)
        return (description, isStyleBonusPreviewText)

    def __onItemsInstalled(self, item, slotId, season, component):
        self.__fillAnchorsData(True)
        if self.__ctx.mode.selectedItem is not None:
            if self.__ctx.mode.isRegion:
                outfit = self.__ctx.mode.currentOutfit
                slotType = CustomizationTabs.SLOT_TYPES[self.__ctx.tabId]
                emptyRegions = getEmptyRegions(outfit, slotType)
                self.__service.highlightRegions(emptyRegions)
            if component is not None and not component.isFilled():
                self.__slotSelector.selectSlot(slotId)
        elif slotId == self.__ctx.mode.selectedSlot:
            self.__locateCameraOnAnchor(slotId)
            if self.__ctx.season == season or self.__ctx.mode.modeId in CustomizationModes.ALL_STYLES:
                self.soundManager.playInstantSound(SOUNDS.APPLY)
        if self.__ctx.mode.modeId not in CustomizationModes.ALL_STYLES and self.__ctx.season == season and not self.viewModel.getIsBuyViewActive():
            self.soundManager.playInstantSound(SOUNDS.APPLY)
        with self.viewModel.transaction() as model:
            self.__updateBaseData(model)
            self.__updateItems(model)
            fillSeasonsModel(model.seasonsModel, self.__ctx)
            packBottomPanelBillData(model.billModel, model.getIsBuyViewActive())
        return

    @args2params(int)
    def __onSelectItem(self, itemId):
        self.__tryHideCarouselArrowsHint()
        self.__ctx.mode.selectItem(itemId)
        self.__setItemVisited(itemId)
        with self.viewModel.transaction() as model:
            self.__updateBaseData(model)
            self.__updateItems(model)

    def __setItemVisited(self, itemId):
        visitedSet = self.getSetting(CUSTOMIZATION_STYLE_ITEMS_VISITED, set())
        visitedSet.add(itemId)
        self.setSetting(CUSTOMIZATION_STYLE_ITEMS_VISITED, visitedSet)

    def __onUpdateSwitchers(self, left, right):
        with self.viewModel.transaction() as model:
            model.carouselModel.setIsLeftAvailable(left)
            model.carouselModel.setIsRightAvailable(right)

    @args2params(bool)
    def __onPressSelectNextItem(self, isLeft):
        if self.__ctx.mode.selectedSlot is None:
            return
        else:
            item = self.__carouselDP.getNextItem(isLeft)
            if item is None:
                return
            self.__ctx.mode.selectItem(item.intCD)
            self.__tryHideCarouselArrowsHint()
            return

    def __onUnselectItem(self):
        self.__ctx.mode.unselectItem()

    def __onItemSelected(self, intCD):
        self.__slotSelector.selectItem(intCD)
        if self.__ctx.mode.isRegion:
            outfit = self.__ctx.mode.currentOutfit
            slotType = self.__ctx.mode.slotType
            emptyRegions = getEmptyRegions(outfit, slotType)
            self.__service.highlightRegions(emptyRegions if self.__ctx.tabId != CustomizationTabs.MODIFICATIONS else ApplyArea.ALL)
        self.__updateSelection()

    def __updateItems(self, model):
        self.__updateSelection()
        selectedItemId = self.__selectedItem.intCD if self.__selectedItem is not None else INVALID_ID
        itemsListModel = model.carouselModel.getCarouselItemsList()
        for index, item in enumerate(itemsListModel):
            itemIntCD = item.getIntCD()
            if self.__ctx.mode.modeId == CustomizationModes.EDITABLE_STYLE or itemIntCD == selectedItemId or item.getIsSelected() or item.getIsEquipped():
                itemsListModel.setViewModel(index, self.__getItemDataByCD(itemIntCD))

        itemsListModel.invalidate()
        return

    def __updateSelection(self):
        if self.__ctx.mode.selectedItem is not None:
            self.__selectedItem = self.__ctx.mode.selectedItem
        elif self.__ctx.mode.selectedSlot is not None:
            slotId = self.__ctx.mode.selectedSlot
            if slotId.slotType == GUI_ITEM_TYPE.STYLE and self.__ctx.mode.modeId != CustomizationModes.EDITABLE_STYLE:
                self.__selectedItem = self.__ctx.mode.modifiedStyle
            else:
                self.__selectedItem = self.__ctx.mode.getItemFromSlot(slotId)
        else:
            self.__selectedItem = None
        if self.__ctx.vehicleAnchorsUpdater is not None and self.__ctx.tabId in (CustomizationTabs.EMBLEMS, CustomizationTabs.INSCRIPTIONS):
            self.__ctx.vehicleAnchorsUpdater.forceMaxAlpha(self.__selectedItem is not None)
        self.__carouselDP.selectItem(self.__selectedItem)
        self.__updateStageSwitcherVisibility()
        self.__updateMagneticTool()
        return

    def __onSlotSelected(self, slotId):
        if self.__ctx.mode.isRegion:
            if self.__ctx.tabId in (CustomizationTabs.MODIFICATIONS,) + CustomizationTabs.STYLES_ALL:
                applyArea = ApplyArea.ALL
            else:
                applyArea = appliedToFromSlotsIds([slotId])
            self.__service.selectRegions(applyArea)
            item = self.__ctx.mode.getItemFromSlot(slotId)
            if item is not None:
                self.__locateCameraOnAnchor(slotId)
            else:
                self.resetCustomizationCamera(False)
        else:
            self.__locateCameraOnAnchor(slotId)
        self.__updateSelection()
        return

    def __onSlotUnselected(self):
        self.resetCustomizationCamera(False)
        if self.__ctx.mode.isRegion:
            self.__service.selectRegions(ApplyArea.NONE)
        with self.viewModel.transaction() as model:
            self.__updateBaseData(model)
            if self.__selectedItem is not None:
                self.__updateItems(model)
        return

    def __onItemUnselected(self):
        self.__slotSelector.unselectItem()
        if self.__ctx.mode.isRegion:
            self.__service.highlightRegions(ApplyArea.NONE)
        with self.viewModel.transaction() as model:
            self.__updateBaseData(model)
            self.__updateItems(model)

    @args2params(int)
    def __onSelectTab(self, tabId):
        self.__ctx.changeTab(tabId)

    @args2params(int)
    def __onHoverItem(self, itemId):
        self.__ctx.resetItemsNovelty((itemId,))

    def __onApplyToAllSeasonsChange(self):
        self.__toolbarProvider.setIsApplyToAllSeasons(not self.__toolbarProvider.isApplyToAllSeasonsSelected)

    def __onApplyToAllSeasonsSelectedChanged(self):
        self.viewModel.setIsApplyToAllSeasonsSelected(self.__toolbarProvider.isApplyToAllSeasonsSelected)

    def __onAutoRentHintClose(self):
        self.__settingsCore.serverSettings.setOnceOnlyHintsSettings({OnceOnlyHints.C11N_AUTOPROLONGATION_HINT: HINT_SHOWN_STATUS})
        self.viewModel.billModel.setShowAutoRentHint(self.__settingsCore.serverSettings.getOnceOnlyHintsSetting(OnceOnlyHints.C11N_AUTOPROLONGATION_HINT) != HINT_SHOWN_STATUS)

    def __onAutoRentChange(self):
        self.__ctx.mode.changeAutoRent()
        self.viewModel.billModel.setIsAutoRentSelected(self.__ctx.mode.isAutoRentEnabled())
        if self.viewModel.getIsBuyViewActive():
            self._binSubView.updateModel(updatePurchaseItems=False)

    def __onComponentChanged(self, *__, **_):
        with self.viewModel.transaction() as model:
            self.__updateBaseData(model)
            if self.__ctx.mode.modeId in CustomizationModes.STYLED:
                self.__updateItems(model)

    def __onFilterPopover(self, isOpened):
        with self.viewModel.transaction() as model:
            model.setIsFilterPopoverOpened(isOpened)

    def __onOnboardingView(self, isOpened):
        with self.viewModel.transaction() as model:
            model.setIsOnboardingViewOpened(isOpened)

    def __selectInitialTab(self):
        visibleTabs = self.__carouselDP.getVisibleTabs()
        if visibleTabs:
            initialTabID = self.__getInitialTab()
            self.__ctx.changeTab(findFirst(lambda tabID: tabID == initialTabID, visibleTabs, first(visibleTabs)))
        else:
            _logger.info('There is no visible customization tabs for current vehicle: %s', g_currentVehicle.item)

    def __getInitialTab(self):
        if self.__service.isStyleInstalled() and self.__ctx.mode.currentOutfit.style is not None:
            return getTabByItem(self.__ctx.mode.currentOutfit.style)
        else:
            hasAnyCustomization = bool({item for item in (self.__service.getItemByCD(sd.intCD) for sd in self.__ctx.mode.currentOutfit.slotsData()) if ItemTags.NATIONAL_EMBLEM not in item.descriptor.parentGroup.itemPrototype.tags})
            if not hasAnyCustomization:
                availableStylesForCurrentVehicle = self.__service.getItems(GUI_ITEM_TYPE.STYLE, g_currentVehicle.item, REQ_CRITERIA.INVENTORY_OR_UNLOCKED).values()
                if availableStylesForCurrentVehicle:
                    if any((s.is3D for s in availableStylesForCurrentVehicle)):
                        return CustomizationTabs.STYLED_3D
                    return CustomizationTabs.STYLED_2D
            return CustomizationTabs.CAMOUFLAGES

    @args2params(str)
    def __onSelectSeason(self, seasonName):
        if seasonName in SEASON_NAME_TO_TYPE:
            season = SEASON_NAME_TO_TYPE[seasonName]
        else:
            season = SeasonType.UNDEFINED
            _logger.error('Wrong season  %(season)d', {'season': seasonName})
        self.__ctx.changeSeason(season)

    @args2params(int, int)
    def __onRequestItems(self, startIndex, endIndex):
        self.__fillItemsInRange(startIndex, endIndex)

    def __fillItemsInRange(self, startIndex, endIndex):
        carouselData = self.__carouselDP.getCarouselData()
        newItemsRange = carouselData.items[startIndex:endIndex + 1]
        if not newItemsRange:
            return
        with self.viewModel.transaction() as model:
            needInvalidate = False
            itemsList = model.carouselModel.getCarouselItemsList()
            itemsLength = len(itemsList)
            for index, intCD in enumerate(newItemsRange):
                newIndex = startIndex + index
                if newIndex >= itemsLength:
                    break
                itemModel = itemsList.getValue(newIndex)
                if not itemModel.getIsFilled():
                    needInvalidate = True
                    itemData = self.__getItemDataByCD(intCD)
                    itemsList.setViewModel(newIndex, itemData)

            if needInvalidate:
                itemsList.invalidate()

    def __fillCarouselModel(self, carouselModel, carouselData):
        useBookmarks = self.__carouselDP.getSetting(CustomizationFilter.DISPLAY_GROUP) and len(carouselData.bookmarks) > 1 or self.__ctx.modeId == CustomizationModes.EDITABLE_STYLE
        hasProgressiveItems = any((bookmark['isProgressive'] for bookmark in carouselData.bookmarks))
        displayedBookmarks = carouselData.bookmarks if useBookmarks else [{'bookmarkName': '',
          'bookmarkIndex': 0,
          'isProgressive': hasProgressiveItems}]
        newFirstItemId = INVALID_ID
        equippedFirstItemId = INVALID_ID
        mainTypeFirstItemId = INVALID_ID
        itemsList = carouselModel.getCarouselItemsList()
        itemsList.clear()
        for intCD in carouselData.items:
            itemData = self.__getItemDataEmpty(intCD)
            if newFirstItemId == INVALID_ID and itemData.getNoveltyCounter() > 0:
                newFirstItemId = intCD
            if equippedFirstItemId == INVALID_ID and itemData.getIsEquipped():
                equippedFirstItemId = intCD
            if mainTypeFirstItemId == INVALID_ID and itemData.getIsMainType():
                mainTypeFirstItemId = intCD
            itemsList.addViewModel(itemData)

        itemsList.invalidate()
        bookmarksList = carouselModel.getBookmarksList()
        bookmarksList.clear()
        for bookmark in displayedBookmarks:
            bookmarkItem = CustomizationCarouselBookmarkModel()
            bookmarkItem.setBookmarkName(bookmark['bookmarkName'])
            bookmarkItem.setBookmarkIndex(bookmark['bookmarkIndex'])
            bookmarkItem.setIsProgressive(bookmark['isProgressive'])
            bookmarksList.addViewModel(bookmarkItem)

        bookmarksList.invalidate()
        arrowsList = carouselModel.getArrowsList()
        arrowsList.clear()
        for arrow in carouselData.arrows:
            arrowItem = CustomizationCarouselArrowModel()
            arrowItem.setArrowIndex(arrow['index'])
            arrowItem.setIsEnabled(arrow['enabled'])
            arrowsList.addViewModel(arrowItem)

        arrowsList.invalidate()
        carouselModel.setFilteredItemsCount(self.__carouselDP.itemCount)
        carouselModel.setTotalItemsCount(len(carouselData.items))
        carouselModel.setIsProgressionDecalsBannerVisible(self.__ctx.tabId == CustomizationTabs.PROJECTION_DECALS and hasProgressiveItems)
        carouselModel.setScrollStartItemId(findFirst(lambda i: i != INVALID_ID, (newFirstItemId, equippedFirstItemId, mainTypeFirstItemId), INVALID_ID))

    def __getItemDataEmpty(self, itemCD):
        return packEmptyCustomizationItemData(item=self.__service.getItemByCD(itemCD), vehicle=g_currentVehicle.item, isApplied=itemCD in self.__carouselDP.getAppliedItems())

    def __getItemDataByCD(self, itemCD):
        item = self.__service.getItemByCD(itemCD)
        inventoryCount = self.__ctx.mode.getItemInventoryCount(item)
        purchaseLimit = self.__ctx.mode.getPurchaseLimit(item)
        isApplied = itemCD in self.__carouselDP.getAppliedItems()
        isBaseStyleItem = itemCD in self.__carouselDP.getBaseStyleItems()
        if item.isStyleOnly or isBaseStyleItem:
            isDarked = isUsedUp = False
        else:
            isDarked = purchaseLimit <= 0 and inventoryCount <= 0
            isUsedUp = isItemUsedUp(item)
        showEditableHint = False
        showEditBtnHint = False
        if item.itemTypeID == GUI_ITEM_TYPE.STYLE:
            getOnceOnlyHintsSetting = self.__settingsCore.serverSettings.getOnceOnlyHintsSetting
            autoRentEnabled = self.__ctx.mode.isAutoRentEnabled(item.intCD)
            if item.isProgressionRequired:
                showEditableHint = not bool(getOnceOnlyHintsSetting(OnceOnlyHints.C11N_PROGRESSION_REQUIRED_STYLE_SLOT_HINT))
                showEditBtnHint = not bool(getOnceOnlyHintsSetting(OnceOnlyHints.C11N_PROGRESSION_REQUIRED_STYLE_SLOT_BUTTON_HINT))
            elif item.isEditable:
                showEditableHint = not bool(getOnceOnlyHintsSetting(OnceOnlyHints.C11N_EDITABLE_STYLE_SLOT_HINT))
                showEditBtnHint = not bool(getOnceOnlyHintsSetting(OnceOnlyHints.C11N_EDITABLE_STYLE_SLOT_BUTTON_HINT))
        else:
            autoRentEnabled = False
        isChained, isUnsuitable = self.__carouselDP.processDependentParams(item)
        selectedItemCD = INVALID_ID if self.__selectedItem is None else self.__selectedItem.intCD
        return packCustomizationItemData(settingsProvider=self, item=item, count=inventoryCount, isApplied=isApplied, isDarked=isDarked, isUsedUp=isUsedUp, autoRentEnabled=autoRentEnabled, vehicle=g_currentVehicle.item, showEditableHint=showEditableHint, showEditBtnHint=showEditBtnHint, isChained=isChained, isUnsuitable=isUnsuitable, isInProgress=item.isQuestInProgress(), isSelected=selectedItemCD == itemCD)

    def __fillTypesModel(self, model):
        model.setPaint(GUI_ITEM_TYPE.PAINT)
        model.setCamouflage(GUI_ITEM_TYPE.CAMOUFLAGE)
        model.setModification(GUI_ITEM_TYPE.MODIFICATION)
        model.setOutfit(GUI_ITEM_TYPE.OUTFIT)
        model.setStyle(GUI_ITEM_TYPE.STYLE)
        model.setDecal(GUI_ITEM_TYPE.DECAL)
        model.setEmblem(GUI_ITEM_TYPE.EMBLEM)
        model.setInscription(GUI_ITEM_TYPE.INSCRIPTION)
        model.setProjectionDecal(GUI_ITEM_TYPE.PROJECTION_DECAL)
        model.setInsignia(GUI_ITEM_TYPE.INSIGNIA)
        model.setPersonalNumber(GUI_ITEM_TYPE.PERSONAL_NUMBER)
        model.setSequence(GUI_ITEM_TYPE.SEQUENCE)
        model.setAttachment(GUI_ITEM_TYPE.ATTACHMENT)

    def __onTabChanged(self, tabIndex, itemCD=None):
        self.__checkHighlighter()
        self.__fillAnchorsData()
        self.__updateData()
        if self.__ctx.c11nCameraManager is not None:
            self.resetCustomizationCamera(False)
        self.__tryHideCarouselArrowsHint()
        return

    def __checkHighlighter(self):
        self.__service.stopHighlighter()
        if self.__ctx.mode.isRegion:
            slotType = self.__ctx.mode.slotType
            modeId = self.__ctx.modeId
            highlightingMode = chooseMode(slotType, modeId, g_currentVehicle.item)
            self.__service.startHighlighter(highlightingMode)

    def __onSeasonChanged(self, seasonType):
        seasonName = SEASON_TYPE_TO_NAME.get(seasonType)
        self.soundManager.playInstantSound(SOUNDS.SEASON_SELECT.format(seasonName))
        self.__ctx.mode.unselectSlot()
        self.__slotSelector.unselectSlot()
        self.__fillAnchorsData(True)
        self.__updateData()

    def __onRemoveAll(self):
        if self.__isHistoric and self.__isNonHistoric and self.__isFantastical:
            filterMethod = lambda item: item.customizationDisplayType() == CustomizationDisplayType.HISTORICAL or item.customizationDisplayType() == CustomizationDisplayType.NON_HISTORICAL or item.customizationDisplayType() == CustomizationDisplayType.FANTASTICAL
        elif self.__isHistoric and self.__isNonHistoric:
            filterMethod = lambda item: item.customizationDisplayType() == CustomizationDisplayType.HISTORICAL or item.customizationDisplayType() == CustomizationDisplayType.NON_HISTORICAL
        elif self.__isHistoric and self.__isFantastical:
            filterMethod = lambda item: item.customizationDisplayType() == CustomizationDisplayType.HISTORICAL or item.customizationDisplayType() == CustomizationDisplayType.FANTASTICAL
        elif self.__isNonHistoric and self.__isFantastical:
            filterMethod = lambda item: item.customizationDisplayType() == CustomizationDisplayType.NON_HISTORICAL or item.customizationDisplayType() == CustomizationDisplayType.FANTASTICAL
        elif self.__isHistoric:
            filterMethod = lambda item: item.customizationDisplayType() == CustomizationDisplayType.HISTORICAL
        elif self.__isNonHistoric:
            filterMethod = lambda item: item.customizationDisplayType() == CustomizationDisplayType.NON_HISTORICAL
        elif self.__isFantastical:
            filterMethod = lambda item: item.customizationDisplayType() == CustomizationDisplayType.FANTASTICAL
        else:
            filterMethod = None
        for season in SeasonType.COMMON_SEASONS:
            self.__ctx.mode.removeItemsFromSeason(season=season, filterMethod=filterMethod)

        if self.__ctx.modeId in CustomizationModes.STYLED:
            self.__ctx.mode.clearSlot()
        if self._binSubView:
            self._binSubView.updateModel()
        return

    def __onCustomizationClear(self):
        self.__toolbarProvider.hide()
        self.__ctx.mode.cancelChanges()
        if self.__ctx.modeId == CustomizationModes.EDITABLE_STYLE:
            self.__ctx.changeMode(self.__ctx.prevModeId)
            self.__ctx.mode.cancelChanges()

    def __onRegionHighlighted(self, areaId, regionIdx, highlightingType, highlightingResult):
        if self.__ctx.tabId in (CustomizationTabs.MODIFICATIONS,) + CustomizationTabs.STYLES_ALL:
            areaId = Area.MISC
        slotType = self.__ctx.mode.slotType
        if highlightingType:
            if highlightingResult:
                self.soundManager.playInstantSound(SOUNDS.CHOOSE)
                slotId = C11nId(areaId, slotType, regionIdx)
                self.__slotSelector.selectSlot(slotId)
            else:
                self.__ctx.mode.unselectItem()
                self.__ctx.mode.unselectSlot()
        else:
            if highlightingResult:
                self.soundManager.playInstantSound(SOUNDS.HOVER)
            if highlightingResult != self.viewModel.getIsHoverVehicleSlot():
                self.viewModel.setIsHoverVehicleSlot(highlightingResult)
            self.__hoverAnchor(areaId, slotType, regionIdx, highlightingResult)

    @args2params(bool)
    def __onExpandCarousel(self, isExpanded):
        if isExpanded:
            self.soundManager.playInstantSound(SOUNDS.EDIT_MODE_SWITCH_ON)
            self.soundManager.setState(SOUNDS.STATE_STYLEINFO, SOUNDS.STATE_STYLEINFO_SHOW)
            self.soundManager.setRTPC(SOUNDS.RTPC_STYLEINFO, 1)
        else:
            self.soundManager.playInstantSound(SOUNDS.EDIT_MODE_SWITCH_OFF)
            self.soundManager.setState(SOUNDS.STATE_STYLEINFO, SOUNDS.STATE_STYLEINFO_HIDE)
            self.soundManager.setRTPC(SOUNDS.RTPC_STYLEINFO, 0)
        self.fireEvent(events.LobbyInterfaceEvent(events.LobbyInterfaceEvent.TOGGLE_VISIBILITY, ctx={'headerIsVisible': not isExpanded,
         'ignoreTopOffset': True}), EVENT_BUS_SCOPE.LOBBY)

    @th_async
    def __closeConfirmator(self):
        if isVehicleEmpty() or not self.__ctx.isOutfitsModified() or self.__ctx.mode.modeId in CustomizationModes.STYLED and self.__ctx.mode.isOutfitsEmpty():
            isOk = True
        else:
            isOk = yield th_await(showCloseConfirmWithoutApplyingChangesDialog())
        if isOk:
            self.__forceClose = True
            self.__close()
        raise AsyncReturn(isOk)

    def __onCloseBinEsc(self):
        self.updateIsBinSubViewActive(False)
        self.__ctx.c11nCameraManager.moveToCustomizationCamera()

    def onCloseStyleInfo(self, needToRevertStyle=True):
        if needToRevertStyle:
            self.__ctx.events.onHideStyleInfo()
        self.soundManager.setState(SOUNDS.STATE_STYLEINFO, SOUNDS.STATE_STYLEINFO_HIDE)
        self.soundManager.setRTPC(SOUNDS.RTPC_STYLEINFO, 0)
        self.resetCustomizationCamera(False)
        self.__service.restartHighlighter()
        with self.viewModel.transaction() as model:
            model.setIsStyleInfoViewActive(False)

    def __close(self):
        if self.__forceClose:
            self.__closeConfirmationsHelper.stop()
        self.fireEvent(events.LoadViewEvent(SFViewLoadParams(VIEW_ALIAS.LOBBY_HANGAR)), scope=EVENT_BUS_SCOPE.LOBBY)
        self.destroy()

    def __onMoveSpace(self, args=None):
        if args is None:
            return
        else:
            self.__toolbarProvider.lobbyViewMouseEvent({'dx': args.get('dx'),
             'dy': args.get('dy'),
             'dz': args.get('dz')})
            self.fireEvent(CameraRelatedEvents(CameraRelatedEvents.LOBBY_VIEW_MOUSE_MOVE, ctx={'dx': args.get('dx'),
             'dy': args.get('dy'),
             'dz': args.get('dz')}), EVENT_BUS_SCOPE.GLOBAL)
            self.fireEvent(events.LobbySimpleEvent(events.LobbySimpleEvent.NOTIFY_SPACE_MOVED, ctx={'dx': args.get('dx'),
             'dy': args.get('dy'),
             'dz': args.get('dz')}), EVENT_BUS_SCOPE.GLOBAL)
            return

    @args2params(bool)
    def __onSceneOverChange(self, isOver):
        self.fireEvent(LobbySimpleEvent(LobbySimpleEvent.NOTIFY_CURSOR_OVER_3DSCENE, ctx={'isOver3dScene': isOver}), EVENT_BUS_SCOPE.GLOBAL)

    @args2params(bool)
    def __onSceneDraggingChange(self, isDragging):
        self.fireEvent(events.LobbySimpleEvent(events.LobbySimpleEvent.NOTIFY_CURSOR_DRAGGING, ctx={'isDragging': isDragging}))

    def __onSceneClick(self):
        if self.__ctx.mode.isRegion:
            return
        if self.__toolbarProvider.handleLobbyClick():
            return
        self.__ctx.mode.unselectItem()
        self.__ctx.mode.unselectSlot()

    def __setAnchors(self, anchors):
        if self.__ctx.vehicleAnchorsUpdater is not None:
            with self.viewModel.transaction() as model:
                self.__ctx.vehicleAnchorsUpdater.setAnchors(anchors, model.markersModel.getMarkersList())
        return

    def __initAnchorsPositions(self):
        entity = self.__ctx.c11nCameraManager.vEntity
        self.__initAnchorsPositionsCallback = None
        if entity is not None:
            if entity.isVehicleLoaded:
                entity.appearance.updateAnchorsParams()
            else:
                self.__initAnchorsPositionsCallback = BigWorld.callback(0.0, self.__initAnchorsPositions)
                return
        self.resetCustomizationCamera(resetRotation=False)
        self.__fillAnchorsData()
        return

    @args2params(int, int, int)
    def __onSelectAnchor(self, areaId, slotType, regionIdx):
        slotID = C11nId(areaId, slotType, regionIdx)
        anchorState = self.__ctx.vehicleAnchorsUpdater.getAnchorState(slotID)
        if anchorState == CUSTOMIZATION_ALIASES.ANCHOR_STATE_REMOVED:
            self.__ctx.mode.removeItem(slotID)
            self.__hoverAnchor(areaId, slotType, regionIdx, True)
            return
        self.__slotSelector.selectSlot(slotID)

    @args2params(int, int, int, bool)
    def __onHoverAnchor(self, areaId, slotType, regionIdx, hover):
        self.__hoverAnchor(areaId, slotType, regionIdx, hover)

    def __hoverAnchor(self, areaId, slotType, regionIdx, hover):
        slotId = C11nId(areaId, slotType, regionIdx)
        if hover:
            self.__ctx.events.onAnchorHovered(slotId)
        else:
            self.__ctx.events.onAnchorUnhovered(slotId)

    @args2params(int, int, int)
    def __onDragAnchor(self, areaId, slotType, regionIdx):
        slotId = C11nId(areaId, slotType, regionIdx)
        if slotId.slotType not in (GUI_ITEM_TYPE.PROJECTION_DECAL, GUI_ITEM_TYPE.EMBLEM, GUI_ITEM_TYPE.INSCRIPTION):
            return
        elif self.__ctx.mode.selectedItem is not None or self.__ctx.mode.selectedSlot is not None:
            return
        else:
            item = self.__ctx.mode.getItemFromSlot(slotId)
            if item is not None:
                component = self.__ctx.mode.getComponentFromSlot(slotId)
                progressionLevel = item.getUsedProgressionLevel(component)
                if self.__toolbarProvider.isApplyToAllSeasonsSelected:
                    self.__ctx.mode.removeItemFromAllSeasons(slotId)
                else:
                    self.__ctx.mode.removeItem(slotId)
                self.__ctx.mode.selectItem(item.intCD, progressionLevel)
            return

    def __fillAnchorsData(self, update=False):
        if not g_currentVehicle.isPresent():
            _logger.warning('There is no vehicle in hangar for customization.')
            return
        elif update:
            if self.__ctx.vehicleAnchorsUpdater is not None:
                self.__ctx.vehicleAnchorsUpdater.updateAnchorsVisibility()
            return
        else:
            anchors = self.__ctx.mode.getAnchorsData()
            entity = self.__hangarSpace.getVehicleEntity()
            if entity and entity.isVehicleLoaded:
                self.__setAnchors(anchors)
            return

    def __onVehicleLoadFinished(self):
        self.__setAnchors(self.__ctx.mode.getAnchorsData())
        if self.__ctx.c11nCameraManager is None:
            _logger.warning('Missing customization camera manager')
            return
        else:
            return

    def __onVehicleChangeStarted(self):
        entity = self.__hangarSpace.getVehicleEntity()
        if entity and entity.appearance:
            entity.appearance.loadState.unsubscribe(self.__onVehicleLoadFinished, self.__onVehicleLoadStarted)

    def __onVehicleLoadStarted(self):
        pass

    def __onAnchorsStatesChanged(self, changedStates):
        with self.viewModel.transaction() as model:
            markerList = model.markersModel.getMarkersList()
            for index, state in changedStates.iteritems():
                if index >= len(markerList):
                    continue
                markerList[index].setState(state)

            markerList.invalidate()

    def __updateStageSwitcherVisibility(self):
        isVisibleSwitcher = self.__ctx.mode.modeId == CustomizationModes.STYLED_3D and self.__ctx.mode.currentOutfit.style and self.__ctx.mode.currentOutfit.style.isProgression
        self.__stageSwitcherProvider.setVisibility(isVisibleSwitcher)

    def __updateMagneticTool(self):
        with self.viewModel.magneticToolModel.transaction() as model:
            fillMagneticTool(model, self.__ctx.mode.selectedItem, g_currentVehicle.item, self.__ctx.tabId)
