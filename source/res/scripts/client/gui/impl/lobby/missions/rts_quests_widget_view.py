# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/missions/rts_quests_widget_view.py
from frameworks.wulf import ViewSettings, ViewFlags
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.missions.widget.daily_quests_widget_view_model import DailyQuestsWidgetViewModel
from helpers import dependency
from daily_quests_widget_view import DailyQuestsWidgetView
from skeletons.gui.game_control import IRTSProgressionController
from gui.shared.event_dispatcher import showRTSMetaRootWindow
from gui.impl.gen.view_models.views.lobby.rts.meta_tab_model import Tabs
from skeletons.gui.game_control import IRTSBattlesController

class RtsQuestsWidgetView(DailyQuestsWidgetView):
    __progressionCtrl = dependency.descriptor(IRTSProgressionController)
    __battlesController = dependency.instance(IRTSBattlesController)

    def __init__(self):
        settings = ViewSettings(R.views.lobby.rts.QuestsWidget(), ViewFlags.COMPONENT, DailyQuestsWidgetViewModel())
        super(RtsQuestsWidgetView, self).__init__(settings)

    def _initialize(self, *args, **kwargs):
        super(RtsQuestsWidgetView, self)._initialize(*args, **kwargs)
        self.__battlesController.onControlModeChanged += self.__onGameModeChanged
        self.__battlesController.onGameModeChanged += self.__onGameModeChanged
        self.viewModel.onAppear += self.__onAppear

    def _finalize(self):
        super(RtsQuestsWidgetView, self)._finalize()
        self.__battlesController.onControlModeChanged -= self.__onGameModeChanged
        self.__battlesController.onGameModeChanged -= self.__onGameModeChanged
        self.viewModel.onAppear -= self.__onAppear

    def _getQuests(self):
        isCommander = self.__battlesController.isCommander()
        return self.__progressionCtrl.getQuests(isCommander, includeFuture=False)

    def _onQuestClick(self):
        showRTSMetaRootWindow(Tabs.QUESTS.value)

    def __onGameModeChanged(self, *_):
        self._updateViewModel()

    def __onAppear(self):
        self._markVisited()
