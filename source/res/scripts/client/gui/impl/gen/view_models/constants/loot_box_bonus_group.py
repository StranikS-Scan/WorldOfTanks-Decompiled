# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/constants/loot_box_bonus_group.py
from frameworks.wulf import ViewModel

class LootBoxBonusGroup(ViewModel):
    __slots__ = ()
    VEHICLE = 'vehicle'
    PREMIUM = 'premium'
    CURRENCY = 'currency'
    VEHICLECUSTOMIZATIONS = 'vehicleCustomizations'
    CREW = 'crew'
    BOOSTERS = 'boosters'
    EQUIPMENTS = 'equipments'
    ACCOUNTCUSTOMIZATIONS = 'accountCustomizations'
    FEATUREITEMS = 'featureItems'

    def __init__(self, properties=0, commands=0):
        super(LootBoxBonusGroup, self).__init__(properties=properties, commands=commands)

    def _initialize(self):
        super(LootBoxBonusGroup, self)._initialize()
