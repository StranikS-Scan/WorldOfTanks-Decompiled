# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/techtree/data.py
import logging
from itertools import chain
from random import choice
import typing
from CurrentVehicle import g_currentVehicle
from gui.Scaleform.daapi.view.lobby.techtree import nodes
from gui.Scaleform.daapi.view.lobby.techtree.dumpers import _BaseDumper
from gui.Scaleform.daapi.view.lobby.techtree.settings import NODE_STATE, MAX_PATH_LIMIT, SelectedNation
from gui.Scaleform.daapi.view.lobby.techtree.settings import RESEARCH_ITEMS
from gui.Scaleform.daapi.view.lobby.techtree.settings import UnlockProps, UnlockStats, DEFAULT_UNLOCK_PROPS
from gui.Scaleform.daapi.view.lobby.techtree.techtree_dp import g_techTreeDP
from gui.Scaleform.genConsts.NODE_STATE_FLAGS import NODE_STATE_FLAGS
from gui.game_control.veh_comparison_basket import getInstalledModulesCDs
from gui.limited_ui.lui_rules_storage import LuiRules
from gui.shop import canBuyGoldForItemThroughWeb
from gui.prb_control import prbDispatcherProperty
from gui.shared.economics import getGUIPrice
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.utils.requesters import REQ_CRITERIA
from helpers import dependency
from items import ITEM_TYPE_NAMES, getTypeOfCompactDescr as getTypeOfCD, vehicles as vehicles_core
from shared_utils.vehicle_utils import ModuleDependencies
from skeletons.gui.game_control import ITradeInController, IBootcampController, ILimitedUIController
from skeletons.gui.shared import IItemsCache
from skeletons.gui.lobby_context import ILobbyContext
from soft_exception import SoftException
_logger = logging.getLogger(__name__)
__all__ = ('ResearchItemsData', 'NationTreeData')

