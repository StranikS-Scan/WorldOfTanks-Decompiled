# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/comp7/gui/impl/gen/view_models/views/lobby/missions/comp7_daily_quests_widget_view_model.py
from comp7.gui.impl.gen.view_models.views.lobby.missions.comp7_widget_quest_model import Comp7WidgetQuestModel
from gui.impl.gen.view_models.views.lobby.missions.widget.daily_quests_widget_view_model import DailyQuestsWidgetViewModel

class Comp7DailyQuestsWidgetViewModel(DailyQuestsWidgetViewModel):
    __slots__ = ()

    def __init__(self, properties=5, commands=2):
        super(Comp7DailyQuestsWidgetViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def comp7WidgetQuest(self):
        return self._getViewModel(4)

    @staticmethod
    def getComp7WidgetQuestType():
        return Comp7WidgetQuestModel

    def _initialize(self):
        super(Comp7DailyQuestsWidgetViewModel, self)._initialize()
        self._addViewModelProperty('comp7WidgetQuest', Comp7WidgetQuestModel())
