# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/techtree/unlock.py
from collections import namedtuple
import BigWorld
from debug_utils import LOG_ERROR, LOG_DEBUG
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.Scaleform.daapi.view import dialogs
from gui.techtree.settings import RequestState, UnlockStats
from gui.techtree.techtree_dp import g_techTreeDP
from gui.impl import backport
from gui.shared import event_dispatcher
from gui.shared.formatters import text_styles
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.gui_items.processors import Processor, plugins as proc_plugs
UnlockItemCtx = namedtuple('UnlockItemCtx', ('itemCD', 'itemTypeID', 'parentCD', 'unlockIdx'))

def makeCostCtx(vehXP, xpCost, xpDiscount):
    freeXP = xpCost - vehXP
    if freeXP < 0:
        freeXP = 0
    if xpCost < vehXP:
        vehXP = xpCost
    return {'xpCost': xpCost,
     'vehXP': vehXP,
     'freeXP': freeXP,
     'xpDiscount': xpDiscount}


class UnlockItemConfirmator(proc_plugs.DialogAbstractConfirmator):

    def __init__(self, unlockCtx, costCtx, activeHandler=None, isEnabled=True):
        super(UnlockItemConfirmator, self).__init__(activeHandler, isEnabled)
        self._unlockCtx = unlockCtx
        self._costCtx = costCtx
        self.__itemType = None
        g_clientUpdateManager.addCallbacks({'serverSettings.blueprints_config.isEnabled': self.__onBlueprintsModeChanged,
         'serverSettings.blueprints_config.useBlueprintsForUnlock': self.__onBlueprintsModeChanged})
        return

    def __del__(self):
        self.__destroy()
        super(UnlockItemConfirmator, self).__del__()

    def _makeMeta(self):
        item = self.itemsCache.items.getItemByCD(self._unlockCtx.itemCD)
        xpCost = backport.getIntegralFormat(self._costCtx['xpCost'])
        freeXp = backport.getIntegralFormat(self._costCtx['freeXP'])
        ctx = {'xpCost': text_styles.expText(xpCost),
         'freeXP': text_styles.expText(freeXp),
         'typeString': item.userType,
         'userString': item.userName}
        self.__itemType = item.itemTypeID
        if self.__itemType == GUI_ITEM_TYPE.VEHICLE:
            key = 'confirmUnlockVehicle'
        else:
            key = 'confirmUnlockItem'
        return dialogs.I18nConfirmDialogMeta('confirmUnlock', meta=dialogs.HtmlMessageLocalDialogMeta('html_templates:lobby/dialogs', key, ctx=ctx))

    def __destroy(self):
        self._unlockCtx = None
        self._costCtx = None
        self.__itemType = None
        g_clientUpdateManager.removeObjectCallbacks(self)
        return

    def __onBlueprintsModeChanged(self, _):
        if self.__itemType == GUI_ITEM_TYPE.VEHICLE:
            self.__destroy()
            event_dispatcher.showHangar()


class UnlockItemValidator(proc_plugs.SyncValidator):

    def __init__(self, unlockCtx, costCtx, isEnabled=True):
        super(UnlockItemValidator, self).__init__(isEnabled)
        self.__unlockCtx = unlockCtx
        self.__costCtx = costCtx

    def __del__(self):
        self.__unlockCtx = None
        self.__costCtx = None
        return

    def _validate(self):
        itemCD, itemTypeID, parentCD, unlockIdx = self.__unlockCtx[:]
        itemGetter = self.itemsCache.items.getItemByCD
        vehicle = itemGetter(parentCD)
        item = itemGetter(itemCD)
        xpCost = self.__costCtx['xpCost']
        if vehicle.itemTypeID != GUI_ITEM_TYPE.VEHICLE:
            LOG_ERROR('Int compact descriptor is not for vehicle', parentCD)
            return proc_plugs.makeError('vehicle_invalid')
        if not vehicle.isUnlocked:
            LOG_ERROR('Vehicle is not unlocked', itemCD, parentCD)
            return proc_plugs.makeError('vehicle_locked')
        if item.isUnlocked:
            return proc_plugs.makeError('already_unlocked')
        stats = self.itemsCache.items.stats
        unlockStats = UnlockStats(stats.unlocks, stats.vehiclesXPs, stats.freeXP)
        if itemTypeID == GUI_ITEM_TYPE.VEHICLE:
            result, _ = g_techTreeDP.isNext2Unlock(itemCD, **unlockStats._asdict())
            if not result:
                LOG_ERROR('Required items are not unlocked', self.__unlockCtx)
                return proc_plugs.makeError('required_locked')
        else:
            _xpCost, _itemCD, required = vehicle.getUnlocksDescr(unlockIdx)
            if _itemCD != itemCD:
                LOG_ERROR('Item is invalid', self.__unlockCtx)
                return proc_plugs.makeError('item_invalid')
            if _xpCost != xpCost:
                LOG_ERROR('XP cost is invalid', self.__unlockCtx)
                return proc_plugs.makeError('xp_cost_invalid')
            if not unlockStats.isSeqUnlocked(required):
                LOG_ERROR('Required items are not unlocked', self.__unlockCtx)
                return proc_plugs.makeError('required_locked')
        if unlockStats.getVehTotalXP(parentCD) < xpCost:
            LOG_ERROR('XP not enough for unlock', self.__unlockCtx)
            return proc_plugs.makeError()
        return proc_plugs.makeError('in_processing') if RequestState.inProcess('unlock') else proc_plugs.makeSuccess()


class UnlockItemProcessor(Processor):

    def __init__(self, vehTypeCD, unlockIdx, plugins=None):
        if plugins is None:
            plugins = []
        super(UnlockItemProcessor, self).__init__(plugins)
        self.vehTypeCD = vehTypeCD
        self.unlockIdx = unlockIdx
        return

    def _request(self, callback):
        RequestState.sent('unlock')
        BigWorld.player().stats.unlock(self.vehTypeCD, self.unlockIdx, lambda code: self._response(code, callback))

    def _response(self, code, callback, errStr='', ctx=None):
        LOG_DEBUG('Server response', code, errStr, ctx)
        RequestState.received('unlock')
        return callback(self._errorHandler(code, errStr='server_error', ctx=ctx)) if code < 0 else callback(self._successHandler(code, ctx=ctx))
