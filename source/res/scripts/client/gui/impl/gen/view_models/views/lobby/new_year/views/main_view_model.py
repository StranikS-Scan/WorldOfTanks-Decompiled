# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/views/main_view_model.py
from enum import IntEnum
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.new_year.views.albums.ny_album_view_model import NyAlbumViewModel
from gui.impl.gen.view_models.views.lobby.new_year.views.break_decorations.ny_break_decorations_view_model import NyBreakDecorationsViewModel
from gui.impl.gen.view_models.views.lobby.new_year.views.challenge.new_year_challenge_model import NewYearChallengeModel
from gui.impl.gen.view_models.views.lobby.new_year.views.craft.ny_craft_view_model import NyCraftViewModel
from gui.impl.gen.view_models.views.lobby.new_year.views.gift_system.ny_gift_system_view_model import NyGiftSystemViewModel
from gui.impl.gen.view_models.views.lobby.new_year.views.glade.ny_glade_view_model import NyGladeViewModel
from gui.impl.gen.view_models.views.lobby.new_year.views.new_year_info_view_model import NewYearInfoViewModel
from gui.impl.gen.view_models.views.lobby.new_year.views.ny_back_button_model import NyBackButtonModel
from gui.impl.gen.view_models.views.lobby.new_year.views.ny_main_menu_model import NyMainMenuModel
from gui.impl.gen.view_models.views.lobby.new_year.views.ny_sidebar_model import NySidebarModel
from gui.impl.gen.view_models.views.lobby.new_year.views.ny_vehicles_view_model import NyVehiclesViewModel
from gui.impl.gen.view_models.views.lobby.new_year.views.rewards_info.ny_rewards_info_view_model import NyRewardsInfoViewModel

class MainViews(IntEnum):
    GLADE = 0
    CHALLENGE = 1
    CRAFT_MACHINE = 2
    POST = 3
    SHARDS = 4
    COLLECTIONS = 5
    REWARDS = 6
    INFO = 7
    VEHICLES = 8


class SwitchStates(IntEnum):
    DONE = 0
    DEFAULT = 1
    TO_GLADE_WITH_INTRO = 2
    WITH_SWITCHING_OBJS = 3


class MainViewModel(ViewModel):
    __slots__ = ('onClose', 'onFadeInDone', 'onMoveSpace')

    def __init__(self, properties=16, commands=3):
        super(MainViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def backButton(self):
        return self._getViewModel(0)

    @property
    def gladeModel(self):
        return self._getViewModel(1)

    @property
    def collectionsModel(self):
        return self._getViewModel(2)

    @property
    def mainMenu(self):
        return self._getViewModel(3)

    @property
    def sidebar(self):
        return self._getViewModel(4)

    @property
    def infoModel(self):
        return self._getViewModel(5)

    @property
    def shardsModel(self):
        return self._getViewModel(6)

    @property
    def craftMachineModel(self):
        return self._getViewModel(7)

    @property
    def rewardsModel(self):
        return self._getViewModel(8)

    @property
    def challengeModel(self):
        return self._getViewModel(9)

    @property
    def giftSystemModel(self):
        return self._getViewModel(10)

    @property
    def vehiclesModel(self):
        return self._getViewModel(11)

    def getViewType(self):
        return MainViews(self._getNumber(12))

    def setViewType(self, value):
        self._setNumber(12, value.value)

    def getSwitchState(self):
        return SwitchStates(self._getNumber(13))

    def setSwitchState(self, value):
        self._setNumber(13, value.value)

    def getIsAnimatedShow(self):
        return self._getBool(14)

    def setIsAnimatedShow(self, value):
        self._setBool(14, value)

    def getIsGladeIntroActive(self):
        return self._getBool(15)

    def setIsGladeIntroActive(self, value):
        self._setBool(15, value)

    def _initialize(self):
        super(MainViewModel, self)._initialize()
        self._addViewModelProperty('backButton', NyBackButtonModel())
        self._addViewModelProperty('gladeModel', NyGladeViewModel())
        self._addViewModelProperty('collectionsModel', NyAlbumViewModel())
        self._addViewModelProperty('mainMenu', NyMainMenuModel())
        self._addViewModelProperty('sidebar', NySidebarModel())
        self._addViewModelProperty('infoModel', NewYearInfoViewModel())
        self._addViewModelProperty('shardsModel', NyBreakDecorationsViewModel())
        self._addViewModelProperty('craftMachineModel', NyCraftViewModel())
        self._addViewModelProperty('rewardsModel', NyRewardsInfoViewModel())
        self._addViewModelProperty('challengeModel', NewYearChallengeModel())
        self._addViewModelProperty('giftSystemModel', NyGiftSystemViewModel())
        self._addViewModelProperty('vehiclesModel', NyVehiclesViewModel())
        self._addNumberProperty('viewType')
        self._addNumberProperty('switchState')
        self._addBoolProperty('isAnimatedShow', True)
        self._addBoolProperty('isGladeIntroActive', False)
        self.onClose = self._addCommand('onClose')
        self.onFadeInDone = self._addCommand('onFadeInDone')
        self.onMoveSpace = self._addCommand('onMoveSpace')
