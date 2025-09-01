# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/tech_tree/tech_tree_view.py
import json
from collections import namedtuple
from logging import getLogger
import typing
import Event
import nations
from account_helpers import AccountSettings
from account_helpers.AccountSettings import NATIONS_VISITED
from frameworks.state_machine import BaseStateObserver, visitor
from frameworks.wulf import ViewSettings, WindowFlags
from frameworks.wulf.view.array import fillStringsArray
from gui.Scaleform.daapi.view.lobby.store.browser.shop_helpers import getPremiumVehiclesUrl
from gui.Scaleform.daapi.view.lobby.techtree import dumpers
from gui.Scaleform.daapi.view.lobby.techtree.data import NationTreeData
from gui.Scaleform.daapi.view.lobby.techtree.listeners import TTListenerDecorator
from gui.Scaleform.daapi.view.lobby.techtree.settings import NODE_STATE
from gui.Scaleform.daapi.view.lobby.techtree.settings import SelectedNation
from gui.Scaleform.daapi.view.lobby.techtree.sound_constants import TECHTREE_SOUND_SPACE
from gui.Scaleform.daapi.view.lobby.techtree.states import TechtreeState
from gui.Scaleform.daapi.view.lobby.techtree.techtree_dp import g_techTreeDP
from gui.Scaleform.genConsts.NODE_STATE_FLAGS import NODE_STATE_FLAGS
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.Scaleform.lobby_entry import getLobbyStateMachine
from gui.impl.backport import BackportContextMenuWindow, createContextMenuData, BackportTooltipWindow
from gui.impl.backport import createTooltipData
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.tech_tree.tech_tree_view_model import TechTreeViewModel, NationEnum
from gui.impl.gui_decorators import args2params
from gui.impl.pub import ViewImpl, WindowImpl
from gui.lobby_state_machine.routable_view import IRoutableView
from gui.lobby_state_machine.router import SubstateRouter
from gui.shared import event_dispatcher as shared_events
from gui.shared.event_dispatcher import showVehicleHubModules
from gui.shared.utils.vehicle_collector_helper import hasCollectibleVehicles
from gui.sounds.ambients import LobbySubViewEnv
from helpers import dependency
from shared_utils import first
from skeletons.gui.game_control import IVehicleComparisonBasket
from skeletons.gui.lobby_context import ILobbyContext
if typing.TYPE_CHECKING:
    from typing import Tuple, List, Set, Dict, Optional
    from gui.Scaleform.daapi.view.lobby.techtree.settings import UnlockProps
    from gui.Scaleform.daapi.view.lobby.techtree.nodes import RealNode
    from gui.lobby_state_machine.lobby_state_machine import LobbyStateMachine
    from frameworks.state_machine import State
    from gui.shared.events import NavigationEvent
_logger = getLogger(__name__)
_VEHICLE_URL_FILTER_PARAM = 1
_GUINode = namedtuple('_GUINode', ('id', 'state', 'unlockProps'))

