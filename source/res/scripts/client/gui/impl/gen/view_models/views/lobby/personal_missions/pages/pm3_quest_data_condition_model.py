# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/personal_missions/pages/pm3_quest_data_condition_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.personal_missions.pages.pm3_quest_data_progress_type_model import Pm3QuestDataProgressTypeModel

class Pm3QuestDataConditionModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=4, commands=0):
        super(Pm3QuestDataConditionModel, self).__init__(properties=properties, commands=commands)

    def getTitle(self):
        return self._getString(0)

    def setTitle(self, value):
        self._setString(0, value)

    def getLabel(self):
        return self._getString(1)

    def setLabel(self, value):
        self._setString(1, value)

    def getIcon(self):
        return self._getString(2)

    def setIcon(self, value):
        self._setString(2, value)

    def getProgressLines(self):
        return self._getArray(3)

    def setProgressLines(self, value):
        self._setArray(3, value)

    @staticmethod
    def getProgressLinesType():
        return Pm3QuestDataProgressTypeModel

    def _initialize(self):
        super(Pm3QuestDataConditionModel, self)._initialize()
        self._addStringProperty('title', '')
        self._addStringProperty('label', '')
        self._addStringProperty('icon', '')
        self._addArrayProperty('progressLines', Array())
