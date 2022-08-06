# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/battle_matters/popovers/battle_matters_filter_popover_view_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.battle_matters.popovers.filter_control_view_model import FilterControlViewModel

class BattleMattersFilterPopoverViewModel(ViewModel):
    __slots__ = ('onToggleFilter',)
    ARG_CONTROL_TYPE = 'name'
    ARG_CONTROL_NATION = 'nation'

    def __init__(self, properties=2, commands=1):
        super(BattleMattersFilterPopoverViewModel, self).__init__(properties=properties, commands=commands)

    def getTypes(self):
        return self._getArray(0)

    def setTypes(self, value):
        self._setArray(0, value)

    @staticmethod
    def getTypesType():
        return FilterControlViewModel

    def getNations(self):
        return self._getArray(1)

    def setNations(self, value):
        self._setArray(1, value)

    @staticmethod
    def getNationsType():
        return FilterControlViewModel

    def _initialize(self):
        super(BattleMattersFilterPopoverViewModel, self)._initialize()
        self._addArrayProperty('types', Array())
        self._addArrayProperty('nations', Array())
        self.onToggleFilter = self._addCommand('onToggleFilter')