class _NationTreeViewDumper(dumpers._BaseDumper):

    def __init__(self, cache=None):
        if cache is None:
            cache = {'techTreeNodes': {},
             'nodeOverrides': {}}
        super(_NationTreeViewDumper, self).__init__(cache)
        return

    def clear(self, full=False):
        self._cache['techTreeNodes'].clear()
        self._cache['nodeOverrides'].clear()
        if full:
            self._vClassInfo.clear()

    def dump(self, data):
        self.clear()
        nodeRows = {node.getNodeCD():node.getDisplayInfo()['row'] for node in data.getNodes()}
        techTreeNodes = self._cache['techTreeNodes']
        for node in data.getNodes():
            techTreeNodes[node.getNodeCD()] = self._getTechTreeNodes(node, nodeRows)

        nodeOverrides = self._cache['nodeOverrides']
        for node in data.getNodes():
            nodeOverrides[node.getNodeCD()] = self._getNodeOverrides(node)

        return self._cache

    def _getTechTreeNodes(self, node, nodeRows):
        displayInfo = node.getDisplayInfo()
        currentNodeRow = displayInfo['row']
        childIds = [ inPin['childID'] for line in displayInfo['lines'] for inPin in line['inPins'] ]
        childBranchOrders = [ nodeRows[childId] - currentNodeRow for childId in childIds ]
        nodeTags = node.getTags()
        nodeState = node.getState()
        return {'id': node.getNodeCD(),
         'name': node.getShortUserName(),
         'techName': node.getItem().name,
         'nation': nations.NAMES[node.getNationID()],
         'type': self._vClassInfo.getInfoByTags(nodeTags)['name'],
         'level': node.getLevel(),
         'orderPriority': currentNodeRow,
         'childIds': childIds,
         'childBranchOrders': childBranchOrders,
         'isPremium': NODE_STATE.isPremium(nodeState)}

    def _getNodeOverrides(self, node):
        nodeState = node.getState()
        nodeUnlockProps = node.getUnlockProps()
        nodePrice = node.getItem().getBuyPrice()
        nodePriceCurrency = nodePrice.getCurrency()
        nodeCompareData = node.getCompareData()
        return {'id': node.getNodeCD(),
         'isResearched': NODE_STATE.isUnlocked(nodeState),
         'readyForResearch': NODE_STATE.isNext2Unlock(nodeState),
         'hasEnoughXp': bool(nodeState & NODE_STATE_FLAGS.ENOUGH_XP),
         'requiredXp': nodeUnlockProps.xpCost,
         'isDiscountedXp': nodeUnlockProps.xpCost < nodeUnlockProps.xpFullCost,
         'earnedXp': node.getEarnedXP(),
         'isElite': bool(nodeState & NODE_STATE_FLAGS.ELITE),
         'isInInventory': NODE_STATE.inInventory(nodeState),
         'hasEnoughCurrency': bool(nodeState & NODE_STATE_FLAGS.ENOUGH_MONEY),
         'highlightedForPurchase': bool(nodeState & NODE_STATE_FLAGS.LAST_2_BUY),
         'priceAmount': nodePrice.price.get(nodePriceCurrency),
         'priceCurrency': nodePriceCurrency,
         'isDiscountedPrice': nodePrice.isActionPrice(),
         'readyForRecovery': bool(nodeState & NODE_STATE_FLAGS.RESTORE_AVAILABLE),
         'isRented': bool(nodeState & NODE_STATE_FLAGS.VEHICLE_IN_RENT),
         'readyForTradeIn': bool(nodeState & NODE_STATE_FLAGS.CAN_TRADE_IN),
         'readyForComparison': nodeCompareData.get('modeAvailable', False) and not nodeCompareData.get('cmpBasketFull', False)}


class _TechTreeStatesObserver(BaseStateObserver):

    def __init__(self):
        super(_TechTreeStatesObserver, self).__init__()
        self.onSwitchNation = Event.Event()

    def clear(self):
        super(_TechTreeStatesObserver, self).clear()
        self.onSwitchNation.clear()

    def isObservingState(self, state):
        lsm = state.getMachine()
        return visitor.isDescendantOf(state, lsm.getStateByCls(TechtreeState))

    def onEnterState(self, state, event):
        if event is None:
            return
        else:
            self.onSwitchNation(event.params)
            return


def _getVehCDs(invalidationResult):
    return {r[0] for r in invalidationResult}


