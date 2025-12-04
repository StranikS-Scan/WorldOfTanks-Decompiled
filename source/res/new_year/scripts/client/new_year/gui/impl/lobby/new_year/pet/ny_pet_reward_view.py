# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: new_year/scripts/client/new_year/gui/impl/lobby/new_year/pet/ny_pet_reward_view.py
import random
import SoundGroups
from constants import LOOTBOX_TOKEN_PREFIX
from gui.Scaleform.Waiting import Waiting
from helpers import dependency
from items.tankmen import RECRUIT_TMAN_TOKEN_PREFIX
from messenger.proto.events import g_messengerEvents
from new_year.gui.impl.gen.view_models.views.lobby.new_year.views.pet_reward_view_model import PetRewardViewModel
from new_year.gui.impl.new_year.sounds import RaccoonStates
from frameworks.wulf import ViewFlags, ViewSettings, WindowFlags
from gui.impl.pub import ViewImpl, WindowImpl
from gui.impl.gen import R
from new_year.gui.shared.ny_machine_helper import getMachineLootboxToken
from new_year.skeletons.new_year import ITamagotchiDataProvider, ITamagotchiWebRequester, IRaccoonAnimationController
from gui.server_events.recruit_helper import getRecruitInfo
_WAIT_ID = 'tamagotchiGift'

class PetRewardView(ViewImpl):
    __slots__ = ()
    RANDOM_RANGE = (1, 50)
    _dataProvider = dependency.descriptor(ITamagotchiDataProvider)
    _webRequester = dependency.descriptor(ITamagotchiWebRequester)
    _raccoonController = dependency.descriptor(IRaccoonAnimationController)

    def __init__(self):
        settings = ViewSettings(layoutID=R.views.new_year.lobby.new_year.PetRewardView(), flags=ViewFlags.VIEW, model=PetRewardViewModel())
        super(PetRewardView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(PetRewardView, self).getViewModel()

    def _getEvents(self):
        return ((self.viewModel.onClose, self.__onClose),
         (self._dataProvider.onGiftObtained, self.__onGiftObtained),
         (self._raccoonController.onShowGift, self.__showReward),
         (self._dataProvider.onMailRewards, self.__onMailRewards))

    def _initialize(self):
        self._dataProvider.onUpdateTipsRequested(False)
        Waiting.show(_WAIT_ID)
        self._webRequester.takeGift()
        super(PetRewardView, self)._initialize()

    def _finalize(self):
        g_messengerEvents.onUnlockPopUpMessages()
        super(PetRewardView, self)._finalize()
        Waiting.hide(_WAIT_ID)
        self._raccoonController.releaseLetterAction()
        self._dataProvider.onUpdateTipsRequested(True)

    def __onClose(self):
        SoundGroups.g_instance.setState(RaccoonStates.GROUP, RaccoonStates.MAIN)
        self.destroyWindow()

    def __onGiftObtained(self, isSuccess, _, count, isSecret, isRecalculation):
        g_messengerEvents.onLockPopUpMessages(lockHigh=True)
        Waiting.hide(_WAIT_ID)
        if not isSuccess:
            self.destroyWindow()
            return
        SoundGroups.g_instance.setState(RaccoonStates.GROUP, RaccoonStates.LETTER)
        with self.viewModel.transaction() as tx:
            tx.setOpenedLetters(count)
            tx.setTextNumber(random.randint(*self.RANDOM_RANGE))
        self._raccoonController.showLetterAction()

    def __onMailRewards(self, rewards):
        tokens = rewards.get('tokens', {})
        for name, token in tokens.iteritems():
            if name.startswith(LOOTBOX_TOKEN_PREFIX) and name == getMachineLootboxToken():
                self.viewModel.setNumberOfTokens(token.get('count', 0))
            if name.startswith(RECRUIT_TMAN_TOKEN_PREFIX):
                recruitInfo = getRecruitInfo(name)
                if recruitInfo is None:
                    continue
                self.viewModel.setTankmanName(recruitInfo.getFullUserName())
                self.viewModel.setTankmanIcon(recruitInfo.getDynIconName())

        return

    def __showReward(self):
        window = self.getWindow()
        window.setReadyToAnim(True)
        window.show()
        with self.viewModel.transaction() as tx:
            tx.setStartVideo(True)


class PetRewardViewWindow(WindowImpl):
    __slots__ = ('__isReadyToAnim',)

    def __init__(self, parent=None):
        super(PetRewardViewWindow, self).__init__(WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, content=PetRewardView(), parent=parent)
        self.__isReadyToAnim = False

    def setReadyToAnim(self, value):
        self.__isReadyToAnim = value

    def show(self, focus=True):
        if self.__isReadyToAnim:
            super(PetRewardViewWindow, self).show(focus)
