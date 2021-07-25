# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/detachment/detachment_states.py
from AccountCommands import LOCK_REASON
from items import ITEM_TYPES
from soft_exception import SoftException
import crew2.detachment_states
from crew2.detachment_inventory_proxy import CommonPDataInventoryProxy
from helpers import dependency
from skeletons.gui.shared import IItemsCache
from skeletons.gui.detachment import IDetachementStates

class PDataInventoryProxy(CommonPDataInventoryProxy):

    def refresh(self, pdata):
        self._inventory = pdata['inventory']

    def isVehicleLocked(self, vehInvID, lockReasonToIgnore=None):
        lockReason, _ = self._inventory[ITEM_TYPES.vehicle]['lock'].get(vehInvID, (None, None))
        isLocked = lockReason is not None and lockReason != LOCK_REASON.NONE
        if lockReasonToIgnore is None:
            return isLocked
        else:
            return isLocked if isLocked and not lockReason & lockReasonToIgnore else False

    def getVehicleInvID(self, vehTypeCompDescr):
        raise SoftException('not supported')

    def onLevelUp(self, detInvID, newDetDescr, oldDetDescr, isConversionProcess=False):
        raise SoftException('not supported')


class DetachmentStates(IDetachementStates):
    _itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self):
        self._states = None
        self._inventoryProxy = None
        return

    def init(self):
        self._inventoryProxy = PDataInventoryProxy({'inventory': None})
        self._refreshProxy()
        self._states = crew2.detachment_states.DetachmentStates(self._inventoryProxy)
        self._itemsCache.onSyncCompleted += self._onSyncCompleted
        return

    def fini(self):
        self._itemsCache.onSyncCompleted -= self._onSyncCompleted
        self._states = None
        self._inventoryProxy = None
        return

    @property
    def states(self):
        return self._states

    def _refreshProxy(self):
        pdata = {'inventory': self._itemsCache.items.inventory.getDataRoot()}
        self._inventoryProxy.refresh(pdata)

    def _onSyncCompleted(self, _, __):
        self._refreshProxy()
