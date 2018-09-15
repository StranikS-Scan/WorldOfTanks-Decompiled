# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/techtree/data.py
from AccountCommands import LOCK_REASON
from CurrentVehicle import g_currentVehicle
from debug_utils import LOG_CURRENT_EXCEPTION, LOG_DEBUG, LOG_ERROR
from gui.Scaleform.genConsts.NODE_STATE_FLAGS import NODE_STATE_FLAGS
from gui.prb_control import prbDispatcherProperty
from gui.Scaleform.daapi.view.lobby.techtree.dumpers import _BaseDumper
from gui.shared.economics import getGUIPrice
from gui.Scaleform.daapi.view.lobby.techtree.settings import NODE_STATE, MAX_PATH_LIMIT, SelectedNation
from gui.Scaleform.daapi.view.lobby.techtree.settings import RESEARCH_ITEMS
from gui.Scaleform.daapi.view.lobby.techtree.settings import UnlockProps, UnlockStats
from gui.Scaleform.daapi.view.lobby.techtree.settings import makeDefUnlockProps
from gui.Scaleform.daapi.view.lobby.techtree.techtree_dp import g_techTreeDP
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.utils.requesters import REQ_CRITERIA
from helpers import dependency
from items import ITEM_TYPE_NAMES, getTypeOfCompactDescr as getTypeOfCD, vehicles as vehicles_core
from skeletons.gui.game_control import ITradeInController
from skeletons.gui.shared import IItemsCache
__all__ = ('ResearchItemsData', 'NationTreeData')

