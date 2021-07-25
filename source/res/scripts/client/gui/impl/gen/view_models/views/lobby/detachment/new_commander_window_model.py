# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/detachment/new_commander_window_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.detachment.common.commander_card_model import CommanderCardModel
from gui.impl.gen.view_models.views.lobby.detachment.common.vehicle_model import VehicleModel

class NewCommanderWindowModel(ViewModel):
    __slots__ = ('onClose', 'onCommanderClick', 'onContinue', 'onCancel')

    def __init__(self, properties=3, commands=4):
        super(NewCommanderWindowModel, self).__init__(properties=properties, commands=commands)

    @property
    def vehicle(self):
        return self._getViewModel(0)

    def getIsNextButtonDisabled(self):
        return self._getBool(1)

    def setIsNextButtonDisabled(self, value):
        self._setBool(1, value)

    def getCommandersList(self):
        return self._getArray(2)

    def setCommandersList(self, value):
        self._setArray(2, value)

    def _initialize(self):
        super(NewCommanderWindowModel, self)._initialize()
        self._addViewModelProperty('vehicle', VehicleModel())
        self._addBoolProperty('isNextButtonDisabled', True)
        self._addArrayProperty('commandersList', Array())
        self.onClose = self._addCommand('onClose')
        self.onCommanderClick = self._addCommand('onCommanderClick')
        self.onContinue = self._addCommand('onContinue')
        self.onCancel = self._addCommand('onCancel')
