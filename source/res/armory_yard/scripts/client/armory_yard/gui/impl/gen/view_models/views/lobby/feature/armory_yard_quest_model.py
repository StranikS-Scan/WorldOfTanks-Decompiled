# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: armory_yard/scripts/client/armory_yard/gui/impl/gen/view_models/views/lobby/feature/armory_yard_quest_model.py
from frameworks.wulf import Array
from gui.impl.gen.view_models.common.missions.quest_model import QuestModel

class ArmoryYardQuestModel(QuestModel):
    __slots__ = ()

    def __init__(self, properties=23, commands=0):
        super(ArmoryYardQuestModel, self).__init__(properties=properties, commands=commands)

    def getChapterId(self):
        return self._getNumber(13)

    def setChapterId(self, value):
        self._setNumber(13, value)

    def getLevels(self):
        return self._getArray(14)

    def setLevels(self, value):
        self._setArray(14, value)

    @staticmethod
    def getLevelsType():
        return int

    def getShowLevelsAsRange(self):
        return self._getBool(15)

    def setShowLevelsAsRange(self, value):
        self._setBool(15, value)

    def getVehicleTypes(self):
        return self._getArray(16)

    def setVehicleTypes(self, value):
        self._setArray(16, value)

    @staticmethod
    def getVehicleTypesType():
        return unicode

    def getVehicleNations(self):
        return self._getArray(17)

    def setVehicleNations(self, value):
        self._setArray(17, value)

    @staticmethod
    def getVehicleNationsType():
        return unicode

    def getBattleTypes(self):
        return self._getArray(18)

    def setBattleTypes(self, value):
        self._setArray(18, value)

    @staticmethod
    def getBattleTypesType():
        return int

    def getCurrent(self):
        return self._getNumber(19)

    def setCurrent(self, value):
        self._setNumber(19, value)

    def getTotal(self):
        return self._getNumber(20)

    def setTotal(self, value):
        self._setNumber(20, value)

    def getIconKey(self):
        return self._getString(21)

    def setIconKey(self, value):
        self._setString(21, value)

    def getEarned(self):
        return self._getNumber(22)

    def setEarned(self, value):
        self._setNumber(22, value)

    def _initialize(self):
        super(ArmoryYardQuestModel, self)._initialize()
        self._addNumberProperty('chapterId', 0)
        self._addArrayProperty('levels', Array())
        self._addBoolProperty('showLevelsAsRange', False)
        self._addArrayProperty('vehicleTypes', Array())
        self._addArrayProperty('vehicleNations', Array())
        self._addArrayProperty('battleTypes', Array())
        self._addNumberProperty('current', 0)
        self._addNumberProperty('total', 0)
        self._addStringProperty('iconKey', '')
        self._addNumberProperty('earned', 0)
