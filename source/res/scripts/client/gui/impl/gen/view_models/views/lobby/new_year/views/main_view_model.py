# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/views/main_view_model.py
from enum import IntEnum
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.new_year.views.albums.ny_album_view_model import NyAlbumViewModel
from gui.impl.gen.view_models.views.lobby.new_year.views.break_decorations.ny_break_decorations_view_model import NyBreakDecorationsViewModel
from gui.impl.gen.view_models.views.lobby.new_year.views.craft.ny_craft_view_model import NyCraftViewModel
from gui.impl.gen.view_models.views.lobby.new_year.views.glade.ny_glade_view_model import NyGladeViewModel
from gui.impl.gen.view_models.views.lobby.new_year.views.new_year_info_view_model import NewYearInfoViewModel
from gui.impl.gen.view_models.views.lobby.new_year.views.ny_back_button_model import NyBackButtonModel
from gui.impl.gen.view_models.views.lobby.new_year.views.ny_main_menu_model import NyMainMenuModel
from gui.impl.gen.view_models.views.lobby.new_year.views.ny_sidebar_model import NySidebarModel
from gui.impl.gen.view_models.views.lobby.new_year.views.rewards_info.ny_rewards_info_view_model import NyRewardsInfoViewModel

class MainViews(IntEnum):
    GLADE = 0
    CRAFT_MACHINE = 1
    SHARDS = 2
    COLLECTIONS = 3
    REWARDS = 4
    INFO = 5
    VEHICLES = 6


class SwitchStates(IntEnum):
    DONE = 0
    DEFAULT = 1
    TO_GLADE_WITH_INTRO = 2
    WITH_SWITCHING_OBJS = 3


class MainViewModel(ViewModel):
    __slots__ = ('onClose', 'onFadeInDone', 'onMoveSpace')

    def __init__(self, properties=13, commands=3):
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
    def collectionsModel(self):
        return self._getViewModel(2)

    @staticmethod
    def getCollectionsModelType():
        return NyAlbumViewModel

    @property
    def mainMenu(self):
        return self._getViewModel(3)

    @staticmethod
    def getMainMenuType():
        return NyMainMenuModel

    @property
    def sidebar(self):
        return self._getViewModel(4)

    @staticmethod
    def getSidebarType():
        return NySidebarModel

    @property
    def infoModel(self):
        return self._getViewModel(5)

    @staticmethod
    def getInfoModelType():
        return NewYearInfoViewModel

    @property
    def shardsModel(self):
        return self._getViewModel(6)

    @staticmethod
    def getShardsModelType():
        return NyBreakDecorationsViewModel

    @property
    def craftMachineModel(self):
        return self._getViewModel(7)

    @staticmethod
    def getCraftMachineModelType():
        return NyCraftViewModel

    @property
    def rewardsModel(self):
        return self._getViewModel(8)

    @staticmethod
    def getRewardsModelType():
        return NyRewardsInfoViewModel

    def getViewType(self):
        return MainViews(self._getNumber(9))

    def setViewType(self, value):
        self._setNumber(9, value.value)

    def getSwitchState(self):
        return SwitchStates(self._getNumber(10))

    def setSwitchState(self, value):
        self._setNumber(10, value.value)

    def getIsAnimatedShow(self):
        return self._getBool(11)

    def setIsAnimatedShow(self, value):
        self._setBool(11, value)

    def getIsGladeIntroActive(self):
        return self._getBool(12)

    def setIsGladeIntroActive(self, value):
        self._setBool(12, value)

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
        self._addNumberProperty('viewType')
        self._addNumberProperty('switchState')
        self._addBoolProperty('isAnimatedShow', True)
        self._addBoolProperty('isGladeIntroActive', False)
        self.onClose = self._addCommand('onClose')
        self.onFadeInDone = self._addCommand('onFadeInDone')
        self.onMoveSpace = self._addCommand('onMoveSpace')
