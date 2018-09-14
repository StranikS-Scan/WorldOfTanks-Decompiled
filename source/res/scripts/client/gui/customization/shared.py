# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/customization/shared.py
import cPickle
from CurrentVehicle import g_currentVehicle
from items.qualifiers import CREW_ROLE
from gui.shared.ItemsCache import g_itemsCache
from gui.shared.formatters import text_styles, icons
from gui.shared.tooltips import ACTION_TOOLTIPS_TYPE

class CUSTOMIZATION_TYPE(object):
    CAMOUFLAGE = 0
    EMBLEM = 1
    INSCRIPTION = 2
    ALL = (CAMOUFLAGE, EMBLEM, INSCRIPTION)


class DURATION(object):
    PERMANENT = 0
    MONTH = 30
    WEEK = 7
    ALL = (PERMANENT, MONTH, WEEK)


class QUALIFIER_TYPE(CREW_ROLE):
    CAMOUFLAGE = 'camouflage'


class FILTER_TYPE(object):
    QUALIFIER = 0
    GROUP = 1
    PURCHASE_TYPE = 2
    SHOW_IN_DOSSIER = 3


class PURCHASE_TYPE(object):
    PURCHASE = 0
    QUEST = 1
    IGR = 2
    ALL = (PURCHASE, QUEST, IGR)


class INSTALLATION(object):
    INVOICED = -2
    REMOVAL = -1
    NORMAL = 0


class ELEMENT_PLACEMENT(object):
    HULL = 0
    TURRET = 2


QUALIFIER_TYPE_INDEX = (QUALIFIER_TYPE.ALL,
 QUALIFIER_TYPE.COMMANDER,
 QUALIFIER_TYPE.GUNNER,
 QUALIFIER_TYPE.DRIVER,
 QUALIFIER_TYPE.RADIOMAN,
 QUALIFIER_TYPE.LOADER)
DEFAULT_GROUP_VALUE = 'all_groups'
QUALIFIER_TYPE_NAMES = dict([ (v, k) for k, v in QUALIFIER_TYPE.__dict__.iteritems() if not k.startswith('_') ])
QUALIFIER_TYPE_NAMES.update(dict([ (v, k) for k, v in CREW_ROLE.__dict__.iteritems() if not k.startswith('_') and not k == 'RANGE' ]))
TYPE_NAME = {'emblems': CUSTOMIZATION_TYPE.EMBLEM,
 'inscriptions': CUSTOMIZATION_TYPE.INSCRIPTION,
 'camouflages': CUSTOMIZATION_TYPE.CAMOUFLAGE}
SLOT_TYPE = {CUSTOMIZATION_TYPE.EMBLEM: 'player',
 CUSTOMIZATION_TYPE.INSCRIPTION: 'inscription'}
CAMOUFLAGE_GROUP_MAPPING = ('winter', 'summer', 'desert')
_ACTION_TOOLTIP_MAPPING = {CUSTOMIZATION_TYPE.CAMOUFLAGE: ACTION_TOOLTIPS_TYPE.CAMOUFLAGE,
 CUSTOMIZATION_TYPE.EMBLEM: ACTION_TOOLTIPS_TYPE.EMBLEMS,
 CUSTOMIZATION_TYPE.INSCRIPTION: ACTION_TOOLTIPS_TYPE.EMBLEMS}
BONUS_ICONS = {'16x16': {'main_skill': '../maps/icons/library/qualifiers/16x16/{0}.png',
           'camouflage': '../maps/icons/library/qualifiers/16x16/camouflage.png'},
 '42x42': {'main_skill': '../maps/icons/library/qualifiers/42x42/{0}.png',
           'camouflage': '../maps/icons/library/qualifiers/42x42/camouflage.png'}}
EMBLEM_IGR_GROUP_NAME = 'group5'

def getBonusIcon16x16(qualifierType):
    if qualifierType == QUALIFIER_TYPE.CAMOUFLAGE:
        return BONUS_ICONS['16x16'][qualifierType]
    else:
        return BONUS_ICONS['16x16']['main_skill'].format(qualifierType)


def getBonusIcon42x42(qualifierType):
    if qualifierType == QUALIFIER_TYPE.CAMOUFLAGE:
        return BONUS_ICONS['42x42'][qualifierType]
    else:
        return BONUS_ICONS['42x42']['main_skill'].format(qualifierType)


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
        for slotIdx in range(0, len(newSlotsData[cType])):
            newSlotItem = newSlotsData[cType][slotIdx]
            oldSlotItem = oldSlotsData[cType][slotIdx]
            functionToRun(newSlotItem, oldSlotItem, cType, slotIdx)


def getAdjustedSlotIndex(initialIndex, cType, slotsData):
    if initialIndex == 1:
        slotItem = slotsData[cType][initialIndex]
        adjacentSlotItem = slotsData[cType][0]
        if slotItem['spot'] != adjacentSlotItem['spot']:
            return initialIndex - 1
        else:
            return initialIndex
    return initialIndex


def elementsDiffer(firstElement, secondElement):
    if firstElement is None and secondElement is not None:
        return True
    elif secondElement is None and firstElement is not None:
        return True
    else:
        return True if firstElement is not None and secondElement is not None and firstElement.getID() != secondElement.getID() else False


def checkInQuest(element, purchaseType):
    """ Check if provided element is actually came from quest.
    
    :param element: customization element
    :param purchaseType: current purchase type
    :return: True if element came from quest, False otherwise
    """
    return element is not None and element.isInQuests and not element.isInDossier and purchaseType == PURCHASE_TYPE.QUEST
