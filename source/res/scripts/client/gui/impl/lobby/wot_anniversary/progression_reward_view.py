# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/wot_anniversary/progression_reward_view.py
import logging
import typing
from frameworks.wulf import ViewSettings, WindowFlags, WindowLayer
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.wot_anniversary.progression_reward_view_model import ProgressionRewardViewModel
from gui.impl.lobby.common.view_helpers import packBonusModelAndTooltipData
from gui.impl.lobby.common.view_wrappers import createBackportTooltipDecorator
from gui.impl.lobby.wot_anniversary.bonus_packers import getWotAnniversaryRewardBonusPacker, composeBonuses
from gui.impl.pub import ViewImpl
from gui.impl.pub.lobby_window import LobbyWindow
from helpers import dependency
from skeletons.gui.wot_anniversary import IWotAnniversaryController
if typing.TYPE_CHECKING:
    from gui.impl.backport import TooltipData
_logger = logging.getLogger(__name__)
_MAIN_REWARDS_LENGTH = 3

class ProgressionRewardView(ViewImpl):
    __wotAnniversaryController = dependency.descriptor(IWotAnniversaryController)

    def __init__(self, closeCallback=None, *args, **kwargs):
        settings = ViewSettings(R.views.lobby.wot_anniversary.ProgressionRewardView(), model=ProgressionRewardViewModel(), args=args, kwargs=kwargs)
        self.__tooltips = {}
        self.__closeCallback = closeCallback
        super(ProgressionRewardView, self).__init__(settings)

    @property
    def viewModel(self):
        return self.getViewModel()

    @createBackportTooltipDecorator()
    def createToolTip(self, event):
        return super(ProgressionRewardView, self).createToolTip(event)

    def getTooltipData(self, event):
        tooltipId = event.getArgument('tooltipId')
        return None if tooltipId is None else self.__tooltips.get(tooltipId)

    def _getEvents(self):
        return super(ProgressionRewardView, self)._getEvents() + ((self.viewModel.onClose, self.__onClose),)

    def _onLoading(self, bonuses, reachedStageIdx, *args, **kwargs):
        super(ProgressionRewardView, self)._onLoading(*args, **kwargs)
        progressionConfig = self.__wotAnniversaryController.config.progression
        if not 0 <= reachedStageIdx < len(progressionConfig):
            _logger.error('Incorrect reachedStageIdx=%s is changed to 0.', reachedStageIdx)
            reachedStageIdx = 0
        if reachedStageIdx == 0:
            openedSlotsCount = progressionConfig[reachedStageIdx].tokenCount
        else:
            openedSlotsCount = progressionConfig[reachedStageIdx].tokenCount - progressionConfig[reachedStageIdx - 1].tokenCount
        with self.viewModel.transaction() as tx:
            tx.setOpenedSlotsCount(openedSlotsCount)
            tx.setIsFirstStage(reachedStageIdx == 0)
            bonuses = composeBonuses(bonuses)
            packer = getWotAnniversaryRewardBonusPacker()
            packBonusModelAndTooltipData(bonuses[:_MAIN_REWARDS_LENGTH], tx.getMainRewards(), self.__tooltips, packer=packer)
            packBonusModelAndTooltipData(bonuses[_MAIN_REWARDS_LENGTH:], tx.getAdditionalRewards(), self.__tooltips, packer=packer)

    def _finalize(self):
        self.__tooltips.clear()
        if self.__closeCallback is not None:
            self.__closeCallback()
            self.__closeCallback = None
        super(ProgressionRewardView, self)._finalize()
        return

    def __onClose(self):
        self.destroyWindow()


class ProgressionRewardWindow(LobbyWindow):

    def __init__(self, parent=None, *args, **kwargs):
        super(ProgressionRewardWindow, self).__init__(WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, layer=WindowLayer.TOP_WINDOW, content=ProgressionRewardView(*args, **kwargs), parent=parent)
