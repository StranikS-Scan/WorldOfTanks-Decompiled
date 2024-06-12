# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/techtree/data/nation_tree_data.py
import logging
from itertools import chain
from random import choice
from CurrentVehicle import g_currentVehicle
from gui.Scaleform.daapi.view.lobby.techtree import nodes
from gui.Scaleform.daapi.view.lobby.techtree.data.data import _ItemsData
from gui.Scaleform.daapi.view.lobby.techtree.data.research_items_data import ResearchItemsData
from gui.Scaleform.daapi.view.lobby.techtree.settings import NODE_STATE
from gui.Scaleform.daapi.view.lobby.techtree.techtree_dp import g_techTreeDP
from gui.Scaleform.genConsts.NODE_STATE_FLAGS import NODE_STATE_FLAGS
from gui.shop import canBuyGoldForItemThroughWeb
from gui.shared.economics import getGUIPrice
from gui.shared.gui_items import GUI_ITEM_TYPE
from items import getTypeOfCompactDescr as getTypeOfCD
_logger = logging.getLogger(__name__)

class NationTreeData(_ItemsData):

    def __init__(self, dumper):
        super(NationTreeData, self).__init__(dumper)
        self._scrollIndex = -1

    def clear(self, full=False):
        self._scrollIndex = -1
        super(NationTreeData, self).clear(full)

    def load(self, nationID, override=None):
        self.clear()
        g_techTreeDP.setOverride(override)
        g_techTreeDP.load()
        getItem = self.getItem
        selectedID = ResearchItemsData.getRootCD()
        unlockStats = self.getUnlockStats()
        for node, displayInfo in g_techTreeDP.getNationTreeIterator(nationID):
            nodeCD = node.nodeCD
            if node.isAnnouncement:
                self._addNode(nodeCD, self._makeAnnouncementNode(node, displayInfo))
            item = getItem(nodeCD)
            if item.isHidden:
                continue
            index = self._addNode(nodeCD, self._makeRealExposedNode(node, item, unlockStats, displayInfo))
            if nodeCD == selectedID:
                self._scrollIndex = index

        ResearchItemsData.clearRootCD()
        self._findSelectedNode(nationID)
        if self._scrollIndex < 0:
            self._findActionNode(nationID)

    def getRootItem(self):
        return self._nodes[0] if self._nodes else None

    def invalidateUnlocks(self, unlocks):
        next2Unlock = []
        unlocked = []
        prevUnlocked = []
        unlockStats = self.getUnlockStats()
        items = g_techTreeDP.getNext2UnlockByItems(unlocks, **unlockStats._asdict())
        if items:
            next2Unlock = [ (item[0], self._changeNext2Unlock(item[0], item[1], unlockStats), item[1].makeTuple()) for item in items.iteritems() ]
        filtered = [ unlock for unlock in unlocks if getTypeOfCD(unlock) == GUI_ITEM_TYPE.VEHICLE ]
        if filtered:
            unlocked = [ (item, self._change2UnlockedByCD(item)) for item in filtered ]
            parents = map(g_techTreeDP.getTopLevel, filtered)
            prevUnlocked = [ (item, self._changePreviouslyUnlockedByCD(item)) for item in chain(*parents) if not self.__isInInventory(item) ]
        return (next2Unlock, unlocked, prevUnlocked)

    def invalidateXpCosts(self):
        result = []
        nodes_ = [ item for item in self._getNodesToInvalidate() if NODE_STATE_FLAGS.NEXT_2_UNLOCK & item.getState() ]
        statsAsDict = self.getUnlockStats()._asdict()
        for node in nodes_:
            nodeCD = node.getNodeCD()
            props = node.getUnlockProps()
            _, newProps = g_techTreeDP.isNext2Unlock(nodeCD, **statsAsDict)
            if newProps.parentID != props.parentID:
                node.setUnlockProps(newProps)
                result.append((nodeCD, newProps))

        return result

    def _changeNext2Unlock(self, nodeCD, unlockProps, unlockStats):
        try:
            node = self._nodes[self._nodesIdx[nodeCD]]
        except KeyError as e:
            _logger.exception(e)
            return 0

        state = NODE_STATE.setNext2Unlock(node.getState())
        totalXP = g_techTreeDP.getAllVehiclePossibleXP(unlockProps.parentID, unlockStats)
        if totalXP >= unlockProps.xpCost:
            state = NODE_STATE.addIfNot(state, NODE_STATE_FLAGS.ENOUGH_XP)
        else:
            state = NODE_STATE.removeIfHas(state, NODE_STATE_FLAGS.ENOUGH_XP)
        if self.getItem(nodeCD).isElite:
            state = NODE_STATE.addIfNot(state, NODE_STATE_FLAGS.ELITE)
        state = NODE_STATE.addIfNot(state, NODE_STATE_FLAGS.BLUEPRINT)
        node.setState(state)
        node.setUnlockProps(unlockProps)
        return state

    def _change2Unlocked(self, node):
        state = super(NationTreeData, self)._change2Unlocked(node)
        return NODE_STATE.changeLast2Buy(state, self._isLastUnlocked(node.getNodeCD()))

    def _changePreviouslyUnlocked(self, node):
        state = node.getState()
        return NODE_STATE.changeLast2Buy(state, self._isLastUnlocked(node.getNodeCD()))

    def _change2UnlockedByCD(self, nodeCD):
        try:
            node = self._nodes[self._nodesIdx[nodeCD]]
        except KeyError as e:
            _logger.exception(e)
            return 0

        return self._change2Unlocked(node)

    def _changePreviouslyUnlockedByCD(self, nodeCD):
        try:
            node = self._nodes[self._nodesIdx[nodeCD]]
        except KeyError as e:
            _logger.exception(e)
            return 0

        return self._changePreviouslyUnlocked(node)

    def _makeRealExposedNode(self, node, guiItem, unlockStats, displayInfo):
        nodeCD = node.nodeCD
        earnedXP = unlockStats.getVehXP(nodeCD)
        state = NODE_STATE_FLAGS.LOCKED
        available, unlockProps = g_techTreeDP.isNext2Unlock(nodeCD, level=guiItem.level, **unlockStats._asdict())
        if guiItem.isUnlocked:
            state = NODE_STATE_FLAGS.UNLOCKED
            if guiItem.isInInventory:
                state |= NODE_STATE_FLAGS.IN_INVENTORY
                if self._canSell(nodeCD):
                    state |= NODE_STATE_FLAGS.CAN_SELL
            else:
                if canBuyGoldForItemThroughWeb(nodeCD) or self._mayObtainForMoney(nodeCD):
                    state |= NODE_STATE_FLAGS.ENOUGH_MONEY
                if self._isLastUnlocked(nodeCD):
                    state |= NODE_STATE_FLAGS.LAST_2_BUY
            if nodeCD in self._wereInBattle:
                state |= NODE_STATE_FLAGS.WAS_IN_BATTLE
            if guiItem.buyPrices.itemPrice.isActionPrice() and not guiItem.isRestorePossible():
                state |= NODE_STATE_FLAGS.ACTION
        else:
            if available:
                state = NODE_STATE_FLAGS.NEXT_2_UNLOCK
                if g_techTreeDP.getAllVehiclePossibleXP(unlockProps.parentID, unlockStats) >= unlockProps.xpCost:
                    state |= NODE_STATE_FLAGS.ENOUGH_XP
            if unlockProps.discount:
                state |= NODE_STATE_FLAGS.ACTION
        if guiItem.isElite:
            state |= NODE_STATE_FLAGS.ELITE
        if guiItem.isPremium:
            state |= NODE_STATE_FLAGS.PREMIUM
        if guiItem.isRented and not guiItem.isPremiumIGR:
            state = self._checkExpiredRent(state, guiItem)
            state = self._checkMoney(state, nodeCD)
        if guiItem.isRentable and not guiItem.isInInventory:
            state = self._checkMoney(state, nodeCD)
        if self._isVehicleCanBeChanged():
            state |= NODE_STATE_FLAGS.VEHICLE_CAN_BE_CHANGED
        bpfProps = self._getBlueprintsProps(node.nodeCD, guiItem.level)
        if bpfProps is not None and bpfProps.totalCount > 0:
            state |= NODE_STATE_FLAGS.BLUEPRINT
        state = self._checkRestoreState(state, guiItem)
        state = self._checkRentableState(state, guiItem)
        state = self._checkTradeInState(state, guiItem)
        state = self._checkTechTreeEvents(state, guiItem, unlockProps)
        state = self._checkEarlyAccessState(state, guiItem)
        price = getGUIPrice(guiItem, self._stats.money, self._items.shop.exchangeRate)
        return nodes.RealNode(node.nodeCD, guiItem, earnedXP, state, displayInfo, unlockProps=unlockProps, bpfProps=bpfProps, price=price)

    @staticmethod
    def _makeAnnouncementNode(node, displayInfo):
        info = g_techTreeDP.getAnnouncementByName(node.nodeName)
        state = NODE_STATE_FLAGS.NOT_CLICKABLE
        state |= NODE_STATE_FLAGS.ANNOUNCEMENT
        if info.isElite:
            state |= NODE_STATE_FLAGS.ELITE
        return nodes.AnnouncementNode(node.nodeCD, info, state, displayInfo)

    def _canSell(self, nodeCD):
        return self.getItem(nodeCD).canSell

    def _needLast2BuyFlag(self, nodeCD):
        return self._isLastUnlocked(nodeCD)

    def _findSelectedNode(self, nationID):
        if not g_currentVehicle.isPresent():
            return
        vehicle = g_currentVehicle.item
        if nationID != vehicle.nationID:
            return
        nodeCD = vehicle.intCD
        if nodeCD in self._nodesIdx.keys():
            index = self._nodesIdx[nodeCD]
            node = self._nodes[index]
            if self._scrollIndex < 0:
                self._scrollIndex = index
            if vehicle.isInInventory:
                node.addStateFlag(NODE_STATE_FLAGS.SELECTED)
            else:
                _logger.error('Current vehicle not found in inventory: %d', nodeCD)
        elif vehicle.isCollectible:
            _logger.info('Current vehicle with id=%d is collectible. It is not in nation tree', nodeCD)
        elif vehicle.isHidden:
            _logger.debug('Current vehicle is hidden. Is it define in nation tree: %d', nodeCD)
        else:
            _logger.error('Current vehicle not found in nation tree: %d', nodeCD)

    def _findActionNode(self, nationID):

        def _filterFunc(nodeCD):
            if nodeCD in self._nodesIdx.keys():
                index = self._nodesIdx[nodeCD]
                node = self._nodes[index]
                return g_techTreeDP.isActionStartNode(node)
            return False

        vehicleCDs = g_techTreeDP.techTreeEventsListener.getVehicles(nationID)
        startNodes = filter(_filterFunc, vehicleCDs)
        if startNodes:
            self._scrollIndex = self._nodesIdx[choice(startNodes)]
            self._nodes[self._scrollIndex].addStateFlag(NODE_STATE_FLAGS.SELECTED)
        elif self._scrollIndex < 0:
            self._scrollIndex = 0

    def __isInInventory(self, nodeCD):
        try:
            node = self._nodes[self._nodesIdx[nodeCD]]
        except KeyError as e:
            _logger.exception(e)
            return False

        return NODE_STATE.inInventory(node.getState())
