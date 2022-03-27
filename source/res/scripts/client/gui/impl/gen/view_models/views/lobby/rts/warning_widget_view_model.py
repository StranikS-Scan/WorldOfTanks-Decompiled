# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/rts/warning_widget_view_model.py
from frameworks.wulf import ViewModel

class WarningWidgetViewModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=1, commands=0):
        super(WarningWidgetViewModel, self).__init__(properties=properties, commands=commands)

    def getMessage(self):
        return self._getString(0)

    def setMessage(self, value):
        self._setString(0, value)

    def _initialize(self):
        super(WarningWidgetViewModel, self)._initialize()
        self._addStringProperty('message', '')
