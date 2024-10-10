# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/techtree/vehicle_tech_tree.py
import weakref
import typing
import nations
from frameworks.wulf import ViewFlags, ViewSettings, ViewModel
from account_helpers.AccountSettings import AccountSettings, EarlyAccess
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.framework.managers.optimization_manager import ExternalFullscreenGraphicsOptimizationComponent
from gui.Scaleform.genConsts.CONTACTS_ALIASES import CONTACTS_ALIASES
from gui.Scaleform.genConsts.SESSION_STATS_CONSTANTS import SESSION_STATS_CONSTANTS
from gui.impl.gui_decorators import args2params
from gui.impl.lobby.early_access.early_access_window_events import showEarlyAccessVehicleView
from gui.impl.lobby.techtree.tech_tree_custom_hints import TechTreeCustomHints
from gui.impl.lobby.techtree.tech_tree_tooltips import nationTechTreeTooltipDecorator
from gui.Scaleform.daapi.view.lobby.store.browser.shop_helpers import getPremiumVehiclesUrl
from gui.impl.gen.view_models.views.lobby.blueprints.blueprint_screen_tooltips import BlueprintScreenTooltips
from gui.shared import EVENT_BUS_SCOPE, events
from gui.techtree.nation_tree_data import NationTreeData
from gui.techtree.dumpers import StubDumper
from gui.Scaleform.genConsts.CONTEXT_MENU_HANDLER_TYPE import CONTEXT_MENU_HANDLER_TYPE
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.impl.backport import createContextMenuData, BackportContextMenuWindow, createTooltipData
from gui.techtree.go_back_helper import BackButtonContextKeys
from gui.impl.lobby.common.view_wrappers import createBackportTooltipDecorator
from gui.impl.gen import R
from gui.impl.lobby.techtree.model_placeholders import fillVehicleTechTreeNodesModel, updateVehiclePrices, updateVehiclesInfo, updateVehiclesUnlocks, updateVehiclesCmpStatus, updateEarlyAccessNodes, fillNationTechTreeModel, formatBlueprintBalance, updateBlueprintsMode
from gui.techtree.selected_nation import SelectedNation
from gui.impl.lobby.techtree.sound_constants import TECHTREE_SOUND_SPACE, Sounds
from gui.impl.gen.view_models.views.lobby.techtree.vehicle_tech_tree_model import VehicleTechTreeModel
from gui.techtree.listeners import TTListenerDecorator, IPage
from gui.impl.pub import ViewImpl
from gui.shared.event_dispatcher import showCollectibleVehicles, showBlueprintView, showVehicleBuyDialog, showHangar, showShop, showResearchView, getTechTreeLoadEvent
from gui.shared.gui_items import GUI_ITEM_TYPE_NAMES, GUI_ITEM_TYPE
from gui.shared.utils.vehicle_collector_helper import hasCollectibleVehicles
from gui.shared.gui_items.items_actions import factory as ItemsActionsFactory
from gui.shop import canBuyGoldForVehicleThroughWeb
from gui.sounds.ambients import LobbySubViewEnv
from helpers import dependency, time_utils
from messenger.gui.Scaleform.view.lobby import MESSENGER_VIEW_ALIAS
from skeletons.gui.game_control import IVehicleComparisonBasket
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
from skeletons.gui.game_control import IEarlyAccessController
from gui.shared.utils.requesters.blueprints_requester import getNationalFragmentCD
from blueprints.BlueprintTypes import BlueprintTypes
from skeletons.gui.techtree_events import ITechTreeEventsListener
from shared_utils import findFirst
_VEHICLE_URL_FILTER_PARAM = 1
if typing.TYPE_CHECKING:
    from frameworks.wulf import View, ViewEvent

