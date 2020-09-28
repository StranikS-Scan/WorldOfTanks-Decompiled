# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/wt_event/box_card_model.py
from frameworks.wulf import ViewModel
from gui.impl.wrappers.user_list_model import UserListModel
from gui.impl.gen.view_models.views.lobby.wt_event.reward_model import RewardModel

class BoxCardModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=5, commands=0):
        super(BoxCardModel, self).__init__(properties=properties, commands=commands)

    @property
    def rewards(self):
        return self._getViewModel(0)

    def getId(self):
        return self._getString(1)

    def setId(self, value):
        self._setString(1, value)

    def getQuantity(self):
        return self._getNumber(2)

    def setQuantity(self, value):
        self._setNumber(2, value)

    def getName(self):
        return self._getString(3)

    def setName(self, value):
        self._setString(3, value)

    def getDescription(self):
        return self._getString(4)

    def setDescription(self, value):
        self._setString(4, value)

    def _initialize(self):
        super(BoxCardModel, self)._initialize()
        self._addViewModelProperty('rewards', UserListModel())
        self._addStringProperty('id', '')
        self._addNumberProperty('quantity', 0)
        self._addStringProperty('name', '')
        self._addStringProperty('description', '')
