# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: new_year/scripts/client/new_year/gui/impl/gen/view_models/views/lobby/new_year/views/main_view_model.py
from enum import IntEnum
from frameworks.wulf import ViewModel
from new_year.gui.impl.gen.view_models.views.lobby.new_year.components.ny_currency_panel_model import NyCurrencyPanelModel
from new_year.gui.impl.gen.view_models.views.lobby.new_year.views.city.ny_city_view_model import NyCityViewModel
from new_year.gui.impl.gen.view_models.views.lobby.new_year.views.leaderboard.ny_leaderboard_model import NyLeaderboardModel
from new_year.gui.impl.gen.view_models.views.lobby.new_year.views.new_year_info_view_model import NewYearInfoViewModel
from new_year.gui.impl.gen.view_models.views.lobby.new_year.views.ny_back_button_model import NyBackButtonModel
from new_year.gui.impl.gen.view_models.views.lobby.new_year.views.ny_main_menu_model import NyMainMenuModel
from new_year.gui.impl.gen.view_models.views.lobby.new_year.views.ny_progress_widget_model import NyProgressWidgetModel
from new_year.gui.impl.gen.view_models.views.lobby.new_year.views.ny_sidebar_model import NySidebarModel
from new_year.gui.impl.gen.view_models.views.lobby.new_year.views.pet.ny_pet_model import NyPetModel
from new_year.gui.impl.gen.view_models.views.lobby.new_year.views.surprise_machine.ny_surprise_machine_model import NySurpriseMachineModel

class MainViews(IntEnum):
    CITY = 0
    PET = 1
    LEADERS = 2
    MACHINE = 3
    INFO = 4


class SwitchStates(IntEnum):
    DONE = 0
    DEFAULT = 1
    TO_GLADE_WITH_INTRO = 2
    WITH_SWITCHING_OBJS = 3


class MainViewModel(ViewModel):
    __slots__ = ('onClose', 'onFadeInDone', 'onMouseOver3dScene', 'onMoveSpace', 'onRewardInfo')

    def __init__(self, properties=14, commands=5):
        super(MainViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def backButton(self):
        return self._getViewModel(0)

    @staticmethod
    def getBackButtonType():
        return NyBackButtonModel

    @property
    def mainMenu(self):
        return self._getViewModel(1)

    @staticmethod
    def getMainMenuType():
        return NyMainMenuModel

    @property
    def sidebar(self):
        return self._getViewModel(2)

    @staticmethod
    def getSidebarType():
        return NySidebarModel

    @property
    def currencyPanel(self):
        return self._getViewModel(3)

    @staticmethod
    def getCurrencyPanelType():
        return NyCurrencyPanelModel

    @property
    def progressWidgetModel(self):
        return self._getViewModel(4)

    @staticmethod
    def getProgressWidgetModelType():
        return NyProgressWidgetModel

    @property
    def cityModel(self):
        return self._getViewModel(5)

    @staticmethod
    def getCityModelType():
        return NyCityViewModel

    @property
    def surpriseMachineModel(self):
        return self._getViewModel(6)

    @staticmethod
    def getSurpriseMachineModelType():
        return NySurpriseMachineModel

    @property
    def petModel(self):
        return self._getViewModel(7)

    @staticmethod
    def getPetModelType():
        return NyPetModel

    @property
    def infoModel(self):
        return self._getViewModel(8)

    @staticmethod
    def getInfoModelType():
        return NewYearInfoViewModel

    @property
    def leaderboardModel(self):
        return self._getViewModel(9)

    @staticmethod
    def getLeaderboardModelType():
        return NyLeaderboardModel

    def getViewType(self):
        return MainViews(self._getNumber(10))

    def setViewType(self, value):
        self._setNumber(10, value.value)

    def getSwitchState(self):
        return SwitchStates(self._getNumber(11))

    def setSwitchState(self, value):
        self._setNumber(11, value.value)

    def getIsAnimatedShow(self):
        return self._getBool(12)

    def setIsAnimatedShow(self, value):
        self._setBool(12, value)

    def getIsControlsLocked(self):
        return self._getBool(13)

    def setIsControlsLocked(self, value):
        self._setBool(13, value)

    def _initialize(self):
        super(MainViewModel, self)._initialize()
        self._addViewModelProperty('backButton', NyBackButtonModel())
        self._addViewModelProperty('mainMenu', NyMainMenuModel())
        self._addViewModelProperty('sidebar', NySidebarModel())
        self._addViewModelProperty('currencyPanel', NyCurrencyPanelModel())
        self._addViewModelProperty('progressWidgetModel', NyProgressWidgetModel())
        self._addViewModelProperty('cityModel', NyCityViewModel())
        self._addViewModelProperty('surpriseMachineModel', NySurpriseMachineModel())
        self._addViewModelProperty('petModel', NyPetModel())
        self._addViewModelProperty('infoModel', NewYearInfoViewModel())
        self._addViewModelProperty('leaderboardModel', NyLeaderboardModel())
        self._addNumberProperty('viewType')
        self._addNumberProperty('switchState')
        self._addBoolProperty('isAnimatedShow', True)
        self._addBoolProperty('isControlsLocked', False)
        self.onClose = self._addCommand('onClose')
        self.onFadeInDone = self._addCommand('onFadeInDone')
        self.onMouseOver3dScene = self._addCommand('onMouseOver3dScene')
        self.onMoveSpace = self._addCommand('onMoveSpace')
        self.onRewardInfo = self._addCommand('onRewardInfo')
