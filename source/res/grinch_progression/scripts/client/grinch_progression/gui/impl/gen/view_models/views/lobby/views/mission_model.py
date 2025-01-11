# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: grinch_progression/scripts/client/grinch_progression/gui/impl/gen/view_models/views/lobby/views/mission_model.py
from grinch_progression.gui.impl.gen.view_models.views.lobby.views.enums import VehicleRole
from frameworks.wulf import ViewModel

class MissionModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=8, commands=0):
        super(MissionModel, self).__init__(properties=properties, commands=commands)

    def getQuestId(self):
        return self._getString(0)

    def setQuestId(self, value):
        self._setString(0, value)

    def getRole(self):
        return VehicleRole(self._getString(1))

    def setRole(self, value):
        self._setString(1, value.value)

    def getChapter(self):
        return self._getNumber(2)

    def setChapter(self, value):
        self._setNumber(2, value)

    def getDescription(self):
        return self._getString(3)

    def setDescription(self, value):
        self._setString(3, value)

    def getCurrent(self):
        return self._getNumber(4)

    def setCurrent(self, value):
        self._setNumber(4, value)

    def getTarget(self):
        return self._getNumber(5)

    def setTarget(self, value):
        self._setNumber(5, value)

    def getPrize(self):
        return self._getNumber(6)

    def setPrize(self, value):
        self._setNumber(6, value)

    def getIsWeekly(self):
        return self._getBool(7)

    def setIsWeekly(self, value):
        self._setBool(7, value)

    def _initialize(self):
        super(MissionModel, self)._initialize()
        self._addStringProperty('questId', '')
        self._addStringProperty('role', VehicleRole.CARRIER.value)
        self._addNumberProperty('chapter', 0)
        self._addStringProperty('description', '')
        self._addNumberProperty('current', 0)
        self._addNumberProperty('target', 0)
        self._addNumberProperty('prize', 0)
        self._addBoolProperty('isWeekly', False)
