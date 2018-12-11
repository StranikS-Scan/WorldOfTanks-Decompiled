# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/items/components/ny_constants.py
from collections import defaultdict
TOYS_XML_PATH = 'scripts/item_defs/ny19/toys.xml'
SLOTS_XML_PATH = 'scripts/item_defs/ny19/slots.xml'
LEVEL_REWARDS_XML_PATH = 'scripts/item_defs/ny19/level_rewards.xml'
VARIADIC_DISCOUNTS_XML_PATH = 'scripts/item_defs/ny19/variadic_discounts.xml'
COLLECTION2018_REWARDS_XML_PATH = 'scripts/item_defs/ny18/collection_rewards.xml'
COLLECTION2019_REWARDS_XML_PATH = 'scripts/item_defs/ny19/collection_rewards.xml'

class CustomizationObjects(object):
    FIR = 'Fir'
    FIELD_KITCHEN = 'FieldKitchen'
    PARKING = 'TankParking'
    ILLUMINATION = 'Illumination'
    ALL = (FIR,
     FIELD_KITCHEN,
     PARKING,
     ILLUMINATION)


TOY_OBJECTS_IDS_BY_NAME = {name:idx for idx, name in enumerate(CustomizationObjects.ALL)}

class ToySettings(object):
    NEW_YEAR = 'NewYear'
    CHRISTMAS = 'Christmas'
    FAIRYTALE = 'Fairytale'
    ORIENTAL = 'Oriental'
    SOVIET = 'soviet'
    TRADITIONAL_WESTERN = 'traditionalWestern'
    MODERN_WESTERN = 'modernWestern'
    ASIAN = 'asian'
    NEW = (NEW_YEAR,
     CHRISTMAS,
     FAIRYTALE,
     ORIENTAL)
    OLD = (SOVIET,
     TRADITIONAL_WESTERN,
     MODERN_WESTERN,
     ASIAN)
    ALL = NEW + OLD


TOY_SETTING_IDS_BY_NAME = {name:idx for idx, name in enumerate(ToySettings.ALL)}

class ToyTypes(object):
    TOP = 'top'
    BALL = 'ball'
    GARLAND = 'garland'
    FLOOR = 'floor'
    TABLE = 'table'
    KITCHEN = 'kitchen'
    SCULPTURE = 'sculpture'
    DECORATION = 'decoration'
    TREES = 'trees'
    GROUND_LIGHT = 'ground_light'
    ALL = (TOP,
     BALL,
     GARLAND,
     FLOOR,
     TABLE,
     KITCHEN,
     SCULPTURE,
     DECORATION,
     TREES,
     GROUND_LIGHT)


TOY_TYPES = ToyTypes.ALL
TOY_TYPE_IDS_BY_NAME = {name:idx for idx, name in enumerate(TOY_TYPES)}
MAX_TOY_RANK = 5
MIN_TOY_RANK = 1
RANDOM_VALUE = -1
INVALID_TOY_ID = -1
RANK_COLORS = ('orange', 'yellow', 'green', 'blue', 'violet')
COLORS_BY_RANK = {name:idx for idx, name in enumerate(RANK_COLORS, 1)}
RANK_NAMES = ('simple', 'unusual', 'rare', 'unique', 'epic')
NAMES_BY_RANK = {name:idx for idx, name in enumerate(RANK_NAMES, 1)}

class NY_STATE(object):
    NOT_STARTED = 'not_started'
    IN_PROGRESS = 'in_progress'
    SUSPENDED = 'suspended'
    FINISHED = 'finished'
    ENABLED = (IN_PROGRESS, SUSPENDED)
    ALL = (NOT_STARTED,
     IN_PROGRESS,
     SUSPENDED,
     FINISHED)


