# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/detachment/common/detachment_dropdown_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.detachment.common.detachment_dropdown_item_model import DetachmentDropdownItemModel

class DetachmentDropdownModel(ViewModel):
    __slots__ = ('onChange',)

    def __init__(self, properties=2, commands=1):
        super(DetachmentDropdownModel, self).__init__(properties=properties, commands=commands)

    def getItems(self):
        return self._getArray(0)

    def setItems(self, value):
        self._setArray(0, value)

    def getSelected(self):
        return self._getArray(1)

    def setSelected(self, value):
        self._setArray(1, value)

    def _initialize(self):
        super(DetachmentDropdownModel, self)._initialize()
        self._addArrayProperty('items', Array())
        self._addArrayProperty('selected', Array())
        self.onChange = self._addCommand('onChange')
