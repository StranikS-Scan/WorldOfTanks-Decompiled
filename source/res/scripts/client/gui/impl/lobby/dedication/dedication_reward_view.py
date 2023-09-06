# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/dedication/dedication_reward_view.py
from frameworks.wulf import ViewSettings, WindowFlags
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.dedication.dedication_reward_view_model import DedicationRewardViewModel
from gui.impl.pub import ViewImpl
from gui.impl.pub.lobby_window import LobbyWindow
from gui.server_events.bonuses import getNonQuestBonuses
from gui.shared.missions.packers.bonus import packMissionsBonusModelAndTooltipData, getDefaultBonusPacker
from gui.sounds.filters import switchHangarOverlaySoundFilter

class DedicationRewardView(ViewImpl):
    __slots__ = ('__tooltipItems', '__onCloseCallback')

    def __init__(self, *args, **kwargs):
        settings = ViewSettings(R.views.lobby.dedication.DedicationRewardView())
        settings.model = DedicationRewardViewModel()
        settings.args = args
        settings.kwargs = kwargs
        self.__tooltipItems = {}
        self.__onCloseCallback = None
        super(DedicationRewardView, self).__init__(settings)
        return

    @property
    def viewModel(self):
        return super(DedicationRewardView, self).getViewModel()

    def createToolTip(self, event):
        if event.contentID == R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent():
            tooltipId = event.getArgument('tooltipId')
            if tooltipId is None:
                return
            tooltipData = self.__tooltipItems.get(tooltipId)
            if tooltipData is None:
                return
            window = backport.BackportTooltipWindow(tooltipData, self.getParentWindow())
            window.load()
            return window
        else:
            return super(DedicationRewardView, self).createToolTip(event)

    @staticmethod
    def _convertNonQuestBonuses(bonuses):
        rewards = []
        for bonus in bonuses:
            items = []
            for key, value in bonus.iteritems():
                items.extend(getNonQuestBonuses(key, value))

            rewards.extend(items)

        return rewards

    def _initialize(self, bonuses, data, onClose):
        super(DedicationRewardView, self)._initialize()
        self.__onCloseCallback = onClose

    def _finalize(self):
        self.__tooltipItems = None
        if self.__onCloseCallback is not None and callable(self.__onCloseCallback):
            self.__onCloseCallback()
        switchHangarOverlaySoundFilter(on=False)
        super(DedicationRewardView, self)._finalize()
        return

    def _onLoading(self, bonuses, data, *args, **kwargs):
        switchHangarOverlaySoundFilter(on=True)
        self._setAwards(bonuses, data)

    def _setAwards(self, bonuses, data):
        rewards = self._convertNonQuestBonuses(bonuses)
        with self.viewModel.transaction() as tx:
            tx.setLevel(str(data.get('reason', '')))
            packMissionsBonusModelAndTooltipData(rewards, getDefaultBonusPacker(), tx.getMainRewards(), tooltipData=self.__tooltipItems)


class DedicationRewardWindow(LobbyWindow):
    __slots__ = ()

    def __init__(self, bonuses, data, closeCallback):
        super(DedicationRewardWindow, self).__init__(content=DedicationRewardView(bonuses=bonuses, data=data, onClose=closeCallback), wndFlags=WindowFlags.WINDOW_FULLSCREEN | WindowFlags.WINDOW, decorator=None)
        return
