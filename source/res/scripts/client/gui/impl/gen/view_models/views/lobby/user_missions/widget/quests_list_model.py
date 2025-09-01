# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/user_missions/widget/quests_list_model.py
from frameworks.wulf import Array, ViewModel
from gui.impl.gen.view_models.views.lobby.user_missions.widget.widget_quest_model import WidgetQuestModel

class QuestsListModel(ViewModel):
    __slots__ = ('onMissionClick', 'onMarkAsViewed')

    def __init__(self, properties=1, commands=2):
        super(QuestsListModel, self).__init__(properties=properties, commands=commands)

    def getQuests(self):
        return self._getArray(0)

    def setQuests(self, value):
        self._setArray(0, value)

    @staticmethod
    def getQuestsType():
        return WidgetQuestModel

    def _initialize(self):
        super(QuestsListModel, self)._initialize()
        self._addArrayProperty('quests', Array())
        self.onMissionClick = self._addCommand('onMissionClick')
        self.onMarkAsViewed = self._addCommand('onMarkAsViewed')
