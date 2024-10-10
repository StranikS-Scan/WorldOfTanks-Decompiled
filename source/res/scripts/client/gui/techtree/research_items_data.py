# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/techtree/research_items_data.py
import logging
from gui.techtree import nodes
from gui.techtree.data import _ItemsData, _checkCollectibleEnabled
from gui.techtree.settings import NODE_STATE, MAX_PATH_LIMIT, RESEARCH_ITEMS, UnlockProps, DEFAULT_UNLOCK_PROPS
from gui.techtree.techtree_dp import g_techTreeDP
from gui.impl.gen.view_models.views.lobby.techtree.node_state_flags import NodeStateFlags
from gui.game_control.veh_comparison_basket import getInstalledModulesCDs
from gui.shop import canBuyGoldForItemThroughWeb
from gui.shared.economics import getGUIPrice
from gui.shared.gui_items import GUI_ITEM_TYPE
from helpers import dependency
from items import ITEM_TYPE_NAMES, getTypeOfCompactDescr as getTypeOfCD, vehicles as vehicles_core
from shared_utils.vehicle_utils import ModuleDependencies
from skeletons.gui.shared import IItemsCache
_logger = logging.getLogger(__name__)

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
                state = NODE_STATE.remove(state, NodeStateFlags.DASHED)
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
                state = NODE_STATE.add(state, NodeStateFlags.DASHED)
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
                state = NODE_STATE.add(state, NodeStateFlags.INSTALLED)
            else:
                state = NODE_STATE.remove(state, NodeStateFlags.INSTALLED)
            if item.itemTypeID == GUI_ITEM_TYPE.VEHICLE and item.isElite:
                state = NODE_STATE.add(state, NodeStateFlags.ELITE)
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
            if available and state & NodeStateFlags.LOCKED > 0:
                state ^= NodeStateFlags.LOCKED
                state = NODE_STATE.addIfNot(state, NodeStateFlags.NEXT_2_UNLOCK)
                if xp >= unlockProps.xpCost:
                    state = NODE_STATE.addIfNot(state, NodeStateFlags.ENOUGH_XP)
                else:
                    state = NODE_STATE.removeIfHas(state, NodeStateFlags.ENOUGH_XP)
                state = NODE_STATE.addIfNot(state, NodeStateFlags.BLUEPRINT)
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
        state = NodeStateFlags.LOCKED
        if topLevel and itemTypeID == GUI_ITEM_TYPE.VEHICLE:
            available, unlockProps = g_techTreeDP.isNext2Unlock(nodeCD, level=guiItem.level, **unlockStats._asdict())
            xp = g_techTreeDP.getAllVehiclePossibleXP(unlockProps.parentID, unlockStats)
        if guiItem.isUnlocked:
            state = NodeStateFlags.UNLOCKED
            if itemTypeID != GUI_ITEM_TYPE.VEHICLE and rootItem.isInInventory and guiItem.isInstalled(rootItem) and not rootItem.rentalIsOver:
                state |= NodeStateFlags.INSTALLED
            elif guiItem.isInInventory:
                if rootItem.isInInventory or itemTypeID == GUI_ITEM_TYPE.VEHICLE:
                    state |= NodeStateFlags.IN_INVENTORY
                if self._canSell(nodeCD):
                    state |= NodeStateFlags.CAN_SELL
            elif canBuyGoldForItemThroughWeb(nodeCD) or self._mayObtainForMoney(nodeCD):
                state |= NodeStateFlags.ENOUGH_MONEY
            if nodeCD in self._wereInBattle:
                state |= NodeStateFlags.WAS_IN_BATTLE
            if guiItem.buyPrices.itemPrice.isActionPrice() and not self.bootcamp.isInBootcamp():
                state |= NodeStateFlags.ACTION
        else:
            if not topLevel:
                available = unlockStats.isSeqUnlocked(unlockProps.required) and unlockStats.isUnlocked(self._rootCD) or itemTypeID == GUI_ITEM_TYPE.VEHICLE and guiItem.isEarlyAccess and unlockStats.isUnlocked(self._rootCD)
                xp = g_techTreeDP.getAllVehiclePossibleXP(self._rootCD, unlockStats)
            if available:
                state = NodeStateFlags.NEXT_2_UNLOCK
                if xp >= unlockProps.xpCost:
                    state |= NodeStateFlags.ENOUGH_XP
            if itemTypeID == GUI_ITEM_TYPE.VEHICLE and unlockProps.discount:
                state |= NodeStateFlags.ACTION
        if itemTypeID == GUI_ITEM_TYPE.VEHICLE:
            if guiItem.isElite:
                state |= NodeStateFlags.ELITE
            if guiItem.isPremium:
                state |= NodeStateFlags.PREMIUM
            if guiItem.isCollectible:
                state |= NodeStateFlags.COLLECTIBLE
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
                state |= NodeStateFlags.VEHICLE_CAN_BE_CHANGED
            if guiItem.isHidden:
                state |= NodeStateFlags.PURCHASE_DISABLED
            state = self._checkRestoreState(state, guiItem)
            state = self._checkRentableState(state, guiItem)
            state = self._checkTradeInState(state, guiItem)
            state = self._checkTechTreeEvents(state, guiItem, unlockProps)
            state = self._checkEarlyAccessState(state, guiItem)
            bpfProps = self._getBlueprintsProps(nodeCD, rootItem.level)
            if bpfProps is not None and bpfProps.totalCount > 0:
                state |= NodeStateFlags.BLUEPRINT
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
        state = NodeStateFlags.NOT_CLICKABLE
        state |= NodeStateFlags.ANNOUNCEMENT
        if info.isElite:
            state |= NodeStateFlags.ELITE
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
            node.addStateFlag(NodeStateFlags.AUTO_UNLOCKED)
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
