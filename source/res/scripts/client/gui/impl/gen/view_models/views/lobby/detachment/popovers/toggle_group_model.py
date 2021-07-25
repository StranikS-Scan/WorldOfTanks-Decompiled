# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/detachment/popovers/toggle_group_model.py
from frameworks.wulf import Array
from gui.impl.gen import R
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.detachment.common.toggle_button_base_model import ToggleButtonBaseModel

class ToggleGroupModel(ViewModel):
    __slots__ = ()
    DEFAULT = 'default'
    LEVEL = 'level'
    GRADE = 'grade'
    NATION = 'nation'
    SPECIALITY = 'speciality'
    SPECIALIZATION = 'specialization'

    def __init__(self, properties=4, commands=0):
        super(ToggleGroupModel, self).__init__(properties=properties, commands=commands)

    def getLabel(self):
        return self._getResource(0)

    def setLabel(self, value):
        self._setResource(0, value)

    def getId(self):
        return self._getString(1)

    def setId(self, value):
        self._setString(1, value)

    def getType(self):
        return self._getString(2)

    def setType(self, value):
        self._setString(2, value)

    def getFilters(self):
        return self._getArray(3)

    def setFilters(self, value):
        self._setArray(3, value)

    def _initialize(self):
        super(ToggleGroupModel, self)._initialize()
        self._addResourceProperty('label', R.invalid())
        self._addStringProperty('id', '')
        self._addStringProperty('type', '')
        self._addArrayProperty('filters', Array())
