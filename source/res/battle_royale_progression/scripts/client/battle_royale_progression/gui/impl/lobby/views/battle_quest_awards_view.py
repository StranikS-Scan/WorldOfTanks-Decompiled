# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale_progression/scripts/client/battle_royale_progression/gui/impl/lobby/views/battle_quest_awards_view.py
from battle_royale_progression.gui.impl.gen.view_models.views.lobby.views.battle_quest_awards_model import BattleQuestAwardsModel, BattleStatus
from battle_royale_progression.gui.impl.lobby.views.bonus_packer import getBonusPacker
from battle_royale_progression.gui.sounds_constants import GENERAL_SOUND_SPACE
from frameworks.wulf import ViewSettings, WindowFlags
from gui.battle_pass.battle_pass_bonuses_packers import packBonusModelAndTooltipData
from gui.impl.gen import R
from gui.impl.lobby.common.view_wrappers import createBackportTooltipDecorator
from gui.impl.pub import ViewImpl
from gui.impl.pub.lobby_window import LobbyNotificationWindow
from gui.server_events.bonuses import getNonQuestBonuses

def awardsFactory(items, ctx=None):
    bonuses = []
    for key, value in items.iteritems():
        bonuses.extend(getNonQuestBonuses(key, value, ctx))

    return bonuses


class BattleQuestAwardsView(ViewImpl):
    _COMMON_SOUND_SPACE = GENERAL_SOUND_SPACE
    __slots__ = ('__tooltipData', '_stage')

    def __init__(self, stage):
        settings = ViewSettings(R.views.battle_royale_progression.BattleQuestAwardsView())
        settings.model = BattleQuestAwardsModel()
        self.__tooltipData = {}
        self._stage = stage
        super(BattleQuestAwardsView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(BattleQuestAwardsView, self).getViewModel()

    @createBackportTooltipDecorator()
    def createToolTip(self, event):
        return super(BattleQuestAwardsView, self).createToolTip(event)

    def getTooltipData(self, event):
        tooltipId = event.getArgument('tooltipId')
        return None if tooltipId is None else self.__tooltipData.get(tooltipId)

    def updateModel(self):
        level = self._stage.get('stage', 0)
        isFinishStage = self._stage.get('finishStage', False)
        rewardsData = self._stage.get('detailedRewards', ())
        bonuses = awardsFactory(rewardsData)
        with self.viewModel.transaction() as model:
            model.setBattleStatus(BattleStatus.INPROGRESS if not isFinishStage else BattleStatus.COMPLETED)
            model.setLevel(level)
            rewards = model.getRewards()
            packBonusModelAndTooltipData(bonuses, rewards, self.__tooltipData, getBonusPacker())

    def _onLoading(self, *args, **kwargs):
        super(BattleQuestAwardsView, self)._onLoading(args, kwargs)
        self.updateModel()
        self.__addListeners()

    def _finalize(self):
        self.__removeListeners()

    def __addListeners(self):
        with self.viewModel.transaction() as model:
            model.onClose += self.__onClose
            model.onApprove += self.__onApprove

    def __removeListeners(self):
        with self.viewModel.transaction() as model:
            model.onClose -= self.__onClose
            model.onApprove -= self.__onApprove

    def __onClose(self):
        self.destroyWindow()

    def __onApprove(self):
        self.__onClose()


class BattleQuestAwardsViewWindow(LobbyNotificationWindow):
    __slots__ = ()

    def __init__(self, stage, parent=None):
        super(BattleQuestAwardsViewWindow, self).__init__(wndFlags=WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, content=BattleQuestAwardsView(stage), parent=parent)
