# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/nation_change_helpers/client_nation_change_helper.py
from CurrentVehicle import g_currentVehicle
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.utils.functions import makeTooltip
from helpers import dependency
from nation_change.nation_change_helpers import iterVehTypeCDsInNationGroup, isMainInNationGroup
from skeletons.gui.shared import IItemsCache

def getValidVehicleCDForNationChange(vehCompDescr):
    tempVehCD = vehCompDescr
    vehicle = _getItem(vehCompDescr)
    if vehicle.hasNationGroup:
        if vehicle.isInInventory:
            if not vehicle.activeInNationGroup:
                tempVehCD = iterVehTypeCDsInNationGroup(vehCompDescr).next()
        elif not isMainInNationGroup(vehCompDescr):
            tempVehCD = iterVehTypeCDsInNationGroup(vehCompDescr).next()
    return tempVehCD


def getChangeNationTooltip():
    isChangeNationVisible = g_currentVehicle.isPresent() and g_currentVehicle.item.hasNationGroup
    isNationChangeAvailable = g_currentVehicle.isPresent() and g_currentVehicle.item.isNationChangeAvailable
    if isChangeNationVisible:
        if isNationChangeAvailable:
            changeNationTooltipHeader = R.strings.tooltips.hangar.nationChange.header()
            changeNationTooltipBody = R.strings.tooltips.hangar.nationChange.body()
        else:
            changeNationTooltipHeader = R.strings.tooltips.hangar.nationChange.disabled.header()
            if g_currentVehicle.item.isBroken:
                changeNationTooltipBody = R.strings.tooltips.hangar.nationChange.disabled.body.destroyed()
            elif g_currentVehicle.item.isInBattle:
                changeNationTooltipBody = R.strings.tooltips.hangar.nationChange.disabled.body.inBattle()
            elif g_currentVehicle.item.isInUnit:
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
