# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: armory_yard/scripts/client/armory_yard/gui/impl/gen/view_models/views/lobby/feature/armory_yard_quest_model.py
from frameworks.wulf import Array
from gui.impl.gen.view_models.common.missions.quest_model import QuestModel

class ArmoryYardQuestModel(QuestModel):
    __slots__ = ()

    def __init__(self, properties=16, commands=0):
        super(ArmoryYardQuestModel, self).__init__(properties=properties, commands=commands)

    def getChapterId(self):
        return self._getNumber(11)

    def setChapterId(self, value):
        self._setNumber(11, value)

    def getLevels(self):
        return self._getArray(12)

    def setLevels(self, value):
        self._setArray(12, value)

    @staticmethod
    def getLevelsType():
        return int

    def getShowLevelsAsRange(self):
        return self._getBool(13)

    def setShowLevelsAsRange(self, value):
        self._setBool(13, value)

    def getVehicleTypes(self):
        return self._getArray(14)

    def setVehicleTypes(self, value):
        self._setArray(14, value)

    @staticmethod
    def getVehicleTypesType():
        return unicode

    def getBattleTypes(self):
        return self._getArray(15)

    def setBattleTypes(self, value):
        self._setArray(15, value)

    @staticmethod
    def getBattleTypesType():
        return int

    def _initialize(self):
        super(ArmoryYardQuestModel, self)._initialize()
        self._addNumberProperty('chapterId', 0)
        self._addArrayProperty('levels', Array())
        self._addBoolProperty('showLevelsAsRange', False)
        self._addArrayProperty('vehicleTypes', Array())
        self._addArrayProperty('battleTypes', Array())
