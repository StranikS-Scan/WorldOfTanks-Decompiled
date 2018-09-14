# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/techtree/data.py
import operator
from AccountCommands import LOCK_REASON
from CurrentVehicle import g_currentVehicle
from debug_utils import LOG_CURRENT_EXCEPTION, LOG_ERROR, LOG_DEBUG
from gui.prb_control.prb_helpers import prbDispatcherProperty, preQueueFunctionalProperty
from gui.shared import g_itemsCache, REQ_CRITERIA
from gui.shared.gui_items import GUI_ITEM_TYPE
from items import vehicles, getTypeOfCompactDescr, ITEM_TYPE_NAMES
from gui.Scaleform.daapi.view.lobby.techtree import NODE_STATE, MAX_PATH_LIMIT, _RESEARCH_ITEMS, makeDefUnlockProps, UnlockProps, UnlockStats
from gui.Scaleform.daapi.view.lobby.techtree.dumpers import _BaseDumper
from gui.Scaleform.daapi.view.lobby.techtree.techtree_dp import g_techTreeDP
__all__ = ['ResearchItemsData', 'NationTreeData']

class _ItemsData(object):

    def __init__(self, dumper):
        super(_ItemsData, self).__init__()
        if dumper is not None and isinstance(dumper, _BaseDumper):
            self._dumper = dumper
        else:
            raise Exception, 'Dumper is invalid.'
        self._nodes = []
        self._nodesIdx = {}
        self._items = g_itemsCache.items
        self._stats = g_itemsCache.items.stats
        self._wereInBattle = self._getNodesWereInBattle()
        return

    def _isVehicleCanBeChanged(self):
        vehicleCanBeChanged = False
        if self.prbDispatcher is not None:
            permission = self.prbDispatcher.getGUIPermissions()
            if permission is not None:
                vehicleCanBeChanged = permission.canChangeVehicle()
        return vehicleCanBeChanged

    def _getAllPossibleXP(self, nodeCD, unlockStats):
        criteria = REQ_CRITERIA.VEHICLE.ELITE | ~REQ_CRITERIA.IN_CD_LIST([nodeCD])
        eliteVehicles = g_itemsCache.items.getVehicles(criteria)
        dirtyResult = sum(map(operator.attrgetter('xp'), eliteVehicles.values()))
        exchangeRate = self._items.shop.freeXPConversion[0]
        result = min(int(dirtyResult / exchangeRate) * exchangeRate, self._stats.gold * exchangeRate)
        result += unlockStats.getVehTotalXP(nodeCD)
        return result

    def _checkMoneyForRentOrBuy(self, state, nodeCD):
        state = NODE_STATE.removeIfHas(state, NODE_STATE.ENOUGH_MONEY)
        if self._canRentOrBuy(nodeCD):
            state |= NODE_STATE.ENOUGH_MONEY
        return state

    def _checkExpiredRent(self, state, item):
        state = NODE_STATE.addIfNot(state, NODE_STATE.VEHICLE_IN_RENT)
        if item.rentalIsOver:
            state = NODE_STATE.removeIfHas(state, NODE_STATE.IN_INVENTORY)
            state = NODE_STATE.removeIfHas(state, NODE_STATE.VEHICLE_IN_RENT)
        return state

    @prbDispatcherProperty
    def prbDispatcher(self):
        return None

    @preQueueFunctionalProperty
    def preQueueFunctional(self):
        return None

    def __del__(self):
        LOG_DEBUG('Data deleted:', self)

    def clear(self, full = False):
        while len(self._nodes):
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

    def getItem(self, itemCD):
        return self._items.getItemByCD(itemCD)

    def getRootItem(self):
        raise NotImplementedError, 'Must be overridden in subclass'

    def getInventoryVehicles(self):
        nodeCDs = map(lambda node: node['id'], self._getNodesToInvalidate())
        LOG_DEBUG('getInventoryVehicles', nodeCDs)
        vehicles = self._items.getVehicles(REQ_CRITERIA.INVENTORY | REQ_CRITERIA.IN_CD_LIST(nodeCDs))
        return dict(map(lambda item: (item.inventoryID, item), vehicles.itervalues()))

    def getUnlockStats(self):
        return UnlockStats(self._stats.unlocks, self._stats.vehiclesXPs, self._stats.freeXP)

    def dump(self):
        return self._dumper.dump(self)

    def invalidateCredits(self):
        return self._invalidateMoney(filter(lambda item: NODE_STATE.isBuyForCredits(item['state']), self._getNodesToInvalidate()))

    def invalidateGold(self):
        return self._invalidateMoney(filter(lambda item: NODE_STATE.isBuyForGold(item['state']), self._getNodesToInvalidate()))

    def invalidateFreeXP(self):
        return self._invalidateXP(filter(lambda item: NODE_STATE.NEXT_2_UNLOCK & item['state'], self._getNodesToInvalidate()))

    def invalidateVTypeXP(self):
        filtered = filter(lambda item: NODE_STATE.NEXT_2_UNLOCK & item['state'], self._getNodesToInvalidate())
        return self._invalidateXP(filtered)

    def invalidateElites(self, elites):
        return self._addStateFlag(filter(lambda node: node['id'] in elites, self._getNodesToInvalidate()), NODE_STATE.ELITE)

    def invalidateInventory(self, nodeCDs):
        result = []
        nodes = filter(lambda node: node['id'] in nodeCDs, self._getNodesToInvalidate())
        for node in nodes:
            nodeCD = node['id']
            state = node['state']
            item = self.getItem(nodeCD)
            if item.isInInventory:
                state = NODE_STATE.removeIfHas(state, NODE_STATE.ENOUGH_MONEY)
                state = NODE_STATE.addIfNot(state, NODE_STATE.IN_INVENTORY)
                state = NODE_STATE.removeIfHas(state, NODE_STATE.VEHICLE_IN_RENT)
                if item.isRented and not item.isPremiumIGR:
                    state = self._checkExpiredRent(state, item)
                    state = self._checkMoneyForRentOrBuy(state, nodeCD)
                if self._canSell(nodeCD):
                    state = NODE_STATE.addIfNot(state, NODE_STATE.CAN_SELL)
                else:
                    state = NODE_STATE.removeIfHas(state, NODE_STATE.CAN_SELL)
            else:
                state = NODE_STATE.removeIfHas(state, NODE_STATE.IN_INVENTORY)
                state = NODE_STATE.removeIfHas(state, NODE_STATE.VEHICLE_IN_RENT)
                state = NODE_STATE.removeIfHas(state, NODE_STATE.CAN_SELL)
                state = NODE_STATE.removeIfHas(state, NODE_STATE.SELECTED)
                state = self._checkMoneyForRentOrBuy(state, nodeCD)
            node['state'] = state
            result.append((nodeCD, state))

        return result

    def invalidateLocks(self, locks):
        result = False
        inventory = self.getInventoryVehicles()
        for invID, lock in locks.iteritems():
            if invID in inventory.keys():
                result = True
                break

        return result

    def invalidatePrbState(self):
        nodes = self._getNodesToInvalidate()
        canChanged = self._isVehicleCanBeChanged()
        result = []
        for node in nodes:
            nodeCD = node['id']
            state = node['state']
            if getTypeOfCompactDescr(nodeCD) == GUI_ITEM_TYPE.VEHICLE:
                item = self.getItem(nodeCD)
                if not item.isInInventory:
                    continue
                if canChanged:
                    state = NODE_STATE.addIfNot(state, NODE_STATE.VEHICLE_CAN_BE_CHANGED)
                else:
                    state = NODE_STATE.removeIfHas(state, NODE_STATE.VEHICLE_CAN_BE_CHANGED)
                if state > -1:
                    node['state'] = state
                    result.append((nodeCD, state))

        return result

    def isHasVehicles(self):
        return bool(len(self.getInventoryVehicles()) > 0)

    def _addNode(self, nodeCD, node):
        index = len(self._nodes)
        self._nodesIdx[nodeCD] = index
        self._nodes.append(node)
        return index

    def _getNodesWereInBattle(self):
        accDossier = self._items.getAccountDossier(None)
        if accDossier:
            return set(accDossier.getTotalStats().getVehicles().keys())
        else:
            return set()

    def _getNodesToInvalidate(self):
        return self._nodes

    def _addStateFlag(self, nodes, stateFlag, exclude = None):
        result = []
        for node in nodes:
            nodeCD = node['id']
            state = node['state']
            if not state & stateFlag:
                state |= stateFlag
                if exclude is not None and state & exclude:
                    state ^= exclude
                node['state'] = state
                result.append((nodeCD, state))

        return result

    def _change2Unlocked(self, node):
        state = NODE_STATE.change2Unlocked(node['state'])
        if state < 0:
            return node['state']
        node['state'] = state
        if self._canBuy(node['id']):
            state = NODE_STATE.add(state, NODE_STATE.ENOUGH_MONEY)
        else:
            state = NODE_STATE.remove(state, NODE_STATE.ENOUGH_MONEY)
        if state < 0:
            return node['state']
        node['state'] = state
        return state

    def _canBuy(self, nodeCD):
        item = self.getItem(nodeCD)
        canBuy, reason = item.mayPurchase(self._stats.money)
        if not canBuy and reason == 'credit_error':
            return item.mayPurchaseWithExchange(self._stats.money, self._items.shop.exchangeRate)
        else:
            return canBuy

    def _canRentOrBuy(self, nodeCD):
        item = self.getItem(nodeCD)
        money = self._stats.money
        canBuy, buyReason = item.mayPurchase(money)
        canRentOrBuy, rentReason = item.mayRentOrBuy(money)
        canBuyWithExchange = item.mayPurchaseWithExchange(money, g_itemsCache.items.shop.exchangeRate)
        if not canRentOrBuy:
            if not canBuy and buyReason == 'credit_error':
                return canBuyWithExchange
            return canBuy
        return canRentOrBuy

    def _canSell(self, nodeCD):
        raise NotImplementedError

    def _invalidateMoney(self, nodes):
        result = []
        for node in nodes:
            state = node['state']
            nodeID = node['id']
            if self._canRentOrBuy(nodeID):
                state = NODE_STATE.add(state, NODE_STATE.ENOUGH_MONEY)
            else:
                state = NODE_STATE.remove(state, NODE_STATE.ENOUGH_MONEY)
            if state > -1:
                node['state'] = state
                result.append((nodeID, state))

        return result

    def _invalidateXP(self, nodes):
        result = []
        stats = self.getUnlockStats()
        for node in nodes:
            state = node['state']
            props = node['unlockProps']
            if self._getAllPossibleXP(props.parentID, stats) >= props.xpCost:
                state = NODE_STATE.add(state, NODE_STATE.ENOUGH_XP)
            else:
                state = NODE_STATE.remove(state, NODE_STATE.ENOUGH_XP)
            if state > -1:
                node['state'] = state
                result.append((node['id'], state))

        return result


