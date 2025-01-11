# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/views/ny_main_menu_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.new_year.components.ny_main_menu_tab_model import NyMainMenuTabModel
from gui.impl.gen.view_models.views.lobby.new_year.components.ny_resources_balance_model import NyResourcesBalanceModel
from gui.impl.gen.view_models.views.lobby.new_year.components.ny_trigger_hint_tabs_model import NyTriggerHintTabsModel
from gui.impl.gen.view_models.views.lobby.new_year.components.ny_widget_friend_info_model import NyWidgetFriendInfoModel
from gui.impl.gen.view_models.views.lobby.new_year.components.ny_widget_level_progress_model import NyWidgetLevelProgressModel

class NyMainMenuModel(ViewModel):
    __slots__ = ('onSwitchContent', 'onGoToFriendsList', 'onShowLootList')

    def __init__(self, properties=9, commands=3):
        super(NyMainMenuModel, self).__init__(properties=properties, commands=commands)

    @property
    def balance(self):
        return self._getViewModel(0)

    @staticmethod
    def getBalanceType():
        return NyResourcesBalanceModel

    @property
    def widgetLevelProgress(self):
        return self._getViewModel(1)

    @staticmethod
    def getWidgetLevelProgressType():
        return NyWidgetLevelProgressModel

    @property
    def widgetFriendStatus(self):
        return self._getViewModel(2)

    @staticmethod
    def getWidgetFriendStatusType():
        return NyWidgetFriendInfoModel

    @property
    def triggerHintTabs(self):
        return self._getViewModel(3)

    @staticmethod
    def getTriggerHintTabsType():
        return NyTriggerHintTabsModel

    def getItemsMenu(self):
        return self._getArray(4)

    def setItemsMenu(self, value):
        self._setArray(4, value)

    @staticmethod
    def getItemsMenuType():
        return NyMainMenuTabModel

    def getStartIndexMenu(self):
        return self._getNumber(5)

    def setStartIndexMenu(self, value):
        self._setNumber(5, value)

    def getIsFriendHangar(self):
        return self._getBool(6)

    def setIsFriendHangar(self, value):
        self._setBool(6, value)

    def getIsGiftMachineLootListAvailable(self):
        return self._getBool(7)

    def setIsGiftMachineLootListAvailable(self, value):
        self._setBool(7, value)

    def getCurrentView(self):
        return self._getString(8)

    def setCurrentView(self, value):
        self._setString(8, value)

    def _initialize(self):
        super(NyMainMenuModel, self)._initialize()
        self._addViewModelProperty('balance', NyResourcesBalanceModel())
        self._addViewModelProperty('widgetLevelProgress', NyWidgetLevelProgressModel())
        self._addViewModelProperty('widgetFriendStatus', NyWidgetFriendInfoModel())
        self._addViewModelProperty('triggerHintTabs', NyTriggerHintTabsModel())
        self._addArrayProperty('itemsMenu', Array())
        self._addNumberProperty('startIndexMenu', 0)
        self._addBoolProperty('isFriendHangar', False)
        self._addBoolProperty('isGiftMachineLootListAvailable', False)
        self._addStringProperty('currentView', '')
        self.onSwitchContent = self._addCommand('onSwitchContent')
        self.onGoToFriendsList = self._addCommand('onGoToFriendsList')
        self.onShowLootList = self._addCommand('onShowLootList')
