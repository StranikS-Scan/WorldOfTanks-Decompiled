# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/personal_missions/pages/pm3_quest_element_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.personal_missions.pages.pm3_quest_data_condition_model import Pm3QuestDataConditionModel
from gui.impl.gen.view_models.views.lobby.personal_missions.pages.pm3_quest_data_progress_type_model import Pm3QuestDataProgressTypeModel

class Pm3QuestElementModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(Pm3QuestElementModel, self).__init__(properties=properties, commands=commands)

    def getConditions(self):
        return self._getArray(0)

    def setConditions(self, value):
        self._setArray(0, value)

    @staticmethod
    def getConditionsType():
        return Pm3QuestDataConditionModel

    def getRepeatCount(self):
        return self._getArray(1)

    def setRepeatCount(self, value):
        self._setArray(1, value)

    @staticmethod
    def getRepeatCountType():
        return Pm3QuestDataProgressTypeModel

    def getRepeatProgressText(self):
        return self._getBool(2)

    def setRepeatProgressText(self, value):
        self._setBool(2, value)

    def _initialize(self):
        super(Pm3QuestElementModel, self)._initialize()
        self._addArrayProperty('conditions', Array())
        self._addArrayProperty('repeatCount', Array())
        self._addBoolProperty('repeatProgressText', False)
