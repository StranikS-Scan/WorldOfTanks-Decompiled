# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/new_year/ny_constants.py
from items.components.ny_constants import CustomizationObjects, ToySettings, TOY_SETTING_IDS_BY_NAME
from shared_utils import CONST_CONTAINER

class AnchorNames(CONST_CONTAINER):
    TREE = 'ChristmasTree'
    FIELD_KITCHEN = 'FieldKitchen'
    SCULPTURE = 'SnowSculpture'
    ILLUMINATION = 'OuterTreesIllumination'


ANCHOR_TO_OBJECT = {AnchorNames.TREE: CustomizationObjects.FIR,
 AnchorNames.FIELD_KITCHEN: CustomizationObjects.FIELD_KITCHEN,
 AnchorNames.SCULPTURE: CustomizationObjects.PARKING,
 AnchorNames.ILLUMINATION: CustomizationObjects.ILLUMINATION}
OBJECT_TO_ANCHOR = {v:k for k, v in ANCHOR_TO_OBJECT.iteritems()}
MAX_LEVEL = 10
TOY_PREFIX = 'toy_'
TOY_COLLECTIONS = ['ny18Toys', 'ny19Toys']

class Collections(CONST_CONTAINER):
    NewYear19 = 'ny19'
    NewYear18 = 'ny18'


COLLECTIONS_SETTINGS = {Collections.NewYear19: ToySettings.NEW,
 Collections.NewYear18: ToySettings.OLD}
COLLECTIONS_SETTINGS_IDS = {Collections.NewYear19: tuple((TOY_SETTING_IDS_BY_NAME[name] for name in ToySettings.NEW)),
 Collections.NewYear18: tuple((TOY_SETTING_IDS_BY_NAME[name] for name in ToySettings.OLD))}

class SyncDataKeys(CONST_CONTAINER):
    INVENTORY_TOYS = 'inventoryToys'
    SLOTS = 'slots'
    TOY_FRAGMENTS = 'toyFragments'
    LEVEL = 'level'
    SELECTED_DISCOUNTS = 'selectedDiscounts'
    TOY_COLLECTION = 'toyCollection'
    COLLECTION_DISTRIBUTIONS = 'collectionDistributions'
    ALBUMS = 'albums'
