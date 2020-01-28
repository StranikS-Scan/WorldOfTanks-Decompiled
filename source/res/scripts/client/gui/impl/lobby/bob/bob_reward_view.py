# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/bob/bob_reward_view.py
import logging
from gui.impl.lobby.progressive_reward.progressive_reward_award_view import ProgressiveRewardAwardView
from gui.impl.gen.view_models.views.lobby.bob.bob_reward_model import BobRewardModel
from gui.impl.pub.lobby_window import LobbyWindow
from gui.impl.gen import R
from frameworks.wulf import WindowFlags
from helpers import dependency
from gui.impl import backport
from skeletons.gui.game_control import IBobController, IBobSoundController
from gui.game_control.bob_sound_controller import BOB_TEAM_REWARD_OPEN
from skeletons.gui.customization import ICustomizationService
_logger = logging.getLogger(__name__)

class BobRewardType(object):
    PERSONAL_REWARD = 0
    TEAM_REWARD = 1


class BobRewardView(ProgressiveRewardAwardView):
    __bobController = dependency.descriptor(IBobController)
    __bobSounds = dependency.descriptor(IBobSoundController)
    __c11nService = dependency.descriptor(ICustomizationService)

    def __init__(self, *args):
        super(BobRewardView, self).__init__(*args)
        self.__rewardType = None
        return

    def _initialize(self, bonuses, rewardType, *_):
        self.__rewardType = rewardType
        super(BobRewardView, self)._initialize(bonuses, '', 0)
        self.viewModel.onNextAction += self.__onNextAction
        self.__bobController.onUpdated += self.__updateNextBtn
        with self.viewModel.transaction() as tx:
            isTeam = rewardType == BobRewardType.TEAM_REWARD
            tx.setIsTeamReward(isTeam)
            title, description = self.__getBonusText(bonuses, rewardType)
            tx.setTitle(title)
            tx.setDescription(description)
            bg = R.images.gui.maps.icons.bob.hangar.rewardsScreen.other_bg() if self.__bobController.isNaAsiaRealm() else R.images.gui.maps.icons.bob.hangar.rewardsScreen.cis_bg()
            tx.setBackground(bg)
        self.__updateNextBtn()

    @property
    def viewModel(self):
        return super(BobRewardView, self).getViewModel()

    def _onLoaded(self, *args, **kwargs):
        super(BobRewardView, self)._onLoaded(*args, **kwargs)
        if self.__rewardType == BobRewardType.TEAM_REWARD:
            self.__bobSounds.playSound(BOB_TEAM_REWARD_OPEN)

    def _finalize(self):
        self.viewModel.onNextAction -= self.__onNextAction
        self.__bobController.onUpdated -= self.__updateNextBtn
        super(BobRewardView, self)._finalize()

    def _setSteps(self, *_):
        pass

    def _setBonuses(self, bonuses):
        super(BobRewardView, self)._setBonuses(bonuses)
        if self.__rewardType == BobRewardType.TEAM_REWARD:
            rewardsList = self.viewModel.getRewards()
            for item in rewardsList:
                item.setRendererType('BobTeamAward')

    def _getInitViewModel(self):
        return BobRewardModel()

    def __updateNextBtn(self):
        self.viewModel.setShowNextBtn(self.__hasNext())

    def __hasNext(self):
        return self.__rewardType == BobRewardType.PERSONAL_REWARD and self.__bobController.checkPersonalReward() > 0

    def __onNextAction(self):
        if self.__hasNext():
            self.__bobController.claimReward(self.__bobController.claimPersonalRewardToken)
        else:
            _logger.warning('Could not open next personal reward')
        self.viewModel.setFadeOut(True)

    def __getBonusText(self, bonuses, rewardType):
        if rewardType == BobRewardType.PERSONAL_REWARD:
            if self.__bobController.isRuEuRealm():
                decription = R.strings.bob.rewardsScreen.personal()
            else:
                decription = R.strings.bob.rewardsScreen.personal.na_asia()
            return (R.strings.bob.rewardsScreen.title(), backport.text(decription))
        if rewardType == BobRewardType.TEAM_REWARD:
            for bonus in bonuses:
                bonusName = bonus.get('bonusName')
                if bonusName == 'vehicles':
                    return (R.strings.bob.rewardsScreen.rentTitle(), backport.text(R.strings.bob.rewardsScreen.team.vehicle(), vehicle=bonus.get('userName')))
                if bonusName == 'customizations':
                    intCD = bonus['specialArgs'][0]
                    customization = self.__c11nService.getItemByCD(intCD)
                    return (R.strings.bob.rewardsScreen.title(), backport.text(R.strings.bob.rewardsScreen.team.camouflage(), camouflage=customization.userName))
                if bonusName == 'dossier':
                    return (R.strings.bob.rewardsScreen.title(), backport.text(R.strings.bob.rewardsScreen.team.achievement(), achievement=bonus['userName']))


class BobRewardWindow(LobbyWindow):
    __slots__ = ()

    def __init__(self, bonuses, rewardType):
        super(BobRewardWindow, self).__init__(content=BobRewardView(R.views.lobby.bob.bob_reward_window.BobRewardWindow(), bonuses, rewardType), wndFlags=WindowFlags.OVERLAY, decorator=None)
        return
