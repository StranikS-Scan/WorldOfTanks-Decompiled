# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/comp7/gui/impl/gen/view_models/views/lobby/season_modifier_model.py
from frameworks.wulf import ViewModel

class SeasonModifierModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=1, commands=0):
        super(SeasonModifierModel, self).__init__(properties=properties, commands=commands)

    def getEnabled(self):
        return self._getBool(0)

    def setEnabled(self, value):
        self._setBool(0, value)

    def _initialize(self):
        super(SeasonModifierModel, self)._initialize()
        self._addBoolProperty('enabled', False)
