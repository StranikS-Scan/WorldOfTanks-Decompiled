# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/battle_pass/battle_pass_voting_confirm_view.py
from account_helpers.settings_core.settings_constants import BattlePassStorageKeys
from frameworks.wulf import ViewSettings
from gui import SystemMessages
from gui.battle_pass.battle_pass_award import BattlePassAwardsManager as awardsManager
from gui.battle_pass.battle_pass_helpers import BackgroundPositions
from gui.impl.gen.view_models.views.lobby.battle_pass.battle_pass_voting_confirm_view_model import BattlePassVotingConfirmViewModel
from gui.impl.gen import R
from gui.impl.lobby.dialogs.full_screen_dialog_view import FullScreenDialogView
from gui.shared.gui_items.processors.common import ChooseFinalBattlePassReward
from gui.shared.utils import decorators
from gui.sounds.filters import switchHangarOverlaySoundFilter
from helpers import dependency
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.game_control import IBattlePassController

class BattlePassVotingConfirmView(FullScreenDialogView):
    __slots__ = ('__reward',)
    __battlePassController = dependency.descriptor(IBattlePassController)
    __settingsCore = dependency.descriptor(ISettingsCore)

    def __init__(self, data):
        settings = ViewSettings(R.views.lobby.battle_pass.BattlePassVotingConfirmView())
        settings.model = BattlePassVotingConfirmViewModel()
        self.__reward = data.get('finalReward')
        super(BattlePassVotingConfirmView, self).__init__(settings)

    @property
    def viewModel(self):
        return self.getViewModel()

    def _setBaseParams(self, model):
        if self.__reward is None:
            return
        else:
            model.setStyleName(self.__reward.getStyleName())
            model.setRecruitName(self.__reward.getRecruitName())
            model.setIsBattlePassBought(self.__battlePassController.isBought())
            vehiclePos = awardsManager.getVehicleBackgroundPosition(self.__reward.getVehicleCD())
            if vehiclePos == BackgroundPositions.LEFT:
                model.setIsLeft(True)
            elif vehiclePos == BackgroundPositions.RIGHT:
                model.setIsRight(True)
            return

    def _initialize(self):
        super(BattlePassVotingConfirmView, self)._initialize()
        self.__battlePassController.onBattlePassSettingsChange += self.__onSettingsChange
        switchHangarOverlaySoundFilter(on=True)

    def _finalize(self):
        super(BattlePassVotingConfirmView, self)._finalize()
        self.__battlePassController.onBattlePassSettingsChange -= self.__onSettingsChange
        switchHangarOverlaySoundFilter(on=False)

    def _addListeners(self):
        self.viewModel.onVoteClick += self.__onVoteClick

    def _removeListeners(self):
        self.viewModel.onVoteClick -= self.__onVoteClick

    def _blurBackGround(self):
        pass

    def __onVoteClick(self):
        if self.__reward is None:
            return
        else:
            self.__chooseFinalReward(self.__reward.getVehicleCD(), self.__battlePassController.getSeasonID())
            return

    def __setVotedWithBoughtBP(self):
        self.__settingsCore.serverSettings.saveInBPStorage({BattlePassStorageKeys.VOTED_WITH_BOUGHT_BP: self.__battlePassController.isBought()})

    @decorators.process('chooseFinalReward')
    def __chooseFinalReward(self, rewardID, seasonID):
        result = yield ChooseFinalBattlePassReward(rewardID, seasonID).request()
        if result.userMsg:
            SystemMessages.pushMessage(result.userMsg, type=result.sysMsgType)
        if result.success:
            self.__setVotedWithBoughtBP()
            super(BattlePassVotingConfirmView, self)._onAcceptClicked()

    def __onSettingsChange(self, *_):
        if not self.__battlePassController.isVisible() or self.__battlePassController.isPaused():
            self.destroyWindow()
