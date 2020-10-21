# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/event/ift_item_group_model.py
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.ui_kit.list_model import ListModel
from gui.impl.gen.view_models.views.lobby.event.ift_item_model import IftItemModel

class IftItemGroupModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(IftItemGroupModel, self).__init__(properties=properties, commands=commands)

    @property
    def items(self):
        return self._getViewModel(0)

    def getType(self):
        return self._getString(1)

    def setType(self, value):
        self._setString(1, value)

    def getTitle(self):
        return self._getString(2)

    def setTitle(self, value):
        self._setString(2, value)

    def _initialize(self):
        super(IftItemGroupModel, self)._initialize()
        self._addViewModelProperty('items', ListModel())
        self._addStringProperty('type', '')
        self._addStringProperty('title', '')
