# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/gui/impl/battle/full_stats.py
from LSArenaPhasesComponent import LSArenaPhasesComponent
from LSTeamInfoStatsComponent import LSTeamInfoStatsComponent
from frameworks.wulf import ViewSettings, WindowFlags, WindowLayer
from gui.battle_control import avatar_getter
from gui.impl.lobby.common.tooltips.extended_text_tooltip import ExtendedTextTooltip
from gui.impl.wrappers.function_helpers import replaceNoneKwargsModel
from last_stand.gui.ls_gui_constants import BATTLE_CTRL_ID
from last_stand.gui.impl.gen.view_models.views.battle.full_stats_view_model import FullStatsViewModel
from gui.impl.pub import ViewImpl, WindowImpl
from last_stand_common.last_stand_constants import ARENA_BONUS_TYPE_TO_LEVEL
from helpers import dependency
from gui.impl import backport
from gui.impl.gen import R
from last_stand.gui.impl.lobby.widgets.event_stats import EventStats
from skeletons.gui.battle_session import IBattleSessionProvider

class FullEventStatsView(ViewImpl):
    _sessionProvider = dependency.descriptor(IBattleSessionProvider)
    _FIRST_PHASE = 1

    def __init__(self):
        settings = ViewSettings(layoutID=self.getLayoutID(), model=FullStatsViewModel())
        super(FullEventStatsView, self).__init__(settings)
        self.setChildView(resourceID=R.aliases.last_stand.shared.TeamStats(), view=EventStats())

    def _onLoading(self, *args, **kwargs):
        super(FullEventStatsView, self)._onLoading(*args, **kwargs)
        with self.viewModel.transaction() as tx:
            self.__updateHeader(model=tx)

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.lobby.common.tooltips.ExtendedTextTooltip():
            text = event.getArgument('text', '')
            stringifyKwargs = event.getArgument('stringifyKwargs', '')
            return ExtendedTextTooltip(text, stringifyKwargs)
        return super(FullEventStatsView, self).createToolTipContent(event, contentID)

    @classmethod
    def getLayoutID(cls):
        return R.views.last_stand.mono.battle.tab_screen()

    @property
    def vehicleStats(self):
        return LSTeamInfoStatsComponent.getInstance()

    @property
    def arenaPhases(self):
        return LSArenaPhasesComponent.getInstance()

    @property
    def activePhase(self):
        return max(self._FIRST_PHASE, getattr(self.arenaPhases, 'activePhase', 0))

    @property
    def battleGUICtrl(self):
        return self._sessionProvider.dynamic.getControllerByID(BATTLE_CTRL_ID.LS_BATTLE_GUI_CTRL)

    @property
    def viewModel(self):
        return super(FullEventStatsView, self).getViewModel()

    def _subscribe(self):
        super(FullEventStatsView, self)._subscribe()
        lsBattleGuiCtrl = self.battleGUICtrl
        if lsBattleGuiCtrl:
            lsBattleGuiCtrl.onPhaseChanged += self.__onPhaseChanged

    def _unsubscribe(self):
        super(FullEventStatsView, self)._unsubscribe()
        lsBattleGuiCtrl = self.battleGUICtrl
        if lsBattleGuiCtrl:
            lsBattleGuiCtrl.onPhaseChanged -= self.__onPhaseChanged

    @replaceNoneKwargsModel
    def __updateHeader(self, model=None):
        arena = avatar_getter.getArena()
        if arena:
            model.setDifficultyLevel(ARENA_BONUS_TYPE_TO_LEVEL.get(arena.bonusType, 1))
        locTitle = R.strings.last_stand_battle.eventStats.activeWave()
        model.setMissionTitle(backport.text(locTitle, num=self.activePhase))
        model.setMissionTask(backport.text(R.strings.last_stand_battle.eventStats.mission()))

    def __onPhaseChanged(self):
        self.__updateHeader()


class FullEventStatsWindow(WindowImpl):
    __slots__ = ()

    def __init__(self, parent=None):
        super(FullEventStatsWindow, self).__init__(wndFlags=WindowFlags.WINDOW_FULLSCREEN | WindowFlags.WINDOW | WindowFlags.WINDOW_MODALITY_MASK, content=FullEventStatsView(), layer=WindowLayer.OVERLAY, parent=parent)
