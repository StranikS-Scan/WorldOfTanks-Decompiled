# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/detachment/common/radio_buttons_group_model.py
from frameworks.wulf import Array
from gui.impl.gen import R
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.detachment.common.radio_button_model import RadioButtonModel

class RadioButtonsGroupModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=4, commands=0):
        super(RadioButtonsGroupModel, self).__init__(properties=properties, commands=commands)

    def getLabel(self):
        return self._getResource(0)

    def setLabel(self, value):
        self._setResource(0, value)

    def getId(self):
        return self._getString(1)

    def setId(self, value):
        self._setString(1, value)

    def getSelectedId(self):
        return self._getString(2)

    def setSelectedId(self, value):
        self._setString(2, value)

    def getList(self):
        return self._getArray(3)

    def setList(self, value):
        self._setArray(3, value)

    def _initialize(self):
        super(RadioButtonsGroupModel, self)._initialize()
        self._addResourceProperty('label', R.invalid())
        self._addStringProperty('id', '')
        self._addStringProperty('selectedId', '')
        self._addArrayProperty('list', Array())
