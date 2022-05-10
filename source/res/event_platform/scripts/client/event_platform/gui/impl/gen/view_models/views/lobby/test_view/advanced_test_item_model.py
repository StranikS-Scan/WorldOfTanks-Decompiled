# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: event_platform/scripts/client/event_platform/gui/impl/gen/view_models/views/lobby/test_view/advanced_test_item_model.py
from frameworks.wulf import Array
from gui.impl.gen import R
from frameworks.wulf import ViewModel
from event_platform.gui.impl.gen.view_models.views.lobby.test_view.advanced_award_model import AdvancedAwardModel

class AdvancedTestItemModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=5, commands=0):
        super(AdvancedTestItemModel, self).__init__(properties=properties, commands=commands)

    def getId(self):
        return self._getNumber(0)

    def setId(self, value):
        self._setNumber(0, value)

    def getName(self):
        return self._getString(1)

    def setName(self, value):
        self._setString(1, value)

    def getIcon(self):
        return self._getResource(2)

    def setIcon(self, value):
        self._setResource(2, value)

    def getFlag(self):
        return self._getBool(3)

    def setFlag(self, value):
        self._setBool(3, value)

    def getAwards(self):
        return self._getArray(4)

    def setAwards(self, value):
        self._setArray(4, value)

    def _initialize(self):
        super(AdvancedTestItemModel, self)._initialize()
        self._addNumberProperty('id', 0)
        self._addStringProperty('name', '')
        self._addResourceProperty('icon', R.invalid())
        self._addBoolProperty('flag', False)
        self._addArrayProperty('awards', Array())
