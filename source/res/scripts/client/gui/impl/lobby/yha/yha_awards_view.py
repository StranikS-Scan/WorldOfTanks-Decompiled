# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/yha/yha_awards_view.py
import logging
import typing
import SoundGroups
from frameworks.wulf import ViewSettings
from gui.battle_pass.battle_pass_decorators import createBackportTooltipDecorator
from gui.impl.backport import TooltipData
from gui.impl.gen.view_models.views.lobby.yha.yha_awards_view_model import YhaAwardsViewModel
from gui.impl.gen import R
from gui.impl.lobby.yha.yha_bonus_packers import getBonuses, packBonusModelAndTooltips
from gui.impl.pub.lobby_window import LobbyNotificationWindow
from gui.impl.pub import ViewImpl
from gui.sounds.filters import switchHangarOverlaySoundFilter
_logger = logging.getLogger(__name__)
_ENTER_SOUND_EVENT = 'bp_reward_screen'

class YhaAwardsView(ViewImpl):
    __slots__ = ('__rewardModels', '__tooltips')

    def __init__(self, *args, **kwargs):
        settings = ViewSettings(R.views.lobby.yha.YhaAwardsView())
        settings.model = YhaAwardsViewModel()
        settings.args = args
        settings.kwargs = kwargs
        super(YhaAwardsView, self).__init__(settings)
        self.__tooltips = []

    @property
    def viewModel(self):
        return super(YhaAwardsView, self).getViewModel()

    @createBackportTooltipDecorator()
    def createToolTip(self, event):
        return super(YhaAwardsView, self).createToolTip(event)

    def getTooltipData(self, event):
        tooltipId = event.getArgument('tooltipId')
        return self.__tooltips[int(tooltipId)] if tooltipId is not None else None

    def _onLoading(self, rewards, *args, **kwargs):
        bonuses = getBonuses(rewards)
        models, self.__tooltips = packBonusModelAndTooltips(bonuses)
        with self.viewModel.transaction() as tx:
            rewardsList = tx.getRewards()
            rewardsList.clear()
            for model in models:
                rewardsList.addViewModel(model)

            rewardsList.invalidate()
        switchHangarOverlaySoundFilter(on=True)
        SoundGroups.g_instance.playSound2D(_ENTER_SOUND_EVENT)

    def _finalize(self):
        switchHangarOverlaySoundFilter(on=False)


class YhaAwardsWindow(LobbyNotificationWindow):
    __slots__ = ()

    def __init__(self, rewards, parent=None):
        super(YhaAwardsWindow, self).__init__(content=YhaAwardsView(rewards), parent=parent)
