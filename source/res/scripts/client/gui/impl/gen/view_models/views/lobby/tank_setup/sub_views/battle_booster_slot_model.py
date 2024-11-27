# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/tank_setup/sub_views/battle_booster_slot_model.py
from gui.impl.gen.view_models.views.lobby.tank_setup.sub_views.base_slot_model import BaseSlotModel

class BattleBoosterSlotModel(BaseSlotModel):
    __slots__ = ()

    def __init__(self, properties=24, commands=0):
        super(BattleBoosterSlotModel, self).__init__(properties=properties, commands=commands)

    def getDescription(self):
        return self._getString(21)

    def setDescription(self, value):
        self._setString(21, value)

    def getIsBuyMoreVisible(self):
        return self._getBool(22)

    def setIsBuyMoreVisible(self, value):
        self._setBool(22, value)

    def getIsBuyMoreDisabled(self):
        return self._getBool(23)

    def setIsBuyMoreDisabled(self, value):
        self._setBool(23, value)

    def _initialize(self):
        super(BattleBoosterSlotModel, self)._initialize()
        self._addStringProperty('description', '')
        self._addBoolProperty('isBuyMoreVisible', True)
        self._addBoolProperty('isBuyMoreDisabled', False)
