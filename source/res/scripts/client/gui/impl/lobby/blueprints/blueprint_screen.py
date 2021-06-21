# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/blueprints/blueprint_screen.py
import BigWorld
import nations
from account_helpers import AccountSettings
from account_helpers.AccountSettings import VEHICLES_WITH_BLUEPRINT_CONFIRM, STORAGE_BLUEPRINTS_CAROUSEL_FILTER
from adisp import process
from async import async, await
from blueprints.BlueprintTypes import BlueprintTypes
from frameworks.wulf import ViewSettings
from frameworks.wulf.gui_constants import ViewFlags, ViewStatus
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.lobby.go_back_helper import getBackBtnDescription
from gui.Scaleform.daapi.view.lobby.techtree.techtree_dp import g_techTreeDP
from gui.Scaleform.framework.managers.loaders import SFViewLoadParams
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.impl.backport import createTooltipData, BackportTooltipWindow
from gui.impl.dialogs import dialogs
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.blueprints.blueprint_screen_model import BlueprintScreenModel
from gui.impl.gen.view_models.views.lobby.blueprints.blueprint_screen_scheme_item_model import BlueprintScreenSchemeItemModel
from gui.impl.gen.view_models.views.lobby.blueprints.blueprint_screen_tooltips import BlueprintScreenTooltips
from gui.impl.gen.view_models.views.lobby.blueprints.blueprint_value_price import BlueprintValuePrice
from gui.impl.lobby.blueprints import getBlueprintTooltipData
from gui.impl.lobby.blueprints.fragments_balance_content import FragmentsBalanceContent
from gui.impl.pub import ViewImpl
from gui.server_events.formatters import DISCOUNT_TYPE
from gui.shared import g_eventBus, event_dispatcher, events
from gui.shared.event_bus import EVENT_BUS_SCOPE
from gui.shared.gui_items.items_actions import factory
from gui.shared.gui_items.items_actions.actions import UnlockItemActionWithResult
from gui.shared.utils.functions import getVehTypeIconName
from gui.shared.utils.requesters.blueprints_requester import SPECIAL_BLUEPRINT_LEVEL, getNationalFragmentCD
from helpers import dependency, int2roman
from helpers.blueprint_generator import g_blueprintGenerator
from skeletons.connection_mgr import IConnectionManager
from skeletons.gui.shared import IItemsCache

