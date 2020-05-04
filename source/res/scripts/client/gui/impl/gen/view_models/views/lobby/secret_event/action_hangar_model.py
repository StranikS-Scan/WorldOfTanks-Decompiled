# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/secret_event/action_hangar_model.py
from gui.impl.wrappers.user_list_model import UserListModel
from gui.impl.gen.view_models.views.lobby.secret_event.action_menu_model import ActionMenuModel
from gui.impl.gen.view_models.views.lobby.secret_event.action_progress_model import ActionProgressModel
from gui.impl.gen.view_models.views.lobby.secret_event.characteristics_model import CharacteristicsModel
from gui.impl.gen.view_models.views.lobby.secret_event.general_model import GeneralModel
from gui.impl.gen.view_models.views.lobby.secret_event.general_progress_model import GeneralProgressModel
from gui.impl.gen.view_models.views.lobby.secret_event.order_model import OrderModel

class ActionHangarModel(ActionMenuModel):
    __slots__ = ('onSelectGeneralChanged', 'onMoveSpace', 'onCursorOver3DScene', 'onBuyOrderClick')

    def __init__(self, properties=10, commands=7):
        super(ActionHangarModel, self).__init__(properties=properties, commands=commands)

    @property
    def generals(self):
        return self._getViewModel(4)

    @property
    def orders(self):
        return self._getViewModel(5)

    @property
    def generalProgress(self):
        return self._getViewModel(6)

    @property
    def actionProgress(self):
        return self._getViewModel(7)

    @property
    def characteristics(self):
        return self._getViewModel(8)

    def getSelectedGeneralId(self):
        return self._getNumber(9)

    def setSelectedGeneralId(self, value):
        self._setNumber(9, value)

    def _initialize(self):
        super(ActionHangarModel, self)._initialize()
        self._addViewModelProperty('generals', UserListModel())
        self._addViewModelProperty('orders', UserListModel())
        self._addViewModelProperty('generalProgress', GeneralProgressModel())
        self._addViewModelProperty('actionProgress', ActionProgressModel())
        self._addViewModelProperty('characteristics', CharacteristicsModel())
        self._addNumberProperty('selectedGeneralId', 0)
        self.onSelectGeneralChanged = self._addCommand('onSelectGeneralChanged')
        self.onMoveSpace = self._addCommand('onMoveSpace')
        self.onCursorOver3DScene = self._addCommand('onCursorOver3DScene')
        self.onBuyOrderClick = self._addCommand('onBuyOrderClick')
