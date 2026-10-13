# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fort_rush/scripts/client/fort_rush/gui/impl/gen/view_models/views/battle/views/fort_rush_hud_team_unit_model.py
from gui.impl.gen.view_models.common.battle_player import VehicleTypeEnum
from frameworks.wulf import ViewModel

class FortRushHudTeamUnitModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(FortRushHudTeamUnitModel, self).__init__(properties=properties, commands=commands)

    def getId(self):
        return self._getString(0)

    def setId(self, value):
        self._setString(0, value)

    def getType(self):
        return VehicleTypeEnum(self._getString(1))

    def setType(self, value):
        self._setString(1, value.value)

    def getIsDestroyed(self):
        return self._getBool(2)

    def setIsDestroyed(self, value):
        self._setBool(2, value)

    def _initialize(self):
        super(FortRushHudTeamUnitModel, self)._initialize()
        self._addStringProperty('id', '')
        self._addStringProperty('type', VehicleTypeEnum.UNDEFINED.value)
        self._addBoolProperty('isDestroyed', False)
