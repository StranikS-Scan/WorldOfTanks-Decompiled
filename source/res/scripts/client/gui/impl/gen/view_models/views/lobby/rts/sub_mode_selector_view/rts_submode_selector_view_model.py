# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/rts/sub_mode_selector_view/rts_submode_selector_view_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.rts.sub_mode_selector_view.submode_view_model import SubmodeViewModel

class RtsSubmodeSelectorViewModel(ViewModel):
    __slots__ = ('onModeSelected',)

    def __init__(self, properties=2, commands=1):
        super(RtsSubmodeSelectorViewModel, self).__init__(properties=properties, commands=commands)

    def getCurrentSubMode(self):
        return self._getString(0)

    def setCurrentSubMode(self, value):
        self._setString(0, value)

    def getSubModes(self):
        return self._getArray(1)

    def setSubModes(self, value):
        self._setArray(1, value)

    def _initialize(self):
        super(RtsSubmodeSelectorViewModel, self)._initialize()
        self._addStringProperty('currentSubMode', '')
        self._addArrayProperty('subModes', Array())
        self.onModeSelected = self._addCommand('onModeSelected')
