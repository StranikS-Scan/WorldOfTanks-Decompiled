# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/nation_change_helpers/client_nation_change_helper.py
from __future__ import absolute_import
import typing
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.utils.functions import makeTooltip
from helpers import dependency
from nation_change.nation_change_helpers import iterVehTypeCDsInNationGroup, isMainInNationGroup
from skeletons.gui.shared import IItemsCache
if typing.TYPE_CHECKING:
    from gui.shared.gui_items.Vehicle import Vehicle

def getValidVehicleCDForNationChange(vehCompDescr):
    tempVehCD = vehCompDescr
    vehicle = _getItem(vehCompDescr)
    if vehicle.hasNationGroup:
        if vehicle.isInInventory:
            if not vehicle.activeInNationGroup:
                tempVehCD = next(iterVehTypeCDsInNationGroup(vehCompDescr))
        elif not isMainInNationGroup(vehCompDescr):
            tempVehCD = next(iterVehTypeCDsInNationGroup(vehCompDescr))
    return tempVehCD


def getChangeNationTooltip(vehicle):
    isChangeNationVisible = vehicle is not None and vehicle.hasNationGroup
    isNationChangeAvailable = vehicle is not None and vehicle.isNationChangeAvailable
    if isChangeNationVisible:
        if isNationChangeAvailable:
            changeNationTooltipHeader = R.strings.tooltips.hangar.nationChange.header()
            changeNationTooltipBody = R.strings.tooltips.hangar.nationChange.body()
        else:
            changeNationTooltipHeader = R.strings.tooltips.hangar.nationChange.disabled.header()
            if vehicle.isBroken:
                changeNationTooltipBody = R.strings.tooltips.hangar.nationChange.disabled.body.destroyed()
            elif vehicle.isInBattle:
                changeNationTooltipBody = R.strings.tooltips.hangar.nationChange.disabled.body.inBattle()
            elif vehicle.isInUnit:
                changeNationTooltipBody = R.strings.tooltips.hangar.nationChange.disabled.body.inSquad()
            else:
                changeNationTooltipBody = ''
        if changeNationTooltipBody == '':
            changeNationTooltip = makeTooltip(backport.text(changeNationTooltipHeader), '')
        else:
            changeNationTooltip = makeTooltip(backport.text(changeNationTooltipHeader), backport.text(changeNationTooltipBody))
    else:
        changeNationTooltip = ''
    return changeNationTooltip


@dependency.replace_none_kwargs(itemsCache=IItemsCache)
def _getItem(itemID, itemsCache=None):
    return itemsCache.items.getItemByCD(itemID)
