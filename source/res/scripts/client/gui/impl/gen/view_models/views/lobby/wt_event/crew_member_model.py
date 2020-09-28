# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/wt_event/crew_member_model.py
from frameworks.wulf import ViewModel

class CrewMemberModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=6, commands=0):
        super(CrewMemberModel, self).__init__(properties=properties, commands=commands)

    def getName(self):
        return self._getString(0)

    def setName(self, value):
        self._setString(0, value)

    def getType(self):
        return self._getString(1)

    def setType(self, value):
        self._setString(1, value)

    def getDescription(self):
        return self._getString(2)

    def setDescription(self, value):
        self._setString(2, value)

    def getPerk(self):
        return self._getBool(3)

    def setPerk(self, value):
        self._setBool(3, value)

    def getRankIcon(self):
        return self._getString(4)

    def setRankIcon(self, value):
        self._setString(4, value)

    def getTankmanID(self):
        return self._getNumber(5)

    def setTankmanID(self, value):
        self._setNumber(5, value)

    def _initialize(self):
        super(CrewMemberModel, self)._initialize()
        self._addStringProperty('name', '')
        self._addStringProperty('type', '')
        self._addStringProperty('description', '')
        self._addBoolProperty('perk', False)
        self._addStringProperty('rankIcon', '')
        self._addNumberProperty('tankmanID', 0)
