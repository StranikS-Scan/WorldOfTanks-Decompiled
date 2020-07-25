# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/tank_setup/common/hints_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.tank_setup.common.hint_model import HintModel

class HintsModel(ViewModel):
    __slots__ = ('onHintZoneAdded', 'onHintZoneHidden', 'onHintZoneClicked')

    def __init__(self, properties=3, commands=3):
        super(HintsModel, self).__init__(properties=properties, commands=commands)

    def getIsEnabled(self):
        return self._getBool(0)

    def setIsEnabled(self, value):
        self._setBool(0, value)

    def getSyncInitiator(self):
        return self._getNumber(1)

    def setSyncInitiator(self, value):
        self._setNumber(1, value)

    def getHints(self):
        return self._getArray(2)

    def setHints(self, value):
        self._setArray(2, value)

    def _initialize(self):
        super(HintsModel, self)._initialize()
        self._addBoolProperty('isEnabled', True)
        self._addNumberProperty('syncInitiator', 0)
        self._addArrayProperty('hints', Array())
        self.onHintZoneAdded = self._addCommand('onHintZoneAdded')
        self.onHintZoneHidden = self._addCommand('onHintZoneHidden')
        self.onHintZoneClicked = self._addCommand('onHintZoneClicked')
