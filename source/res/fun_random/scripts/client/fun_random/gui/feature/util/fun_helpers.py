# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/gui/feature/util/fun_helpers.py
import typing
from gui import GUI_NATIONS_ORDER_INDEX
from gui.shared.gui_items.Vehicle import VEHICLE_TYPES_ORDER_INDICES
if typing.TYPE_CHECKING:
    from gui.shared.gui_items import Vehicle

def getProgressionInfoByExecutor(executorQuestID):
    progressionName, counterAmount = executorQuestID.split('_')[-2:]
    return (progressionName, int(counterAmount))


def getProgressionNameByTrigger(triggerQuestID):
    return triggerQuestID.split('_')[-1]


def getVehicleComparisonKey(vehicle):
    return (not vehicle.isInInventory,
     not vehicle.isEvent,
     not vehicle.isOnlyForBattleRoyaleBattles,
     not vehicle.isFavorite,
     GUI_NATIONS_ORDER_INDEX[vehicle.nationName],
     VEHICLE_TYPES_ORDER_INDICES[vehicle.type],
     vehicle.level,
     tuple(vehicle.buyPrices.itemPrice.price.iterallitems(byWeight=True)),
     vehicle.userName)


def notifyCaller(callback, result):
    if callback is not None:
        callback(result)
    return


def mergeIntervals(allPrimeTimes):
    primeTimes = {}
    for serverPrimeTimes in allPrimeTimes:
        for serverShortName in serverPrimeTimes:
            primeTimes[serverShortName] = primeTimes.get(serverShortName, []) + serverPrimeTimes[serverShortName]

    return {serverShortName:_normalizeIntervals(intervals) for serverShortName, intervals in primeTimes.iteritems()}


def _normalizeIntervals(intervals):
    if not intervals:
        return []
    intervals = sorted(intervals)
    mergedIntervals = [intervals[0]]
    for interval in intervals[1:]:
        _, endFirst = mergedIntervals[-1]
        startSecond, endSecond = interval
        if startSecond <= endFirst < endSecond:
            mergedIntervals[-1][1] = endSecond
        if startSecond > endFirst:
            mergedIntervals.append(interval)

    return mergedIntervals
