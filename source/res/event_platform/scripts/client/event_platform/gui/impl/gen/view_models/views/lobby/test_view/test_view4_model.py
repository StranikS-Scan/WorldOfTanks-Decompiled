# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: event_platform/scripts/client/event_platform/gui/impl/gen/view_models/views/lobby/test_view/test_view4_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from event_platform.gui.impl.gen.view_models.views.lobby.test_view.advanced_test_item_model import AdvancedTestItemModel
from event_platform.gui.impl.gen.view_models.views.lobby.test_view.award_model import AwardModel

class TestView4Model(ViewModel):
    __slots__ = ('onFirstButtonClicked', 'onSecondButtonClicked')

    def __init__(self, properties=5, commands=2):
        super(TestView4Model, self).__init__(properties=properties, commands=commands)

    @property
    def award(self):
        return self._getViewModel(0)

    @property
    def award2(self):
        return self._getViewModel(1)

    def getHeader(self):
        return self._getString(2)

    def setHeader(self, value):
        self._setString(2, value)

    def getDescriptor(self):
        return self._getString(3)

    def setDescriptor(self, value):
        self._setString(3, value)

    def getAdvancedItems(self):
        return self._getArray(4)

    def setAdvancedItems(self, value):
        self._setArray(4, value)

    def _initialize(self):
        super(TestView4Model, self)._initialize()
        self._addViewModelProperty('award', AwardModel())
        self._addViewModelProperty('award2', AwardModel())
        self._addStringProperty('header', '')
        self._addStringProperty('descriptor', '')
        self._addArrayProperty('advancedItems', Array())
        self.onFirstButtonClicked = self._addCommand('onFirstButtonClicked')
        self.onSecondButtonClicked = self._addCommand('onSecondButtonClicked')
