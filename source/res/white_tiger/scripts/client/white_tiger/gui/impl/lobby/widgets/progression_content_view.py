# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/impl/lobby/widgets/progression_content_view.py
from frameworks.wulf import ViewSettings, ViewFlags
from gui.impl.pub import ViewImpl
from helpers import dependency
from gui.impl.gen import R
from gui.impl.pub.view_component import ViewComponent
from gui.battle_pass.battle_pass_bonuses_packers import packBonusModelAndTooltipData
from white_tiger.gui.wt_bonus_packers import getWTEventBonusPacker
from white_tiger.gui.impl.gen.view_models.views.lobby.widgets.progression_content_view_model import ProgressionContentViewModel
from white_tiger.gui.impl.gen.view_models.views.lobby.feature.progression.progression_level_model import ProgressionLevelModel
from white_tiger.gui.impl.gen.view_models.views.lobby.tooltips.stamp_tooltip_view_model import StampTooltipViewModel
from white_tiger.skeletons.white_tiger_controller import IWhiteTigerController
from white_tiger.skeletons.economics_controller import IEconomicsController
from white_tiger.gui.white_tiger_account_settings import AccountSettingsKeys, getSettings
import typing
if typing.TYPE_CHECKING:
    from typing import Tuple
    from gui.server_events.bonuses import SimpleBonus
_BONUSES_PRIORITY = ('ticket', 'battlePassPoints', 'lootBox', 'credits', 'premium_plus', 'crystal', 'equipCoin', 'customizations', 'dossier')
_BONUSES_ORDER = dict(((n, idx) for idx, n in enumerate(_BONUSES_PRIORITY)))

def wtRewardSortKey(reward):
    name = reward.getName()
    return (_BONUSES_ORDER.get(name, float('inf')), name)


class ProgressionContentView(ViewComponent[ProgressionContentViewModel]):
    __wtCtrl = dependency.descriptor(IWhiteTigerController)
    __economicsCtrl = dependency.descriptor(IEconomicsController)

    def __init__(self, layoutID=R.aliases.white_tiger.shared.ProgressionContent(), **kwargs):
        super(ProgressionContentView, self).__init__(layoutID=layoutID, flags=ViewFlags.LOBBY_SUB_VIEW, model=ProgressionContentViewModel)
        self.__tooltipData = {}

    def _onLoading(self, *args, **kwargs):
        super(ProgressionContentView, self)._onLoading(args, kwargs)
        self.__updateModel()

    @property
    def viewModel(self):
        return super(ProgressionContentView, self).getViewModel()

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.white_tiger.mono.lobby.tooltips.stamp_tooltip():
            settings = ViewSettings(layoutID=R.views.white_tiger.mono.lobby.tooltips.stamp_tooltip(), model=StampTooltipViewModel())
            return ViewImpl(settings)
        return super(ProgressionContentView, self).createToolTipContent(event, contentID)

    def getTooltipData(self, event):
        tooltipId = event.getArgument('tooltipId')
        return None if tooltipId is None else self.__tooltipData.get(tooltipId)

    def _getEvents(self):
        return ((self.__economicsCtrl.onProgressUpdated, self.__updateModel), (self.__economicsCtrl.onRewardsUpdated, self.__updateModel), (self.__economicsCtrl.onProgressSeenByUser, self.__onProgressSeenByUser))

    def __updateModel(self):
        if not self.__wtCtrl.isAvailable():
            return
        with self.viewModel.transaction() as model:
            self.__fillProgression(model)

    def __fillProgression(self, model):
        self.__tooltipData = {}
        previousStamps = getSettings(AccountSettingsKeys.WT_LAST_SEEN_STAMPS)
        currentStamps = self.__economicsCtrl.getStampsCount()
        stampsPerLevel = self.__economicsCtrl.getStampsCountPerLevel()
        currentLevel = self.__economicsCtrl.getCurrentLevel()
        model.setStampsCurrent(currentStamps)
        model.setStampsPrevious(previousStamps)
        model.setStampsNeededPerStage(stampsPerLevel)
        model.setCurrentStage(currentLevel)
        progression = self.__getItemsProgression()
        stages = model.getStages()
        stages.clear()
        stages.reserve(len(progression))
        for _, rewards in progression:
            item = ProgressionLevelModel()
            rewardsList = item.getRewards()
            rewardsList.reserve(len(rewards))
            packBonusModelAndTooltipData(rewards, rewardsList, self.__tooltipData, getWTEventBonusPacker())
            stages.addViewModel(item)

        stages.invalidate()

    def __getItemsProgression(self):
        result = []
        for data in self.__economicsCtrl.getConfig()['progression']:
            rewards = self.__economicsCtrl.getProgressionRewards(data.get('quest', ''))
            rewards = sorted(rewards, key=wtRewardSortKey)
            result.append((data.get('level', 0), rewards))

        return result

    def __onProgressSeenByUser(self, currentlySeenStamps, currentlySeenLevel):
        with self.viewModel.transaction() as model:
            model.setStampsPrevious(currentlySeenStamps)
