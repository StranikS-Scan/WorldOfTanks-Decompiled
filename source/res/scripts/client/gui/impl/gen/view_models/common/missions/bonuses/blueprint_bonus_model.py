# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/common/missions/bonuses/blueprint_bonus_model.py
from gui.impl.gen.view_models.common.missions.bonuses.icon_bonus_model import IconBonusModel

class BlueprintBonusModel(IconBonusModel):
    __slots__ = ()

    def __init__(self, properties=8, commands=0):
        super(BlueprintBonusModel, self).__init__(properties=properties, commands=commands)

    def getType(self):
        return self._getString(7)

    def setType(self, value):
        self._setString(7, value)

    def _initialize(self):
        super(BlueprintBonusModel, self)._initialize()
        self._addStringProperty('type', '')
