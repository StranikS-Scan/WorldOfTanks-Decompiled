# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/early_access/early_access_quest_model.py
from frameworks.wulf import Array
from gui.impl.gen.view_models.common.missions.quest_model import QuestModel
from gui.impl.gen.view_models.views.lobby.common.vehicle_model import VehicleModel

class EarlyAccessQuestModel(QuestModel):
    __slots__ = ()

    def __init__(self, properties=19, commands=0):
        super(EarlyAccessQuestModel, self).__init__(properties=properties, commands=commands)

    def getChapterId(self):
        return self._getString(13)

    def setChapterId(self, value):
        self._setString(13, value)

    def getTokensForCompletion(self):
        return self._getNumber(14)

    def setTokensForCompletion(self, value):
        self._setNumber(14, value)

    def getVehicleType(self):
        return self._getString(15)

    def setVehicleType(self, value):
        self._setString(15, value)

    def getMinVehicleLvl(self):
        return self._getNumber(16)

    def setMinVehicleLvl(self, value):
        self._setNumber(16, value)

    def getMaxVehicleLvl(self):
        return self._getNumber(17)

    def setMaxVehicleLvl(self, value):
        self._setNumber(17, value)

    def getRequiredVehicles(self):
        return self._getArray(18)

    def setRequiredVehicles(self, value):
        self._setArray(18, value)

    @staticmethod
    def getRequiredVehiclesType():
        return VehicleModel

    def _initialize(self):
        super(EarlyAccessQuestModel, self)._initialize()
        self._addStringProperty('chapterId', '')
        self._addNumberProperty('tokensForCompletion', 0)
        self._addStringProperty('vehicleType', '')
        self._addNumberProperty('minVehicleLvl', 0)
        self._addNumberProperty('maxVehicleLvl', 10)
        self._addArrayProperty('requiredVehicles', Array())
