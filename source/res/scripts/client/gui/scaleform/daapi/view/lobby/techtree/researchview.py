# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/techtree/ResearchView.py
from debug_utils import LOG_DEBUG
from gui import SystemMessages
from gui.Scaleform.daapi import LobbySubView
from gui.Scaleform.daapi.view.meta.ResearchViewMeta import ResearchViewMeta
from gui.Scaleform.daapi.view.lobby.techtree.settings import NODE_STATE
from gui.Scaleform.daapi.view.lobby.techtree.listeners import TTListenerDecorator
from gui.shared import g_itemsCache, event_dispatcher as shared_events

class ResearchView(LobbySubView, ResearchViewMeta):
    __background_alpha__ = 0.0

    def __init__(self, data):
        super(ResearchView, self).__init__()
        self._data = data
        self._canBeClosed = True
        self._listener = TTListenerDecorator()

    def redraw(self):
        raise NotImplementedError, 'Must be overridden in subclass'

    def showSystemMessage(self, typeString, message):
        msgType = SystemMessages.SM_TYPE.lookup(typeString)
        if msgType is None:
            msgType = SystemMessages.SM_TYPE.Error
        SystemMessages.pushMessage(message, msgType)
        return

    def invalidateCredits(self):
        result = self._data.invalidateCredits()
        if len(result):
            self.as_setNodesStatesS(NODE_STATE.ENOUGH_MONEY, result)

    def invalidateGold(self):
        result = self._data.invalidateGold()
        if len(result):
            self.as_setNodesStatesS(NODE_STATE.ENOUGH_MONEY, result)
        self.invalidateFreeXP()
        self.invalidateCredits()

    def invalidateFreeXP(self):
        result = self._data.invalidateFreeXP()
        if len(result):
            self.as_setNodesStatesS(NODE_STATE.ENOUGH_XP, result)

    def invalidateElites(self, elites):
        result = self._data.invalidateElites(elites)
        if len(result):
            self.as_setNodesStatesS(NODE_STATE.ELITE, result)

    def invalidateVTypeXP(self, xps):
        self.as_setVehicleTypeXPS(xps.items())
        result = self._data.invalidateVTypeXP()
        if len(result):
            self.as_setNodesStatesS(NODE_STATE.ENOUGH_XP, result)

    def invalidateUnlocks(self, unlocks):
        next2Unlock, unlocked = self._data.invalidateUnlocks(unlocks)
        if len(unlocked):
            LOG_DEBUG('unlocked', unlocked)
            self.as_setNodesStatesS(NODE_STATE.UNLOCKED, unlocked)
        if len(next2Unlock):
            LOG_DEBUG('next2Unlock', next2Unlock)
            self.as_setNext2UnlockS(next2Unlock)

    def invalidateInventory(self, data):
        result = self._data.invalidateInventory(data)
        if len(result):
            self.as_setInventoryItemsS(result)

    def invalidatePrbState(self):
        result = self._data.invalidatePrbState()
        if len(result):
            self.as_setNodesStatesS(NODE_STATE.VEHICLE_CAN_BE_CHANGED, result)

    def invalidateVehLocks(self, locks):
        raise NotImplementedError, 'Must be overridden in subclass'

    def invalidateWalletStatus(self, status):
        raise NotImplementedError, 'Must be overridden in subclass'

    def invalidateRent(self, vehicles):
        raise NotImplementedError, 'Must be overridden in subclass'

    def request4SelectInHangar(self, itemCD):
        shared_events.selectVehicleInHangar(itemCD)

    def request4Info(self, itemCD, rootCD):
        vehicle = g_itemsCache.items.getItemByCD(int(rootCD))
        if vehicle:
            shared_events.showModuleInfo(int(itemCD), vehicle.descriptor)

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
