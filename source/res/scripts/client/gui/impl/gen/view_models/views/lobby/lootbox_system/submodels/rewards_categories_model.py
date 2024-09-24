# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/lootbox_system/submodels/rewards_categories_model.py
from enum import Enum
from frameworks.wulf import ViewModel

class Type(Enum):
    LOOTBOX = 'lootBox'
    VEHICLES = 'vehicles'
    STYLE = 'style'
    STYLE3D = 'style_3d'
    CREWMEMBER = 'tmanToken'
    PREMIUMPLUS = 'premium_plus'
    CREDITS = 'credits'
    GOLD = 'gold'
    CRYSTAL = 'crystal'
    FREEXP = 'freeXP'
    CUSTOMIZATIONS = 'customizations'
    EXPERIMENTALEQUIPMENT = 'experimental_equipment'
    COMPONENTS = 'equipCoin'
    IMPROVEDEQUIPMENT = 'improved_equipment'
    BOUNTYEQUIPMENT = 'trophy_equipment'
    STANDARDEQUIPMENT = 'standard_equipment'
    DIRECTIVES = 'battleBooster_gift'
    TRAININGMATERIALS = 'training_materials'
    BLUEPRINTS = 'blueprints'
    BATTLEBONUSX5 = 'battle_bonus_x5'
    CREWBONUSX3 = 'crew_bonus_x3'
    PERSONALRESERVES = 'personal_reserves'
    CONSUMABLES = 'consumables'
    RATIONS = 'rations'


class RewardsCategoriesModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(RewardsCategoriesModel, self).__init__(properties=properties, commands=commands)

    def getType(self):
        return self._getString(0)

    def setType(self, value):
        self._setString(0, value)

    def getCount(self):
        return self._getNumber(1)

    def setCount(self, value):
        self._setNumber(1, value)

    def _initialize(self):
        super(RewardsCategoriesModel, self)._initialize()
        self._addStringProperty('type', '')
        self._addNumberProperty('count', 0)
