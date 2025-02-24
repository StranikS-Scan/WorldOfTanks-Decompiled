# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/comp7/gui/Scaleform/daapi/view/lobby/hangar/daily_quest_widget.py
import typing
from comp7.gui.impl.lobby.comp7_helpers.comp7_weekly_quests_widget import Comp7WeeklyQuestsWidgetView
from comp7.skeletons.gui.game_control import IComp7WeeklyQuestsController
from gui.Scaleform.daapi.view.lobby.hangar.daily_quest_widget import BaseQuestsWidgetComponent
from helpers import dependency
from skeletons.gui.game_control import IComp7Controller
if typing.TYPE_CHECKING:
    from comp7.gui.game_control.comp7_controller import Comp7Controller
    from comp7.gui.game_control.comp7_weekly_quests_controller import Comp7WeeklyQuestsController
    from gui.Scaleform.daapi.view.lobby.hangar.daily_quest_widget import DailyQuestWidget

class Comp7QuestWidgetComponent(BaseQuestsWidgetComponent):
    injectQuestsWidgetViewType = Comp7WeeklyQuestsWidgetView
    __comp7Controller = dependency.descriptor(IComp7Controller)
    __comp7WeeklyQuestsCtrl = dependency.descriptor(IComp7WeeklyQuestsController)

    @classmethod
    def shouldComponentBeActive(cls):
        return cls.__comp7Controller.isComp7PrbActive() and not cls.__comp7WeeklyQuestsCtrl.isInHideState()

    def _injectAndSetVisibilityOfWidgetView(self):
        injector = self._injector
        view = injector.createInjectView()
        view.setVisible(not self._shouldHide())
        view.getViewModel().onDisappear += self._injector.destroyQuestsWidgetView

    def _hasIncompleteQuests(self):
        return True if super(Comp7QuestWidgetComponent, self)._hasIncompleteQuests() else not self.__comp7WeeklyQuestsCtrl.isInHideState()

    def _onSyncCompleted(self):
        self._executeShowOrHide()
