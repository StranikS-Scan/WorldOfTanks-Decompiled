# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/tank_setup/sub_views/battle_booster_slot_model.py
from gui.impl.gen.view_models.views.lobby.tank_setup.sub_views.base_slot_model import BaseSlotModel

class BattleBoosterSlotModel(BaseSlotModel):
    __slots__ = ()

    def __init__(self, properties=16, commands=0):
        super(BattleBoosterSlotModel, self).__init__(properties=properties, commands=commands)

    def getDescription(self):
        return self._getString(13)

    def setDescription(self, value):
        self._setString(13, value)

    def getIsBuyMoreDisabled(self):
        return self._getBool(14)

    def setIsBuyMoreDisabled(self, value):
        self._setBool(14, value)

    def getIsCrewBooster(self):
        return self._getBool(15)

    def setIsCrewBooster(self, value):
        self._setBool(15, value)

    def _initialize(self):
        super(BattleBoosterSlotModel, self)._initialize()
        self._addStringProperty('description', '')
        self._addBoolProperty('isBuyMoreDisabled', False)
        self._addBoolProperty('isCrewBooster', False)
