# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/components/new_year_main_widget_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.new_year.components.ny_economic_bonus_model import NyEconomicBonusModel
from gui.impl.gen.view_models.views.lobby.new_year.components.ny_widget_level_progress_model import NyWidgetLevelProgressModel

class NewYearMainWidgetModel(ViewModel):
    __slots__ = ('onGoToGladeView', 'onChangeBonus', 'onGoToChallenge')

    def __init__(self, properties=9, commands=3):
        super(NewYearMainWidgetModel, self).__init__(properties=properties, commands=commands)

    @property
    def widgetLevelProgress(self):
        return self._getViewModel(0)

    @staticmethod
    def getWidgetLevelProgressType():
        return NyWidgetLevelProgressModel

    def getIsLobbyMode(self):
        return self._getBool(1)

    def setIsLobbyMode(self, value):
        self._setBool(1, value)

    def getIsExtendedAnim(self):
        return self._getBool(2)

    def setIsExtendedAnim(self, value):
        self._setBool(2, value)

    def getIsVisible(self):
        return self._getBool(3)

    def setIsVisible(self, value):
        self._setBool(3, value)

    def getIsEnabled(self):
        return self._getBool(4)

    def setIsEnabled(self, value):
        self._setBool(4, value)

    def getIsInited(self):
        return self._getBool(5)

    def setIsInited(self, value):
        self._setBool(5, value)

    def getSelectedBonus(self):
        return self._getString(6)

    def setSelectedBonus(self, value):
        self._setString(6, value)

    def getBonusError(self):
        return self._getBool(7)

    def setBonusError(self, value):
        self._setBool(7, value)

    def getEconomicBonuses(self):
        return self._getArray(8)

    def setEconomicBonuses(self, value):
        self._setArray(8, value)

    @staticmethod
    def getEconomicBonusesType():
        return NyEconomicBonusModel

    def _initialize(self):
        super(NewYearMainWidgetModel, self)._initialize()
        self._addViewModelProperty('widgetLevelProgress', NyWidgetLevelProgressModel())
        self._addBoolProperty('isLobbyMode', True)
        self._addBoolProperty('isExtendedAnim', False)
        self._addBoolProperty('isVisible', True)
        self._addBoolProperty('isEnabled', True)
        self._addBoolProperty('isInited', False)
        self._addStringProperty('selectedBonus', '')
        self._addBoolProperty('bonusError', False)
        self._addArrayProperty('economicBonuses', Array())
        self.onGoToGladeView = self._addCommand('onGoToGladeView')
        self.onChangeBonus = self._addCommand('onChangeBonus')
        self.onGoToChallenge = self._addCommand('onGoToChallenge')