@dependency.replace_none_kwargs(lobbyContext=ILobbyContext)
def _checkCollectibleEnabled(state, lobbyContext=None):
    if lobbyContext.getServerSettings().isCollectorVehicleEnabled():
        state = NODE_STATE.removeIfHas(state, NODE_STATE_FLAGS.PURCHASE_DISABLED)
    else:
        state = NODE_STATE.addIfNot(state, NODE_STATE_FLAGS.PURCHASE_DISABLED)
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
        return self._invalidateXP([ item for item in self._getNodesToInvalidate() if NODE_STATE_FLAGS.NEXT_2_UNLOCK & item.getState() ])

    def invalidateVTypeXP(self):
        return self._invalidateXP([ item for item in self._getNodesToInvalidate() if NODE_STATE_FLAGS.NEXT_2_UNLOCK & item.getState() ])

    def invalidateElites(self, elites):
        return self._addStateFlag([ node for node in self._getNodesToInvalidate() if node.getNodeCD() in elites ], NODE_STATE_FLAGS.ELITE)

    def invalidateInventory(self, nodeCDs):
        result = []
        nodes_ = (node for node in self._getNodesToInvalidate() if node.getNodeCD() in nodeCDs)
        for node in nodes_:
            nodeCD = node.getNodeCD()
            state = node.getState()
            item = self.getItem(nodeCD)
            if item.isInInventory:
                state = NODE_STATE.removeIfHas(state, NODE_STATE_FLAGS.ENOUGH_MONEY)
                state = NODE_STATE.addIfNot(state, NODE_STATE_FLAGS.IN_INVENTORY)
                state = NODE_STATE.removeIfHas(state, NODE_STATE_FLAGS.VEHICLE_IN_RENT)
                state = NODE_STATE.removeIfHas(state, NODE_STATE_FLAGS.LAST_2_BUY)
                if item.isRented and not item.isPremiumIGR:
                    state = self._checkExpiredRent(state, item)
                    state = self._checkMoney(state, nodeCD)
                if self._canSell(nodeCD):
                    state = NODE_STATE.addIfNot(state, NODE_STATE_FLAGS.CAN_SELL)
                else:
                    state = NODE_STATE.removeIfHas(state, NODE_STATE_FLAGS.CAN_SELL)
            else:
                state = NODE_STATE.removeIfHas(state, NODE_STATE_FLAGS.IN_INVENTORY)
                state = NODE_STATE.removeIfHas(state, NODE_STATE_FLAGS.VEHICLE_IN_RENT)
                state = NODE_STATE.removeIfHas(state, NODE_STATE_FLAGS.CAN_SELL)
                state = NODE_STATE.removeIfHas(state, NODE_STATE_FLAGS.SELECTED)
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
                NODE_STATE.addIfNot(state, NODE_STATE_FLAGS.BLUEPRINT)
            else:
                NODE_STATE.removeIfHas(state, NODE_STATE_FLAGS.BLUEPRINT)
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
                    state = NODE_STATE.addIfNot(state, NODE_STATE_FLAGS.VEHICLE_CAN_BE_CHANGED)
                else:
                    state = NODE_STATE.removeIfHas(state, NODE_STATE_FLAGS.VEHICLE_CAN_BE_CHANGED)
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
        state = NODE_STATE.removeIfHas(state, NODE_STATE_FLAGS.ENOUGH_MONEY)
        if canBuyGoldForItemThroughWeb(nodeCD) or self._mayObtainForMoney(nodeCD):
            state |= NODE_STATE_FLAGS.ENOUGH_MONEY
        return state

    def _checkRestoreState(self, state, item):
        state = NODE_STATE.removeIfHas(state, NODE_STATE_FLAGS.RESTORE_AVAILABLE)
        money = self._stats.money
        exchangeRate = self._items.shop.exchangeRate
        mayRent, _ = item.mayRent(money)
        if item.isRestoreAvailable():
            if item.mayRestoreWithExchange(money, exchangeRate) or not mayRent:
                state = NODE_STATE.addIfNot(state, NODE_STATE_FLAGS.RESTORE_AVAILABLE)
        return state

    def _checkExpiredRent(self, state, item):
        state = NODE_STATE.addIfNot(state, NODE_STATE_FLAGS.VEHICLE_IN_RENT)
        if item.rentalIsOver:
            state = NODE_STATE.removeIfHas(state, NODE_STATE_FLAGS.IN_INVENTORY)
            state = NODE_STATE.removeIfHas(state, NODE_STATE_FLAGS.VEHICLE_IN_RENT)
            state |= NODE_STATE_FLAGS.VEHICLE_RENTAL_IS_OVER
        return state

    def _checkRentableState(self, state, item):
        state = NODE_STATE.removeIfHas(state, NODE_STATE_FLAGS.RENT_AVAILABLE)
        if item.isRentable and item.isRentAvailable and (not item.isRented or item.rentalIsOver):
            state = NODE_STATE.addIfNot(state, NODE_STATE_FLAGS.RENT_AVAILABLE)
        return state

    def _checkTradeInState(self, state, item):
        if item.itemTypeID != GUI_ITEM_TYPE.VEHICLE:
            return state
        state = NODE_STATE.removeIfHas(state, NODE_STATE_FLAGS.CAN_TRADE_IN)
        if item.canTradeIn:
            state = NODE_STATE.addIfNot(state, NODE_STATE_FLAGS.CAN_TRADE_IN)
        state = NODE_STATE.removeIfHas(state, NODE_STATE_FLAGS.CAN_TRADE_OFF)
        if item.canTradeOff:
            state = NODE_STATE.addIfNot(state, NODE_STATE_FLAGS.CAN_TRADE_OFF)
        return state

    def _checkBuyingActionState(self, state, item):
        state = NODE_STATE.removeIfHas(state, NODE_STATE_FLAGS.ACTION)
        if item.buyPrices.itemPrice.isActionPrice() and not item.isRestorePossible():
            state = NODE_STATE.addIfNot(state, NODE_STATE_FLAGS.ACTION)
        return state

    def _checkCollectibleActionState(self, state, item):
        state = NODE_STATE.removeIfHas(state, NODE_STATE_FLAGS.COLLECTIBLE_ACTION)
        if item.buyPrices.itemPrice.isActionPrice():
            state = NODE_STATE.addIfNot(state, NODE_STATE_FLAGS.COLLECTIBLE_ACTION)
        return state

    def _checkTechTreeEvents(self, state, guiItem, unlockProps):
        if g_techTreeDP.techTreeEventsListener.hasActiveAction(guiItem.intCD):
            if guiItem.itemTypeID == GUI_ITEM_TYPE.VEHICLE:
                if self._hideTechTreeEvent:
                    state |= NODE_STATE_FLAGS.TECH_TREE_EVENT_DISCOUNT_ONLY
                else:
                    state |= NODE_STATE_FLAGS.HAS_TECH_TREE_EVENT
                NODE_STATE.removeIfHas(state, NODE_STATE_FLAGS.ACTION)
                noUnlockDiscount = not unlockProps or not unlockProps.discount
                noUnlockDiscount and guiItem.buyPrices.itemPrice.isActionPrice() and not guiItem.isRestorePossible() and NODE_STATE.add(state, NODE_STATE_FLAGS.ACTION)
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
            state = NODE_STATE.add(state, NODE_STATE_FLAGS.ENOUGH_MONEY)
        else:
            state = NODE_STATE.remove(state, NODE_STATE_FLAGS.ENOUGH_MONEY)
        if state < 0:
            return node.getState()
        if not node.isActionPrice():
            state = NODE_STATE.removeIfHas(state, NODE_STATE_FLAGS.ACTION)
        else:
            state = NODE_STATE.addIfNot(state, NODE_STATE_FLAGS.ACTION)
        state = NODE_STATE.addIfNot(state, NODE_STATE_FLAGS.BLUEPRINT)
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
                state = NODE_STATE.add(state, NODE_STATE_FLAGS.ENOUGH_MONEY)
            else:
                state = NODE_STATE.remove(state, NODE_STATE_FLAGS.ENOUGH_MONEY)
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
                state = NODE_STATE.add(state, NODE_STATE_FLAGS.ENOUGH_XP)
            else:
                state = NODE_STATE.remove(state, NODE_STATE_FLAGS.ENOUGH_XP)
            if state > -1:
                node.setState(state)
                result.append((node.getNodeCD(), state))

        return result

    def _getBlueprintsProps(self, vehicleCD, level):
        return self._items.blueprints.getBlueprintData(vehicleCD, level)


