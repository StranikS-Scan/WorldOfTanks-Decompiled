# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/views/glade/customization_levelup_model.py
from frameworks.wulf import ViewModel
from gui.impl.wrappers.user_list_model import UserListModel
from gui.impl.gen.view_models.views.lobby.new_year.views.glade.levelup_price_model import LevelupPriceModel

class CustomizationLevelupModel(ViewModel):
    __slots__ = ('onLevelUp',)

    def __init__(self, properties=4, commands=1):
        super(CustomizationLevelupModel, self).__init__(properties=properties, commands=commands)

    @property
    def price(self):
        return self._getViewModel(0)

    @staticmethod
    def getPriceType():
        return LevelupPriceModel

    def getObject(self):
        return self._getString(1)

    def setObject(self, value):
        self._setString(1, value)

    def getTargetLevel(self):
        return self._getNumber(2)

    def setTargetLevel(self, value):
        self._setNumber(2, value)

    def getIsEnoughToBuy(self):
        return self._getBool(3)

    def setIsEnoughToBuy(self, value):
        self._setBool(3, value)

    def _initialize(self):
        super(CustomizationLevelupModel, self)._initialize()
        self._addViewModelProperty('price', UserListModel())
        self._addStringProperty('object', '')
        self._addNumberProperty('targetLevel', 0)
        self._addBoolProperty('isEnoughToBuy', True)
        self.onLevelUp = self._addCommand('onLevelUp')
