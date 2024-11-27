# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: new_year/scripts/client/new_year/gui/impl/gen/view_models/views/lobby/new_year/views/main_view_model.py
from enum import IntEnum
from frameworks.wulf import ViewModel
from new_year.gui.impl.gen.view_models.views.lobby.new_year.components.ny_currency_panel_model import NyCurrencyPanelModel
from new_year.gui.impl.gen.view_models.views.lobby.new_year.views.city.ny_city_view_model import NyCityViewModel
from new_year.gui.impl.gen.view_models.views.lobby.new_year.views.new_year_info_view_model import NewYearInfoViewModel
from new_year.gui.impl.gen.view_models.views.lobby.new_year.views.ny_back_button_model import NyBackButtonModel
from new_year.gui.impl.gen.view_models.views.lobby.new_year.views.ny_main_menu_model import NyMainMenuModel
from new_year.gui.impl.gen.view_models.views.lobby.new_year.views.ny_sidebar_model import NySidebarModel
from new_year.gui.impl.gen.view_models.views.lobby.new_year.views.pet.ny_pet_model import NyPetModel
from new_year.gui.impl.gen.view_models.views.lobby.new_year.views.quests.ny_quests_model import NyQuestsModel
from new_year.gui.impl.gen.view_models.views.lobby.new_year.views.rewards_info.ny_rewards_info_view_model import NyRewardsInfoViewModel
from new_year.gui.impl.gen.view_models.views.lobby.new_year.views.surprise_machine.ny_surprise_machine_model import NySurpriseMachineModel

class MainViews(IntEnum):
    CITY = 0
    TASKS = 1
    MACHINE = 2
    REWARDS = 3
    PET = 4
    INFO = 5


class SwitchStates(IntEnum):
    DONE = 0
    DEFAULT = 1
    TO_GLADE_WITH_INTRO = 2
    WITH_SWITCHING_OBJS = 3


class MainViewModel(ViewModel):
    __slots__ = ('onClose', 'onFadeInDone', 'onMoveSpace')

    def __init__(self, properties=14, commands=3):
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
    def cityModel(self):
        return self._getViewModel(4)

    @staticmethod
    def getCityModelType():
        return NyCityViewModel

    @property
    def questsModel(self):
        return self._getViewModel(5)

    @staticmethod
    def getQuestsModelType():
        return NyQuestsModel

    @property
    def surpriseMachineModel(self):
        return self._getViewModel(6)

    @staticmethod
    def getSurpriseMachineModelType():
        return NySurpriseMachineModel

    @property
    def rewardsModel(self):
        return self._getViewModel(7)

    @staticmethod
    def getRewardsModelType():
        return NyRewardsInfoViewModel

    @property
    def petModel(self):
        return self._getViewModel(8)

    @staticmethod
    def getPetModelType():
        return NyPetModel

    @property
    def infoModel(self):
        return self._getViewModel(9)

    @staticmethod
    def getInfoModelType():
        return NewYearInfoViewModel

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
        self._addViewModelProperty('cityModel', NyCityViewModel())
        self._addViewModelProperty('questsModel', NyQuestsModel())
        self._addViewModelProperty('surpriseMachineModel', NySurpriseMachineModel())
        self._addViewModelProperty('rewardsModel', NyRewardsInfoViewModel())
        self._addViewModelProperty('petModel', NyPetModel())
        self._addViewModelProperty('infoModel', NewYearInfoViewModel())
        self._addNumberProperty('viewType')
        self._addNumberProperty('switchState')
        self._addBoolProperty('isAnimatedShow', True)
        self._addBoolProperty('isControlsLocked', False)
        self.onClose = self._addCommand('onClose')
        self.onFadeInDone = self._addCommand('onFadeInDone')
        self.onMoveSpace = self._addCommand('onMoveSpace')
