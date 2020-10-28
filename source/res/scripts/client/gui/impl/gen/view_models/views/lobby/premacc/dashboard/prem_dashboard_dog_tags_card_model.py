# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/premacc/dashboard/prem_dashboard_dog_tags_card_model.py
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.ui_kit.counter_model import CounterModel

class PremDashboardDogTagsCardModel(ViewModel):
    __slots__ = ('onGoToDogTagsView',)

    def __init__(self, properties=4, commands=1):
        super(PremDashboardDogTagsCardModel, self).__init__(properties=properties, commands=commands)

    @property
    def Counter(self):
        return self._getViewModel(0)

    def getIsAvailable(self):
        return self._getBool(1)

    def setIsAvailable(self, value):
        self._setBool(1, value)

    def getBackground(self):
        return self._getString(2)

    def setBackground(self, value):
        self._setString(2, value)

    def getEngraving(self):
        return self._getString(3)

    def setEngraving(self, value):
        self._setString(3, value)

    def _initialize(self):
        super(PremDashboardDogTagsCardModel, self)._initialize()
        self._addViewModelProperty('Counter', CounterModel())
        self._addBoolProperty('isAvailable', True)
        self._addStringProperty('background', '')
        self._addStringProperty('engraving', '')
        self.onGoToDogTagsView = self._addCommand('onGoToDogTagsView')