class ResearchItemsData(_ItemsData):
    _rootCD = None

    def __init__(self, dumper):
        super(ResearchItemsData, self).__init__(dumper)
        self._autoGunCD = -1
        self._autoTurretCD = -1
        self._topLevel = []
        self._topLevelCDs = {}
        self._installed = []
        self._enableInstallItems = False

    def clear(self, full = False):
        while len(self._topLevel):
            self._topLevel.pop().clear()

        self._topLevelCDs.clear()
        super(ResearchItemsData, self).clear(full=full)

    @classmethod
    def setRootCD(cls, cd):
        cls._rootCD = int(cd)

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
            result = vehicles.getVehicleType(cls._rootCD).id[0]
        return result

    def getRootItem(self):
        rootCD = self.getRootCD()
        raise rootCD is not None or AssertionError
        return self.getItem(rootCD)

    def isRedrawNodes(self, unlocks):
        return self._rootCD in unlocks

    def getRootStatusString(self):
        status = ''
        item = self.getRootItem()
        if item.isInInventory:
            lockReason = item.lock
            if lockReason == LOCK_REASON.ON_ARENA:
                status = 'battle'
            elif lockReason in (LOCK_REASON.PREBATTLE, LOCK_REASON.UNIT, LOCK_REASON.UNIT_CLUB):
                status = 'inPrebattle'
            elif item.repairCost > 0:
                status = 'destroyed'
        return status

    def isInstallItemsEnabled(self):
        rootItem = self.getRootItem()
        return rootItem.isInInventory and not rootItem.lock and not rootItem.repairCost

    def load(self):
        g_techTreeDP.load()
        self.clear()
        rootItem = self.getRootItem()
        unlockStats = self.getUnlockStats()
        self.__loadRoot(rootItem, unlockStats)
        self.__loadAutoUnlockItems(rootItem, unlockStats)
        self.__loadItems(rootItem, unlockStats)
        self.__loadTopLevel(rootItem, unlockStats)

    def invalidateUnlocks(self, unlocks):
        mapping = dict(map(lambda item: (item['id'], item), self._getNodesToInvalidate()))
        unlocked = []
        for nodeCD in unlocks:
            if nodeCD in mapping:
                node = mapping[nodeCD]
                unlocked.append((nodeCD, self._change2Unlocked(node)))
                mapping.pop(nodeCD)

        next2Unlock = self._findNext2UnlockItems(mapping.values())
        return (next2Unlock, unlocked)

    def invalidateInstalled(self):
        nodes = self._getNodesToInvalidate()
        rootItem = self.getRootItem()
        result = []
        for node in nodes:
            nodeCD = node['id']
            state = node['state']
            item = self.getItem(nodeCD)
            if rootItem.isInInventory and item.isInstalled(rootItem):
                state = NODE_STATE.add(state, NODE_STATE.INSTALLED)
            else:
                state = NODE_STATE.remove(state, NODE_STATE.INSTALLED)
            if item.itemTypeID == GUI_ITEM_TYPE.VEHICLE and item.isElite:
                state = NODE_STATE.add(state, NODE_STATE.ELITE)
            if state > -1:
                node['state'] = state
                result.append((nodeCD, state))

        return result

    def _addTopNode(self, nodeCD, node):
        index = len(self._topLevel)
        self._topLevelCDs[nodeCD] = index
        self._topLevel.append(node)
        return index

    def _getNodesToInvalidate(self):
        toInvalidate = self._nodes[:]
        toInvalidate.extend(self._topLevel)
        return toInvalidate

    def _findNext2UnlockItems(self, nodes):
        result = []
        topLevelCDs = self._topLevelCDs.keys()
        unlockStats = self.getUnlockStats()
        unlockKwargs = unlockStats._asdict()
        for node in nodes:
            nodeCD = node['id']
            state = node['state']
            itemTypeID, _, _ = vehicles.parseIntCompactDescr(nodeCD)
            if itemTypeID == GUI_ITEM_TYPE.VEHICLE and (nodeCD in topLevelCDs or nodeCD == self.getRootCD()):
                available, unlockProps = g_techTreeDP.isNext2Unlock(nodeCD, **unlockKwargs)
                xp = self._getAllPossibleXP(unlockProps.parentID, unlockStats)
            else:
                unlockProps = node['unlockProps']
                required = unlockProps.required
                available = len(required) and unlockStats.isSeqUnlocked(required) and not unlockStats.isUnlocked(nodeCD)
                xp = self._getAllPossibleXP(self.getRootCD(), unlockStats)
            if available and state & NODE_STATE.LOCKED > 0:
                state ^= NODE_STATE.LOCKED
                state = NODE_STATE.addIfNot(state, NODE_STATE.NEXT_2_UNLOCK)
                if xp >= unlockProps.xpCost:
                    state = NODE_STATE.addIfNot(state, NODE_STATE.ENOUGH_XP)
                else:
                    state = NODE_STATE.removeIfHas(state, NODE_STATE.ENOUGH_XP)
                node['state'] = state
                result.append((node['id'], state, unlockProps._makeTuple()))

        return result

    def _canBuy(self, nodeCD):
        result = False
        if getTypeOfCompactDescr(nodeCD) == GUI_ITEM_TYPE.VEHICLE or self.isInstallItemsEnabled():
            result = super(ResearchItemsData, self)._canBuy(nodeCD)
        return result

    def _canSell(self, nodeCD):
        item = self.getItem(nodeCD)
        if item.isInInventory:
            if getTypeOfCompactDescr(nodeCD) == GUI_ITEM_TYPE.VEHICLE:
                canSell = item.canSell
            else:
                canSell = item.isInstalled(self.getRootItem())
        else:
            canSell = False
        return canSell

    def _getNodeData(self, nodeCD, rootItem, guiItem, unlockStats, unlockProps, path, level = -1, topLevel = False):
        itemTypeID = guiItem.itemTypeID
        available = False
        xp = 0
        state = NODE_STATE.LOCKED
        if topLevel and itemTypeID == GUI_ITEM_TYPE.VEHICLE:
            available, unlockProps = g_techTreeDP.isNext2Unlock(nodeCD, **unlockStats._asdict())
            xp = self._getAllPossibleXP(unlockProps.parentID, unlockStats)
        if guiItem.isUnlocked:
            state = NODE_STATE.UNLOCKED
            if itemTypeID != GUI_ITEM_TYPE.VEHICLE and rootItem.isInInventory and guiItem.isInstalled(rootItem):
                state |= NODE_STATE.INSTALLED
            elif guiItem.isInInventory:
                if rootItem.isInInventory or itemTypeID == GUI_ITEM_TYPE.VEHICLE:
                    state |= NODE_STATE.IN_INVENTORY
                if self._canSell(nodeCD):
                    state |= NODE_STATE.CAN_SELL
            elif self._canBuy(nodeCD):
                state |= NODE_STATE.ENOUGH_MONEY
            if nodeCD in self._wereInBattle:
                state |= NODE_STATE.WAS_IN_BATTLE
            if guiItem.buyPrice != guiItem.defaultPrice:
                state |= NODE_STATE.SHOP_ACTION
        else:
            if not topLevel:
                available = unlockStats.isSeqUnlocked(unlockProps.required) and unlockStats.isUnlocked(self._rootCD)
                xp = self._getAllPossibleXP(self._rootCD, unlockStats)
            if available:
                state = NODE_STATE.NEXT_2_UNLOCK
                if xp >= unlockProps.xpCost:
                    state |= NODE_STATE.ENOUGH_XP
        if itemTypeID == GUI_ITEM_TYPE.VEHICLE:
            if guiItem.isElite:
                state |= NODE_STATE.ELITE
            if guiItem.isPremium:
                state |= NODE_STATE.PREMIUM
            if guiItem.isRented and not guiItem.isPremiumIGR:
                state = self._checkExpiredRent(state, guiItem)
                state = self._checkMoneyForRentOrBuy(state, nodeCD)
            if guiItem.isRentable and not guiItem.isInInventory:
                state = self._checkMoneyForRentOrBuy(state, nodeCD)
            if self._isVehicleCanBeChanged():
                state |= NODE_STATE.VEHICLE_CAN_BE_CHANGED
            renderer = 'root' if self._rootCD == nodeCD else 'vehicle'
        else:
            renderer = 'item'
        return {'id': nodeCD,
         'earnedXP': unlockStats.getVehXP(nodeCD),
         'state': state,
         'unlockProps': unlockProps,
         'displayInfo': {'path': list(path),
                         'renderer': renderer,
                         'level': level}}

    def __loadRoot(self, rootItem, unlockStats):
        rootCD = rootItem.intCD
        node = self._getNodeData(rootCD, rootItem, rootItem, unlockStats, makeDefUnlockProps(), set(), topLevel=True)
        index = self._addNode(rootCD, node)
        raise index == 0 or AssertionError('Index of root must be 0')

    def __loadAutoUnlockItems(self, rootItem, unlockStats):
        autoUnlocked = rootItem.getAutoUnlockedItemsMap()
        hasFakeTurrets = not rootItem.hasTurrets
        rootCD = rootItem.intCD
        itemGetter = self.getItem
        self._autoGunCD = -1
        self._autoTurretCD = -1
        for itemTypeID in _RESEARCH_ITEMS:
            if itemTypeID > len(ITEM_TYPE_NAMES) - 1:
                continue
            nodeCD = autoUnlocked[ITEM_TYPE_NAMES[itemTypeID]]
            if itemTypeID == GUI_ITEM_TYPE.TURRET:
                self._autoTurretCD = nodeCD
                if hasFakeTurrets:
                    continue
            elif itemTypeID == GUI_ITEM_TYPE.GUN:
                self._autoGunCD = nodeCD
            node = self._getNodeData(nodeCD, rootItem, itemGetter(nodeCD), unlockStats, makeDefUnlockProps(), {rootCD})
            node['state'] |= NODE_STATE.AUTO_UNLOCKED
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

    def __loadItems(self, rootItem, unlockStats):
        itemGetter = self.getItem
        rootCD = rootItem.intCD
        maxPath = 0
        nodes = []
        for unlockIdx, xpCost, nodeCD, required in rootItem.getUnlocksDescrs():
            itemTypeID = getTypeOfCompactDescr(nodeCD)
            required.add(rootCD)
            path = required.copy()
            path = self.__fixPath(itemTypeID, path)
            maxPath = max(len(path), maxPath)
            nodes.append((nodeCD,
             itemTypeID,
             UnlockProps(rootCD, unlockIdx, xpCost, required),
             path))

        for nodeCD, itemTypeID, unlockProps, path in nodes:
            node = self._getNodeData(nodeCD, rootItem, itemGetter(nodeCD), unlockStats, unlockProps, path, level=self.__fixLevel(itemTypeID, path, maxPath))
            self._addNode(nodeCD, node)

    def __loadTopLevel(self, rootItem, unlockStats):
        itemGetter = self.getItem
        rootCD = self.getRootCD()
        for nodeCD in g_techTreeDP.getTopLevel(rootCD):
            node = self._getNodeData(nodeCD, rootItem, itemGetter(nodeCD), unlockStats, makeDefUnlockProps(), set(), topLevel=True)
            self._addTopNode(nodeCD, node)