class VehicleTechTree(ViewImpl):
    __slots__ = ('__treeData', '__listener', '__invalidator', '__customHints', '__ctx', '__graphicOptimization')
    __sound_env__ = LobbySubViewEnv
    _COMMON_SOUND_SPACE = TECHTREE_SOUND_SPACE
    __lobbyContext = dependency.descriptor(ILobbyContext)
    __itemsCache = dependency.descriptor(IItemsCache)
    __cmpBasket = dependency.descriptor(IVehicleComparisonBasket)
    __earlyAccessController = dependency.descriptor(IEarlyAccessController)
    __techTreeEventsListener = dependency.descriptor(ITechTreeEventsListener)

    def __init__(self, layoutID, *args, **kwargs):
        settings = ViewSettings(layoutID)
        settings.flags = ViewFlags.LOBBY_SUB_VIEW
        settings.model = VehicleTechTreeModel()
        self.__treeData = NationTreeData(StubDumper())
        self.__listener = TTListenerDecorator()
        self.__invalidator = VehicleTechTreeInvalidator(self, self.__treeData)
        self.__ctx = kwargs.get('ctx', {})
        self.__customHints = TechTreeCustomHints(self)
        self.__graphicOptimization = ExternalFullscreenGraphicsOptimizationComponent()
        super(VehicleTechTree, self).__init__(settings)

    @property
    def viewModel(self):
        return super(VehicleTechTree, self).getViewModel()

    def createContextMenu(self, event):
        if event.contentID == R.views.common.BackportContextMenu():
            nodeId = int(event.getArgument('nodeId'))
            node = self.__treeData.getNodeByItemCD(nodeId)
            if node.getTypeName() == GUI_ITEM_TYPE_NAMES[GUI_ITEM_TYPE.VEHICLE]:
                contextMenuArgs = {'vehCD': nodeId,
                 'nodeState': node.getState()}
                contextMenuType = CONTEXT_MENU_HANDLER_TYPE.BLUEPRINT_VEHICLE if self.__blueprintMode else CONTEXT_MENU_HANDLER_TYPE.RESEARCH_VEHICLE
                contextMenuData = createContextMenuData(contextMenuType, contextMenuArgs)
                window = BackportContextMenuWindow(contextMenuData, self.getParentWindow())
                window.load()
                return window
        return super(VehicleTechTree, self).createContextMenu(event)

    @nationTechTreeTooltipDecorator
    @createBackportTooltipDecorator()
    def createToolTip(self, event):
        return super(VehicleTechTree, self).createToolTip(event)

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.lobby.early_access.tooltips.EarlyAccessEntryPointPausedTooltip():
            return ViewImpl(ViewSettings(contentID, model=ViewModel()))
        return ViewImpl(ViewSettings(contentID, model=ViewModel())) if contentID == R.views.lobby.techtree.tooltips.ParagonsEntryPointTooltip() else super(VehicleTechTree, self).createToolTipContent(event, contentID)

    def getTooltipData(self, event):
        tooltipId = event.getArgument('tooltipId')
        if tooltipId == VehicleTechTreeModel.TECHTREE_VEHICLE_TOOLTIP:
            nodeId = int(event.getArgument('nodeId'))
            node = self.__treeData.getNodeByItemCD(nodeId)
            return createTooltipData(isSpecial=True, specialArgs=(node, nodeId), specialAlias=TOOLTIPS_CONSTANTS.TECHTREE_VEHICLE)
        elif tooltipId == BlueprintScreenTooltips.TOOLTIP_BLUEPRINT:
            return createTooltipData(isSpecial=True, specialAlias=TOOLTIPS_CONSTANTS.BLUEPRINT_INFO, specialArgs=(int(event.getArgument('nodeId')),))
        elif tooltipId == BlueprintScreenTooltips.TOOLTIP_BLUEPRINT_CONVERT_COUNT:
            return createTooltipData(isSpecial=True, specialAlias=TOOLTIPS_CONSTANTS.BLUEPRINT_CONVERT_INFO, specialArgs=(int(event.getArgument('nodeId')),))
        elif tooltipId == VehicleTechTreeModel.VEHICLE_COLLECTOR_TOOLTIP:
            return createTooltipData(isSpecial=True, specialArgs=(event.getArgument('nation'),), specialAlias=TOOLTIPS_CONSTANTS.VEHICLE_COLLECTOR_INFO)
        elif tooltipId == VehicleTechTreeModel.BLUEPRINT_FRAGMENT_INFO:
            specialArgs = BlueprintTypes.INTELLIGENCE_DATA if event.getArgument('isUniversal') else getNationalFragmentCD(SelectedNation.getIndex())
            return createTooltipData(isSpecial=True, specialArgs=[specialArgs], specialAlias=VehicleTechTreeModel.BLUEPRINT_FRAGMENT_INFO)
        else:
            return None

    def update(self):
        self.__stopTopOfTheTreeSounds()
        self.__playBlueprintPlusSound()
        with self.viewModel.transaction() as ts:
            ts.setSelectedNation(SelectedNation.getName())
            fillNationTechTreeModel(ts, self.__techTreeEventsListener, self.__treeData.getAvailableNations())
            self.__treeData.load(SelectedNation.getIndex())
            fillVehicleTechTreeNodesModel(ts, self.__treeData.getNodes())
            self.__setVehicleCollectorState(SelectedNation.getIndex())
            ts.setIsCmpAvailable(self.__cmpBasket.isEnabled())
            formatBlueprintBalance(ts)
            ts.setIsParagonsEnabled(self.__techTreeEventsListener.isParagonsAnnounceActive())
            updateBlueprintsMode(ts, self.__blueprintMode, self.__lobbyContext.getServerSettings().blueprintsConfig.isBlueprintsAvailable())
            self.updateEarlyAccessState()

    def updateEarlyAccessState(self):
        with self.viewModel.transaction() as ts:
            ts.setIsEarlyAccessPaused(self.__earlyAccessController.isPaused())
            ts.setEarlyAccessCurrentTokens(self.__earlyAccessController.getTokensBalance())
            earlyAccessNation = nations.NAMES[self.__earlyAccessController.getNationID()] if self.__earlyAccessController.isQuestActive() else ''
            ts.setEarlyAccessNation(earlyAccessNation)
            updateEarlyAccessNodes(ts, self.__earlyAccessController)
            self.__updateEarlyAccessShown()

    def _getEvents(self):
        return ((self.viewModel.onNationChange, self.__onNationChange),
         (self.viewModel.goToCollectionVehicle, self.__goToVehicleCollection),
         (self.viewModel.goToBlueprintView, self.__goToBlueprintView),
         (self.viewModel.goToModulesTechTree, self.__goToModulesTechTree),
         (self.viewModel.buyVehicle, self.__buyVehicle),
         (self.viewModel.unlockVehicle, self.__unlockVehicle),
         (self.viewModel.restoreVehicle, self.__restoreVehicle),
         (self.viewModel.addVehicleToCompare, self.__addVehicleToCompare),
         (self.viewModel.onClose, self.__onClose),
         (self.viewModel.goToPremiumShop, self.__goToPremiumShop),
         (self.viewModel.onBlueprintModeChanged, self.__onBlueprintModeChanged),
         (self.viewModel.goToEarlyAccess, self.__goToEarlyAccess))

    def _getListeners(self):
        return ((MESSENGER_VIEW_ALIAS.CHANNEL_MANAGEMENT_WINDOW, self.__closePremiumPanel, EVENT_BUS_SCOPE.LOBBY),
         (CONTACTS_ALIASES.CONTACTS_POPOVER, self.__closePremiumPanel, EVENT_BUS_SCOPE.LOBBY),
         (SESSION_STATS_CONSTANTS.SESSION_STATS_POPOVER, self.__closePremiumPanel, EVENT_BUS_SCOPE.LOBBY),
         (VIEW_ALIAS.NOTIFICATIONS_LIST, self.__closePremiumPanel, EVENT_BUS_SCOPE.LOBBY),
         (events.ReferralProgramEvent.SHOW_REFERRAL_PROGRAM_WINDOW, self.__closePremiumPanel, EVENT_BUS_SCOPE.LOBBY),
         (events.ChannelCarouselEvent.OPEN_BUTTON_CLICK, self.__closePremiumPanel, EVENT_BUS_SCOPE.LOBBY))

    def _onLoading(self, *args, **kwargs):
        super(VehicleTechTree, self)._onLoading(*args, **kwargs)
        self.__resolveLoadCtx()
        self.__setSettings()
        self.update()
        self.__customHints.init(SelectedNation.getIndex())
        self.__graphicOptimization.init()

    def _finalize(self):
        self.__customHints.fini()
        self.__graphicOptimization.fini()
        super(VehicleTechTree, self)._finalize()

    def _subscribe(self):
        self.__listener.startListen(self.__invalidator)
        super(VehicleTechTree, self)._subscribe()

    def _unsubscribe(self):
        self.__listener.stopListen()
        super(VehicleTechTree, self)._unsubscribe()

    def __resolveLoadCtx(self):
        nation = self.__ctx.get(BackButtonContextKeys.NATION, None)
        if nation is not None and nation in nations.INDICES:
            nationIdx = nations.INDICES[nation]
            SelectedNation.select(nationIdx)
        else:
            SelectedNation.byDefault()
        return

    @property
    def __blueprintMode(self):
        return self.__ctx.get(BackButtonContextKeys.BLUEPRINT_MODE, False)

    @__blueprintMode.setter
    def __blueprintMode(self, value):
        self.__ctx[BackButtonContextKeys.BLUEPRINT_MODE] = value

    @args2params(str)
    def __onNationChange(self, nationName):
        self.__stopTopOfTheTreeSounds()
        with self.viewModel.transaction() as ts:
            ts.setSelectedNation(nationName)
            nationID = nations.INDICES.get(nationName, nations.NONE_INDEX)
            SelectedNation.select(nationID)
            self.__treeData.load(nationID)
            fillVehicleTechTreeNodesModel(ts, self.__treeData.getNodes())
            self.__setVehicleCollectorState(nationID)
            formatBlueprintBalance(ts)
            updateEarlyAccessNodes(ts, self.__earlyAccessController)
            self.__updateEarlyAccessShown()
            self.__customHints.setCurrentNation(nationID)

    @args2params(str)
    def __goToVehicleCollection(self, nationName):
        self.__stopTopOfTheTreeSounds()
        nationID = nations.INDICES.get(nationName, nations.NONE_INDEX)
        showCollectibleVehicles(nationID)

    @args2params(int)
    def __goToBlueprintView(self, vehicleCD):
        self.__stopTopOfTheTreeSounds()
        showBlueprintView(vehicleCD, self.__createExitEvent())

    @args2params(int)
    def __unlockVehicle(self, vehicleCD):
        node = self.__treeData.getNodeByItemCD(vehicleCD)
        unlockProps = node.getUnlockProps() if node is not None else None
        if unlockProps is not None:
            ItemsActionsFactory.doAction(ItemsActionsFactory.UNLOCK_ITEM, vehicleCD, unlockProps)
        return

    @args2params(int)
    def __buyVehicle(self, vehicleCD):
        vehicle = self.__itemsCache.items.getItemByCD(vehicleCD)
        if canBuyGoldForVehicleThroughWeb(vehicle):
            showVehicleBuyDialog(vehicle)
        else:
            ItemsActionsFactory.doAction(ItemsActionsFactory.BUY_VEHICLE, vehicleCD)

    @args2params(int)
    def __addVehicleToCompare(self, vehicleCD):
        self.__cmpBasket.addVehicle(vehicleCD)

    @args2params(int)
    def __restoreVehicle(self, vehicleCD):
        ItemsActionsFactory.doAction(ItemsActionsFactory.BUY_VEHICLE, vehicleCD)

    @args2params(int)
    def __goToModulesTechTree(self, vehicleCD):
        self.soundManager.playInstantSound(Sounds.RESET)
        self.__stopTopOfTheTreeSounds()
        self.__customHints.markNationHints(SelectedNation.getIndex())
        showResearchView(vehicleCD, self.__createExitEvent())

    def __createExitEvent(self):
        return getTechTreeLoadEvent(SelectedNation.getName(), self.__blueprintMode)

    def __onClose(self):
        self.__stopTopOfTheTreeSounds()
        showHangar()

    @args2params(str, int)
    def __goToPremiumShop(self, nationName, level):
        self.__stopTopOfTheTreeSounds()
        params = {'nation': nationName,
         'level': level,
         'vehicleFilterByUrl': _VEHICLE_URL_FILTER_PARAM}
        showShop(url=getPremiumVehiclesUrl(), params=params)

    @args2params(bool)
    def __onBlueprintModeChanged(self, isEnabled):
        self.__blueprintMode = isEnabled
        if isEnabled:
            self.soundManager.playInstantSound(Sounds.BLUEPRINT_VIEW_ON_SOUND_ID)
            self.__playBlueprintPlusSound()
        else:
            self.soundManager.playInstantSound(Sounds.BLUEPRINT_VIEW_OFF_SOUND_ID)
        updateBlueprintsMode(self.viewModel, isEnabled, self.__lobbyContext.getServerSettings().blueprintsConfig.isBlueprintsAvailable())

    def __goToEarlyAccess(self):
        showEarlyAccessVehicleView(isFromTechTree=True)

    def __updateEarlyAccessShown(self):
        hasEarlyAccess = self.__earlyAccessController.isQuestActive() and not AccountSettings.getEarlyAccess(EarlyAccess.TREE_SEEN)
        self.viewModel.setIsEarlyAccessFirstTimeShown(hasEarlyAccess)
        if hasEarlyAccess and self.__earlyAccessController.getNationID() == SelectedNation.getIndex():
            AccountSettings.setEarlyAccess(EarlyAccess.TREE_SEEN, True)

    def __closePremiumPanel(self, _=None):
        self.viewModel.setClosePremiumPanelTrigger(time_utils.getCurrentTimestamp())

    def __setSettings(self):
        self.__treeData.load(SelectedNation.getIndex())
        with self.viewModel.transaction() as ts:
            settings = self.__treeData.getDisplaySettings()
            ts.settings.setRowsNumber(settings.rowsNumber)
            ts.settings.setColumnsNumber(settings.columnsNumber)
            ts.settings.setPremiumRowsNumber(settings.premiumRowsNumber)

    def __setVehicleCollectorState(self, nationID):
        isVehicleCollectorEnabled = self.__lobbyContext.getServerSettings().isCollectorVehicleEnabled()
        self.viewModel.setHasCollectibleVehicles(isVehicleCollectorEnabled and hasCollectibleVehicles(nationID))

    def __playBlueprintPlusSound(self):
        if self.__blueprintMode and findFirst(lambda node: node.getBpfProps() and node.getBpfProps().canConvert, self.__treeData.getNodes()) is not None:
            self.soundManager.playInstantSound(Sounds.BLUEPRINT_VIEW_PLUS_SOUND_ID)
        return

    def __stopTopOfTheTreeSounds(self):
        self.soundManager.playInstantSound(Sounds.TOP_OF_THE_TREE_ANIMATION_STOP_ANIMATION)