class _ItemsData(object):
    """
     Class for storing data of nodes.
    """
    tradeIn = dependency.descriptor(ITradeInController)

    @dependency.replace_none_kwargs(itemsCache=IItemsCache)
    def __init__(self, dumper, itemsCache=None):
        super(_ItemsData, self).__init__()
        if dumper is not None and isinstance(dumper, _BaseDumper):
            self._dumper = dumper
        else:
            raise Exception('Dumper is invalid.')
        self._nodes = []
        self._nodesIdx = {}
        self._items = itemsCache.items
        self._stats = itemsCache.items.stats
        self._wereInBattle = self._getNodesWereInBattle()
        return

    def _isVehicleCanBeChanged(self):
        vehicleCanBeChanged = False
        if self.prbDispatcher is not None:
            permission = self.prbDispatcher.getGUIPermissions()
            if permission is not None:
                vehicleCanBeChanged = permission.canChangeVehicle()
        return vehicleCanBeChanged

    def _checkMoney(self, state, nodeCD):
        state = NODE_STATE.removeIfHas(state, NODE_STATE_FLAGS.ENOUGH_MONEY)
        if self._mayObtainForMoney(nodeCD):
            state |= NODE_STATE_FLAGS.ENOUGH_MONEY
        return state

    def _checkRestoreState(self, state, item):
        state = NODE_STATE.removeIfHas(state, NODE_STATE_FLAGS.RESTORE_AVAILABLE)
        money = self._stats.money
        exchangeRate = self._items.shop.exchangeRate
        mayRent, rentReason = item.mayRent(money)
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
        if not item.isRented and item.isRentable and item.isRentAvailable:
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

    @prbDispatcherProperty
    def prbDispatcher(self):
        return None

    def __del__(self):
        LOG_DEBUG('Data deleted:', self)

    def clear(self, full=False):
        """
        Clears data.
        :param full: if value equals True than removes references that
        set in __init__, otherwise - clears nodes data only.
        """
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
        """
        Gets gui item by itemCD.
        :param itemCD: item compact descriptor (int type).
        :return: instance of gui item. @see gui.shared.gui_items.
        """
        return self._items.getItemByCD(itemCD)

    def getRootItem(self):
        """
        Gets root vehicle.
        :return: instance of Vehicle. @see gui.shared.gui_items.
        """
        raise NotImplementedError('Must be overridden in subclass')

    def getInventoryVehicles(self):
        """
        Gets vehicles from inventory.
        :return: dict( <inventoryID> : <gui item>, ... ).
        """
        nodeCDs = map(lambda node: node['id'], self._getNodesToInvalidate())
        LOG_DEBUG('getInventoryVehicles', nodeCDs)
        inventory_vehicles = self._items.getVehicles(REQ_CRITERIA.INVENTORY | REQ_CRITERIA.IN_CD_LIST(nodeCDs))
        return dict(map(lambda item: (item.invID, item), inventory_vehicles.itervalues()))

    def getVehicleCDs(self):
        """
        :return: list with vehicle compact descriptors
        """
        return [ i['id'] for i in self._getNodesToInvalidate() if getTypeOfCD(i['id']) == GUI_ITEM_TYPE.VEHICLE ]

    def getUnlockStats(self):
        """
        Gets statistics to resolve unlock states for nodes.
        :return: instance of UnlockStats.
        """
        return UnlockStats(self._stats.unlocks, self._stats.vehiclesXPs, self._stats.freeXP)

    def dump(self):
        """
        Gets data dump.
        :return: data representation.
        """
        return self._dumper.dump(self)

    def invalidateCredits(self):
        """
        Updates states of nodes for which changed their access to buy after
        updates value of credits.
        :return: [(<int:vehicle compact descriptor>, <new state>), ... ]
        """
        return self._invalidateMoney(filter(lambda item: NODE_STATE.isBuyForCredits(item['state']), self._getNodesToInvalidate()))

    def invalidateGold(self):
        """
        Updates states of nodes for which changed their access to buy after
        updates value of gold.
        :return: [(<int:vehicle compact descriptor>, <new state>), ... ]
        """
        return self._invalidateMoney(filter(lambda item: NODE_STATE.isBuyForGold(item['state']), self._getNodesToInvalidate()))

    def invalidateFreeXP(self):
        """
        Updates states of nodes for which changed their access to unlock after
        updates value of free experience.
        :return: [(<int:vehicle compact descriptor>, <new state>), ... ]
        """
        return self._invalidateXP(filter(lambda item: NODE_STATE_FLAGS.NEXT_2_UNLOCK & item['state'], self._getNodesToInvalidate()))

    def invalidateVTypeXP(self):
        """
        Updates states of nodes that received new value of experience and changed
        their access to unlock.
        :return: [(<int:vehicle compact descriptor>, <new state>), ... ]
        """
        filtered = filter(lambda item: NODE_STATE_FLAGS.NEXT_2_UNLOCK & item['state'], self._getNodesToInvalidate())
        return self._invalidateXP(filtered)

    def invalidateElites(self, elites):
        """
        Updates states of nodes that become elite.
        :param elites: set(<int:item compact descriptor>, ...).
        :return: [(<int:vehicle compact descriptor>, <new state>), ... ].
        """
        return self._addStateFlag(filter(lambda node: node['id'] in elites, self._getNodesToInvalidate()), NODE_STATE_FLAGS.ELITE)

    def invalidateInventory(self, nodeCDs):
        """
        Updates states of nodes that have been purchased.
        :param nodeCDs: list(<int:item compact descriptor>, ...).
        :return: [(<int:vehicle compact descriptor>, <new state>), ... ].
        """
        result = []
        nodes = filter(lambda node: node['id'] in nodeCDs, self._getNodesToInvalidate())
        for node in nodes:
            nodeCD = node['id']
            state = node['state']
            item = self.getItem(nodeCD)
            if item.isInInventory:
                state = NODE_STATE.removeIfHas(state, NODE_STATE_FLAGS.ENOUGH_MONEY)
                state = NODE_STATE.addIfNot(state, NODE_STATE_FLAGS.IN_INVENTORY)
                state = NODE_STATE.removeIfHas(state, NODE_STATE_FLAGS.VEHICLE_IN_RENT)
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
                state = self._checkMoney(state, nodeCD)
            state = self._checkRestoreState(state, item)
            state = self._checkRentableState(state, item)
            state = self._checkTradeInState(state, item)
            node['state'] = state
            result.append((nodeCD, state))

        return result

    def invalidateLocks(self, locks):
        """
        Updates lock status of nodes (in inventory) that received new value.
        :param locks: dict(<inventory ID> : <value of lock>, ...), see AccountCommands.LOCK_REASON.
        :return: True if lock status of nodes has been changed, otherwise - False.
        """
        result = False
        inventory = self.getInventoryVehicles()
        for invID, lock in locks.iteritems():
            if invID in inventory.keys():
                result = True
                break

        return result

    def invalidatePrbState(self):
        """
        Finds vehicles that is in inventory,
        :return: [(<int:vehicle compact descriptor>, <new state>), ... ].
        """
        nodes = self._getNodesToInvalidate()
        canChanged = self._isVehicleCanBeChanged()
        result = []
        for node in nodes:
            nodeCD = node['id']
            state = node['state']
            if getTypeOfCD(nodeCD) == GUI_ITEM_TYPE.VEHICLE:
                item = self.getItem(nodeCD)
                if not item.isInInventory:
                    continue
                if canChanged:
                    state = NODE_STATE.addIfNot(state, NODE_STATE_FLAGS.VEHICLE_CAN_BE_CHANGED)
                else:
                    state = NODE_STATE.removeIfHas(state, NODE_STATE_FLAGS.VEHICLE_CAN_BE_CHANGED)
                if state > -1:
                    node['state'] = state
                    result.append((nodeCD, state))

        return result

    def invalidateDiscounts(self, discountTargets):
        """
        Updates discount prices of nodes
        """
        nodes = self._getNodesToInvalidate()
        for node in nodes:
            if node['id'] in discountTargets:
                return True

        return False

    def invalidateRestore(self, vehicles):
        """
        Updates TechTree if nation vehicles equal selected nation
        """
        for intCD in vehicles:
            _, nationID, _ = vehicles_core.parseIntCompactDescr(intCD)
            if nationID == SelectedNation.getIndex():
                return True

        return False

    def isHasVehicles(self):
        return bool(len(self.getInventoryVehicles()) > 0)

    def _addNode(self, nodeCD, node):
        """
        Adds node to list of nodes.
        :param nodeCD: int-type compact descriptor.
        :param node: dict containing node data.
        :return: integer containing index in list.
        """
        index = len(self._nodes)
        self._nodesIdx[nodeCD] = index
        self._nodes.append(node)
        return index

    def _getNodesWereInBattle(self):
        """
        Gets set of int-type compact descriptors for vehicles that where in battle.
        :return: set([<int-type compact descriptor>, ...])
        """
        accDossier = self._items.getAccountDossier(None)
        return set(accDossier.getTotalStats().getVehicles().keys()) if accDossier else set()

    def _getNodesToInvalidate(self):
        """
        Gets list of nodes where search changes.
        :return: list of nodes.
        """
        return self._nodes

    def _addStateFlag(self, nodes, stateFlag, exclude=None):
        """
        Adds flag to state of node.
        :param nodes: list of nodes where add flag.
        :param stateFlag: value of flag.
        :param exclude: value of flag to exclude.
        :return: list( (<node ID>, <new state>), ... ) for nodes where changed the state.
        """
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
        """
        Changes state of node to 'unlocked'.
        :param node: node data.
        :return: int containing new state of node.
        """
        state = NODE_STATE.change2Unlocked(node['state'])
        if state < 0:
            return node['state']
        node['state'] = state
        if self._mayObtainForMoney(node['id']):
            state = NODE_STATE.add(state, NODE_STATE_FLAGS.ENOUGH_MONEY)
        else:
            state = NODE_STATE.remove(state, NODE_STATE_FLAGS.ENOUGH_MONEY)
        if state < 0:
            return node['state']
        node['state'] = state
        return state

    def _mayObtainForMoney(self, nodeCD):
        """
        Can player rent or buy or restore item by nodeCD.
        :param nodeCD: int-type compact descriptor.
        :return: bool.
        """
        item = self.getItem(nodeCD)
        money = self._stats.money
        if item.itemTypeID == GUI_ITEM_TYPE.VEHICLE:
            money = self.tradeIn.addTradeInPriceIfNeeded(item, money)
        return item.mayObtainWithMoneyExchange(money, self._items.shop.exchangeRate)

    def _canSell(self, nodeCD):
        """
        Can player sell item by nodeCD.
        :param nodeCD: int-type compact descriptor.
        :return: bool.
        """
        raise NotImplementedError

    def _invalidateMoney(self, nodes):
        """
        Updates states of nodes that have become available/unavailable for purchase.
        :param nodes: list of nodes where search changes.
        :return: list( (<node ID>, <new state>), ... ) for nodes where changed the state.
        """
        result = []
        for node in nodes:
            state = node['state']
            nodeID = node['id']
            node['GUIPrice'] = getGUIPrice(self.getItem(nodeID), self._stats.money, self._items.shop.exchangeRate)
            if self._mayObtainForMoney(nodeID):
                state = NODE_STATE.add(state, NODE_STATE_FLAGS.ENOUGH_MONEY)
            else:
                state = NODE_STATE.remove(state, NODE_STATE_FLAGS.ENOUGH_MONEY)
            if state > -1:
                node['state'] = state
                result.append((nodeID, state))

        return result

    def _invalidateXP(self, nodes):
        """
        Updates states of nodes that have become available/unavailable for unlock.
        :param nodes: list of nodes where search changes.
        :return: list( (<node ID>, <new state>), ... ) for nodes where changed the state.
        """
        result = []
        stats = self.getUnlockStats()
        for node in nodes:
            state = node['state']
            props = node['unlockProps']
            if g_techTreeDP.getAllVehiclePossibleXP(props.parentID, stats) >= props.xpCost:
                state = NODE_STATE.add(state, NODE_STATE_FLAGS.ENOUGH_XP)
            else:
                state = NODE_STATE.remove(state, NODE_STATE_FLAGS.ENOUGH_XP)
            if state > -1:
                node['state'] = state
                result.append((node['id'], state))

        return result


