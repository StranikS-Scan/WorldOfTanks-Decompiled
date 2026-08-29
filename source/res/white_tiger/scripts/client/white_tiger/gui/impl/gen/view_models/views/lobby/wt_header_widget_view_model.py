# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/impl/gen/view_models/views/lobby/wt_header_widget_view_model.py
from frameworks.wulf import ViewModel

class WtHeaderWidgetViewModel(ViewModel):
    __slots__ = ('onClick',)

    def __init__(self, properties=2, commands=1):
        super(WtHeaderWidgetViewModel, self).__init__(properties=properties, commands=commands)

    def getCurrentProgression(self):
        return self._getNumber(0)

    def setCurrentProgression(self, value):
        self._setNumber(0, value)

    def getTotalProgression(self):
        return self._getNumber(1)

    def setTotalProgression(self, value):
        self._setNumber(1, value)

    def _initialize(self):
        super(WtHeaderWidgetViewModel, self)._initialize()
        self._addNumberProperty('currentProgression', 0)
        self._addNumberProperty('totalProgression', 0)
        self.onClick = self._addCommand('onClick')
