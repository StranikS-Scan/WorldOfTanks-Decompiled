# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/postbattle/detailed_personal_efficiency_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.postbattle.enemy_multi_params_model import EnemyMultiParamsModel
from gui.impl.gen.view_models.views.lobby.postbattle.simple_efficiency_model import SimpleEfficiencyModel

class DetailedPersonalEfficiencyModel(ViewModel):
    __slots__ = ()
    EFFICIENCY_DEFENCE_TYPE = 'defence'
    EFFICIENCY_CAPTURE_TYPE = 'capture'
    EFFICIENCY_PARAM_TOOLTIP = 'efficiencyParam'
    EFFICIENCY_HEADER_PARAM_TOOLTIP = 'efficiencyHeaderParam'
    TOTAL_EFFICIENCY_PARAM_TOOLTIP = 'totalEfficiencyParam'

    def __init__(self, properties=4, commands=0):
        super(DetailedPersonalEfficiencyModel, self).__init__(properties=properties, commands=commands)

    def getCapturePoints(self):
        return self._getNumber(0)

    def setCapturePoints(self, value):
        self._setNumber(0, value)

    def getDroppedCapturePoints(self):
        return self._getNumber(1)

    def setDroppedCapturePoints(self, value):
        self._setNumber(1, value)

    def getEnemies(self):
        return self._getArray(2)

    def setEnemies(self, value):
        self._setArray(2, value)

    @staticmethod
    def getEnemiesType():
        return EnemyMultiParamsModel

    def getPersonalEfficiency(self):
        return self._getArray(3)

    def setPersonalEfficiency(self, value):
        self._setArray(3, value)

    @staticmethod
    def getPersonalEfficiencyType():
        return SimpleEfficiencyModel

    def _initialize(self):
        super(DetailedPersonalEfficiencyModel, self)._initialize()
        self._addNumberProperty('capturePoints', 0)
        self._addNumberProperty('droppedCapturePoints', 0)
        self._addArrayProperty('enemies', Array())
        self._addArrayProperty('personalEfficiency', Array())
