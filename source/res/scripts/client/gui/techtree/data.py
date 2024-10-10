# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/techtree/data.py
import logging
import typing
from gui.impl.gen.view_models.views.lobby.techtree.node_state_flags import NodeStateFlags
from gui.techtree.dumpers import _BaseDumper
from gui.techtree.settings import NODE_STATE
from gui.techtree.settings import UnlockStats
from gui.techtree.techtree_dp import g_techTreeDP
from gui.techtree.selected_nation import SelectedNation
from gui.limited_ui.lui_rules_storage import LuiRules
from gui.shop import canBuyGoldForItemThroughWeb
from gui.prb_control import prbDispatcherProperty
from gui.shared.economics import getGUIPrice
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.utils.requesters import REQ_CRITERIA
from helpers import dependency
from items import getTypeOfCompactDescr as getTypeOfCD, vehicles as vehicles_core
from skeletons.gui.game_control import ITradeInController, IBootcampController, ILimitedUIController
from skeletons.gui.shared import IItemsCache
from skeletons.gui.lobby_context import ILobbyContext
from soft_exception import SoftException
_logger = logging.getLogger(__name__)

@dependency.replace_none_kwargs(lobbyContext=ILobbyContext)
def _checkCollectibleEnabled(state, lobbyContext=None):
    if lobbyContext.getServerSettings().isCollectorVehicleEnabled():
        state = NODE_STATE.removeIfHas(state, NodeStateFlags.PURCHASE_DISABLED)
    else:
        state = NODE_STATE.addIfNot(state, NodeStateFlags.PURCHASE_DISABLED)
    return state


