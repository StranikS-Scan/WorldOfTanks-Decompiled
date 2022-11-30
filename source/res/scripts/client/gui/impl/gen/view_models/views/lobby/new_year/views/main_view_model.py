# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/views/main_view_model.py
from enum import IntEnum
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.new_year.views.challenge.new_year_challenge_model import NewYearChallengeModel
from gui.impl.gen.view_models.views.lobby.new_year.views.friend_challenge.ny_friend_challenge_view_model import NyFriendChallengeViewModel
from gui.impl.gen.view_models.views.lobby.new_year.views.friend_glade.ny_friend_glade_view_model import NyFriendGladeViewModel
from gui.impl.gen.view_models.views.lobby.new_year.views.friends.ny_friends_view_model import NyFriendsViewModel
from gui.impl.gen.view_models.views.lobby.new_year.views.gift_machine.ny_gift_machine_view_model import NyGiftMachineViewModel
from gui.impl.gen.view_models.views.lobby.new_year.views.glade.ny_glade_view_model import NyGladeViewModel
from gui.impl.gen.view_models.views.lobby.new_year.views.marketplace.ny_marketplace_view_model import NyMarketplaceViewModel
from gui.impl.gen.view_models.views.lobby.new_year.views.new_year_info_view_model import NewYearInfoViewModel
from gui.impl.gen.view_models.views.lobby.new_year.views.ny_back_button_model import NyBackButtonModel
from gui.impl.gen.view_models.views.lobby.new_year.views.ny_main_menu_model import NyMainMenuModel
from gui.impl.gen.view_models.views.lobby.new_year.views.ny_sidebar_model import NySidebarModel
from gui.impl.gen.view_models.views.lobby.new_year.views.rewards_info.ny_levels_rewards_model import NyLevelsRewardsModel

class MainViews(IntEnum):
    GLADE = 0
    FRIENDS = 1
    CHALLENGE = 2
    MARKETPLACE = 3
    GIFT_MACHINE = 4
    REWARDS = 5
    INFO = 6
    FRIEND_GLADE = 7
    FRIEND_CHALLENGE = 8
    FRIEND_INFO = 9


class SwitchStates(IntEnum):
    DONE = 0
    DEFAULT = 1
    TO_GLADE_WITH_INTRO = 2
    WITH_SWITCHING_OBJS = 3


class MainViewModel(ViewModel):
    __slots__ = ('onClose', 'onStartClose', 'onFadeInDone', 'onGlobalFadeIn', 'onGlobalFadeOut')

    def __init__(self, properties=18, commands=5):
        super(MainViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def backButton(self):
        return self._getViewModel(0)

    @staticmethod
    def getBackButtonType():
        return NyBackButtonModel

    @property
    def gladeModel(self):
        return self._getViewModel(1)

    @staticmethod
    def getGladeModelType():
        return NyGladeViewModel

    @property
    def mainMenu(self):
        return self._getViewModel(2)

    @staticmethod
    def getMainMenuType():
        return NyMainMenuModel

    @property
    def sidebar(self):
        return self._getViewModel(3)

    @staticmethod
    def getSidebarType():
        return NySidebarModel

    @property
    def infoModel(self):
        return self._getViewModel(4)

    @staticmethod
    def getInfoModelType():
        return NewYearInfoViewModel

    @property
    def marketplaceModel(self):
        return self._getViewModel(5)

    @staticmethod
    def getMarketplaceModelType():
        return NyMarketplaceViewModel

    @property
    def friendsModel(self):
        return self._getViewModel(6)

    @staticmethod
    def getFriendsModelType():
        return NyFriendsViewModel

    @property
    def rewardsModel(self):
        return self._getViewModel(7)

    @staticmethod
    def getRewardsModelType():
        return NyLevelsRewardsModel

    @property
    def challengeModel(self):
        return self._getViewModel(8)

    @staticmethod
    def getChallengeModelType():
        return NewYearChallengeModel

    @property
    def friendGladeModel(self):
        return self._getViewModel(9)

    @staticmethod
    def getFriendGladeModelType():
        return NyFriendGladeViewModel

    @property
    def friendChallengeModel(self):
        return self._getViewModel(10)

    @staticmethod
    def getFriendChallengeModelType():
        return NyFriendChallengeViewModel

    @property
    def giftMachineModel(self):
        return self._getViewModel(11)

    @staticmethod
    def getGiftMachineModelType():
        return NyGiftMachineViewModel

    def getViewType(self):
        return MainViews(self._getNumber(12))

    def setViewType(self, value):
        self._setNumber(12, value.value)

    def getSwitchState(self):
        return SwitchStates(self._getNumber(13))

    def setSwitchState(self, value):
        self._setNumber(13, value.value)

    def getIsWaitingShown(self):
        return self._getBool(14)

    def setIsWaitingShown(self, value):
        self._setBool(14, value)

    def getIsAnimatedShow(self):
        return self._getBool(15)

    def setIsAnimatedShow(self, value):
        self._setBool(15, value)

    def getIsGlobalFaded(self):
        return self._getBool(16)

    def setIsGlobalFaded(self, value):
        self._setBool(16, value)

    def getTutorialState(self):
        return self._getNumber(17)

    def setTutorialState(self, value):
        self._setNumber(17, value)

    def _initialize(self):
        super(MainViewModel, self)._initialize()
        self._addViewModelProperty('backButton', NyBackButtonModel())
        self._addViewModelProperty('gladeModel', NyGladeViewModel())
        self._addViewModelProperty('mainMenu', NyMainMenuModel())
        self._addViewModelProperty('sidebar', NySidebarModel())
        self._addViewModelProperty('infoModel', NewYearInfoViewModel())
        self._addViewModelProperty('marketplaceModel', NyMarketplaceViewModel())
        self._addViewModelProperty('friendsModel', NyFriendsViewModel())
        self._addViewModelProperty('rewardsModel', NyLevelsRewardsModel())
        self._addViewModelProperty('challengeModel', NewYearChallengeModel())
        self._addViewModelProperty('friendGladeModel', NyFriendGladeViewModel())
        self._addViewModelProperty('friendChallengeModel', NyFriendChallengeViewModel())
        self._addViewModelProperty('giftMachineModel', NyGiftMachineViewModel())
        self._addNumberProperty('viewType')
        self._addNumberProperty('switchState')
        self._addBoolProperty('isWaitingShown', False)
        self._addBoolProperty('isAnimatedShow', True)
        self._addBoolProperty('isGlobalFaded', False)
        self._addNumberProperty('tutorialState', 0)
        self.onClose = self._addCommand('onClose')
        self.onStartClose = self._addCommand('onStartClose')
        self.onFadeInDone = self._addCommand('onFadeInDone')
        self.onGlobalFadeIn = self._addCommand('onGlobalFadeIn')
        self.onGlobalFadeOut = self._addCommand('onGlobalFadeOut')