class ResearchItemsData(_ItemsData):
    _itemsCache = dependency.descriptor(IItemsCache)
    _rootCD = None
    _moduleInstaller = None

    def __init__(self, dumper):
        super(ResearchItemsData, self).__init__(dumper)
        self._autoGunCD = -1
        self._autoTurretCD = -1
        self._topLevel = []
        self._topLevelCDs = {}
        self._installed = []
        self._enableInstallItems = False

    def clear(self, full=False):
        while self._topLevel:
            self._topLevel.pop().clear()

        self._topLevelCDs.clear()
        super(ResearchItemsData, self).clear(full=full)

    @classmethod
    def setRootCD(cls, cd):
        cls._rootCD = int(cd)
        cls._setModuleInstaller(cls._rootCD)

    @classmethod
    def _setModuleInstaller(cls, vehicleCD):
        stockVehicle = cls._itemsCache.items.getStockVehicle(vehicleCD)
        cls._moduleInstaller = ModuleDependencies(getInstalledModulesCDs(stockVehicle))

    @classmethod
    def getRootCD(cls):
        return cls._rootCD

    @classmethod
    def clearRootCD(cls):
        cls._rootCD = None
        return

    @classmethod
    def getNationID(cls):
        result = 0
        if cls._rootCD is not None:
            result = vehicles_core.getVehicleType(cls._rootCD).id[0]
        return result

    def getRootItem(self):
        rootCD = self.getRootCD()
        return self.getItem(rootCD)

    def getRootNode(self):
        return self._nodes[0] if self._nodes else None

    def getTopLevelByItemCD(self, itemCD):
        itemIdx = self._topLevelCDs[itemCD] if self._topLevelCDs is not None else None
        return self._topLevel[itemIdx] if self._topLevel is not None and itemIdx is not None else None

    def isRedrawNodes(self, unlocks):
        return self._rootCD in unlocks

    def isInstallItemsEnabled(self):
        rootItem = self.getRootItem()
        return rootItem.isInInventory and not rootItem.isLocked and not rootItem.repairCost

    def getTopLevel(self):
        for item in self._topLevel:
            yield item

    def load(self):
        g_techTreeDP.load()
        self.clear()
        rootItem = self.getRootItem()
        unlockStats = self.getUnlockStats()
        self._loadRoot(rootItem, unlockStats)
        self._loadAutoUnlockItems(rootItem, unlockStats)
        self._loadItems(rootItem, unlockStats)
        self._loadTopLevel(rootItem, unlockStats)
        self._loadAnnouncement(rootItem)

    def invalidateUnlocks(self, unlocks):
        mapping = {item.getNodeCD():item for item in self._getNodesToInvalidate()}
        unlocked = []
        for nodeCD in unlocks:
            if nodeCD in mapping:
                node = mapping[nodeCD]
                unlocked.append((nodeCD, self._change2Unlocked(node)))
                mapping.pop(nodeCD)

        next2Unlock = self._findNext2UnlockItems(mapping.values())
        prevUnlocks = []
        for nodeCD, node in mapping.iteritems():
            if getTypeOfCD(nodeCD) == GUI_ITEM_TYPE.VEHICLE:
                continue
            state = node.getState()
            if NODE_STATE.isAvailable2Buy(state) and unlocks & node.getUnlockProps().required:
                prevUnlocks.append((nodeCD, state))

        return (next2Unlock, unlocked, prevUnlocks)

    def invalidateHovered(self, nodeCD):
        result = []
        if nodeCD == -1:
            for node in self._nodes:
                nodeCD = node.getNodeCD()
                state = node.getState()
                state = NODE_STATE.remove(state, NODE_STATE_FLAGS.DASHED)
                if state > -1:
                    node.setState(state)
                    result.append((nodeCD, state))

            _logger.debug('[ModuleDependencies] nodes with "dashed" state cleared: %s', result)
        else:
            conflicted = self._moduleInstaller.updateConflicted(nodeCD, self.getRootItem())
            moduleDependencies = [ moduleCD for moduleTypes in conflicted for moduleCD in moduleTypes ]
            _logger.debug('[ModuleDependencies] nodeCD = %s, module dependencies %s', nodeCD, moduleDependencies)
            for node in self._nodes:
                nodeCD = node.getNodeCD()
                if nodeCD not in moduleDependencies or getTypeOfCD(nodeCD) not in GUI_ITEM_TYPE.VEHICLE_MODULES:
                    continue
                state = node.getState()
                state = NODE_STATE.add(state, NODE_STATE_FLAGS.DASHED)
                if state > -1:
                    node.setState(state)
                    result.append((node.getNodeCD(), state))

            self._moduleInstaller.clearConflictedModules()
            _logger.debug('[ModuleDependencies] nodes with "dashed" state set: %s', result)
        return result

    def invalidateInstalled(self):
        nodes_ = self._getNodesToInvalidate()
        rootItem = self.getRootItem()
        result = []
        for node in nodes_:
            nodeCD = node.getNodeCD()
            state = node.getState()
            item = self.getItem(nodeCD)
            if rootItem.isInInventory and item.isInstalled(rootItem):
                state = NODE_STATE.add(state, NODE_STATE_FLAGS.INSTALLED)
            else:
                state = NODE_STATE.remove(state, NODE_STATE_FLAGS.INSTALLED)
            if item.itemTypeID == GUI_ITEM_TYPE.VEHICLE and item.isElite:
                state = NODE_STATE.add(state, NODE_STATE_FLAGS.ELITE)
            if state > -1:
                node.setState(state)
                result.append((nodeCD, state))

        return result

    def invalidateVehicleCollectorState(self):
        node = self.getRootNode()
        state = _checkCollectibleEnabled(node.getState())
        return [(self.getRootCD(), state)]

    def _addTopNode(self, nodeCD, node):
        index = len(self._topLevel)
        self._topLevelCDs[nodeCD] = index
        self._topLevel.append(node)
        return index

    def _getNodesToInvalidate(self):
        toInvalidate = self._nodes[:]
        toInvalidate.extend(self._topLevel)
        return [ node for node in toInvalidate if not NODE_STATE.isAnnouncement(node.getState()) ]

    def _findNext2UnlockItems(self, nodes_):
        result = []
        topLevelCDs = self._topLevelCDs.keys()
        unlockStats = self.getUnlockStats()
        unlockKwargs = unlockStats._asdict()
        for node in nodes_:
            nodeCD = node.getNodeCD()
            state = node.getState()
            itemTypeID, _, _ = vehicles_core.parseIntCompactDescr(nodeCD)
            if itemTypeID == GUI_ITEM_TYPE.VEHICLE and (nodeCD in topLevelCDs or nodeCD == self.getRootCD()):
                available, unlockProps = g_techTreeDP.isNext2Unlock(nodeCD, **unlockKwargs)
                xp = g_techTreeDP.getAllVehiclePossibleXP(unlockProps.parentID, unlockStats)
            else:
                unlockProps = node.getUnlockProps()
                required = unlockProps.required
                available = len(required) and unlockStats.isSeqUnlocked(required) and not unlockStats.isUnlocked(nodeCD)
                xp = g_techTreeDP.getAllVehiclePossibleXP(self.getRootCD(), unlockStats)
            if available and state & NODE_STATE_FLAGS.LOCKED > 0:
                state ^= NODE_STATE_FLAGS.LOCKED
                state = NODE_STATE.addIfNot(state, NODE_STATE_FLAGS.NEXT_2_UNLOCK)
                if xp >= unlockProps.xpCost:
                    state = NODE_STATE.addIfNot(state, NODE_STATE_FLAGS.ENOUGH_XP)
                else:
                    state = NODE_STATE.removeIfHas(state, NODE_STATE_FLAGS.ENOUGH_XP)
                state = NODE_STATE.addIfNot(state, NODE_STATE_FLAGS.BLUEPRINT)
                node.setState(state)
                result.append((node.getNodeCD(), state, unlockProps.makeTuple()))

        return result

    def _mayObtainForMoney(self, nodeCD):
        result = False
        if getTypeOfCD(nodeCD) == GUI_ITEM_TYPE.VEHICLE or self.isInstallItemsEnabled():
            result = super(ResearchItemsData, self)._mayObtainForMoney(nodeCD)
        return result

    def _canSell(self, nodeCD):
        item = self.getItem(nodeCD)
        if getTypeOfCD(nodeCD) == GUI_ITEM_TYPE.VEHICLE:
            canSell = item.canSell
        else:
            canSell = item.isInInventory
        return canSell

    def _needLast2BuyFlag(self, nodeCD):
        return False

    def _getRootUnlocksDescrs(self, rootItem):
        return rootItem.getUnlocksDescrs()

    def _getNodeData(self, nodeCD, rootItem, guiItem, unlockStats, unlockProps, path, level=-1, topLevel=False):
        itemTypeID = guiItem.itemTypeID
        available = False
        xp = 0
        bpfProps = None
        state = NODE_STATE_FLAGS.LOCKED
        if topLevel and itemTypeID == GUI_ITEM_TYPE.VEHICLE:
            available, unlockProps = g_techTreeDP.isNext2Unlock(nodeCD, level=guiItem.level, **unlockStats._asdict())
            xp = g_techTreeDP.getAllVehiclePossibleXP(unlockProps.parentID, unlockStats)
        if guiItem.isUnlocked:
            state = NODE_STATE_FLAGS.UNLOCKED
            if itemTypeID != GUI_ITEM_TYPE.VEHICLE and rootItem.isInInventory and guiItem.isInstalled(rootItem) and not rootItem.rentalIsOver:
                state |= NODE_STATE_FLAGS.INSTALLED
            elif guiItem.isInInventory:
                if rootItem.isInInventory or itemTypeID == GUI_ITEM_TYPE.VEHICLE:
                    state |= NODE_STATE_FLAGS.IN_INVENTORY
                if self._canSell(nodeCD):
                    state |= NODE_STATE_FLAGS.CAN_SELL
            elif canBuyGoldForItemThroughWeb(nodeCD) or self._mayObtainForMoney(nodeCD):
                state |= NODE_STATE_FLAGS.ENOUGH_MONEY
            if nodeCD in self._wereInBattle:
                state |= NODE_STATE_FLAGS.WAS_IN_BATTLE
            if guiItem.buyPrices.itemPrice.isActionPrice() and not self.bootcamp.isInBootcamp():
                state |= NODE_STATE_FLAGS.ACTION
        else:
            if not topLevel:
                available = unlockStats.isSeqUnlocked(unlockProps.required) and unlockStats.isUnlocked(self._rootCD)
                xp = g_techTreeDP.getAllVehiclePossibleXP(self._rootCD, unlockStats)
            if available:
                state = NODE_STATE_FLAGS.NEXT_2_UNLOCK
                if xp >= unlockProps.xpCost:
                    state |= NODE_STATE_FLAGS.ENOUGH_XP
            if itemTypeID == GUI_ITEM_TYPE.VEHICLE and unlockProps.discount:
                state |= NODE_STATE_FLAGS.ACTION
        if itemTypeID == GUI_ITEM_TYPE.VEHICLE:
            if guiItem.isElite:
                state |= NODE_STATE_FLAGS.ELITE
            if guiItem.isPremium:
                state |= NODE_STATE_FLAGS.PREMIUM
            if guiItem.isCollectible:
                state |= NODE_STATE_FLAGS.COLLECTIBLE
                state = _checkCollectibleEnabled(state)
                if not guiItem.isInInventory:
                    state = self._checkCollectibleActionState(state, guiItem)
            if guiItem.isRented and not guiItem.isPremiumIGR:
                state = self._checkExpiredRent(state, guiItem)
                if not guiItem.isTelecom:
                    state = self._checkMoney(state, nodeCD)
            if guiItem.isRentable and not guiItem.isInInventory and not guiItem.isTelecom:
                state = self._checkMoney(state, nodeCD)
            if self._isVehicleCanBeChanged():
                state |= NODE_STATE_FLAGS.VEHICLE_CAN_BE_CHANGED
            if guiItem.isHidden:
                state |= NODE_STATE_FLAGS.PURCHASE_DISABLED
            state = self._checkRestoreState(state, guiItem)
            state = self._checkRentableState(state, guiItem)
            state = self._checkTradeInState(state, guiItem)
            state = self._checkTechTreeEvents(state, guiItem, unlockProps)
            bpfProps = self._getBlueprintsProps(nodeCD, rootItem.level)
            if bpfProps is not None and bpfProps.totalCount > 0:
                state |= NODE_STATE_FLAGS.BLUEPRINT
            renderer = 'root' if self._rootCD == nodeCD else 'vehicle'
        else:
            renderer = 'item'
        price = getGUIPrice(guiItem, self._stats.money, self._items.shop.exchangeRate)
        displayInfo = {'path': path,
         'renderer': renderer,
         'level': level}
        return nodes.RealNode(nodeCD, guiItem, unlockStats.getVehXP(nodeCD), state, displayInfo, unlockProps=unlockProps, bpfProps=bpfProps, price=price)

    def _getAnnouncementData(self, nodeCD, path, level):
        info = g_techTreeDP.getAnnouncementByCD(nodeCD)
        state = NODE_STATE_FLAGS.NOT_CLICKABLE
        state |= NODE_STATE_FLAGS.ANNOUNCEMENT
        if info.isElite:
            state |= NODE_STATE_FLAGS.ELITE
        displayInfo = {'path': path,
         'renderer': 'vehicle',
         'level': level}
        return nodes.AnnouncementNode(nodeCD, info, state, displayInfo)

    def _getNewCost(self, vehicleCD, level, oldCost):
        blueprintDiscount = self._items.blueprints.getBlueprintDiscount(vehicleCD, level)
        xpCost = self._items.blueprints.calculateCost(oldCost, blueprintDiscount)
        return (xpCost, blueprintDiscount)

    def _loadRoot(self, rootItem, unlockStats):
        rootCD = rootItem.intCD
        node = self._getNodeData(rootCD, rootItem, rootItem, unlockStats, DEFAULT_UNLOCK_PROPS, set(), topLevel=True, level=rootItem.level)
        index = self._addNode(rootCD, node)

    def _loadAutoUnlockItems(self, rootItem, unlockStats):
        autoUnlocked = rootItem.getAutoUnlockedItemsMap()
        hasFakeTurrets = not rootItem.hasTurrets
        rootCD = rootItem.intCD
        itemGetter = self.getItem
        self._autoGunCD = -1
        self._autoTurretCD = -1
        for itemTypeID in RESEARCH_ITEMS:
            if itemTypeID > len(ITEM_TYPE_NAMES) - 1:
                continue
            nodeCD = autoUnlocked[ITEM_TYPE_NAMES[itemTypeID]]
            if itemTypeID == GUI_ITEM_TYPE.TURRET:
                self._autoTurretCD = nodeCD
                if hasFakeTurrets:
                    continue
            elif itemTypeID == GUI_ITEM_TYPE.GUN:
                self._autoGunCD = nodeCD
            node = self._getNodeData(nodeCD, rootItem, itemGetter(nodeCD), unlockStats, DEFAULT_UNLOCK_PROPS, {rootCD})
            node.addStateFlag(NODE_STATE_FLAGS.AUTO_UNLOCKED)
            self._addNode(nodeCD, node)

    def _loadItems(self, rootItem, unlockStats):
        itemGetter = self.getItem
        rootCD = rootItem.intCD
        maxPath = 0
        nodes_ = []
        for unlockIdx, oldCost, nodeCD, required in self._getRootUnlocksDescrs(rootItem):
            itemTypeID = getTypeOfCD(nodeCD)
            required.add(rootCD)
            path = required.copy()
            path = self.__fixPath(itemTypeID, path)
            maxPath = max(len(path), maxPath)
            xpCost = oldCost
            discount = 0
            if itemTypeID == GUI_ITEM_TYPE.VEHICLE:
                item = self.getItem(nodeCD)
                xpCost, discount = self._getNewCost(nodeCD, item.level, oldCost)
            nodes_.append((nodeCD,
             itemTypeID,
             UnlockProps(rootCD, unlockIdx, xpCost, required, discount, oldCost),
             path))

        for nodeCD, itemTypeID, unlockProps, path in nodes_:
            node = self._getNodeData(nodeCD, rootItem, itemGetter(nodeCD), unlockStats, unlockProps, path, level=self.__fixLevel(itemTypeID, path, maxPath))
            self._addNode(nodeCD, node)

    def _loadTopLevel(self, rootItem, unlockStats):
        itemGetter = self.getItem
        rootCD = self.getRootCD()
        for nodeCD in g_techTreeDP.getTopLevel(rootCD):
            node = self._getNodeData(nodeCD, rootItem, itemGetter(nodeCD), unlockStats, DEFAULT_UNLOCK_PROPS, set(), topLevel=True)
            self._addTopNode(nodeCD, node)

    def _loadAnnouncement(self, rootItem):
        rootCD = rootItem.intCD
        for nodeCD in g_techTreeDP.getNextAnnouncements(rootCD):
            node = self._getAnnouncementData(nodeCD, (rootCD,), MAX_PATH_LIMIT)
            self._addNode(nodeCD, node)

    def __fixPath(self, itemTypeID, path):
        if self._autoGunCD in path and self._autoTurretCD in path:
            if itemTypeID == GUI_ITEM_TYPE.TURRET:
                path.remove(self._autoGunCD)
            elif itemTypeID == GUI_ITEM_TYPE.GUN:
                path.remove(self._autoTurretCD)
            elif itemTypeID == GUI_ITEM_TYPE.VEHICLE:
                path.remove(self._autoGunCD)
                path.remove(self._autoTurretCD)
        return path

    def __fixLevel(self, itemTypeID, path, maxPath):
        level = -1
        if itemTypeID == GUI_ITEM_TYPE.VEHICLE and len(path) <= maxPath:
            level = min(maxPath + 1, MAX_PATH_LIMIT)
        return level


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
            prevUnlocked = [ (item, self._changePreviouslyUnlockedByCD(item)) for item in chain(*parents) ]
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