TOY_COLLECTION_BYTES = 42
MAX_TOY_ID = TOY_COLLECTION_BYTES * 8 - 1
TOY_ATMOSPHERE_BY_RANK = (1, 2, 4, 8, 25)
ATMOSPHERE_LIMIT_BY_LEVEL = (0, 10, 26, 51, 77, 107, 160, 216, 288, 375)
MAX_ATMOSPHERE_LEVEL = 10
MIN_ATMOSPHERE_LEVEL = 1
BONUS_FACTOR_BY_ATMOSPHERE_LEVEL = (1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0)
TOY_RATING_BY_RANK = (1, 1, 1, 1, 1)
COLLECTION_RATING_LIMIT_BY_LEVEL = (0, 9, 20, 39, 62)
MAX_COLLECTION_LEVEL = 5
TOY_DECAY_COST_BY_RANK = defaultdict((lambda : 0), **{(ToyTypes.TOP, '1'): 10,
 (ToyTypes.TOP, '2'): 20,
 (ToyTypes.TOP, '3'): 40,
 (ToyTypes.TOP, '4'): 80,
 (ToyTypes.TOP, '5'): 250,
 (ToyTypes.GARLAND, '1'): 10,
 (ToyTypes.GARLAND, '2'): 20,
 (ToyTypes.GARLAND, '3'): 40,
 (ToyTypes.GARLAND, '4'): 80,
 (ToyTypes.GARLAND, '5'): 250,
 (ToyTypes.BALL, '1'): 10,
 (ToyTypes.BALL, '2'): 20,
 (ToyTypes.BALL, '3'): 40,
 (ToyTypes.BALL, '4'): 80,
 (ToyTypes.BALL, '5'): 250,
 (ToyTypes.DECORATION, '1'): 10,
 (ToyTypes.DECORATION, '2'): 20,
 (ToyTypes.DECORATION, '3'): 40,
 (ToyTypes.DECORATION, '4'): 80,
 (ToyTypes.DECORATION, '5'): 250,
 (ToyTypes.FLOOR, '1'): 10,
 (ToyTypes.FLOOR, '2'): 20,
 (ToyTypes.FLOOR, '3'): 40,
 (ToyTypes.FLOOR, '4'): 80,
 (ToyTypes.FLOOR, '5'): 250,
 (ToyTypes.GROUND_LIGHT, '1'): 10,
 (ToyTypes.GROUND_LIGHT, '2'): 20,
 (ToyTypes.GROUND_LIGHT, '3'): 40,
 (ToyTypes.GROUND_LIGHT, '4'): 80,
 (ToyTypes.GROUND_LIGHT, '5'): 250,
 (ToyTypes.KITCHEN, '1'): 10,
 (ToyTypes.KITCHEN, '2'): 20,
 (ToyTypes.KITCHEN, '3'): 40,
 (ToyTypes.KITCHEN, '4'): 80,
 (ToyTypes.KITCHEN, '5'): 250,
 (ToyTypes.SCULPTURE, '1'): 10,
 (ToyTypes.SCULPTURE, '2'): 20,
 (ToyTypes.SCULPTURE, '3'): 40,
 (ToyTypes.SCULPTURE, '4'): 80,
 (ToyTypes.SCULPTURE, '5'): 250,
 (ToyTypes.TABLE, '1'): 10,
 (ToyTypes.TABLE, '2'): 20,
 (ToyTypes.TABLE, '3'): 40,
 (ToyTypes.TABLE, '4'): 80,
 (ToyTypes.TABLE, '5'): 250,
 (ToyTypes.TREES, '1'): 10,
 (ToyTypes.TREES, '2'): 20,
 (ToyTypes.TREES, '3'): 40,
 (ToyTypes.TREES, '4'): 80,
 (ToyTypes.TREES, '5'): 250})
TOY_TYPES_BY_OBJECT = {CustomizationObjects.FIR: (ToyTypes.TOP,
                            ToyTypes.BALL,
                            ToyTypes.GARLAND,
                            ToyTypes.FLOOR),
 CustomizationObjects.FIELD_KITCHEN: (ToyTypes.TABLE, ToyTypes.KITCHEN),
 CustomizationObjects.PARKING: (ToyTypes.SCULPTURE, ToyTypes.DECORATION),
 CustomizationObjects.ILLUMINATION: (ToyTypes.TREES, ToyTypes.GROUND_LIGHT)}

class Craft(object):
    RANDOM_TOY_COST = 100
    COST_BY_RANK = (20, 40, 60, 140, 480)
    NY18_COST_BY_RANK = (10, 20, 30, 70, 240)
    SETTING_COST_FACTOR = 1
    CUSTOMIZATION_COST_FACTOR = {CustomizationObjects.FIR: 1,
     CustomizationObjects.FIELD_KITCHEN: 1,
     CustomizationObjects.PARKING: 1,
     CustomizationObjects.ILLUMINATION: 1}


class BonusCollectionIDs(object):
    CREDITS = TOY_SETTING_IDS_BY_NAME[ToySettings.NEW_YEAR]
    CREW_XP = TOY_SETTING_IDS_BY_NAME[ToySettings.CHRISTMAS]
    XP = TOY_SETTING_IDS_BY_NAME[ToySettings.ORIENTAL]
    FREE_XP = TOY_SETTING_IDS_BY_NAME[ToySettings.FAIRYTALE]


BONUS_THRESHOLDS = {BonusCollectionIDs.CREDITS: ((9, 2.0),
                              (20, 3.0),
                              (39, 4.0),
                              (62, 5.0)),
 BonusCollectionIDs.CREW_XP: ((9, 2.0),
                              (20, 3.0),
                              (39, 4.0),
                              (62, 5.0)),
 BonusCollectionIDs.XP: ((9, 2.0),
                         (20, 3.0),
                         (39, 4.0),
                         (62, 5.0)),
 BonusCollectionIDs.FREE_XP: ((9, 2.0),
                              (20, 3.0),
                              (39, 4.0),
                              (62, 5.0))}
COLLECTION_BONUSES_BY_LEVEL = ((0.0, 0.02, 0.03, 0.04, 0.05),
 (0.0, 0.02, 0.03, 0.04, 0.05),
 (0.0, 0.02, 0.03, 0.04, 0.05),
 (0.0, 0.02, 0.03, 0.04, 0.05))

class TOY_SEEN_MASK(object):
    NONE = 0
    INVENTORY = 1
    COLLECTION = 16
    ANY = INVENTORY | COLLECTION