class BlueprintScreen(ViewImpl):
    __itemsCache = dependency.descriptor(IItemsCache)
    __connectionMgr = dependency.descriptor(IConnectionManager)
    __slots__ = ('__vehicle', '__xpCost', '__fullXpCost', '__discount', '__convertedIndexes', '__exitEvent', '__accountSettings')

    def __init__(self, viewKey, viewModelClazz=BlueprintScreenModel, ctx=None):
        settings = ViewSettings(viewKey)
        settings.flags = ViewFlags.LOBBY_SUB_VIEW
        settings.model = viewModelClazz()
        super(BlueprintScreen, self).__init__(settings)
        self.__vehicle = self.__itemsCache.items.getItemByCD(ctx.get('vehicleCD', None))
        self.__exitEvent = ctx.get('exitEvent') if ctx is not None else None
        self.__xpCost = 0
        self.__fullXpCost = 0
        self.__discount = 0
        self.__convertedIndexes = self.__getConvertedIndexes()
        self.__accountSettings = set(AccountSettings.getSettings(VEHICLES_WITH_BLUEPRINT_CONFIRM))
        g_blueprintGenerator.generate(vehicleCD=self.__vehicle.intCD)
        return

    @property
    def viewModel(self):
        return super(BlueprintScreen, self).getViewModel()

    def createToolTip(self, event):
        if event.contentID == R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent():
            tooltipId = event.getArgument('tooltipId')
            itemCD = event.getArgument('itemCD')
            tooltipData = self.__getTooltipData(tooltipId, itemCD)
            if tooltipData is None:
                return
            window = BackportTooltipWindow(tooltipData, self.getParentWindow())
            if window is not None:
                window.load()
            return window
        else:
            return super(BlueprintScreen, self).createToolTip(event)

    def _initialize(self):
        super(BlueprintScreen, self)._initialize()
        BigWorld.worldDrawEnabled(False)
        self.__addListeners()
        vehicle = self.__vehicle
        bpRequester = self.__itemsCache.items.blueprints
        vehType = getVehTypeIconName(vehicle.type, vehicle.isElite)
        showBlueprintInfotypeIcon = self.__vehicle.level not in SPECIAL_BLUEPRINT_LEVEL
        rows, columns, layout = bpRequester.getLayout(vehicle.intCD, vehicle.level)
        filledCount, totalCount = bpRequester.getBlueprintCount(vehicle.intCD, vehicle.level)
        isSchemeFullCompleted = filledCount == totalCount
        maxFragmentCount = bpRequester.getConvertibleFragmentCount(vehicle.intCD, vehicle.level)
        self.__updateResearchPrice()
        isAvailableForUnlock, needXpToUnlock = self.__checkIsVehicleAvailable()
        with self.getViewModel().transaction() as model:
            model.setVehicleName(vehicle.shortUserName)
            model.setVehicleLevel(int2roman(vehicle.level))
            model.setVehicleType(vehType)
            model.setIsElite(vehicle.isElite)
            model.setShowBlueprintInfotypeIcon(showBlueprintInfotypeIcon)
            model.setConversionAvailable(self.__isConversionAvailable())
            model.setCost(self.gui.systemLocale.getNumberFormat(self.__xpCost))
            model.setDiscount(self.__discount)
            model.setDiscountAbs(self.gui.systemLocale.getNumberFormat(int(self.__fullXpCost - self.__xpCost)))
            model.setIsUnlocked(self.__vehicle.isUnlocked)
            model.setIsAvailableForUnlock(isAvailableForUnlock)
            model.setIsPurchased(self.__vehicle.isPurchased)
            model.setNeedXpToUnlock(needXpToUnlock)
            model.setSchemeCols(columns)
            model.setSchemeRows(rows)
            model.setFilledCount(filledCount)
            model.setIsSchemeFullCompleted(isSchemeFullCompleted)
            model.setMaxConvertibleFragmentCount(maxFragmentCount)
            self.__updateLayout(model, layout)
            model.setShowUnavailableConfirm(not isAvailableForUnlock and not isSchemeFullCompleted and vehicle.intCD not in self.__accountSettings)
            conversionMaxCost = model.conversionMaxCost
            self.__updateConversionData(conversionMaxCost)
            model.setBackBtnLabel(getBackBtnDescription(self.__exitEvent, self.__exitEvent.name, vehicle.shortUserName))
            model.setCurrentStateView(BlueprintScreenModel.INIT)
        self.setChildView(R.dynamic_ids.blueprint_screen.balance_content(), FragmentsBalanceContent(vehicle.intCD))

    def _finalize(self):
        if self.__vehicle is not None:
            g_blueprintGenerator.cancel(vehicleCD=self.__vehicle.intCD)
        self.__removeListeners()
        AccountSettings.setSettings(VEHICLES_WITH_BLUEPRINT_CONFIRM, self.__accountSettings)
        self.__convertedIndexes = None
        self.__accountSettings = None
        if self.__connectionMgr.isConnected():
            BigWorld.worldDrawEnabled(True)
        if self.__exitEvent is not None:
            storageFilter = AccountSettings.getSessionSettings(STORAGE_BLUEPRINTS_CAROUSEL_FILTER)
            storageFilter['scroll_to'] = None
            AccountSettings.setSessionSettings(STORAGE_BLUEPRINTS_CAROUSEL_FILTER, storageFilter)
            self.__exitEvent = None
        super(BlueprintScreen, self)._finalize()
        return

    def __addListeners(self):
        g_clientUpdateManager.addCallbacks({'stats.unlocks': self.__onUnlockVehicle,
         'stats.freeXP': self.__onUpdateXP,
         'stats.vehTypeXP': self.__onUpdateXP,
         'blueprints': self.__onUpdateBlueprints,
         'serverSettings.blueprints_config': self.__onBlueprintsSettingsChanged})
        self.viewModel.onGoToConversionScreen += self.__onGoToConversionScreen
        self.viewModel.onGoToAllConversion += self.__onGoToAllConversion
        self.viewModel.onClose += self.__onCloseAction
        self.viewModel.onResearchVehicle += self.__onResearchVehicle
        self.viewModel.onSubmitUnavailableConfirm += self.__onSubmitUnavailableConfirm
        self.viewModel.onOpenVehicleViewBtnClicked += self.__onOpenVehicleViewBtnClicked

    def __removeListeners(self):
        self.viewModel.onGoToConversionScreen -= self.__onGoToConversionScreen
        self.viewModel.onGoToAllConversion -= self.__onGoToAllConversion
        self.viewModel.onClose -= self.__onCloseAction
        self.viewModel.onResearchVehicle -= self.__onResearchVehicle
        self.viewModel.onSubmitUnavailableConfirm -= self.__onSubmitUnavailableConfirm
        self.viewModel.onOpenVehicleViewBtnClicked -= self.__onOpenVehicleViewBtnClicked
        g_clientUpdateManager.removeObjectCallbacks(self)

    @async
    def __onGoToConversionScreen(self, args):
        isResearchClicked, (usedFragmentsData, fragmentCount) = yield await(dialogs.blueprintsConversion(parent=self.getParentWindow(), vehicleCD=self.__vehicle.intCD))
        if isResearchClicked and self.viewStatus == ViewStatus.LOADED:
            layoutId = int(args['value'])
            factory.doAction(factory.CONVERT_BLUEPRINT_FRAGMENT, self.__vehicle.intCD, fragmentCount, layoutId, usedNationalFragments=usedFragmentsData)

    @async
    def __onGoToAllConversion(self, _=None):
        isResearchClicked, (usedFragmentsData, fragmentCount) = yield await(dialogs.blueprintsConversion(parent=self.getParentWindow(), vehicleCD=self.__vehicle.intCD, fragmentCount=self.viewModel.getMaxConvertibleFragmentCount()))
        if isResearchClicked and self.viewStatus == ViewStatus.LOADED:
            factory.doAction(factory.CONVERT_BLUEPRINT_FRAGMENT, self.__vehicle.intCD, fragmentCount, usedNationalFragments=usedFragmentsData)

    def __onCloseAction(self):
        if self.__exitEvent is not None:
            g_eventBus.handleEvent(self.__exitEvent, scope=EVENT_BUS_SCOPE.LOBBY)
            self.__exitEvent = None
        else:
            self.destroyWindow()
        return

    def __onSubmitUnavailableConfirm(self):
        self.__accountSettings.add(self.__vehicle.intCD)

    def __onOpenVehicleViewBtnClicked(self):
        event_dispatcher.showResearchView(self.__vehicle.intCD, exitEvent=events.LoadViewEvent(SFViewLoadParams(VIEW_ALIAS.LOBBY_TECHTREE), ctx={'nation': self.__vehicle.nationName}))

    @process
    def __onResearchVehicle(self, _=None):
        self.viewModel.setBlueprintAnimPaused(True)
        result = yield UnlockItemActionWithResult(self.__vehicle.intCD, g_techTreeDP.getUnlockProps(self.__vehicle.intCD, self.__vehicle.level)).doAsyncAction()
        btnResult = result.success if result is not None else False
        if not btnResult and self.viewStatus == ViewStatus.LOADED:
            self.viewModel.setBlueprintAnimPaused(False)
        return

    def __onBlueprintsSettingsChanged(self, diff):
        if 'levels' in diff:
            self.__onUpdateBlueprints(diff)
        elif not self.__itemsCache.items.blueprints.isBlueprintsAvailable():
            event_dispatcher.showHangar()

    def __onUpdateBlueprints(self, _):
        bpRequester = self.__itemsCache.items.blueprints
        layout = self.__getLayout()
        self.__updateResearchPrice()
        filledCount, totalCount = bpRequester.getBlueprintCount(self.__vehicle.intCD, self.__vehicle.level)
        isSchemeFullCompleted = filledCount == totalCount
        maxFragCount = bpRequester.getConvertibleFragmentCount(self.__vehicle.intCD, self.__vehicle.level)
        with self.getViewModel().transaction() as model:
            model.setCost(self.gui.systemLocale.getNumberFormat(self.__xpCost))
            model.setDiscount(self.__discount)
            model.setDiscountAbs(self.gui.systemLocale.getNumberFormat(int(self.__fullXpCost - self.__xpCost)))
            model.setConversionAvailable(self.__isConversionAvailable())
            model.setFilledCount(filledCount)
            model.setIsSchemeFullCompleted(isSchemeFullCompleted)
            model.setMaxConvertibleFragmentCount(maxFragCount)
            model.setCurrentStateView(BlueprintScreenModel.UPDATE)
            self.__updateLayout(model, layout)
            self.__updateConversionData(model.conversionMaxCost)

    def __onUnlockVehicle(self, unlocks):
        if self.__vehicle.intCD not in unlocks:
            return
        layout = self.__getLayout()
        self.__getConvertedIndexes(layout)
        with self.getViewModel().transaction() as model:
            model.setIsElite(self.__vehicle.isElite)
            model.setIsUnlocked(True)
            model.setCurrentStateView(BlueprintScreenModel.UPDATE)
            self.__updateLayout(model, layout)

    def __onUpdateXP(self, _):
        isAvailableForUnlock, needXpToUnlock = self.__checkIsVehicleAvailable()
        with self.getViewModel().transaction() as model:
            model.setIsAvailableForUnlock(isAvailableForUnlock)
            model.setNeedXpToUnlock(needXpToUnlock)

    def __checkIsVehicleAvailable(self):
        stats = self.__itemsCache.items.stats
        vehicleXPs = stats.vehiclesXPs
        freeXP = stats.actualFreeXP
        isAvailableForUnlock, _ = g_techTreeDP.isNext2Unlock(self.__vehicle.intCD, stats.unlocks, vehicleXPs, freeXP, self.__vehicle.level)
        needXpToUnlock = self.__xpCost - vehicleXPs.get(self.__vehicle.intCD, 0)
        needWithFreeXP = needXpToUnlock - freeXP
        needXpToUnlock = min(needXpToUnlock, needWithFreeXP)
        return (isAvailableForUnlock, needXpToUnlock > 0)

    def __updateConversionData(self, model):
        bpRequester = self.__itemsCache.items.blueprints
        intelligenceFragCount = bpRequester.getIntelligenceCount()
        nationFragCost, intelligenceFragCost = bpRequester.getRequiredIntelligenceAndNational(self.__vehicle.level)
        model.setHasAdditionalCost(nationFragCost != 0)
        model.valueMain.setIcon(R.images.gui.maps.icons.blueprints.fragment.special.intelligence())
        model.valueMain.setValue(self.gui.systemLocale.getNumberFormat(intelligenceFragCost))
        model.valueMain.setNotEnough(intelligenceFragCount < intelligenceFragCost)
        model.valueMain.setItemCD(BlueprintTypes.INTELLIGENCE_DATA)
        model.valueMain.setTooltipId(BlueprintScreenTooltips.TOOLTIP_BLUEPRINT)
        additionalValues = model.additionalValues.getItems()
        additionalValues.clear()
        options = bpRequester.getNationalRequiredOptions(self.__vehicle.intCD, self.__vehicle.level)
        allyBallance = bpRequester.getNationalAllianceFragments(self.__vehicle.intCD, self.__vehicle.level)
        lastPriceIdx = len(options) - 1
        for index, (nId, cost) in enumerate(options.iteritems()):
            nationName = nations.MAP[nId]
            price = BlueprintValuePrice()
            price.setValue(self.gui.systemLocale.getNumberFormat(cost))
            price.setIcon(R.images.gui.maps.icons.blueprints.fragment.special.dyn(nationName)())
            price.setNotEnough(allyBallance[nId] < cost)
            price.setHasDelimeter(index < lastPriceIdx)
            price.setItemCD(getNationalFragmentCD(nId))
            price.setTooltipId(BlueprintScreenTooltips.TOOLTIP_BLUEPRINT)
            additionalValues.addViewModel(price)

        additionalValues.invalidate()

    def __updateResearchPrice(self):
        if not self.__vehicle.isUnlocked:
            self.__xpCost, self.__discount, self.__fullXpCost = g_techTreeDP.getOldAndNewCost(self.__vehicle.intCD, self.__vehicle.level)

    def __isConversionAvailable(self):
        return self.__itemsCache.items.blueprints.canConvertToVehicleFragment(self.__vehicle.intCD, self.__vehicle.level) if not self.__vehicle.isUnlocked else False

    def __getLayout(self):
        _, _, layout = self.__itemsCache.items.blueprints.getLayout(self.__vehicle.intCD, self.__vehicle.level)
        return layout

    def __getConvertedIndexes(self, layout=None):
        if layout is None:
            layout = self.__getLayout()
        return set([ idx for idx, layoutID in enumerate(layout) if layoutID == 1 ])

    def __updateLayout(self, model, layout):
        schemeItems = model.getSchemeItems()
        schemeItems.clear()
        receivedCount = 0
        for idx, fragment in enumerate(layout):
            itemModel = BlueprintScreenSchemeItemModel()
            itemModel.setReceived(fragment)
            if fragment and idx not in self.__convertedIndexes:
                itemModel.setIsNew(True)
                receivedCount += 1
                self.__convertedIndexes.add(idx)
            schemeItems.addViewModel(itemModel)

        schemeItems.invalidate()
        model.setReceivedCount(receivedCount)

    def __getTooltipData(self, ttId, itemCD):
        blueprintTooltip = getBlueprintTooltipData(ttId, itemCD)
        if blueprintTooltip is not None:
            return blueprintTooltip
        elif ttId == BlueprintScreenTooltips.TOOLTIP_XP_DISCOUNT:
            return createTooltipData(isSpecial=True, specialAlias=TOOLTIPS_CONSTANTS.PRICE_DISCOUNT, specialArgs=(self.__xpCost, self.__fullXpCost, DISCOUNT_TYPE.XP))
        elif ttId == BlueprintScreenTooltips.TOOLTIP_BLUEPRINT and self.__vehicle.level not in SPECIAL_BLUEPRINT_LEVEL:
            return createTooltipData(isSpecial=True, specialAlias=TOOLTIPS_CONSTANTS.BLUEPRINT_INFO, specialArgs=(self.__vehicle.intCD, True))
        elif ttId == BlueprintScreenTooltips.TOOLTIP_BLUEPRINT_ITEM_PLACE:
            return createTooltipData(isSpecial=True, specialAlias=TOOLTIPS_CONSTANTS.BLUEPRINT_EMPTY_SLOT_INFO, specialArgs=[self.__vehicle.intCD])
        else:
            return createTooltipData(isSpecial=True, specialAlias=TOOLTIPS_CONSTANTS.BLUEPRINT_CONVERT_INFO, specialArgs=[self.__vehicle.intCD]) if ttId == BlueprintScreenTooltips.TOOLTIP_BLUEPRINT_CONVERT_COUNT else None
