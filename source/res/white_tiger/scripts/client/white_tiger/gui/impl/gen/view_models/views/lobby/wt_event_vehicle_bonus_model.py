# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/impl/gen/view_models/views/lobby/wt_event_vehicle_bonus_model.py
from gui.impl.gen.view_models.common.missions.bonuses.bonus_model import BonusModel

class WtEventVehicleBonusModel(BonusModel):
    __slots__ = ()

    def __init__(self, properties=14, commands=0):
        super(WtEventVehicleBonusModel, self).__init__(properties=properties, commands=commands)

    def getType(self):
        return self._getString(7)

    def setType(self, value):
        self._setString(7, value)

    def getLevel(self):
        return self._getNumber(8)

    def setLevel(self, value):
        self._setNumber(8, value)

    def getSpecName(self):
        return self._getString(9)

    def setSpecName(self, value):
        self._setString(9, value)

    def getNation(self):
        return self._getString(10)

    def setNation(self, value):
        self._setString(10, value)

    def getIsElite(self):
        return self._getBool(11)

    def setIsElite(self, value):
        self._setBool(11, value)

    def getIntCD(self):
        return self._getNumber(12)

    def setIntCD(self, value):
        self._setNumber(12, value)

    def getRentBattles(self):
        return self._getNumber(13)

    def setRentBattles(self, value):
        self._setNumber(13, value)

    def _initialize(self):
        super(WtEventVehicleBonusModel, self)._initialize()
        self._addStringProperty('type', '')
        self._addNumberProperty('level', 0)
        self._addStringProperty('specName', '')
        self._addStringProperty('nation', '')
        self._addBoolProperty('isElite', False)
        self._addNumberProperty('intCD', 0)
        self._addNumberProperty('rentBattles', 0)
