# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/postbattle/events/crew_member.py
from gui.impl.gen import R
from frameworks.wulf import ViewModel

class CrewMember(ViewModel):
    __slots__ = ()

    def __init__(self, properties=5, commands=0):
        super(CrewMember, self).__init__(properties=properties, commands=commands)

    def getId(self):
        return self._getNumber(0)

    def setId(self, value):
        self._setNumber(0, value)

    def getName(self):
        return self._getString(1)

    def setName(self, value):
        self._setString(1, value)

    def getRole(self):
        return self._getString(2)

    def setRole(self, value):
        self._setString(2, value)

    def getIcon(self):
        return self._getResource(3)

    def setIcon(self, value):
        self._setResource(3, value)

    def getBattlesLeft(self):
        return self._getNumber(4)

    def setBattlesLeft(self, value):
        self._setNumber(4, value)

    def _initialize(self):
        super(CrewMember, self)._initialize()
        self._addNumberProperty('id', 0)
        self._addStringProperty('name', '')
        self._addStringProperty('role', '')
        self._addResourceProperty('icon', R.invalid())
        self._addNumberProperty('battlesLeft', 0)