class NationTreeData(_ItemsData):

    def __init__(self, dumper):
        super(NationTreeData, self).__init__(dumper)
        self._scrollIndex = -1

    def clear(self, full = False):
        self._scrollIndex = -1
        super(NationTreeData, self).clear(full)

    def load(self, nationID, override = None):
        self.clear()
        vehicleList = sorted(vehicles.g_list.getList(nationID).values(), key=lambda item: item['level'])
        g_techTreeDP.load(override=override)
        getDisplayInfo = g_techTreeDP.getDisplayInfo
        getItem = self.getItem
        selectedID = ResearchItemsData.getRootCD()
        unlockStats = self.getUnlockStats()
        for item in vehicleList:
            nodeCD = item['compactDescr']
            displayInfo = getDisplayInfo(nodeCD)
            if displayInfo is not None:
                item = getItem(nodeCD)
                if item.isHidden:
                    continue
                index = self._addNode(nodeCD, self._getNodeData(nodeCD, item, unlockStats, displayInfo))
                if nodeCD == selectedID:
                    self._scrollIndex = index

        ResearchItemsData.clearRootCD()
        self._findSelectedNode(nationID)
        return

    def getRootItem(self):
        if len(self._nodes):
            return self._nodes[0]
        else:
            return None

    def invalidateUnlocks(self, unlocks):
        next2Unlock = []
        unlocked = []
        unlockStats = self.getUnlockStats()
        items = g_techTreeDP.getNext2UnlockByItems(unlocks, **unlockStats._asdict())
        if len(items):
            next2Unlock = map(lambda item: (item[0], self._changeNext2Unlock(item[0], item[1], unlockStats), item[1]._makeTuple()), items.iteritems())
        filtered = filter(lambda unlock: getTypeOfCompactDescr(unlock) == GUI_ITEM_TYPE.VEHICLE, unlocks)
        if len(filtered):
            unlocked = map(lambda item: (item, self._change2UnlockedByCD(item)), filtered)
        return (next2Unlock, unlocked)

    def invalidateXpCosts(self):
        result = []
        nodes = filter(lambda item: NODE_STATE.NEXT_2_UNLOCK & item['state'], self._getNodesToInvalidate())
        statsAsDict = self.getUnlockStats()._asdict()
        for node in nodes:
            nodeCD = node['id']
            props = node['unlockProps']
            _, newProps = g_techTreeDP.isNext2Unlock(nodeCD, **statsAsDict)
            if newProps.parentID != props.parentID:
                node['unlockProps'] = newProps
                result.append((nodeCD, newProps))

        return result

    def _changeNext2Unlock(self, nodeCD, unlockProps, unlockStats):
        state = NODE_STATE.NEXT_2_UNLOCK
        totalXP = self._getAllPossibleXP(unlockProps.parentID, unlockStats)
        if totalXP >= unlockProps.xpCost:
            state = NODE_STATE.addIfNot(state, NODE_STATE.ENOUGH_XP)
        else:
            state = NODE_STATE.removeIfHas(state, NODE_STATE.ENOUGH_XP)
        if self.getItem(nodeCD).isElite:
            state = NODE_STATE.addIfNot(state, NODE_STATE.ELITE)
        try:
            data = self._nodes[self._nodesIdx[nodeCD]]
            data['state'] = state
            data['unlockProps'] = unlockProps
        except KeyError:
            LOG_CURRENT_EXCEPTION()

        return state

    def _change2UnlockedByCD(self, nodeCD):
        try:
            node = self._nodes[self._nodesIdx[nodeCD]]
        except KeyError:
            LOG_CURRENT_EXCEPTION()
            return 0

        return self._change2Unlocked(node)

    def _getNodeData(self, nodeCD, guiItem, unlockStats, displayInfo):
        earnedXP = unlockStats.getVehXP(nodeCD)
        state = NODE_STATE.LOCKED
        available, unlockProps = g_techTreeDP.isNext2Unlock(nodeCD, **unlockStats._asdict())
        if guiItem.isUnlocked:
            state = NODE_STATE.UNLOCKED
            if guiItem.isInInventory:
                state |= NODE_STATE.IN_INVENTORY
                if self._canSell(nodeCD):
                    state |= NODE_STATE.CAN_SELL
            elif self._canBuy(nodeCD):
                state |= NODE_STATE.ENOUGH_MONEY
            if nodeCD in self._wereInBattle:
                state |= NODE_STATE.WAS_IN_BATTLE
            if guiItem.buyPrice != guiItem.defaultPrice:
                state |= NODE_STATE.SHOP_ACTION
        elif available:
            state = NODE_STATE.NEXT_2_UNLOCK
            if self._getAllPossibleXP(unlockProps.parentID, unlockStats) >= unlockProps.xpCost:
                state |= NODE_STATE.ENOUGH_XP
        if guiItem.isElite:
            state |= NODE_STATE.ELITE
        if guiItem.isPremium:
            state |= NODE_STATE.PREMIUM
        if guiItem.isRented and not guiItem.isPremiumIGR:
            state = self._checkExpiredRent(state, guiItem)
            state = self._checkMoneyForRentOrBuy(state, nodeCD)
        if guiItem.isRentable and not guiItem.isInInventory:
            state = self._checkMoneyForRentOrBuy(state, nodeCD)
        if self._isVehicleCanBeChanged():
            state |= NODE_STATE.VEHICLE_CAN_BE_CHANGED
        return {'id': nodeCD,
         'earnedXP': earnedXP,
         'state': state,
         'unlockProps': unlockProps,
         'displayInfo': displayInfo}

    def _canSell(self, nodeCD):
        return self.getItem(nodeCD).canSell

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
                node['state'] |= NODE_STATE.SELECTED
            else:
                LOG_ERROR('Current vehicle not found in inventory', nodeCD)
        elif vehicle.isHidden:
            LOG_DEBUG('Current vehicle is hidden. Is it define in nation tree:', nodeCD)
        else:
            LOG_ERROR('Current vehicle not found in nation tree', nodeCD)
