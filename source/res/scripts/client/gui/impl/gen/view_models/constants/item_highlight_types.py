# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/constants/item_highlight_types.py
from frameworks.wulf import ViewModel

class ItemHighlightTypes(ViewModel):
    __slots__ = ()
    OPTIONAL_DEVICE = 'optionalDevice'
    TROPHY = 'equipmentTrophy'
    TROPHY_BASIC = 'equipmentTrophyBasic'
    TROPHY_UPGRADED = 'equipmentTrophyUpgraded'
    BATTLE_BOOSTER_REPLACE = 'battleBoosterReplace'
    BATTLE_BOOSTER = 'battleBooster'
    EQUIPMENT_PLUS = 'equipmentPlus'
    BUILT_IN_EQUIPMENT = 'builtInEquipment'
    BATTLE_ABILITY = 'battleAbility'
    INCOMPATIBLE_EQUIPMENT = 'incompatibleEquipment'
    MODERNIZED = 'equipmentModernized'
    MODERNIZED1 = 'equipmentModernized_1'
    MODERNIZED2 = 'equipmentModernized_2'
    MODERNIZED3 = 'equipmentModernized_3'
    PROGRESSION_STYLE_UPGRADED = 'progressionStyleUpgraded_'
    POST_PROGRESSION_MODIFICATION = 'postProgressionModification'
    EMPTY = ''

    def __init__(self, properties=0, commands=0):
        super(ItemHighlightTypes, self).__init__(properties=properties, commands=commands)

    def _initialize(self):
        super(ItemHighlightTypes, self)._initialize()