class _ItemsData(object):
    tradeIn = dependency.descriptor(ITradeInController)
    bootcamp = dependency.descriptor(IBootcampController)
    limitedUIController = dependency.descriptor(ILimitedUIController)

    @dependency.replace_none_kwargs(itemsCache=IItemsCache)
    def __init__(self, dumper, itemsCache=None):
        super(_ItemsData, self).__init__()
        if dumper is not None and isinstance(dumper, _BaseDumper):
            self._dumper = dumper
        else:
            raise SoftException('Dumper is invalid.')
        self._nodes = []
        self._nodesIdx = {}
        self._items = itemsCache.items
        self._stats = itemsCache.items.stats
        self._wereInBattle = self._getNodesWereInBattle()
        self._hideTechTreeEvent = not self.limitedUIController.isRuleCompleted(LuiRules.TECH_TREE_EVENTS)
        return

    def __del__(self):
        _logger.debug('Data deleted: %s', self)

    @prbDispatcherProperty
    def prbDispatcher(self):
        return None

    def clear(self, full=False):
        while self._nodes:
            self._nodes.pop().clear()

        self._nodesIdx.clear()
        if full:
            self._items = None
            self._stats = None
            self._wereInBattle.clear()
            if self._dumper is not None:
                self._dumper.clear(full=True)
                self._dumper = None
        return

    def getNodes(self):
        for node in self._nodes:
            yield node

    def getItem(self, itemCD):
        return self._items.getItemByCD(itemCD)

    def getRootItem(self):
        raise NotImplementedError('Must be overridden in subclass')

    def getNodeByItemCD(self, itemCD):
        nodeIdx = self._nodesIdx[itemCD] if self._nodesIdx is not None else None
        return self._nodes[nodeIdx] if self._nodes is not None and nodeIdx is not None else None

    def getNodeIndex(self, nodeId):
        return self._nodesIdx[nodeId] if self._nodesIdx is not None else None

    def getNodeByIndex(self, idx):
        return self._nodes[idx] if self._nodes is not None and idx is not None else None

    def getInventoryVehicles(self):
        nodeCDs = [ node.getNodeCD() for node in self._getNodesToInvalidate() ]
        _logger.debug('getInventoryVehicles: %r', nodeCDs)
        inventoryVehicles = self._items.getVehicles(REQ_CRITERIA.INVENTORY | REQ_CRITERIA.IN_CD_LIST(nodeCDs))
        return {item.invID:item for item in inventoryVehicles.itervalues()}

    def getVehicleCDs(self):
        return [ i.getNodeCD() for i in self._getNodesToInvalidate() if getTypeOfCD(i.getNodeCD()) == GUI_ITEM_TYPE.VEHICLE ]

    def getUnlockStats(self):
        return UnlockStats(self._stats.unlocks, self._stats.vehiclesXPs, self._stats.freeXP)

    def dump(self):
        return self._dumper.dump(self)

    def invalidateCredits(self):
        return self._invalidateMoney([ item for item in self._getNodesToInvalidate() if NODE_STATE.isBuyForCredits(item.getState()) ])

    def invalidateGold(self):
        return self._invalidateMoney([ item for item in self._getNodesToInvalidate() if NODE_STATE.isBuyForGold(item.getState()) ])

    def invalidateFreeXP(self):
        return self._invalidateXP([ item for item in self._getNodesToInvalidate() if NodeStateFlags.NEXT_2_UNLOCK & item.getState() ])

    def invalidateVTypeXP(self):
        return self._invalidateXP([ item for item in self._getNodesToInvalidate() if NodeStateFlags.NEXT_2_UNLOCK & item.getState() ])

    def invalidateElites(self, elites):
        return self._addStateFlag([ node for node in self._getNodesToInvalidate() if node.getNodeCD() in elites ], NodeStateFlags.ELITE)

    def invalidateInventory(self, nodeCDs):
        result = []
        nodes_ = (node for node in self._getNodesToInvalidate() if node.getNodeCD() in nodeCDs)
        for node in nodes_:
            nodeCD = node.getNodeCD()
            state = node.getState()
            item = self.getItem(nodeCD)
            if item.isInInventory:
                state = NODE_STATE.removeIfHas(state, NodeStateFlags.ENOUGH_MONEY)
                state = NODE_STATE.addIfNot(state, NodeStateFlags.IN_INVENTORY)
                state = NODE_STATE.removeIfHas(state, NodeStateFlags.VEHICLE_IN_RENT)
                state = NODE_STATE.removeIfHas(state, NodeStateFlags.LAST_2_BUY)
                if item.isRented and not item.isPremiumIGR:
                    state = self._checkExpiredRent(state, item)
                    state = self._checkMoney(state, nodeCD)
                if self._canSell(nodeCD):
                    state = NODE_STATE.addIfNot(state, NodeStateFlags.CAN_SELL)
                else:
                    state = NODE_STATE.removeIfHas(state, NodeStateFlags.CAN_SELL)
            else:
                state = NODE_STATE.removeIfHas(state, NodeStateFlags.IN_INVENTORY)
                state = NODE_STATE.removeIfHas(state, NodeStateFlags.VEHICLE_IN_RENT)
                state = NODE_STATE.removeIfHas(state, NodeStateFlags.CAN_SELL)
                state = NODE_STATE.removeIfHas(state, NodeStateFlags.SELECTED)
                state = NODE_STATE.changeLast2Buy(state, self._needLast2BuyFlag(nodeCD))
                state = self._checkMoney(state, nodeCD)
            state = self._checkBuyingActionState(state, item)
            state = self._checkRestoreState(state, item)
            state = self._checkRentableState(state, item)
            state = self._checkTradeInState(state, item)
            node.setState(state)
            result.append((nodeCD, state))

        return result

    def invalidateLocks(self, locks):
        result = False
        inventory = self.getInventoryVehicles()
        for invID, _ in locks.iteritems():
            if invID in inventory.keys():
                result = True
                break

        return result

    def invalidateBlueprints(self, blueprints):
        result = []
        allNodes = self._getNodesToInvalidate()
        for node in allNodes:
            nodeCD = node.getNodeCD()
            if nodeCD not in blueprints:
                continue
            state = node.getState()
            if blueprints[nodeCD]:
                state = NODE_STATE.addIfNot(state, NodeStateFlags.BLUEPRINT)
            result.append((nodeCD, state))

        return result

    def invalidatePrbState(self):
        nodes_ = self._getNodesToInvalidate()
        canChanged = self._isVehicleCanBeChanged()
        result = []
        for node in nodes_:
            nodeCD = node.getNodeCD()
            state = node.getState()
            if getTypeOfCD(nodeCD) == GUI_ITEM_TYPE.VEHICLE:
                item = self.getItem(nodeCD)
                if not item.isInInventory:
                    continue
                if canChanged:
                    state = NODE_STATE.addIfNot(state, NodeStateFlags.VEHICLE_CAN_BE_CHANGED)
                else:
                    state = NODE_STATE.removeIfHas(state, NodeStateFlags.VEHICLE_CAN_BE_CHANGED)
                if state > -1:
                    node.setState(state)
                    result.append((nodeCD, state))

        return result

    def invalidateDiscounts(self, discountTargets):
        nodes_ = self._getNodesToInvalidate()
        for node in nodes_:
            if node.getNodeCD() in discountTargets:
                return True

        return False

    def invalidateRestore(self, vehicles):
        for intCD in vehicles:
            _, nationID, _ = vehicles_core.parseIntCompactDescr(intCD)
            if nationID == SelectedNation.getIndex():
                return True

        return False

    def isHasVehicles(self):
        return bool(len(self.getInventoryVehicles()) > 0)

    def _isVehicleCanBeChanged(self):
        vehicleCanBeChanged = False
        if self.prbDispatcher is not None:
            permission = self.prbDispatcher.getGUIPermissions()
            if permission is not None:
                vehicleCanBeChanged = permission.canChangeVehicle()
        return vehicleCanBeChanged

    def _checkMoney(self, state, nodeCD):
        state = NODE_STATE.removeIfHas(state, NodeStateFlags.ENOUGH_MONEY)
        if canBuyGoldForItemThroughWeb(nodeCD) or self._mayObtainForMoney(nodeCD):
            state |= NodeStateFlags.ENOUGH_MONEY
        return state

    def _checkRestoreState(self, state, item):
        state = NODE_STATE.removeIfHas(state, NodeStateFlags.RESTORE_AVAILABLE)
        money = self._stats.money
        exchangeRate = self._items.shop.exchangeRate
        mayRent, _ = item.mayRent(money)
        if item.isRestoreAvailable():
            if item.mayRestoreWithExchange(money, exchangeRate) or not mayRent:
                state = NODE_STATE.addIfNot(state, NodeStateFlags.RESTORE_AVAILABLE)
        return state

    def _checkExpiredRent(self, state, item):
        state = NODE_STATE.addIfNot(state, NodeStateFlags.VEHICLE_IN_RENT)
        if item.rentalIsOver:
            state = NODE_STATE.removeIfHas(state, NodeStateFlags.IN_INVENTORY)
            state = NODE_STATE.removeIfHas(state, NodeStateFlags.VEHICLE_IN_RENT)
            state |= NodeStateFlags.VEHICLE_RENTAL_IS_OVER
        return state

    def _checkRentableState(self, state, item):
        state = NODE_STATE.removeIfHas(state, NodeStateFlags.RENT_AVAILABLE)
        if item.isRentable and item.isRentAvailable and (not item.isRented or item.rentalIsOver):
            state = NODE_STATE.addIfNot(state, NodeStateFlags.RENT_AVAILABLE)
        return state

    def _checkTradeInState(self, state, item):
        if item.itemTypeID != GUI_ITEM_TYPE.VEHICLE:
            return state
        state = NODE_STATE.removeIfHas(state, NodeStateFlags.CAN_TRADE_IN)
        if item.canTradeIn:
            state = NODE_STATE.addIfNot(state, NodeStateFlags.CAN_TRADE_IN)
        state = NODE_STATE.removeIfHas(state, NodeStateFlags.CAN_TRADE_OFF)
        if item.canTradeOff:
            state = NODE_STATE.addIfNot(state, NodeStateFlags.CAN_TRADE_OFF)
        return state

    def _checkBuyingActionState(self, state, item):
        state = NODE_STATE.removeIfHas(state, NodeStateFlags.ACTION)
        if item.buyPrices.itemPrice.isActionPrice() and not item.isRestorePossible():
            state = NODE_STATE.addIfNot(state, NodeStateFlags.ACTION)
        return state

    def _checkCollectibleActionState(self, state, item):
        state = NODE_STATE.removeIfHas(state, NodeStateFlags.COLLECTIBLE_ACTION)
        if item.buyPrices.itemPrice.isActionPrice():
            state = NODE_STATE.addIfNot(state, NodeStateFlags.COLLECTIBLE_ACTION)
        return state

    def _checkTechTreeEvents(self, state, guiItem, unlockProps):
        if g_techTreeDP.techTreeEventsListener.hasActiveAction(guiItem.intCD) and guiItem.itemTypeID == GUI_ITEM_TYPE.VEHICLE:
            state |= NodeStateFlags.HAS_TECH_TREE_EVENT
            state = NODE_STATE.removeIfHas(state, NodeStateFlags.ACTION)
            noUnlockDiscount = not unlockProps or not unlockProps.discount
            if noUnlockDiscount and guiItem.buyPrices.itemPrice.isActionPrice() and not guiItem.isRestorePossible():
                state = NODE_STATE.add(state, NodeStateFlags.ACTION)
        return state

    def _checkEarlyAccessState(self, state, vehicleItem):
        state = NODE_STATE.removeIfHas(state, NodeStateFlags.EARLY_ACCESS)
        if vehicleItem.isEarlyAccess:
            state = NODE_STATE.addIfNot(state, NodeStateFlags.EARLY_ACCESS)
        return state

    def _addNode(self, nodeCD, node):
        index = len(self._nodes)
        self._nodesIdx[nodeCD] = index
        self._nodes.append(node)
        return index

    def _getNodesWereInBattle(self):
        accDossier = self._items.getAccountDossier(None)
        return set(accDossier.getTotalStats().getVehicles().keys()) if accDossier else set()

    def _getNodesToInvalidate(self):
        return [ node for node in self._nodes if not NODE_STATE.isAnnouncement(node.getState()) ]

    def _addStateFlag(self, nodes_, stateFlag, exclude=None):
        result = []
        for node in nodes_:
            nodeCD = node.getNodeCD()
            state = node.getState()
            if not state & stateFlag:
                state |= stateFlag
                if exclude is not None and state & exclude:
                    state ^= exclude
                node.setState(state)
                result.append((nodeCD, state))

        return result

    def _change2Unlocked(self, node):
        state = NODE_STATE.change2Unlocked(node.getState())
        if state < 0:
            return node.getState()
        node.setState(state)
        if canBuyGoldForItemThroughWeb(node.getNodeCD()) or self._mayObtainForMoney(node.getNodeCD()):
            state = NODE_STATE.add(state, NodeStateFlags.ENOUGH_MONEY)
        else:
            state = NODE_STATE.remove(state, NodeStateFlags.ENOUGH_MONEY)
        if state < 0:
            return node.getState()
        if not node.isActionPrice():
            state = NODE_STATE.removeIfHas(state, NodeStateFlags.ACTION)
        else:
            state = NODE_STATE.addIfNot(state, NodeStateFlags.ACTION)
        state = NODE_STATE.addIfNot(state, NodeStateFlags.BLUEPRINT)
        node.setState(state)
        return state

    def _mayObtainForMoney(self, nodeCD):
        item = self.getItem(nodeCD)
        money = self._stats.money
        if item.itemTypeID == GUI_ITEM_TYPE.VEHICLE:
            money = self.tradeIn.addTradeInPriceIfNeeded(item, money)
        return item.mayObtainWithMoneyExchange(money, self._items.shop.exchangeRate)

    def _canSell(self, nodeCD):
        raise NotImplementedError

    def _needLast2BuyFlag(self, nodeCD):
        raise NotImplementedError

    def _isLastUnlocked(self, nodeCD):
        if self.getItem(nodeCD).isPremium:
            return False
        nextLevels = g_techTreeDP.getNextLevel(nodeCD)
        isAvailable = lambda self, nextCD: self.getItem(nextCD).isUnlocked or g_techTreeDP.isVehicleAvailableToUnlock(nextCD)[0]
        isNextUnavailable = any((not isAvailable(self, nextCD) for nextCD in nextLevels))
        return isNextUnavailable or not nextLevels

    def _invalidateMoney(self, nodes_):
        result = []
        for node in nodes_:
            state = node.getState()
            nodeID = node.getNodeCD()
            node.setGuiPrice(getGUIPrice(self.getItem(nodeID), self._stats.money, self._items.shop.exchangeRate))
            if canBuyGoldForItemThroughWeb(nodeID) or self._mayObtainForMoney(nodeID):
                state = NODE_STATE.add(state, NodeStateFlags.ENOUGH_MONEY)
            else:
                state = NODE_STATE.remove(state, NodeStateFlags.ENOUGH_MONEY)
            if state > -1:
                node.setState(state)
                result.append((nodeID, state))

        return result

    def _invalidateXP(self, nodes_):
        result = []
        stats = self.getUnlockStats()
        for node in nodes_:
            state = node.getState()
            props = node.getUnlockProps()
            if g_techTreeDP.getAllVehiclePossibleXP(props.parentID, stats) >= props.xpCost:
                state = NODE_STATE.add(state, NodeStateFlags.ENOUGH_XP)
            else:
                state = NODE_STATE.remove(state, NodeStateFlags.ENOUGH_XP)
            if state > -1:
                node.setState(state)
                result.append((node.getNodeCD(), state))

        return result

    def _getBlueprintsProps(self, vehicleCD, level):
        return self._items.blueprints.getBlueprintData(vehicleCD, level)
