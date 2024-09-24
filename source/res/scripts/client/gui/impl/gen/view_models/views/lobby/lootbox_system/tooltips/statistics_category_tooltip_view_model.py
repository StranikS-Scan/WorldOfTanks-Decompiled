# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/lootbox_system/tooltips/statistics_category_tooltip_view_model.py
from frameworks.wulf import ViewModel
from gui.impl.wrappers.user_list_model import UserListModel
from gui.impl.gen.view_models.views.lobby.lootbox_system.tooltips.statistics_category_tooltip_bonus_model import StatisticsCategoryTooltipBonusModel

class StatisticsCategoryTooltipViewModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=4, commands=0):
        super(StatisticsCategoryTooltipViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def bonuses(self):
        return self._getViewModel(0)

    @staticmethod
    def getBonusesType():
        return StatisticsCategoryTooltipBonusModel

    def getEventName(self):
        return self._getString(1)

    def setEventName(self, value):
        self._setString(1, value)

    def getBonusesCategory(self):
        return self._getString(2)

    def setBonusesCategory(self, value):
        self._setString(2, value)

    def getCompensatedCount(self):
        return self._getNumber(3)

    def setCompensatedCount(self, value):
        self._setNumber(3, value)

    def _initialize(self):
        super(StatisticsCategoryTooltipViewModel, self)._initialize()
        self._addViewModelProperty('bonuses', UserListModel())
        self._addStringProperty('eventName', '')
        self._addStringProperty('bonusesCategory', '')
        self._addNumberProperty('compensatedCount', 0)
