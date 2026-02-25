# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: cosmic_event/scripts/client/cosmic_event/gui/impl/gen/view_models/views/battle/cosmic_hud/player_record_model.py
from enum import IntEnum
from frameworks.wulf import ViewModel

class RoverEnum(IntEnum):
    OLD = 1
    NEW = 2


class PlayerRecordModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=5, commands=0):
        super(PlayerRecordModel, self).__init__(properties=properties, commands=commands)

    def getName(self):
        return self._getString(0)

    def setName(self, value):
        self._setString(0, value)

    def getClanAbbrev(self):
        return self._getString(1)

    def setClanAbbrev(self, value):
        self._setString(1, value)

    def getScore(self):
        return self._getNumber(2)

    def setScore(self, value):
        self._setNumber(2, value)

    def getVehicle(self):
        return RoverEnum(self._getNumber(3))

    def setVehicle(self, value):
        self._setNumber(3, value.value)

    def getLootResearching(self):
        return self._getBool(4)

    def setLootResearching(self, value):
        self._setBool(4, value)

    def _initialize(self):
        super(PlayerRecordModel, self)._initialize()
        self._addStringProperty('name', '')
        self._addStringProperty('clanAbbrev', '')
        self._addNumberProperty('score', 0)
        self._addNumberProperty('vehicle', RoverEnum.OLD.value)
        self._addBoolProperty('lootResearching', False)