class ResearchItemsData(_ItemsData):
    """
    Nodes data for research items.
    """
    _rootCD = None

    def __init__(self, dumper):
        super(ResearchItemsData, self).__init__(dumper)
        self._autoGunCD = -1
        self._autoTurretCD = -1
        self._topLevel = []
        self._topLevelCDs = {}
        self._installed = []
        self._enableInstallItems = False

    def clear(self, full=False):
        while len(self._topLevel):
            self._topLevel.pop().clear()

        self._topLevelCDs.clear()
        super(ResearchItemsData, self).clear(full=full)

    @classmethod
    def setRootCD(cls, cd):
        """
        Sets root vehicle in research.
        :param cd: int-type compact descriptor.
        """
        cls._rootCD = int(cd)

    @classmethod
    def getRootCD(cls):
        """
        Gets compact descriptor of root vehicle in research.
        :return: int-type compact descriptor.
        """
        return cls._rootCD

    @classmethod
    def clearRootCD(cls):
        """
        Clears root.
        """
        cls._rootCD = None
        return

    @classmethod
    def getNationID(cls):
        result = 0
        if cls._rootCD is not None:
            result = vehicles_core.getVehicleType(cls._rootCD).id[0]
        return result

    def getRootItem(self):
        """
        Gets root vehicle in research.
        :return: instance of Vehicle. @see gui.shared.gui_items.
        """
        rootCD = self.getRootCD()
        assert rootCD is not None
        return self.getItem(rootCD)

    def isRedrawNodes(self, unlocks):
        return self._rootCD in unlocks

    def getRootStatusString(self):
        """
        Returns string containing vehicle status. Note: in current moment show
        'in battle', 'in prebattle', 'destroyed' only (@see WOTD-11097).
        """
        status = None
        item = self.getRootItem()
        if item.isInInventory:
            lockReason = item.lock
            if lockReason == LOCK_REASON.ON_ARENA:
                status = 'battle'
            elif lockReason in (LOCK_REASON.PREBATTLE, LOCK_REASON.UNIT):
                status = 'inPrebattle'
            elif item.repairCost > 0:
                status = 'destroyed'
            elif item.isTelecomDealOver:
                status = 'dealIsOver'
        return status

    def isInstallItemsEnabled(self):
        rootItem = self.getRootItem()
        return rootItem.isInInventory and not rootItem.isLocked and not rootItem.repairCost

    def load(self):
        """
        Loads data of research items for given vehicle (root).
        """
        g_techTreeDP.load()
        self.clear()
        rootItem = self.getRootItem()
        unlockStats = self.getUnlockStats()
        self._loadRoot(rootItem, unlockStats)
        self._loadAutoUnlockItems(rootItem, unlockStats)
        self._loadItems(rootItem, unlockStats)
        self._loadTopLevel(rootItem, unlockStats)

    def invalidateUnlocks(self, unlocks):
        """
        Update status of nodes that became available to unlock or unlock after
        unlocks items (modules, vehicles).
        :param unlocks: set(<int:item compact descriptor>, ...)
        :return: tuple( <list of next to unlock>, <list of unlocked items> ),
           where:
               list of next to unlock - [(
                   <int:item compact descriptor>,
                   <new state>, <instance of UnlockProps>
               ), ... ]
               list of unlocked items - [(
                   <int:item compact descriptor>, <new state>,
               ), ... ]
        """
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
        """
        Finds items that were installed/uninstalled on root vehicle.
        :return: [(<int:item compact descriptor>, <new state>), ... ].
        """
        nodes = self._getNodesToInvalidate()
        rootItem = self.getRootItem()
        result = []
        for node in nodes:
            nodeCD = node['id']
            state = node['state']
            item = self.getItem(nodeCD)
            if rootItem.isInInventory and item.isInstalled(rootItem):
                state = NODE_STATE.add(state, NODE_STATE_FLAGS.INSTALLED)
            else:
                state = NODE_STATE.remove(state, NODE_STATE_FLAGS.INSTALLED)
            if item.itemTypeID == GUI_ITEM_TYPE.VEHICLE and item.isElite:
                state = NODE_STATE.add(state, NODE_STATE_FLAGS.ELITE)
            if state > -1:
                node['state'] = state
                result.append((nodeCD, state))

        return result

    def _addTopNode(self, nodeCD, node):
        """
        Adds node to list of top nodes.
        :param nodeCD: int-type compact descriptor.
        :param node: dict containing node data.
        :return: integer containing index in list.
        """
        index = len(self._topLevel)
        self._topLevelCDs[nodeCD] = index
        self._topLevel.append(node)
        return index

    def _getNodesToInvalidate(self):
        """
        Gets list of nodes where search changes: self_nodes + self._topLevel.
        :return: list of nodes.
        """
        toInvalidate = self._nodes[:]
        toInvalidate.extend(self._topLevel)
        return toInvalidate

    def _findNext2UnlockItems(self, nodes):
        """
        Finds nodes that statuses changed to "next to unlock".
        :param nodes: list of nodes data.
        :return: [(<int:vehicle compact descriptor>, <new state>,
            <new UnlockProps>), ... ].
        """
        result = []
        topLevelCDs = self._topLevelCDs.keys()
        unlockStats = self.getUnlockStats()
        unlockKwargs = unlockStats._asdict()
        for node in nodes:
            nodeCD = node['id']
            state = node['state']
            itemTypeID, _, _ = vehicles_core.parseIntCompactDescr(nodeCD)
            if itemTypeID == GUI_ITEM_TYPE.VEHICLE and (nodeCD in topLevelCDs or nodeCD == self.getRootCD()):
                available, unlockProps = g_techTreeDP.isNext2Unlock(nodeCD, **unlockKwargs)
                xp = g_techTreeDP.getAllVehiclePossibleXP(unlockProps.parentID, unlockStats)
            else:
                unlockProps = node['unlockProps']
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
                node['state'] = state
                result.append((node['id'], state, unlockProps._makeTuple()))

        return result

    def _mayObtainForMoney(self, nodeCD):
        """
        Can player buy item by nodeCD.
        :param nodeCD: int-type compact descriptor.
        :return: bool.
        """
        result = False
        if getTypeOfCD(nodeCD) == GUI_ITEM_TYPE.VEHICLE or self.isInstallItemsEnabled():
            result = super(ResearchItemsData, self)._mayObtainForMoney(nodeCD)
        return result

    def _canSell(self, nodeCD):
        """
        Can player sell item by nodeCD.
        :param nodeCD: int-type compact descriptor.
        :return: bool.
        """
        item = self.getItem(nodeCD)
        if item.isInInventory:
            if getTypeOfCD(nodeCD) == GUI_ITEM_TYPE.VEHICLE:
                canSell = item.canSell
            else:
                canSell = item.isInstalled(self.getRootItem())
        else:
            canSell = False
        return canSell

    def _getRootUnlocksDescrs(self, rootItem):
        return rootItem.getUnlocksDescrs()

    def _getNodeData(self, nodeCD, rootItem, guiItem, unlockStats, unlockProps, path, level=-1, topLevel=False):
        """
        Gets node data that stores to node list.
        """
        itemTypeID = guiItem.itemTypeID
        available = False
        xp = 0
        state = NODE_STATE_FLAGS.LOCKED
        if topLevel and itemTypeID == GUI_ITEM_TYPE.VEHICLE:
            available, unlockProps = g_techTreeDP.isNext2Unlock(nodeCD, **unlockStats._asdict())
            xp = g_techTreeDP.getAllVehiclePossibleXP(unlockProps.parentID, unlockStats)
        if guiItem.isUnlocked:
            state = NODE_STATE_FLAGS.UNLOCKED
            if itemTypeID != GUI_ITEM_TYPE.VEHICLE and rootItem.isInInventory and guiItem.isInstalled(rootItem):
                state |= NODE_STATE_FLAGS.INSTALLED
            elif guiItem.isInInventory:
                if rootItem.isInInventory or itemTypeID == GUI_ITEM_TYPE.VEHICLE:
                    state |= NODE_STATE_FLAGS.IN_INVENTORY
                if self._canSell(nodeCD):
                    state |= NODE_STATE_FLAGS.CAN_SELL
            elif self._mayObtainForMoney(nodeCD):
                state |= NODE_STATE_FLAGS.ENOUGH_MONEY
            if nodeCD in self._wereInBattle:
                state |= NODE_STATE_FLAGS.WAS_IN_BATTLE
            if guiItem.buyPrices.itemPrice.isActionPrice():
                state |= NODE_STATE_FLAGS.SHOP_ACTION
        else:
            if not topLevel:
                available = unlockStats.isSeqUnlocked(unlockProps.required) and unlockStats.isUnlocked(self._rootCD)
                xp = g_techTreeDP.getAllVehiclePossibleXP(self._rootCD, unlockStats)
            if available:
                state = NODE_STATE_FLAGS.NEXT_2_UNLOCK
                if xp >= unlockProps.xpCost:
                    state |= NODE_STATE_FLAGS.ENOUGH_XP
        if itemTypeID == GUI_ITEM_TYPE.VEHICLE:
            if guiItem.isElite:
                state |= NODE_STATE_FLAGS.ELITE
            if guiItem.isPremium:
                state |= NODE_STATE_FLAGS.PREMIUM
            if guiItem.isRented and not guiItem.isPremiumIGR and not guiItem.isTelecom:
                state = self._checkExpiredRent(state, guiItem)
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
            renderer = 'root' if self._rootCD == nodeCD else 'vehicle'
        else:
            renderer = 'item'
        price = getGUIPrice(guiItem, self._stats.money, self._items.shop.exchangeRate)
        return {'id': nodeCD,
         'earnedXP': unlockStats.getVehXP(nodeCD),
         'state': state,
         'unlockProps': unlockProps,
         'GUIPrice': price,
         'displayInfo': {'path': list(path),
                         'renderer': renderer,
                         'level': level}}

    def _loadRoot(self, rootItem, unlockStats):
        """
        First, adds root node. Warning: first node must be root.
        :param rootItem: instance of gui item for root. @see gui.shared.gui_items.
        :param unlockStats: instance of unlockStats.
        """
        rootCD = rootItem.intCD
        node = self._getNodeData(rootCD, rootItem, rootItem, unlockStats, makeDefUnlockProps(), set(), topLevel=True)
        index = self._addNode(rootCD, node)
        assert index == 0, 'Index of root must be 0'

    def _loadAutoUnlockItems(self, rootItem, unlockStats):
        """
        Second, adds auto unlock items by order in _RESEARCH_ITEMS.
        :param rootItem: instance of gui item for root. @see gui.shared.gui_items.
        :param unlockStats: instance of unlockStats.
        """
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
            node = self._getNodeData(nodeCD, rootItem, itemGetter(nodeCD), unlockStats, makeDefUnlockProps(), {rootCD})
            node['state'] |= NODE_STATE_FLAGS.AUTO_UNLOCKED
            self._addNode(nodeCD, node)

    def _loadItems(self, rootItem, unlockStats):
        """
        Third, loads research items.
        :param rootItem: instance of gui item for root. @see gui.shared.gui_items.
        :param unlockStats: instance of unlockStats.
        """
        itemGetter = self.getItem
        rootCD = rootItem.intCD
        maxPath = 0
        nodes = []
        for unlockIdx, xpCost, nodeCD, required in self._getRootUnlocksDescrs(rootItem):
            itemTypeID = getTypeOfCD(nodeCD)
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

    def _loadTopLevel(self, rootItem, unlockStats):
        """
        Fourth, loads vehicles in top level.
        :param rootItem: instance of gui item for root. @see gui.shared.gui_items.
        :param unlockStats: instance of unlockStats.
        """
        itemGetter = self.getItem
        rootCD = self.getRootCD()
        for nodeCD in g_techTreeDP.getTopLevel(rootCD):
            node = self._getNodeData(nodeCD, rootItem, itemGetter(nodeCD), unlockStats, makeDefUnlockProps(), set(), topLevel=True)
            self._addTopNode(nodeCD, node)

    def __fixPath(self, itemTypeID, path):
        """
        Corrects path from root to node:
        - if type of node is turret and path has auto unlocked gun and turret.
        - if type of node is gun and path has auto unlocked gun and turret.
        - if type of node is vehicle and path has auto unlocked gun and turret only.
        :return: list of node IDs in path from root to desired node.
        """
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
        """
        Sets max path to unlocking vehicle to avoid crossing.
        :param itemTypeID: item type index from items.ITEM_TYPE_NAMES.
        :param path: list of node IDs in path from root to desired node.
        :param maxPath: length of max path.
        :return: value of level (length of path) or -1.
        """
        level = -1
        if itemTypeID == GUI_ITEM_TYPE.VEHICLE and len(path) <= maxPath:
            level = min(maxPath + 1, MAX_PATH_LIMIT)
        return level


