# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/hangar/inventory_update_helper.py
from gui.shared.gui_items import GUI_ITEM_TYPE

def updateOnInventoryChanges(itemsCache, vehicle, invDiff):
    isNeedToUpdate = True
    if invDiff is not None and GUI_ITEM_TYPE.TANKMAN in invDiff:
        diff = invDiff[GUI_ITEM_TYPE.TANKMAN]
        if 'compDescr' in diff:
            invIDs = diff['compDescr']
            for tankmanInvID in invIDs.iterkeys():
                tankman = itemsCache.items.getTankman(tankmanInvID)
                if tankman and tankman.isInTank and tankman.vehicleInvID == vehicle.invID:
                    isNeedToUpdate = True
                    break
                isNeedToUpdate = False

    return isNeedToUpdate
