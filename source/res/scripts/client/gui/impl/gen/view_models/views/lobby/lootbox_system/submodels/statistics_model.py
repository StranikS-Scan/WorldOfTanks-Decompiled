# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/lootbox_system/submodels/statistics_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.lootbox_system.submodels.rewards_categories_model import RewardsCategoriesModel

class StatisticsModel(ViewModel):
    __slots__ = ('onReset', 'onUpdateResetState')

    def __init__(self, properties=4, commands=2):
        super(StatisticsModel, self).__init__(properties=properties, commands=commands)

    def getEventName(self):
        return self._getString(0)

    def setEventName(self, value):
        self._setString(0, value)

    def getOpenedCount(self):
        return self._getNumber(1)

    def setOpenedCount(self, value):
        self._setNumber(1, value)

    def getIsResetCompleted(self):
        return self._getBool(2)

    def setIsResetCompleted(self, value):
        self._setBool(2, value)

    def getCategories(self):
        return self._getArray(3)

    def setCategories(self, value):
        self._setArray(3, value)

    @staticmethod
    def getCategoriesType():
        return RewardsCategoriesModel

    def _initialize(self):
        super(StatisticsModel, self)._initialize()
        self._addStringProperty('eventName', '')
        self._addNumberProperty('openedCount', 0)
        self._addBoolProperty('isResetCompleted', False)
        self._addArrayProperty('categories', Array())
        self.onReset = self._addCommand('onReset')
        self.onUpdateResetState = self._addCommand('onUpdateResetState')
