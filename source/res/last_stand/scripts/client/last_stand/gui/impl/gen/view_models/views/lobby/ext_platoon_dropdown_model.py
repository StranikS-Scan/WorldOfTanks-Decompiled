# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/gui/impl/gen/view_models/views/lobby/ext_platoon_dropdown_model.py
from gui.impl.gen.view_models.views.lobby.platoon.platoon_dropdown_model import PlatoonDropdownModel

class ExtPlatoonDropdownModel(PlatoonDropdownModel):
    __slots__ = ()

    def __init__(self, properties=11, commands=1):
        super(ExtPlatoonDropdownModel, self).__init__(properties=properties, commands=commands)

    def getSelectedDifficulty(self):
        return self._getNumber(10)

    def setSelectedDifficulty(self, value):
        self._setNumber(10, value)

    def _initialize(self):
        super(ExtPlatoonDropdownModel, self)._initialize()
        self._addNumberProperty('selectedDifficulty', 1)