class TechTreeView(ViewImpl, IRoutableView):
    __lobbyContext = dependency.descriptor(ILobbyContext)
    __cmpBasket = dependency.descriptor(IVehicleComparisonBasket)
    __sound_env__ = LobbySubViewEnv
    _COMMON_SOUND_SPACE = TECHTREE_SOUND_SPACE

    def __init__(self, layoutID, ctx=None):
        self.__ctx = ctx
        self.__nationTreeData = NationTreeData(_NationTreeViewDumper())
        settings = ViewSettings(layoutID)
        settings.model = TechTreeViewModel()
        self.__techTreeStatesObserver = _TechTreeStatesObserver()
        self.__listener = TTListenerDecorator()
        self.__router = None
        super(TechTreeView, self).__init__(settings)
        return

    def _onLoading(self, *args, **kwargs):
        super(TechTreeView, self)._onLoading(*args, **kwargs)
        self.__onInitNation(self.__ctx)
        self.__listener.startListen(self)

    def _onLoaded(self, *args, **kwargs):
        lsm = getLobbyStateMachine()
        lsm.connect(self.__techTreeStatesObserver)
        self.__router = SubstateRouter(lsm, self, lsm.getStateByCls(TechtreeState))
        self.__router.init()

    def _finalize(self):
        super(TechTreeView, self)._finalize()
        self.__listener.stopListen()
        self.__listener = None
        lsm = getLobbyStateMachine()
        lsm.disconnect(self.__techTreeStatesObserver)
        self.__techTreeStatesObserver = None
        self.__router.fini()
        self.__router = None
        return

    @property
    def viewModel(self):
        return super(TechTreeView, self).getViewModel()

    def getRouterModel(self):
        return self.getViewModel().router

    def redraw(self):
        self.__fullUpdateOfViewModel()

    def createToolTip(self, event):
        tooltipData = None
        if event.contentID == R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent():
            tooltipId = event.getArgument('tooltipId')
            if tooltipId == TOOLTIPS_CONSTANTS.TECHTREE_VEHICLE:
                vehCD = event.getArgument('vehCD', 0)
                vehCD = int(vehCD)
                if not vehCD:
                    return
                thisNode = self.__nationTreeData.getNodeByItemCD(vehCD)
                guiNode = _GUINode(vehCD, thisNode.getState(), thisNode.getUnlockProps())
                parentNodeCD = first(g_techTreeDP.getTopLevel(vehCD))
                if not parentNodeCD:
                    rootItem = self.__nationTreeData.getRootItem()
                    if rootItem:
                        parentNodeCD = rootItem.getNodeCD()
                    else:
                        parentNodeCD = 0
                tooltipData = createTooltipData(isSpecial=True, specialAlias=tooltipId, specialArgs=(guiNode, parentNodeCD))
            elif tooltipId == TOOLTIPS_CONSTANTS.VEHICLE_COLLECTOR_INFO:
                tooltipData = createTooltipData(isSpecial=True, specialAlias=tooltipId, specialArgs=(SelectedNation.getName(),))
            elif tooltipId == TOOLTIPS_CONSTANTS.TRADE_IN:
                vehCD = event.getArgument('vehCD', 0)
                vehCD = int(vehCD)
                if not vehCD:
                    return
                tooltipData = createTooltipData(isSpecial=True, specialAlias=tooltipId, specialArgs=(vehCD,))
        if tooltipData is not None:
            window = BackportTooltipWindow(tooltipData, self.getWindow())
            window.load()
            return window
        else:
            return super(TechTreeView, self).createToolTip(event)

    def createContextMenu(self, event):
        if event.contentID != R.aliases.common.contextMenu.Backport():
            return
        else:
            menuArgs = event.getArgument('menuArgs', None)
            args = json.loads(menuArgs)
            vehCD = args.get('vehCD')
            node = self.__nationTreeData.getNodeByItemCD(vehCD)
            if not node:
                _logger.warning("Couldn't find node by vehCD=%d", vehCD)
                return
            contextMenuArgs = {'vehCD': vehCD,
             'nodeState': node.getState(),
             'newCM': True}
            contextMenuData = createContextMenuData(event.getArgument('menuId'), contextMenuArgs)
            window = BackportContextMenuWindow(contextMenuData, self.getWindow())
            window.load()
            return window

    def _getEvents(self):
        events = ((self.__techTreeStatesObserver.onSwitchNation, self.__onSwitchNation),
         (self.viewModel.onOpenAboutVehicle, self.__onOpenAboutVehicle),
         (self.viewModel.onAddToCompare, self.__onAddToCompare),
         (self.viewModel.onOpenCollectableVehicles, self.__onOpenCollectableVehicles),
         (self.viewModel.onOpenPremiumShop, self.__onOpenPremiumShop))
        return events

    def __onInitNation(self, args):
        nation = args.get('nation', None)
        if nation is not None and nation in nations.INDICES:
            nationIdx = nations.INDICES[nation]
            SelectedNation.select(nationIdx)
        else:
            SelectedNation.byDefault()
        self.__fullUpdateOfViewModel()
        return

    @args2params(str)
    def __onSwitchNation(self, nation):
        if nation == SelectedNation.getName():
            return
        nationID = nations.INDICES[nation]
        SelectedNation.select(nationID)
        self.__fullUpdateOfViewModel()

    @args2params(int, str)
    def __onOpenAboutVehicle(self, vehCD, route):
        showVehicleHubModules(vehCD)

    @args2params(int)
    def __onAddToCompare(self, vehCD):
        self.__cmpBasket.addVehicle(vehCD)

    @args2params(str)
    def __onOpenCollectableVehicles(self, nation):
        nationID = nations.INDICES.get(nation, nations.NONE_INDEX)
        shared_events.showCollectibleVehicles(nationID)

    @args2params(str, int)
    def __onOpenPremiumShop(self, nation, level):
        params = {'nation': nation,
         'level': level,
         'vehicleFilterByUrl': _VEHICLE_URL_FILTER_PARAM}
        shared_events.showShop(url=getPremiumVehiclesUrl(), params=params)

    def __getCollectableVehiclesSate(self):
        isVehicleCollectorEnabled = self.__lobbyContext.getServerSettings().isCollectorVehicleEnabled()
        return isVehicleCollectorEnabled and hasCollectibleVehicles(SelectedNation.getIndex())

    def __fullUpdateOfViewModel(self):
        visitedNations = AccountSettings.getSettings(NATIONS_VISITED)
        self.__nationTreeData.load(SelectedNation.getIndex())
        nationTreeDump = self.__nationTreeData.dump()
        nation = SelectedNation.getName()
        nationIdx = SelectedNation.getIndex()
        with self.viewModel.transaction() as vm:
            vm.setSelectedNation(NationEnum(nation))
            vm.setCollectableVehiclesAvailable(self.__getCollectableVehiclesSate())
            vm.setFirstHighlightedLevel(g_techTreeDP.getDisplaySettings(nationIdx)['firstLevelToHighlight'])
            vm.setShowWelcomeAnimation(nationIdx not in visitedNations)
            fillStringsArray(g_techTreeDP.getAvailableNations(), vm.getAvailableNations())
            self.__fillTechTreeNodes(vm, nationTreeDump['techTreeNodes'])
            self.__fillNodeOverrides(vm, nationTreeDump['nodeOverrides'])
        visitedNations.add(nationIdx)
        AccountSettings.setSettings(NATIONS_VISITED, visitedNations)

    def __fillTechTreeNodes(self, vm, techTreeNodesDump):
        techTreeNodes = vm.getTechTreeNodes()
        techTreeNodes.clear()
        for vehId, vehData in techTreeNodesDump.iteritems():
            techTreeNodes.set(vehId, json.dumps(vehData))

    def __fillNodeOverrides(self, vm, nodeOverridesDump):
        nodeOverrides = vm.getNodeOverrides()
        nodeOverrides.clear()
        for vehId, vehData in nodeOverridesDump.iteritems():
            nodeOverrides.set(vehId, json.dumps(vehData))

    def __updateAllNodeOverrides(self):
        nationTreeDump = self.__nationTreeData.dump()
        with self.viewModel.transaction() as vm:
            self.__fillNodeOverrides(vm, nationTreeDump['nodeOverrides'])

    def __updateCollectableVehiclesState(self):
        with self.viewModel.transaction() as vm:
            vm.setCollectableVehiclesAvailable(self.__getCollectableVehiclesSate())

    def __updateNodeOverrides(self, nodesToUpdate):
        if not nodesToUpdate:
            return
        nodeOverridesDump = self.__nationTreeData.dump()['nodeOverrides']
        with self.viewModel.transaction() as vm:
            nodeOverrides = vm.getNodeOverrides()
            for vehId in nodesToUpdate:
                if vehId not in nodeOverrides:
                    _logger.error('Vehicle with id %d is not in node overrides model', vehId)
                    continue
                if vehId not in nodeOverridesDump:
                    _logger.error('Vehicle with id %d is not in node overrides dump', vehId)
                    continue
                nodeOverrides.set(vehId, json.dumps(nodeOverridesDump[vehId]))

    def __invalidateAllCurrencies(self):
        nodesToUpdate = set()
        nodesToUpdate |= _getVehCDs(self.__nationTreeData.invalidateGold())
        nodesToUpdate |= _getVehCDs(self.__nationTreeData.invalidateFreeXP())
        nodesToUpdate |= _getVehCDs(self.__nationTreeData.invalidateCredits())
        self.__updateNodeOverrides(nodesToUpdate)

    def invalidateBlueprintMode(self, isEnabled):
        pass

    def invalidateVehLocks(self, locks):
        if self.__nationTreeData.invalidateLocks(locks):
            self.__updateAllNodeOverrides()

    def invalidateVTypeXP(self, xps):
        nodesToUpdate = set()
        for vehCD, xp in xps.iteritems():
            node = self.__nationTreeData.getNodeByItemCD(vehCD)
            if node:
                node.setEarnedXP(xp)
                nodesToUpdate.add(vehCD)

        nodesToUpdate |= _getVehCDs(self.__nationTreeData.invalidateVTypeXP())
        nodesToUpdate |= _getVehCDs(self.__nationTreeData.invalidateXpCosts())
        self.__updateNodeOverrides(nodesToUpdate)

    def invalidateWalletStatus(self, status):
        self.__invalidateAllCurrencies()

    def invalidateRent(self, vehicles):
        pass

    def invalidateRestore(self, vehicles):
        if self.__nationTreeData.invalidateRestore(vehicles):
            self.__updateAllNodeOverrides()

    def invalidateBlueprints(self, blueprints):
        if not blueprints:
            return
        nodesToUpdate = _getVehCDs(self.__nationTreeData.invalidateBlueprints(blueprints))
        self.__updateNodeOverrides(nodesToUpdate)

    def invalidateVehicleCollectorState(self):
        self.__updateCollectableVehiclesState()

    def invalidateCredits(self):
        nodesToUpdate = _getVehCDs(self.__nationTreeData.invalidateCredits())
        self.__updateNodeOverrides(nodesToUpdate)

    def invalidateGold(self):
        self.__invalidateAllCurrencies()

    def invalidateFreeXP(self):
        nodesToUpdate = _getVehCDs(self.__nationTreeData.invalidateFreeXP())
        self.__updateNodeOverrides(nodesToUpdate)

    def invalidateElites(self, elites):
        nodesToUpdate = _getVehCDs(self.__nationTreeData.invalidateElites(elites))
        self.__updateNodeOverrides(nodesToUpdate)

    def invalidateUnlocks(self, unlocks):
        next2Unlock, unlocked, prevUnlocked = self.__nationTreeData.invalidateUnlocks(unlocks)
        nodesToUpdate = _getVehCDs(next2Unlock) | _getVehCDs(unlocked) | _getVehCDs(prevUnlocked)
        self.__updateNodeOverrides(nodesToUpdate)

    def invalidateInventory(self, data):
        nodesToUpdate = _getVehCDs(self.__nationTreeData.invalidateInventory(data))
        self.__updateNodeOverrides(nodesToUpdate)

    def invalidatePrbState(self):
        pass

    def invalidateDiscounts(self, data):
        if self.__nationTreeData.invalidateDiscounts(data):
            self.__invalidateAllCurrencies()
            self.__updateAllNodeOverrides()

    def invalidateVehCompare(self):
        self.__updateAllNodeOverrides()

    def invalidateVehPostProgression(self):
        pass

    def clearSelectedNation(self):
        SelectedNation.clear()


class TechTreeWindow(WindowImpl):

    def __init__(self, layer, **kwargs):
        self.__background_alpha__ = 1.0
        layoutID = R.views.mono.tech_tree.main()
        super(TechTreeWindow, self).__init__(WindowFlags.WINDOW, layer=layer, content=TechTreeView(layoutID, kwargs['ctx']))
