# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/views/new_year_vehicles_view_model.py
from frameworks.wulf import ViewModel
from gui.impl.wrappers.user_list_model import UserListModel
from gui.impl.gen.view_models.ui_kit.list_model import ListModel

class NewYearVehiclesViewModel(ViewModel):
    __slots__ = ('onCloseBtnClick', 'onClearBtnClick')

    def __init__(self, properties=5, commands=2):
        super(NewYearVehiclesViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def vehicleSlots(self):
        return self._getViewModel(0)

    @property
    def bonuses(self):
        return self._getViewModel(1)

    def getIsInProgressIntro(self):
        return self._getBool(2)

    def setIsInProgressIntro(self, value):
        self._setBool(2, value)

    def getIsPostEventIntro(self):
        return self._getBool(3)

    def setIsPostEventIntro(self, value):
        self._setBool(3, value)

    def getIntroCooldown(self):
        return self._getNumber(4)

    def setIntroCooldown(self, value):
        self._setNumber(4, value)

    def _initialize(self):
        super(NewYearVehiclesViewModel, self)._initialize()
        self._addViewModelProperty('vehicleSlots', ListModel())
        self._addViewModelProperty('bonuses', UserListModel())
        self._addBoolProperty('isInProgressIntro', False)
        self._addBoolProperty('isPostEventIntro', False)
        self._addNumberProperty('introCooldown', 0)
        self.onCloseBtnClick = self._addCommand('onCloseBtnClick')
        self.onClearBtnClick = self._addCommand('onClearBtnClick')
