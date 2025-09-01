# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7_light/scripts/client/comp7_light/gui/impl/gen/view_models/views/lobby/progression_quests_model.py
from frameworks.wulf import Array, ViewModel
from gui.impl.gen.view_models.views.lobby.user_missions.widget.widget_quest_model import WidgetQuestModel

class ProgressionQuestsModel(ViewModel):
    __slots__ = ('onMissionClick', 'onMarkAsViewed')

    def __init__(self, properties=2, commands=2):
        super(ProgressionQuestsModel, self).__init__(properties=properties, commands=commands)

    def getQuests(self):
        return self._getArray(0)

    def setQuests(self, value):
        self._setArray(0, value)

    @staticmethod
    def getQuestsType():
        return WidgetQuestModel

    def getIsMissionsEnable(self):
        return self._getBool(1)

    def setIsMissionsEnable(self, value):
        self._setBool(1, value)

    def _initialize(self):
        super(ProgressionQuestsModel, self)._initialize()
        self._addArrayProperty('quests', Array())
        self._addBoolProperty('isMissionsEnable', True)
        self.onMissionClick = self._addCommand('onMissionClick')
        self.onMarkAsViewed = self._addCommand('onMarkAsViewed')
