# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/techtree/ResearchView.py
import BigWorld
from CurrentVehicle import g_currentVehicle
from debug_utils import LOG_ERROR, LOG_DEBUG, LOG_WARNING
import enumerations
from gui import SystemMessages
from gui.Scaleform.daapi import LobbySubView
from gui.Scaleform.daapi.view.lobby.techtree import unlock
from gui.Scaleform.daapi.view.meta.ResearchViewMeta import ResearchViewMeta
from gui.Scaleform.daapi.view.lobby.techtree import NODE_STATE
from gui.Scaleform.daapi.view.lobby.techtree.listeners import TTListenerDecorator
from gui.shared import events, g_itemsCache
from gui.shared.event_bus import EVENT_BUS_SCOPE
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.utils import gui_items
from gui.shared.utils.decorators import process
from helpers import i18n

class ResearchView(LobbySubView, ResearchViewMeta):
    MSG_SCOPE = enumerations.Enumeration('Message scope', [('Unlocks', lambda entity, msg: '#system_messages:unlocks/{0:>s}/{1:>s}'.format(entity, msg)),
     ('Shop', lambda entity, msg: '#system_messages:shop/{0:>s}/{1:>s}'.format(entity, msg)),
     ('Inventory', lambda entity, msg: '#system_messages:inventory/{0:>s}/{1:>s}'.format(entity, msg)),
     ('Dialog', lambda entity, msg: '#dialogs:techtree/{0:>s}/{1:>s}'.format(entity, msg))], instance=enumerations.CallabbleEnumItem)

    def __init__(self, data):
        super(ResearchView, self).__init__(backAlpha=0)
        self._data = data
        self._canBeClosed = True
        self._listener = TTListenerDecorator()

    def showModuleInfo(self, itemCD):
        itemCD = int(itemCD)
        vehicleDescr = self._data.getRootItem().descriptor
        self.fireEvent(events.ShowWindowEvent(events.ShowWindowEvent.SHOW_MODULE_INFO_WINDOW, {'moduleCompactDescr': itemCD,
         'vehicleDescr': vehicleDescr}))

    def showVehicleInfo(self, itemCD):
        self.fireEvent(events.ShowWindowEvent(events.ShowWindowEvent.SHOW_VEHICLE_INFO_WINDOW, {'vehicleCompactDescr': int(itemCD)}))

    def selectVehicleInHangar(self, itemCD):
        veh = self._data.getItem(int(itemCD))
        raise veh.isInInventory or AssertionError('Vehicle must be in inventory.')
        g_currentVehicle.selectVehicle(veh.invID)

    def showVehicleStatistics(self, itemCD):
        self.fireEvent(events.LoadEvent(events.LoadEvent.LOAD_PROFILE, {'itemCD': itemCD}), scope=EVENT_BUS_SCOPE.LOBBY)

    def redraw(self):
        raise NotImplementedError, 'Must be overridden in subclass'

    def unlockItem(self, unlockCD, vehCD, unlockIdx, xpCost):
        costCtx = self.getCostCtx(vehCD, xpCost)
        unlockCtx = unlock.UnlockItemCtx(unlockCD, vehCD, unlockIdx, xpCost)
        plugins = [unlock.UnlockItemConfirmator(unlockCtx, costCtx), unlock.UnlockItemValidator(unlockCtx)]
        self._doUnlockItem(unlockCtx, costCtx, plugins)

    def getCostCtx(self, vehCD, xpCost):
        return unlock.makeCostCtx(self._data.getUnlockStats().getVehXP(vehCD), xpCost)

    def buyVehicle(self, vehCD):
        item = self._data.getItem(vehCD)
        if item.itemTypeID is not GUI_ITEM_TYPE.VEHICLE:
            LOG_ERROR('Value of int-type descriptor is not refer to vehicle', vehCD)
            return
        else:
            if item.isInInventory and not item.isRented:
                self._showMessage(self.MSG_SCOPE.Inventory, 'already_exists', item, msgType=SystemMessages.SM_TYPE.Warning)
            else:
                price = item.minRentPrice or item.buyPrice
                money = g_itemsCache.items.stats.money
                if price is None:
                    self._showMessage(self.MSG_SCOPE.Shop, 'not_found', item)
                    return
                canRentOrBuy, reason = item.mayRentOrBuy(money)
                if canRentOrBuy:
                    self._showVehicleBuyWindow(item)
                else:
                    self._showMessage(self.MSG_SCOPE.Shop, 'common_rent_or_buy_error', item)
                    LOG_WARNING('Vehicle ' + item.userName + ' cannot be buy or rent, reason: ' + reason)
            return

    def _showVehicleBuyWindow(self, item):
        self.fireEvent(events.ShowWindowEvent(events.ShowWindowEvent.SHOW_VEHICLE_BUY_WINDOW, {'nationID': item.nationID,
         'itemID': item.innationID}))

    def _sendMoneyValidationMsg(self, price, item, errorID):
        stats = g_itemsCache.items.stats
        money = [price[0] - stats.credits if price[0] > 0 else 0, price[1] - stats.gold if price[1] > 0 else 0]
        self._showMessage(self.MSG_SCOPE.Shop, errorID, item, price=gui_items.formatPrice(money))

    def sellVehicle(self, vehCD):
        item = self._data.getItem(vehCD)
        if item.itemTypeID is not GUI_ITEM_TYPE.VEHICLE:
            LOG_ERROR('Value of int-type descriptor is not refer to vehicle', vehCD)
            return
        if item.isInInventory:
            self.fireEvent(events.ShowWindowEvent(events.ShowWindowEvent.SHOW_VEHICLE_SELL_DIALOG, {'vehInvID': item.inventoryID}))
        else:
            self._showMessage(self.MSG_SCOPE.Inventory, 'not_found', item)

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

    def _showMessage(self, scope, msg, item, msgType = SystemMessages.SM_TYPE.Error, **kwargs):
        kwargs['userString'] = item.userName
        if item.itemTypeID == GUI_ITEM_TYPE.VEHICLE:
            key = scope('vehicle', msg)
        else:
            key = scope('item', msg)
            kwargs['typeString'] = item.userType
        SystemMessages.pushMessage(i18n.makeString(key, **kwargs), type=msgType)

    @process('research')
    def _doUnlockItem(self, unlockCtx, costCtx, plugins):
        self._canBeClosed = False
        result = yield unlock.UnlockItemProcessor(unlockCtx.vehCD, unlockCtx.unlockIdx, plugins=plugins).request()
        self._canBeClosed = True
        if result.success:
            costCtx['xpCost'] = BigWorld.wg_getIntegralFormat(costCtx['xpCost'])
            costCtx['freeXP'] = BigWorld.wg_getIntegralFormat(costCtx['freeXP'])
            self._showMessage(self.MSG_SCOPE.Unlocks, 'unlock_success', self._data.getItem(unlockCtx.unlockCD), msgType=SystemMessages.SM_TYPE.PowerLevel, **costCtx)
        elif len(result.userMsg):
            self._showMessage(self.MSG_SCOPE.Unlocks, result.userMsg, self._data.getItem(unlockCtx.unlockCD))
