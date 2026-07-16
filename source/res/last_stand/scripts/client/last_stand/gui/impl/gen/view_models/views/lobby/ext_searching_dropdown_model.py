# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/gui/impl/gen/view_models/views/lobby/ext_searching_dropdown_model.py
from gui.impl.gen.view_models.views.lobby.platoon.searching_dropdown_model import SearchingDropdownModel

class ExtSearchingDropdownModel(SearchingDropdownModel):
    __slots__ = ()

    def __init__(self, properties=8, commands=1):
        super(ExtSearchingDropdownModel, self).__init__(properties=properties, commands=commands)

    def getSelectedDifficulty(self):
        return self._getNumber(7)

    def setSelectedDifficulty(self, value):
        self._setNumber(7, value)

    def _initialize(self):
        super(ExtSearchingDropdownModel, self)._initialize()
        self._addNumberProperty('selectedDifficulty', 1)
