# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/fun_random/fun_random_hangar_widget_view_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel

class FunRandomHangarWidgetViewModel(ViewModel):
    __slots__ = ('onShowInfo',)

    def __init__(self, properties=2, commands=1):
        super(FunRandomHangarWidgetViewModel, self).__init__(properties=properties, commands=commands)

    def getActiveModeName(self):
        return self._getString(0)

    def setActiveModeName(self, value):
        self._setString(0, value)

    def getModifiersDomains(self):
        return self._getArray(1)

    def setModifiersDomains(self, value):
        self._setArray(1, value)

    @staticmethod
    def getModifiersDomainsType():
        return str

    def _initialize(self):
        super(FunRandomHangarWidgetViewModel, self)._initialize()
        self._addStringProperty('activeModeName', '')
        self._addArrayProperty('modifiersDomains', Array())
        self.onShowInfo = self._addCommand('onShowInfo')
