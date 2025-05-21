# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/gui/impl/lobby/tooltips/difficulty_tooltip.py
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.pub import ViewImpl
from last_stand.gui.impl.gen.view_models.views.lobby.tooltips.difficulty_tooltip_view_model import DifficultyTooltipViewModel
from last_stand.gui.impl.gen.view_models.views.lobby.widgets.difficulty_item_model import StateEnum
from last_stand.gui.impl.gen.view_models.views.lobby.tooltips.difficulty_wave_rewards_model import DifficultyWaveRewardsModel
from last_stand.gui.impl.gen.view_models.views.common.bonus_item_view_model import BonusItemViewModel
from last_stand.gui.impl.lobby.ls_helpers.bonuses_formatters import LSBonusesAwardsComposer, getImgName, getLSMetaAwardFormatter
from last_stand.gui.game_control.ls_artefacts_controller import compareBonusesByPriority
from gui.server_events.awards_formatters import AWARDS_SIZES
from helpers import dependency
from last_stand.skeletons.ls_difficulty_missions_controller import ILSDifficultyMissionsController

class DifficultyTooltipView(ViewImpl):
    __slots__ = ('__isHangar', '__difficulty', '__completedMissions', '__state', '__isLocked')
    lsMissionsCtrl = dependency.descriptor(ILSDifficultyMissionsController)
    _MAX_BONUSES_IN_VIEW = 4

    def __init__(self, isHangar, difficulty, completedMissions, state=StateEnum.DEFAULT, isLocked=True):
        settings = ViewSettings(R.views.last_stand.mono.lobby.tooltips.difficulty_tooltip())
        settings.model = DifficultyTooltipViewModel()
        super(DifficultyTooltipView, self).__init__(settings)
        self.__isHangar = isHangar
        self.__difficulty = difficulty
        self.__completedMissions = completedMissions
        self.__state = state
        self.__isLocked = isLocked

    @property
    def viewModel(self):
        return super(DifficultyTooltipView, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(DifficultyTooltipView, self)._onLoading()
        formatter = LSBonusesAwardsComposer(self._MAX_BONUSES_IN_VIEW, getLSMetaAwardFormatter())
        with self.viewModel.transaction() as model:
            model.setIsHangar(self.__isHangar)
            model.setLevel(self.__difficulty)
            model.setState(self.__state)
            model.setIsLocked(self.__isLocked)
            model.setMaxCompletedMissions(len(self.__completedMissions))
            rewardsWaveVM = model.getRewardsByWave()
            for mission in self.lsMissionsCtrl.missionsSorted(self.__difficulty):
                waveReward = DifficultyWaveRewardsModel()
                waveReward.setIsReceived(mission.index in self.__completedMissions)
                sortedBonuses = sorted(mission.bonusRewards, cmp=compareBonusesByPriority)
                bonusRewards = formatter.getFormattedBonuses(sortedBonuses, AWARDS_SIZES.SMALL)
                rewardsVM = waveReward.getRewards()
                for bonus in bonusRewards:
                    reward = BonusItemViewModel()
                    reward.setUserName(str(bonus.userName))
                    reward.setName(bonus.bonusName)
                    reward.setValue(str(bonus.label))
                    reward.setLabel(str(bonus.label))
                    reward.setIcon(getImgName(bonus.getImage(AWARDS_SIZES.BIG)))
                    reward.setOverlayType(bonus.getOverlayType(AWARDS_SIZES.SMALL))
                    rewardsVM.addViewModel(reward)

                rewardsWaveVM.addViewModel(waveReward)
