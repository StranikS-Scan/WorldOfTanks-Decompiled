# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/techtree/unlock.py
from collections import namedtuple
import BigWorld
from debug_utils import LOG_ERROR, LOG_DEBUG
from gui.Scaleform.daapi.view import dialogs
from gui.Scaleform.daapi.view.lobby.techtree.settings import RequestState, UnlockStats
from gui.Scaleform.daapi.view.lobby.techtree.techtree_dp import g_techTreeDP
from gui.shared import g_itemsCache
from gui.shared.formatters import text_styles
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.gui_items.processors import Processor, plugins
UnlockItemCtx = namedtuple('UnlockItemCtx', ('unlockCD', 'vehCD', 'unlockIdx', 'xpCost'))

def makeCostCtx(vehXP, xpCost):
    xp = vehXP - xpCost
    freeXP = 0
    if xp < 0:
        xp = vehXP
        freeXP = xpCost - xp
    else:
        xp = xpCost
    return {'vehXP': xp,
     'freeXP': freeXP,
     'xpCost': xpCost}


class UnlockItemConfirmator(plugins.DialogAbstractConfirmator):

    def __init__(self, unlockCtx, costCtx, activeHandler = None, isEnabled = True):
        super(UnlockItemConfirmator, self).__init__(activeHandler, isEnabled)
        self._unlockCtx = unlockCtx
        self._costCtx = costCtx

    def __del__(self):
        super(UnlockItemConfirmator, self).__del__()
        self._unlockCtx = None
        self._costCtx = None
        return

    def _makeMeta(self):
        item = g_itemsCache.items.getItemByCD(self._unlockCtx.unlockCD)
        xpCost = BigWorld.wg_getIntegralFormat(self._costCtx['xpCost'])
        freeXp = BigWorld.wg_getIntegralFormat(self._costCtx['freeXP'])
        ctx = {'xpCost': text_styles.expText(xpCost),
         'freeXP': text_styles.expText(freeXp),
         'typeString': item.userType,
         'userString': item.userName}
        if item.itemTypeID == GUI_ITEM_TYPE.VEHICLE:
            key = 'confirmUnlockVehicle'
        else:
            key = 'confirmUnlockItem'
        return dialogs.I18nConfirmDialogMeta('confirmUnlock', meta=dialogs.HtmlMessageLocalDialogMeta('html_templates:lobby/dialogs', key, ctx=ctx))


class UnlockItemValidator(plugins.SyncValidator):

    def __init__(self, unlockCtx, isEnabled = True):
        super(UnlockItemValidator, self).__init__(isEnabled)
        self._unlockCtx = unlockCtx

    def __del__(self):
        self._unlockCtx = None
        return

    def _validate(self):
        unlockCD, vehCD, unlockIdx, xpCost = self._unlockCtx[:]
        itemGetter = g_itemsCache.items.getItemByCD
        vehicle = itemGetter(vehCD)
        item = itemGetter(unlockCD)
        if vehicle.itemTypeID != GUI_ITEM_TYPE.VEHICLE:
            LOG_ERROR('Int compact descriptor is not for vehicle', vehCD)
            return plugins.makeError('vehicle_invalid')
        if not vehicle.isUnlocked:
            LOG_ERROR('Vehicle is not unlocked', unlockCD, vehCD)
            return plugins.makeError('vehicle_locked')
        if item.isUnlocked:
            return plugins.makeError('already_unlocked')
        stats = g_itemsCache.items.stats
        unlockStats = UnlockStats(stats.unlocks, stats.vehiclesXPs, stats.freeXP)
        if item.itemTypeID == GUI_ITEM_TYPE.VEHICLE:
            result, _ = g_techTreeDP.isNext2Unlock(unlockCD, **unlockStats._asdict())
            if not result:
                LOG_ERROR('Required items are not unlocked', self._unlockCtx)
                return plugins.makeError('required_locked')
        else:
            _xpCost, _itemCD, required = vehicle.getUnlocksDescr(self._unlockCtx.unlockIdx)
            if _itemCD != unlockCD:
                LOG_ERROR('Item is invalid', self._unlockCtx)
                return plugins.makeError('item_invalid')
            if _xpCost != xpCost:
                LOG_ERROR('XP cost is invalid', self._unlockCtx)
                return plugins.makeError('xp_cost_invalid')
            if not unlockStats.isSeqUnlocked(required):
                LOG_ERROR('Required items are not unlocked', self._unlockCtx)
                return plugins.makeError('required_locked')
        if unlockStats.getVehTotalXP(vehCD) < xpCost:
            LOG_ERROR('XP not enough for unlock', self._unlockCtx)
            return plugins.makeError()
        if RequestState.inProcess('unlock'):
            return plugins.makeError('in_processing')
        return plugins.makeSuccess()


class UnlockItemProcessor(Processor):

    def __init__(self, vehTypeCD, unlockIdx, plugins = None):
        if plugins is None:
            plugins = []
        super(UnlockItemProcessor, self).__init__(plugins)
        self.vehTypeCD = vehTypeCD
        self.unlockIdx = unlockIdx
        return

    def _request(self, callback):
        RequestState.sent('unlock')
        BigWorld.player().stats.unlock(self.vehTypeCD, self.unlockIdx, lambda code: self._response(code, callback))

    def _response(self, code, callback, errStr = '', ctx = None):
        LOG_DEBUG('Server response', code, errStr, ctx)
        RequestState.received('unlock')
        if code < 0:
            return callback(self._errorHandler(code, errStr='server_error', ctx=ctx))
        return callback(self._successHandler(code, ctx=ctx))
