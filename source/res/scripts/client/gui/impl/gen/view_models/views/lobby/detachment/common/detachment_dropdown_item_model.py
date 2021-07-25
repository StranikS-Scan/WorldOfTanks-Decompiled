# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/detachment/common/detachment_dropdown_item_model.py
from gui.impl.gen import R
from gui.impl.gen.view_models.ui_kit.gf_drop_down_item import GfDropDownItem

class DetachmentDropdownItemModel(GfDropDownItem):
    __slots__ = ()

    def __init__(self, properties=4, commands=0):
        super(DetachmentDropdownItemModel, self).__init__(properties=properties, commands=commands)

    def getIcon(self):
        return self._getResource(3)

    def setIcon(self, value):
        self._setResource(3, value)

    def _initialize(self):
        super(DetachmentDropdownItemModel, self)._initialize()
        self._addResourceProperty('icon', R.invalid())
