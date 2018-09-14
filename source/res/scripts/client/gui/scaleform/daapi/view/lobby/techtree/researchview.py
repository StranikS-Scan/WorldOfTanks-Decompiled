# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/techtree/ResearchView.py
from debug_utils import LOG_DEBUG
from gui import SystemMessages
from gui.Scaleform.daapi import LobbySubView
from gui.Scaleform.daapi.view.lobby.techtree.listeners import TTListenerDecorator
from gui.Scaleform.daapi.view.lobby.vehicle_compare.formatters import getTreeNodeCompareData
from gui.Scaleform.daapi.view.meta.ResearchViewMeta import ResearchViewMeta
from gui.Scaleform.genConsts.NODE_STATE_FLAGS import NODE_STATE_FLAGS
from gui.shared import event_dispatcher as shared_events
from helpers import dependency
from skeletons.gui.game_control import IWalletController, IVehicleComparisonBasket
from skeletons.gui.shared import IItemsCache

class ResearchView(LobbySubView, ResearchViewMeta):
    """
    Common interface to items (vehicle, module) in window of research modules, nation tree:
    - unlocks item;
    - buy vehicles;
    - shows messages in service channel.
    - refreshes data by server diff.
    """
    __background_alpha__ = 0.0
    itemsCache = dependency.descriptor(IItemsCache)
    wallet = dependency.descriptor(IWalletController)
    cmpBasket = dependency.descriptor(IVehicleComparisonBasket)

    def __init__(self, data):
        super(ResearchView, self).__init__()
        self._data = data
        self._canBeClosed = True
        self._listener = TTListenerDecorator()

    def redraw(self):
        """
        Redraws all nodes in view.
        """
        raise NotImplementedError('Must be overridden in subclass')

    def showSystemMessage(self, typeString, message):
        """
        Shows system message.
        :param typeString: string containing 'Error', 'Warning' or 'Information'.
        :param message: text of message.
        """
        msgType = SystemMessages.SM_TYPE.lookup(typeString)
        if msgType is None:
            msgType = SystemMessages.SM_TYPE.Error
        SystemMessages.pushMessage(message, msgType)
        return

    def invalidateCredits(self):
        """
        Value of credits updated.
        """
        result = self._data.invalidateCredits()
        if len(result):
            self.as_setNodesStatesS(NODE_STATE_FLAGS.ENOUGH_MONEY, result)

    def invalidateGold(self):
        """
        Value of gold updated.
        """
        result = self._data.invalidateGold()
        if len(result):
            self.as_setNodesStatesS(NODE_STATE_FLAGS.ENOUGH_MONEY, result)
        self.invalidateFreeXP()
        self.invalidateCredits()

    def invalidateFreeXP(self):
        """
        Value of free experience updated.
        """
        result = self._data.invalidateFreeXP()
        if len(result):
            self.as_setNodesStatesS(NODE_STATE_FLAGS.ENOUGH_XP, result)

    def invalidateElites(self, elites):
        """
        Set of elite vehicles updated.
        :param elites: set([<compactDescr>, ...])
        """
        result = self._data.invalidateElites(elites)
        if len(result):
            self.as_setNodesStatesS(NODE_STATE_FLAGS.ELITE, result)

    def invalidateVTypeXP(self, xps):
        """
        Dict of vehicles experience updated.
        :param xps: dict(<int:vehicle compact descriptor> : <XP>, ...)
        """
        self.as_setVehicleTypeXPS(xps.items())
        result = self._data.invalidateVTypeXP()
        if len(result):
            self.as_setNodesStatesS(NODE_STATE_FLAGS.ENOUGH_XP, result)

    def invalidateUnlocks(self, unlocks):
        """
        Set of unlocks items updated.
        :param unlocks: set([<int:compactDescr>, ...])
        """
        next2Unlock, unlocked = self._data.invalidateUnlocks(unlocks)
        if len(unlocked):
            LOG_DEBUG('unlocked', unlocked)
            self.as_setNodesStatesS(NODE_STATE_FLAGS.UNLOCKED, unlocked)
        if len(next2Unlock):
            LOG_DEBUG('next2Unlock', next2Unlock)
            self.as_setNext2UnlockS(next2Unlock)

    def invalidateInventory(self, data):
        """
        Inventory items are updated, invalidate information about inventory on current page.
        :param data: set of int-type compact descriptors for  modified items (vehicles/modules).
        """
        result = self._data.invalidateInventory(data)
        if len(result):
            self.as_setInventoryItemsS(result)

    def invalidatePrbState(self):
        """
        Player's state has been changed in prebattle, unit, prequeue.
        """
        result = self._data.invalidatePrbState()
        if len(result):
            self.as_setNodesStatesS(NODE_STATE_FLAGS.VEHICLE_CAN_BE_CHANGED, result)

    def invalidateDiscounts(self, data):
        """
        Updates discount prices of nodes
        """
        if self._data.invalidateDiscounts(data):
            self._data.invalidateCredits()
            self._data.invalidateGold()
            self.redraw()

    def invalidateVehLocks(self, locks):
        """
        Updates lock status of vehicles (in inventory) that received new value.
        :param locks: dict(<inventory ID> : <value of lock>, ...), see AccountCommands.LOCK_REASON.
        """
        raise NotImplementedError('Must be overridden in subclass')

    def invalidateWalletStatus(self, status):
        raise NotImplementedError('Must be overridden in subclass')

    def invalidateRent(self, vehicles):
        raise NotImplementedError('Must be overridden in subclass')

    def invalidateRestore(self, vehicles):
        raise NotImplementedError('Must be overridden in subclass')

    def request4Info(self, itemCD, rootCD):
        """
        Overridden method of the class ResearchViewMeta.request4Info
        """
        vehicle = self.itemsCache.items.getItemByCD(int(rootCD))
        if vehicle:
            shared_events.showModuleInfo(int(itemCD), vehicle.descriptor)

    def invalidateVehCompare(self):
        """
        Updates compare add icon status of nodes if change status of comparison basket fullness.
        """
        getVehicle = self.itemsCache.items.getItemByCD

        def getNodeData(vehCD):
            return getTreeNodeCompareData(getVehicle(vehCD))

        self.as_setNodeVehCompareDataS([ (v, getNodeData(v)) for v in self._data.getVehicleCDs() ])

    def _populate(self):
        super(ResearchView, self)._populate()
        self._listener.startListen(self)

    def _dispose(self):
        self._listener.stopListen()
        super(ResearchView, self)._dispose()
        if self._data is not None:
            self._data.clear(full=True)
            self._data = None
        return
