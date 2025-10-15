# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: portal/scripts/client/portal/gui/impl/gen/view_models/views/lobby/tooltips/vehicle_crew.py
from enum import Enum
from frameworks.wulf import ViewModel

class CrewId(Enum):
    KOSHCHEYEV = 'koshcheyev'
    TSAREV = 'tsarev'
    YAGINSKAYA = 'yaginskaya'
    VASILIEVA = 'vasilieva'


class VehicleCrew(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(VehicleCrew, self).__init__(properties=properties, commands=commands)

    def getId(self):
        return CrewId(self._getString(0))

    def setId(self, value):
        self._setString(0, value.value)

    def getName(self):
        return self._getString(1)

    def setName(self, value):
        self._setString(1, value)

    def getDescription(self):
        return self._getString(2)

    def setDescription(self, value):
        self._setString(2, value)

    def _initialize(self):
        super(VehicleCrew, self)._initialize()
        self._addStringProperty('id')
        self._addStringProperty('name', '')
        self._addStringProperty('description', '')
