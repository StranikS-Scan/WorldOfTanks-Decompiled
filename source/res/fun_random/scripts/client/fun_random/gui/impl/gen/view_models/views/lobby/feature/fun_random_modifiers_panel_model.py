# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/gui/impl/gen/view_models/views/lobby/feature/fun_random_modifiers_panel_model.py
from frameworks.wulf import ViewModel

class FunRandomModifiersPanelModel(ViewModel):
    __slots__ = ('onWidgetClick',)

    def __init__(self, properties=1, commands=1):
        super(FunRandomModifiersPanelModel, self).__init__(properties=properties, commands=commands)

    def getIsPanelClicked(self):
        return self._getBool(0)

    def setIsPanelClicked(self, value):
        self._setBool(0, value)

    def _initialize(self):
        super(FunRandomModifiersPanelModel, self)._initialize()
        self._addBoolProperty('isPanelClicked', False)
        self.onWidgetClick = self._addCommand('onWidgetClick')
