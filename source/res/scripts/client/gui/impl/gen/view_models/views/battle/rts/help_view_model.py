# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/battle/rts/help_view_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.battle.rts.help_actions_section_model import HelpActionsSectionModel
from gui.impl.gen.view_models.views.battle.rts.help_controls_section_model import HelpControlsSectionModel

class HelpViewModel(ViewModel):
    __slots__ = ('onClose',)

    def __init__(self, properties=2, commands=1):
        super(HelpViewModel, self).__init__(properties=properties, commands=commands)

    def getControls(self):
        return self._getArray(0)

    def setControls(self, value):
        self._setArray(0, value)

    def getActions(self):
        return self._getArray(1)

    def setActions(self, value):
        self._setArray(1, value)

    def _initialize(self):
        super(HelpViewModel, self)._initialize()
        self._addArrayProperty('controls', Array())
        self._addArrayProperty('actions', Array())
        self.onClose = self._addCommand('onClose')