class VehicleTechTreeInvalidator(IPage):
    __slots__ = ('__viewRef', '__dataProvider')
    __cmpBasket = dependency.descriptor(IVehicleComparisonBasket)
    __itemsCache = dependency.descriptor(IItemsCache)
    __techTreeEventsListener = dependency.descriptor(ITechTreeEventsListener)
    __lobbyContext = dependency.descriptor(ILobbyContext)

    def __init__(self, view, dataProvider):
        self.__viewRef = weakref.ref(view)
        self.__dataProvider = dataProvider

    @property
    def viewModel(self):
        return self.__viewRef().getViewModel()

    def redraw(self):
        self.__viewRef().update()

    def invalidateBlueprints(self, blueprints):
        if not blueprints:
            return
        if all((value is None for value in blueprints.values())):
            result = self.__dataProvider.invalidateBlueprints(blueprints)
            if result:
                with self.viewModel.transaction() as ts:
                    self.__fillNewNodeStates(ts, result)
                    self.__clearCanConvertBlueprintFragments(ts, result)
        else:
            self.__updateBlueprints()

    def __updateBlueprints(self):
        self.__dataProvider.load(SelectedNation.getIndex())
        with self.viewModel.transaction() as ts:
            formatBlueprintBalance(ts)
            nodesArray = ts.getNodes()
            for nodeModel in nodesArray:
                node = self.__dataProvider.getNodeByItemCD(nodeModel.getId())
                bpfProps = node.getBpfProps()
                nodeModel.setBlueprintCanConvert(bpfProps.canConvert if bpfProps is not None else 0)

            nodesArray.invalidate()
        return

    def __clearCanConvertBlueprintFragments(self, model, result):
        if result:
            nodesArray = model.getNodes()
            for id, _ in result:
                idx = self.__dataProvider.getNodeIndex(id)
                nodeModel = nodesArray[idx]
                nodeModel.setBlueprintCanConvert(False)

            nodesArray.invalidate()

    def invalidateBlueprintMode(self, isEnabled):
        self.redraw()

    def invalidateCredits(self):
        result = self.__dataProvider.invalidateCredits()
        with self.viewModel.transaction() as ts:
            fillStateResults = self.__fillNewNodeStates(ts, result)
            updateVehiclePrices(ts, fillStateResults)

    def invalidateGold(self):
        result = []
        result.extend(self.__dataProvider.invalidateGold())
        result.extend(self.__dataProvider.invalidateCredits())
        result.extend(self.__dataProvider.invalidateFreeXP())
        with self.viewModel.transaction() as ts:
            fillStateResults = self.__fillNewNodeStates(ts, result)
            updateVehiclePrices(ts, fillStateResults)

    def invalidateFreeXP(self):
        result = self.__dataProvider.invalidateFreeXP()
        with self.viewModel.transaction() as ts:
            self.__fillNewNodeStates(ts, result)

    def invalidateElites(self, elites):
        result = self.__dataProvider.invalidateElites(elites)
        with self.viewModel.transaction() as ts:
            fillStateResults = self.__fillNewNodeStates(ts, result)
            updateVehiclesInfo(ts, fillStateResults)

    def invalidateVTypeXP(self, xps):
        result = self.__dataProvider.invalidateVTypeXP()
        with self.viewModel.transaction() as ts:
            fillStateResults = self.__fillNewNodeStates(ts, result)
            updateVehiclesUnlocks(ts, fillStateResults)

    def invalidateUnlocks(self, unlocks):
        next2Unlock, unlocked, prevUnlocked = self.__dataProvider.invalidateUnlocks(unlocks)
        result = []
        next2Unlock = [ (item[0], item[1]) for item in next2Unlock ]
        result.extend(next2Unlock)
        result.extend(unlocked)
        result.extend(prevUnlocked)
        if result:
            with self.viewModel.transaction() as ts:
                fillStateResults = self.__fillNewNodeStates(ts, result)
                updateVehiclesUnlocks(ts, fillStateResults)
                self.__clearCanConvertBlueprintFragments(ts, result)

    def invalidateInventory(self, data):
        result = self.__dataProvider.invalidateInventory(data)
        with self.viewModel.transaction() as ts:
            fillStateResults = self.__fillNewNodeStates(ts, result)
            updateVehiclesInfo(ts, fillStateResults)

    def invalidateVehCompare(self):
        with self.viewModel.transaction() as ts:
            self.viewModel.setIsCmpAvailable(self.__cmpBasket.isEnabled())
            updateVehiclesCmpStatus(ts, self.__cmpBasket, self.__itemsCache)

    def invalidateVehicleCollectorState(self):
        isVehicleCollectorEnabled = self.__lobbyContext.getServerSettings().isCollectorVehicleEnabled()
        self.viewModel.setHasCollectibleVehicles(isVehicleCollectorEnabled and hasCollectibleVehicles(SelectedNation.getIndex()))

    def invalidatePrbState(self):
        result = self.__dataProvider.invalidatePrbState()
        with self.viewModel.transaction() as ts:
            self.__fillNewNodeStates(ts, result)

    def invalidateDiscounts(self, data):
        if self.__dataProvider.invalidateDiscounts(data):
            result = self.__dataProvider.invalidateCredits()
            result.extend(self.__dataProvider.invalidateGold())
            with self.viewModel.transaction() as ts:
                fillStateResults = self.__fillNewNodeStates(ts, result)
                updateVehiclePrices(ts, fillStateResults)

    def invalidateVehLocks(self, locks):
        if self.__dataProvider.invalidateLocks(locks):
            self.redraw()

    def invalidateWalletStatus(self, status):
        self.redraw()

    def invalidateRestore(self, vehicles):
        if self.__dataProvider.invalidateRestore(vehicles):
            self.redraw()

    def invalidateEarlyAccess(self):
        self.__viewRef().updateEarlyAccessState()

    def invalidateEventsData(self):
        fillNationTechTreeModel(self.viewModel, self.__techTreeEventsListener, self.__dataProvider.getAvailableNations())

    def invalidateParagonsAnouncement(self):
        self.__viewRef().getViewModel().setIsParagonsEnabled(self.__techTreeEventsListener.isParagonsAnnounceActive())

    def clearSelectedNation(self):
        SelectedNation.clear()

    def __fillNewNodeStates(self, model, result):
        nodes = model.getNodes()
        diffIds = {}
        for nodeId, newState in result:
            idx = self.__dataProvider.getNodeIndex(nodeId)
            node = nodes[idx]
            node.setState(newState)
            diffIds[nodeId] = self.__dataProvider.getNodeByIndex(idx)

        nodes.invalidate()
        return diffIds
