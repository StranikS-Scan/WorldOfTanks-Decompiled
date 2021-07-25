# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/crew2/detachment_inventory_proxy.py
from typing import TYPE_CHECKING, Tuple, List, Dict, Any, Optional
from items import ITEM_TYPES
if TYPE_CHECKING:
    from items.detachment import DetachmentDescr

class IInventoryProxy(object):

    def __getitem__(self, key):
        raise NotImplementedError('must override me')

    def __setitem__(self, key, value):
        raise NotImplementedError('must override me')

    def __contains__(self, item):
        raise NotImplementedError('must override me')

    def sync(self, key):
        raise NotImplementedError('must override me')

    @property
    def excludedInstructors(self):
        raise NotImplementedError('must override me')

    @property
    def detsVehicle(self):
        raise NotImplementedError('must override me')

    @property
    def detsRecycleBin(self):
        raise NotImplementedError('must override me')

    @property
    def vehsLastDetachmentID(self):
        raise NotImplementedError('must override me')

    def getVehicleEqs(self, vehInvID):
        raise NotImplementedError('must override me')

    def getVehicleCompDescr(self, vehInvID):
        raise NotImplementedError('must override me')

    def isVehicleLocked(self, vehInvID, lockReasonToIgnore=None):
        raise NotImplementedError('must override me')

    def validateGetDetachment(self, detInvID):
        raise NotImplementedError('must override me')

    def validateGetInstructor(self, instInvID):
        raise NotImplementedError('must override me')

    def validateGetVehicle(self, vehInvID):
        raise NotImplementedError('must override me')

    def getDetachmentInvIDByInstructor(self, instInvID):
        raise NotImplementedError('must override me')

    def getDetachmentInvIDByVehicle(self, vehInvID):
        raise NotImplementedError('must override me')

    def getExcludedInstructorInfo(self, instInvID):
        raise NotImplementedError('must override me')

    def isVehicleHasCrew(self, vehInvID):
        raise NotImplementedError('must override me')

    def getVehicleCrew(self, vehInvID):
        raise NotImplementedError('must override me')

    def getVehicleInvID(self, vehTypeCompDescr):
        raise NotImplementedError('must override me')

    def onLevelUp(self, detInvID, newDetDescr, oldDetDescr, isConversionProcess=False):
        raise NotImplementedError('must override me')


class CommonPDataInventoryProxy(IInventoryProxy):

    def __init__(self, pdata):
        self._inventory = pdata['inventory']

    def __getitem__(self, key):
        return self._inventory[key]

    def __setitem__(self, key, value):
        self._inventory[key] = value

    def __contains__(self, item):
        return item in self._inventory

    def sync(self, key):
        return self._inventory[key]

    @property
    def excludedInstructors(self):
        return self._inventory[ITEM_TYPES.instructor]['excluded']

    @property
    def detsVehicle(self):
        return self._inventory[ITEM_TYPES.detachment]['vehicle']

    @property
    def detsRecycleBin(self):
        return self._inventory[ITEM_TYPES.detachment]['recycleBin']

    @property
    def vehsLastDetachmentID(self):
        return self._inventory[ITEM_TYPES.vehicle]['lastDetachmentID']

    def getVehicleEqs(self, vehInvID):
        return self._inventory[ITEM_TYPES.vehicle]['eqs'].get(vehInvID, [])

    def getVehicleCompDescr(self, vehInvID):
        return self._inventory[ITEM_TYPES.vehicle]['compDescr'].get(vehInvID)

    def isVehicleLocked(self, vehInvID, lockReasonToIgnore=None):
        lockReason, _, _, _ = self._inventory['vehsLock'].get(vehInvID, (None, None, None, None))
        isLocked = lockReason is not None
        if lockReasonToIgnore is None:
            return isLocked
        else:
            return isLocked if isLocked and not lockReason & lockReasonToIgnore else False

    def validateGetDetachment(self, detInvID):
        detCompDescr = self._inventory[ITEM_TYPES.detachment]['compDescr'].get(detInvID)
        return detCompDescr

    def validateGetInstructor(self, instInvID):
        instCompDescr = self._inventory[ITEM_TYPES.instructor]['compDescr'].get(instInvID)
        return instCompDescr

    def validateGetVehicle(self, vehInvID):
        vehCompDescr = self._inventory[ITEM_TYPES.vehicle]['compDescr'].get(vehInvID)
        return vehCompDescr

    def getDetachmentInvIDByInstructor(self, instInvID):
        return self._inventory[ITEM_TYPES.instructor]['detachment'].get(instInvID)

    def getDetachmentInvIDByVehicle(self, vehInvID):
        return self._inventory[ITEM_TYPES.detachment]['vehicle'].get(vehInvID)

    def getExcludedInstructorInfo(self, instInvID):
        return self._inventory[ITEM_TYPES.instructor]['excluded'].get(instInvID)

    def isVehicleHasCrew(self, vehInvID):
        return any(self._inventory[ITEM_TYPES.vehicle]['crew'].get(vehInvID, []))

    def getVehicleCrew(self, vehInvID):
        res = []
        slotID = 0
        for tmanInvId in self._inventory[ITEM_TYPES.vehicle]['crew'].get(vehInvID, []):
            tmanCompDescr = self._inventory[ITEM_TYPES.tankman]['compDescr'].get(tmanInvId, None)
            res.append({'slotID': slotID,
             'tmanCompDescr': tmanCompDescr})
            slotID += 1

        return res
