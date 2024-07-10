# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/common/missions/bonuses/item_bonus_model.py
from gui.impl.gen.view_models.common.missions.bonuses.bonus_model import BonusModel

class ItemBonusModel(BonusModel):
    __slots__ = ()

    def __init__(self, properties=10, commands=0):
        super(ItemBonusModel, self).__init__(properties=properties, commands=commands)

    def getItem(self):
        return self._getString(8)

    def setItem(self, value):
        self._setString(8, value)

    def getOverlayType(self):
        return self._getString(9)

    def setOverlayType(self, value):
        self._setString(9, value)

    def _initialize(self):
        super(ItemBonusModel, self)._initialize()
        self._addStringProperty('item', '')
        self._addStringProperty('overlayType', '')
