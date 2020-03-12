# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/common/missions/bonuses/item_bonus_model.py
from gui.impl.gen.view_models.common.missions.bonuses.bonus_model import BonusModel

class ItemBonusModel(BonusModel):
    __slots__ = ()

    def __init__(self, properties=7, commands=0):
        super(ItemBonusModel, self).__init__(properties=properties, commands=commands)

    def getItem(self):
        return self._getString(5)

    def setItem(self, value):
        self._setString(5, value)

    def getOverlayType(self):
        return self._getString(6)

    def setOverlayType(self, value):
        self._setString(6, value)

    def _initialize(self):
        super(ItemBonusModel, self)._initialize()
        self._addStringProperty('item', '')
        self._addStringProperty('overlayType', '')
