# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/battle_pass/battle_pass_daily_quests_intro_view.py
from frameworks.wulf import ViewFlags, ViewSettings, WindowFlags, WindowLayer
from gui.impl.lobby.missions.missions_helpers import getDailyEpicQuestToken
from gui.shared.view_helpers.blur_manager import CachedBlur
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.battle_pass.battle_pass_daily_quests_intro_view_model import BattlePassDailyQuestsIntroViewModel
from gui.impl.pub import ViewImpl, WindowImpl
from helpers import dependency
from skeletons.gui.server_events import IEventsCache

class BattlePassDailyQuestsIntroView(ViewImpl):
    __eventsCache = dependency.descriptor(IEventsCache)
    __slots__ = ()

    def __init__(self):
        settings = ViewSettings(R.views.lobby.battle_pass.BattlePassDailyQuestsIntroView())
        settings.flags = ViewFlags.LOBBY_TOP_SUB_VIEW
        settings.model = BattlePassDailyQuestsIntroViewModel()
        super(BattlePassDailyQuestsIntroView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(BattlePassDailyQuestsIntroView, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(BattlePassDailyQuestsIntroView, self)._onLoading(*args, **kwargs)
        epicQuest = self.__eventsCache.getDailyEpicQuest()
        with self.viewModel.transaction() as model:
            dqToken = getDailyEpicQuestToken(epicQuest)
            model.setQuestNumber(dqToken.getNeededCount())


class BattlePassDailyQuestsIntroWindow(WindowImpl):
    __slots__ = ('__blur',)

    def __init__(self, parent=None):
        super(BattlePassDailyQuestsIntroWindow, self).__init__(WindowFlags.WINDOW, content=BattlePassDailyQuestsIntroView(), parent=parent)
        self.__blur = CachedBlur(enabled=True, ownLayer=WindowLayer.TOP_SUB_VIEW)

    def _finalize(self):
        self.__blur.fini()
        super(BattlePassDailyQuestsIntroWindow, self)._finalize()
