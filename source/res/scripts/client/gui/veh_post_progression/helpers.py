# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/veh_post_progression/helpers.py
import typing
from itertools import chain
from account_shared import LayoutIterator
from post_progression_common import VehicleState, parseActionCompDescr, ACTION_TYPES, TankSetupLayouts, GROUP_ID_BY_LAYOUT
_LAYOUT_TO_INSTALLED = ((TankSetupLayouts.EQUIPMENT, 'eqs'), (TankSetupLayouts.BATTLE_BOOSTERS, 'boosters'))

def getVehicleState(actionCDs):
    result = VehicleState()
    for actionCD in actionCDs:
        actionType, itemId, _ = parseActionCompDescr(actionCD)
        if actionType == ACTION_TYPES.FEATURE:
            result.addFeature(itemId)

    return result


def getInstalledShells(shellsCDs, shellsLayout):
    aggregate = {}
    for shellCD, count, _ in LayoutIterator(tuple(chain(*shellsLayout))):
        aggregate[shellCD] = max(count, aggregate.get(shellCD, 0))

    installed = []
    for shellCD in shellsCDs:
        installed.extend((shellCD, aggregate.get(shellCD, 0)))

    return installed


def updateInvInstalled(invData, setupsIndexes):
    for layoutsName, installedName in _LAYOUT_TO_INSTALLED:
        layoutsData = invData[layoutsName]
        setupIdx = setupsIndexes.get(GROUP_ID_BY_LAYOUT[layoutsName], 0)
        invData[installedName] = layoutsData[setupIdx][:] if setupIdx < len(layoutsData) else []
