# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: gui_lootboxes/scripts/client/gui_lootboxes/gui/bonuses/bonuses_order_config.py
import logging
from collections import namedtuple
import resource_helper
_logger = logging.getLogger(__name__)
BONUSES_CONFIG_PATH = 'gui_lootboxes/gui/bonuses_gui_config.xml'
BONUSES_CONFIG_PATH_LIST = [BONUSES_CONFIG_PATH]

class BonusesSortTags(object):
    UNSORTABLE = 'unsortable'
    VEHICLE = 'vehicle'
    UNIQUE_CUSTOMIZATION = 'uniqueCustomization'
    RARITY_OPT_DEV = 'rarityOptionalDevice'
    RARITY_CURRENCY = 'rarityCurrency'
    PREMIUM = 'premium'
    UNIQUE_TANKMEN = 'uniqueTankmen'
    TANKMEN = 'tankmen'
    STYLE = 'style'
    PERSONAL_BOOSTER = 'personalBooster'
    CREW_BOOK = 'crewBook'
    CURRENCY = 'ordinaryCurrency'
    OPT_DEV = 'optionalDevice'
    EQUIPMENT = 'equipment'
    BATTLE_BOOSTER = 'battleBooster'
    CUSTOMIZATION = 'customization'
    SLOT = 'slot'
    BERTH = 'berth'
    BLUEPRINT = 'blueprint'
    NARRATIVE_CLLC_ITEM = 'narrativeCollectionItem'
    CLLC_ITEM_COMP = 'collectionItemCompensation'
    CUSTOM_LOOTBOX = 'customLootBox'
    RANGE = (UNSORTABLE,
     VEHICLE,
     UNIQUE_CUSTOMIZATION,
     RARITY_OPT_DEV,
     RARITY_CURRENCY,
     PREMIUM,
     UNIQUE_TANKMEN,
     TANKMEN,
     STYLE,
     PERSONAL_BOOSTER,
     CREW_BOOK,
     CURRENCY,
     OPT_DEV,
     EQUIPMENT,
     BATTLE_BOOSTER,
     CUSTOMIZATION,
     SLOT,
     BERTH,
     BLUEPRINT,
     NARRATIVE_CLLC_ITEM,
     CLLC_ITEM_COMP,
     CUSTOM_LOOTBOX)


BonusesConfig = namedtuple('BonusesConfig', ['orders', 'defaultOrder'])

def readConfig(pathList):
    finalOrders = {}
    defaultOrder = tuple((v for v in BonusesSortTags.RANGE))
    for path in pathList:
        orders, default = _readConfig(path)
        finalOrders.update(orders)
        if default:
            defaultOrder = default

    return BonusesConfig(finalOrders, defaultOrder)


def _readConfig(path):
    orders = {}
    defaultOrder = tuple()
    tags = set()
    ctx, root = resource_helper.getRoot(path)
    if not root:
        _logger.error('bonuses gui config not found. Path %s', path)
        return (orders, None)
    else:
        for _, tag in resource_helper.getIterator(ctx, root['bonusTags']):
            tags.add(tag.name)

        for _, order in resource_helper.getIterator(ctx, root['orders']):
            orderTags = _readOrder(ctx, order, tags)
            if order.name == 'default':
                defaultOrder = orderTags
            if orderTags is not None:
                for category in resource_helper.readStringItem(ctx, order['categories']).value.split():
                    orders[category] = orderTags

        return (orders, defaultOrder)


def _readOrder(ctx, order, tags):
    res = []
    for _, tag in resource_helper.getIterator(ctx, order):
        if tag.name == 'categories':
            continue
        if tag.name not in tags:
            _logger.error('tag %s in order %s not in tags set', tag, order.name)
            return None
        res.append(tag.name)

    for tag in BonusesSortTags.RANGE:
        if tag not in res:
            res.append(tag)

    return tuple(res)
