# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: armory_yard/scripts/client/armory_yard/gui/impl/gen/view_models/views/lobby/feature/armory_yard_quest_model.py
from frameworks.wulf import Array
from gui.impl.gen.view_models.common.missions.quest_model import QuestModel

class ArmoryYardQuestModel(QuestModel):
    __slots__ = ()

    def __init__(self, properties=14, commands=0):
        super(ArmoryYardQuestModel, self).__init__(properties=properties, commands=commands)

    def getChapterId(self):
        return self._getNumber(11)

    def setChapterId(self, value):
        self._setNumber(11, value)

    def getVehicleType(self):
        return self._getString(12)

    def setVehicleType(self, value):
        self._setString(12, value)

    def getBattleTypes(self):
        return self._getArray(13)

    def setBattleTypes(self, value):
        self._setArray(13, value)

    @staticmethod
    def getBattleTypesType():
        return int

    def _initialize(self):
        super(ArmoryYardQuestModel, self)._initialize()
        self._addNumberProperty('chapterId', 0)
        self._addStringProperty('vehicleType', '')
        self._addArrayProperty('battleTypes', Array())
