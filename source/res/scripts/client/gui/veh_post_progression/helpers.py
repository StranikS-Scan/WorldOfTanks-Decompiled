# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/veh_post_progression/helpers.py
import typing
from itertools import chain
from account_helpers import AccountSettings
from account_helpers.AccountSettings import VPP_ENTRY_POINT_LAST_SEEN_STEP
from account_shared import LayoutIterator
from gui.veh_post_progression.models.ext_money import ExtendedMoney
from post_progression_common import VehicleState, parseActionCompDescr, ACTION_TYPES, TankSetupLayouts, GROUP_ID_BY_LAYOUT
_LAYOUT_TO_INSTALLED = ((TankSetupLayouts.EQUIPMENT, 'eqs'), (TankSetupLayouts.BATTLE_BOOSTERS, 'boosters'))

def getVehicleState(actionCDs):
    result = VehicleState()
    for actionCD in actionCDs:
        actionType, itemId, _ = parseActionCompDescr(actionCD)
        if actionType == ACTION_TYPES.FEATURE:
            result.addFeature(itemId)

    return result


def setFeatures(state, actionCDs):
    state.clean(False, False, True, False)
    for actionCD in actionCDs:
        actionType, itemId, _ = parseActionCompDescr(actionCD)
        if actionType == ACTION_TYPES.FEATURE:
            state.addFeature(itemId)


def setDisabledSwitches(state, groupIDs):
    state.clean(False, False, False, True)
    for groupID in groupIDs:
        state.addDisabledSwitch(groupID)


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


def storeLastSeenStep(vehicleIntCD, stepID):
    lastSeenSteps = AccountSettings.getCounters(VPP_ENTRY_POINT_LAST_SEEN_STEP)
    lastSeenSteps.update({vehicleIntCD: stepID})
    AccountSettings.setCounters(VPP_ENTRY_POINT_LAST_SEEN_STEP, lastSeenSteps)


def needToShowCounter(vehicle):
    showCounter = False
    if vehicle.xp > 0 and vehicle.postProgressionAvailability(unlockOnly=True).result:
        purchasableStep = vehicle.postProgression.getFirstPurchasableStep(ExtendedMoney(xp=vehicle.xp))
        if purchasableStep is not None:
            lastSeenSteps = AccountSettings.getCounters(VPP_ENTRY_POINT_LAST_SEEN_STEP)
            showCounter = lastSeenSteps.get(vehicle.intCD, None) != purchasableStep.stepID
    return showCounter
