# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: tank_academy/scripts/client/tank_academy/gui/impl/gen/view_models/views/lobby/tank_academy/quest_group_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from tank_academy.gui.impl.gen.view_models.views.lobby.tank_academy.quest_progress_model import QuestProgressModel
from tank_academy.gui.impl.gen.view_models.views.lobby.tank_academy.quest_view_model import QuestViewModel

class QuestGroupModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(QuestGroupModel, self).__init__(properties=properties, commands=commands)

    @property
    def questProgress(self):
        return self._getViewModel(0)

    @staticmethod
    def getQuestProgressType():
        return QuestProgressModel

    def getQuests(self):
        return self._getArray(1)

    def setQuests(self, value):
        self._setArray(1, value)

    @staticmethod
    def getQuestsType():
        return QuestViewModel

    def _initialize(self):
        super(QuestGroupModel, self)._initialize()
        self._addViewModelProperty('questProgress', QuestProgressModel())
        self._addArrayProperty('quests', Array())
