# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/views/ny_bonus_dropdown_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.new_year.views.ny_bonus_info_model import NyBonusInfoModel

class NyBonusDropdownModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(NyBonusDropdownModel, self).__init__(properties=properties, commands=commands)

    def getSelectedIdx(self):
        return self._getNumber(0)

    def setSelectedIdx(self, value):
        self._setNumber(0, value)

    def getItems(self):
        return self._getArray(1)

    def setItems(self, value):
        self._setArray(1, value)

    def _initialize(self):
        super(NyBonusDropdownModel, self)._initialize()
        self._addNumberProperty('selectedIdx', 0)
        self._addArrayProperty('items', Array())
