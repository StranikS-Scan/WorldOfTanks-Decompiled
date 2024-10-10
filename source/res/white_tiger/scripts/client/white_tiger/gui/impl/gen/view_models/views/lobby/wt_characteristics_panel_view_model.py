# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/impl/gen/view_models/views/lobby/wt_characteristics_panel_view_model.py
from gui.impl.gen import R
from frameworks.wulf import ViewModel
from gui.impl.wrappers.user_list_model import UserListModel
from white_tiger.gui.impl.gen.view_models.views.lobby.wt_characteristic_model import WtCharacteristicModel

class WtCharacteristicsPanelViewModel(ViewModel):
    __slots__ = ('onLeaveClicked',)

    def __init__(self, properties=3, commands=1):
        super(WtCharacteristicsPanelViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def pros(self):
        return self._getViewModel(0)

    @staticmethod
    def getProsType():
        return WtCharacteristicModel

    @property
    def cons(self):
        return self._getViewModel(1)

    @staticmethod
    def getConsType():
        return WtCharacteristicModel

    def getSpecialInfo(self):
        return self._getResource(2)

    def setSpecialInfo(self, value):
        self._setResource(2, value)

    def _initialize(self):
        super(WtCharacteristicsPanelViewModel, self)._initialize()
        self._addViewModelProperty('pros', UserListModel())
        self._addViewModelProperty('cons', UserListModel())
        self._addResourceProperty('specialInfo', R.invalid())
        self.onLeaveClicked = self._addCommand('onLeaveClicked')
