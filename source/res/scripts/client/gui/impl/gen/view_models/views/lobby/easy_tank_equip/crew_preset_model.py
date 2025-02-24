# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/easy_tank_equip/crew_preset_model.py
from enum import Enum
from frameworks.wulf import Array
from gui.impl.gen.view_models.views.lobby.crew.tankman_model import TankmanModel
from gui.impl.gen.view_models.views.lobby.easy_tank_equip.common.preset_model import PresetModel

class CrewPresetType(Enum):
    EXPERIENCED = 'experienced'
    NEW_CREW = 'newCrew'


class CrewPresetModel(PresetModel):
    __slots__ = ()

    def __init__(self, properties=8, commands=0):
        super(CrewPresetModel, self).__init__(properties=properties, commands=commands)

    def getType(self):
        return CrewPresetType(self._getString(5))

    def setType(self, value):
        self._setString(5, value.value)

    def getTankmen(self):
        return self._getArray(6)

    def setTankmen(self, value):
        self._setArray(6, value)

    @staticmethod
    def getTankmenType():
        return TankmanModel

    def getRecruitsCount(self):
        return self._getNumber(7)

    def setRecruitsCount(self, value):
        self._setNumber(7, value)

    def _initialize(self):
        super(CrewPresetModel, self)._initialize()
        self._addStringProperty('type')
        self._addArrayProperty('tankmen', Array())
        self._addNumberProperty('recruitsCount', 0)
