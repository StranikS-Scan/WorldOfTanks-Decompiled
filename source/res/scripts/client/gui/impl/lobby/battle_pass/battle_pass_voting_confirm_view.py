# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/battle_pass/battle_pass_voting_confirm_view.py
from account_helpers.settings_core.settings_constants import BattlePassStorageKeys
from frameworks.wulf import ViewFlags, ViewSettings
from gui import SystemMessages
from gui.impl.gen.view_models.views.lobby.battle_pass.battle_pass_voting_confirm_view_model import BattlePassVotingConfirmViewModel
from gui.impl.gen import R
from gui.impl.lobby.dialogs.full_screen_dialog_view import FullScreenDialogView
from gui.shared.gui_items.processors.common import ChooseFinalBattlePassReward
from gui.shared.utils import decorators
from gui.sounds.filters import switchHangarOverlaySoundFilter
from helpers import dependency
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.game_control import IBattlePassController
from skeletons.gui.shared import IItemsCache

class BattlePassVotingConfirmView(FullScreenDialogView):
    __slots__ = ('__data',)
    __battlePassController = dependency.descriptor(IBattlePassController)
    __settingsCore = dependency.descriptor(ISettingsCore)
    __itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, data):
        settings = ViewSettings(R.views.lobby.battle_pass.BattlePassVotingConfirmView())
        settings.flags = ViewFlags.OVERLAY_VIEW
        settings.model = BattlePassVotingConfirmViewModel()
        self.__data = data
        super(BattlePassVotingConfirmView, self).__init__(settings)

    @property
    def viewModel(self):
        return self.getViewModel()

    def _setBaseParams(self, model):
        reward = self.__data.get('finalReward')
        vehicle = self.__itemsCache.items.getItemByCD(reward.getVehicleCD())
        model.setVehicleName(vehicle.name.split(':')[1])
        model.setVehicleCD(reward.getVehicleCD())
        model.setStyleName(reward.getStyleName())
        model.setRecruitName(reward.getRecruitName())
        model.setIsBattlePassBought(self.__battlePassController.isBought())

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

    def __onVoteClick(self, args):
        vehicleCD = int(args.get('vehicleCD'))
        self.__chooseFinalReward(vehicleCD, self.__battlePassController.getSeasonID())

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
