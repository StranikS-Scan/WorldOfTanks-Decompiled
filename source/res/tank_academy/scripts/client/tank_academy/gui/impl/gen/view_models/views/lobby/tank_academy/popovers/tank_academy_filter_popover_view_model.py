# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: tank_academy/scripts/client/tank_academy/gui/impl/gen/view_models/views/lobby/tank_academy/popovers/tank_academy_filter_popover_view_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from tank_academy.gui.impl.gen.view_models.views.lobby.tank_academy.popovers.filter_control_view_model import FilterControlViewModel

class TankAcademyFilterPopoverViewModel(ViewModel):
    __slots__ = ('onToggleFilter',)
    ARG_CONTROL_TYPE = 'type'
    ARG_CONTROL_NATION = 'nation'

    def __init__(self, properties=2, commands=1):
        super(TankAcademyFilterPopoverViewModel, self).__init__(properties=properties, commands=commands)

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
        super(TankAcademyFilterPopoverViewModel, self)._initialize()
        self._addArrayProperty('types', Array())
        self._addArrayProperty('nations', Array())
        self.onToggleFilter = self._addCommand('onToggleFilter')
