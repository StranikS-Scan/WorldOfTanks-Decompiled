# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/impl/gen/view_models/views/lobby/common/crew_item_model.py
from frameworks.wulf import ViewModel

class CrewItemModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=4, commands=0):
        super(CrewItemModel, self).__init__(properties=properties, commands=commands)

    def getId(self):
        return self._getNumber(0)

    def setId(self, value):
        self._setNumber(0, value)

    def getRole(self):
        return self._getString(1)

    def setRole(self, value):
        self._setString(1, value)

    def getGroup(self):
        return self._getString(2)

    def setGroup(self, value):
        self._setString(2, value)

    def getIsAvailable(self):
        return self._getBool(3)

    def setIsAvailable(self, value):
        self._setBool(3, value)

    def _initialize(self):
        super(CrewItemModel, self)._initialize()
        self._addNumberProperty('id', 0)
        self._addStringProperty('role', '')
        self._addStringProperty('group', '')
        self._addBoolProperty('isAvailable', False)
