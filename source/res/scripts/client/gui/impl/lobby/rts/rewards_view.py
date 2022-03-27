# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/rts/rewards_view.py
import logging
from frameworks.wulf import ViewSettings, WindowFlags
from gui.impl.backport import BackportTooltipWindow
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.rts.rewards_view_model import RewardsViewModel
from gui.impl.lobby.rts.rts_bonuses_packers import getRTSBonusPacker
from gui.impl.lobby.rts.tooltips.tooltip_helpers import createRTSCurrencyTooltipView
from gui.impl.pub import ViewImpl, WindowImpl, ToolTipWindow
from gui.shared.missions.packers.bonus import packBonusModelAndTooltipData
from skeletons.gui.game_control import IRTSProgressionController, IRTSBattlesController
from helpers import dependency
_logger = logging.getLogger(__name__)

class RewardsView(ViewImpl):
    __slots__ = ('_tooltipData', '__isComplete')
    __progressionCtrl = dependency.instance(IRTSProgressionController)
    __rtsController = dependency.descriptor(IRTSBattlesController)

    def __init__(self):
        settings = ViewSettings(layoutID=R.views.lobby.rts.RewardsView(), model=RewardsViewModel())
        super(RewardsView, self).__init__(settings)
        self._tooltipData = None
        self.__isComplete = False
        return

    def createToolTip(self, event):
        window = None
        tooltipID = event.getArgument('tooltipId', None)
        if tooltipID is None:
            _logger.warning('Expected TooltipID, none found.')
            return super(RewardsView, self).createToolTip(event)
        else:
            tooltipID = int(tooltipID)
            contentID = event.contentID
            tooltipData = self._tooltipData[tooltipID]
            _logger.debug('[REWARDS_VIEW] createTooltip tooltipID %s contentID %s, ', tooltipID or '', contentID)
            if contentID == R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent():
                window = BackportTooltipWindow(tooltipData, self.getParentWindow())
            elif contentID == R.views.lobby.rts.StrategistCurrencyTooltip():
                arg = tooltipData.specialArgs[0]
                content = createRTSCurrencyTooltipView(contentID, arg)
                if content:
                    window = ToolTipWindow(event, content, self.getParentWindow())
                    window.move(event.mouse.positionX, event.mouse.positionY)
            if window is not None:
                window.load()
            return window

    @property
    def viewModel(self):
        return super(RewardsView, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        self._tooltipData = {}
        with self.viewModel.transaction() as model:
            currentProgress = self.__progressionCtrl.getCollectionProgress()
            progression = self.__getItemsProgression()
            for level, rewards in progression:
                if currentProgress == level:
                    packBonusModelAndTooltipData(rewards, getRTSBonusPacker(), model.getRewards(), self._tooltipData)
                    model.getRewards().invalidate()
                    model.setCount(level)
                    break

            self.__isComplete = currentProgress == progression[-1][0]
            model.setIsFinal(self.__isComplete)
            model.onClose += self.__onClose

    def _onLoaded(self, *args, **kwargs):
        soundManager = self.__rtsController.getSoundManager()
        soundManager.onRewardScreenShow(self.__isComplete)

    def _finalize(self):
        with self.viewModel.transaction() as model:
            model.onClose -= self.__onClose
        soundManager = self.__rtsController.getSoundManager()
        soundManager.onRewardScreenClose()

    def __onClose(self):
        self.destroyWindow()

    def __getItemsProgression(self):
        result = [(0, {})]
        for data in self.__progressionCtrl.getConfig().progression:
            rewards = self.__progressionCtrl.getQuestRewards(data.get('quest', ''))
            result.append((data.get('itemsCount', 0), rewards))

        return result


class RewardsViewWindow(WindowImpl):
    __slots__ = ()

    def __init__(self, parent=None):
        super(RewardsViewWindow, self).__init__(wndFlags=WindowFlags.DIALOG | WindowFlags.WINDOW_FULLSCREEN, content=RewardsView(), parent=parent)
