# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/customization_2_0/shared.py
import cPickle
from CurrentVehicle import g_currentVehicle
from gui.customization_2_0.data_aggregator import CUSTOMIZATION_TYPE, DURATION
from gui.shared.ItemsCache import g_itemsCache
from gui.shared.formatters import text_styles, icons
from gui.shared.tooltips import ACTION_TOOLTIPS_TYPE
CAMOUFLAGE_GROUP_MAPPING = ('winter', 'summer', 'desert')
_ACTION_TOOLTIP_MAPPING = {CUSTOMIZATION_TYPE.CAMOUFLAGE: ACTION_TOOLTIPS_TYPE.CAMOUFLAGE,
 CUSTOMIZATION_TYPE.EMBLEM: ACTION_TOOLTIPS_TYPE.EMBLEMS,
 CUSTOMIZATION_TYPE.INSCRIPTION: ACTION_TOOLTIPS_TYPE.EMBLEMS}

def formatPriceGold(value):
    if g_itemsCache.items.stats.gold >= value:
        return text_styles.goldTextBig(value)
    else:
        return formatPriceAlert(value)


def formatPriceCredits(value):
    if g_itemsCache.items.stats.credits >= value:
        return text_styles.creditsTextBig(value)
    else:
        return formatPriceAlert(value)


def formatPriceAlert(value):
    return '{0} {1}'.format(icons.alert(), text_styles.errCurrencyTextBig(value))


def getSalePriceString(cType, element, duration):
    eventName = {CUSTOMIZATION_TYPE.CAMOUFLAGE: 'camouflage',
     CUSTOMIZATION_TYPE.INSCRIPTION: 'inscription',
     CUSTOMIZATION_TYPE.EMBLEM: 'emblem'}[cType] + 'Packet' + {DURATION.PERMANENT: 'Inf',
     DURATION.WEEK: '7',
     DURATION.MONTH: '30'}[duration] + 'CostMultiplier'
    keyData = {CUSTOMIZATION_TYPE.CAMOUFLAGE: g_currentVehicle.item.intCD,
     CUSTOMIZATION_TYPE.INSCRIPTION: element.getGroup(),
     CUSTOMIZATION_TYPE.EMBLEM: element.getGroup()}[cType]
    actionVO = {'key': cPickle.dumps((keyData, eventName)),
     'type': _ACTION_TOOLTIP_MAPPING[cType]}
    if duration == DURATION.PERMANENT:
        actionVO.update({'newPrice': [0, element.getPrice(duration)],
         'oldPrice': [0, element.getDefaultPrice(duration)]})
    else:
        actionVO.update({'newPrice': [element.getPrice(duration), 0],
         'oldPrice': [element.getDefaultPrice(duration), 0]})
    return actionVO


def forEachSlotIn(newSlotsData, oldSlotsData, functionToRun):
    for cType in CUSTOMIZATION_TYPE.ALL:
        for slotIdx in range(0, len(newSlotsData['data'][cType]['data'])):
            newSlotItem = newSlotsData['data'][cType]['data'][slotIdx]
            oldSlotItem = oldSlotsData['data'][cType]['data'][slotIdx]
            functionToRun(newSlotItem, oldSlotItem, cType, slotIdx)