class NationTreeData(_ItemsData):
    """
    Nodes data in selected nation tree.
    """

    def __init__(self, dumper):
        super(NationTreeData, self).__init__(dumper)
        self._scrollIndex = -1

    def clear(self, full=False):
        self._scrollIndex = -1
        super(NationTreeData, self).clear(full)

    def load(self, nationID, override=None):
        """
        Loads data of nation tree by nationID.
        :param nationID: ID of nation. Index in nations.NAMES.
        """
        self.clear()
        vehicleList = sorted(vehicles_core.g_list.getList(nationID).values(), key=lambda item: item.level)
        g_techTreeDP.setOverride(override)
        g_techTreeDP.load()
        getDisplayInfo = g_techTreeDP.getDisplayInfo
        getItem = self.getItem
        selectedID = ResearchItemsData.getRootCD()
        unlockStats = self.getUnlockStats()
        for item in vehicleList:
            nodeCD = item.compactDescr
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
        """
        Gets root vehicle.
        :return: instance of Vehicle or None. @see gui.shared.gui_items.
        """
        return self._nodes[0] if len(self._nodes) else None

    def invalidateUnlocks(self, unlocks):
        """
        Update status of nodes that became available to unlock or unlock after
        unlocks items (modules, vehicles).
        :param unlocks: set(<int:item compact descriptor>, ...)
        :return:  tuple( <list of next to unlock>, <list of unlocked vehicles> ),
           where:
               list of next to unlock - [(
                   <int:vehicle compact descriptor>,
                   <new state>, <instance of UnlockProps>
               ), ... ]
               list of unlocked vehicles - [(
                   <int:vehicle compact descriptor>, <new state>,
               ), ... ]
        """
        next2Unlock = []
        unlocked = []
        unlockStats = self.getUnlockStats()
        items = g_techTreeDP.getNext2UnlockByItems(unlocks, **unlockStats._asdict())
        if len(items):
            next2Unlock = map(lambda item: (item[0], self._changeNext2Unlock(item[0], item[1], unlockStats), item[1]._makeTuple()), items.iteritems())
        filtered = filter(lambda unlock: getTypeOfCD(unlock) == GUI_ITEM_TYPE.VEHICLE, unlocks)
        if len(filtered):
            unlocked = map(lambda item: (item, self._change2UnlockedByCD(item)), filtered)
        return (next2Unlock, unlocked)

    def invalidateXpCosts(self):
        result = []
        nodes = filter(lambda item: NODE_STATE_FLAGS.NEXT_2_UNLOCK & item['state'], self._getNodesToInvalidate())
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
        state = NODE_STATE_FLAGS.NEXT_2_UNLOCK
        totalXP = g_techTreeDP.getAllVehiclePossibleXP(unlockProps.parentID, unlockStats)
        if totalXP >= unlockProps.xpCost:
            state = NODE_STATE.addIfNot(state, NODE_STATE_FLAGS.ENOUGH_XP)
        else:
            state = NODE_STATE.removeIfHas(state, NODE_STATE_FLAGS.ENOUGH_XP)
        if self.getItem(nodeCD).isElite:
            state = NODE_STATE.addIfNot(state, NODE_STATE_FLAGS.ELITE)
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
        """
        Gets node data that stores to node list.
        """
        earnedXP = unlockStats.getVehXP(nodeCD)
        state = NODE_STATE_FLAGS.LOCKED
        available, unlockProps = g_techTreeDP.isNext2Unlock(nodeCD, **unlockStats._asdict())
        if guiItem.isUnlocked:
            state = NODE_STATE_FLAGS.UNLOCKED
            if guiItem.isInInventory:
                state |= NODE_STATE_FLAGS.IN_INVENTORY
                if self._canSell(nodeCD):
                    state |= NODE_STATE_FLAGS.CAN_SELL
            elif self._mayObtainForMoney(nodeCD):
                state |= NODE_STATE_FLAGS.ENOUGH_MONEY
            if nodeCD in self._wereInBattle:
                state |= NODE_STATE_FLAGS.WAS_IN_BATTLE
            if guiItem.buyPrices.itemPrice.isActionPrice():
                state |= NODE_STATE_FLAGS.SHOP_ACTION
        elif available:
            state = NODE_STATE_FLAGS.NEXT_2_UNLOCK
            if g_techTreeDP.getAllVehiclePossibleXP(unlockProps.parentID, unlockStats) >= unlockProps.xpCost:
                state |= NODE_STATE_FLAGS.ENOUGH_XP
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
        state = self._checkRestoreState(state, guiItem)
        state = self._checkRentableState(state, guiItem)
        state = self._checkTradeInState(state, guiItem)
        price = getGUIPrice(guiItem, self._stats.money, self._items.shop.exchangeRate)
        return {'id': nodeCD,
         'earnedXP': earnedXP,
         'state': state,
         'unlockProps': unlockProps,
         'GUIPrice': price,
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
                node['state'] |= NODE_STATE_FLAGS.SELECTED
            else:
                LOG_ERROR('Current vehicle not found in inventory', nodeCD)
        elif vehicle.isHidden:
            LOG_DEBUG('Current vehicle is hidden. Is it define in nation tree:', nodeCD)
        else:
            LOG_ERROR('Current vehicle not found in nation tree', nodeCD)
