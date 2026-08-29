# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/impl/gen/view_models/views/lobby/wt_progression_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from white_tiger.gui.impl.gen.view_models.views.lobby.wt_progression_level_model import WtProgressionLevelModel

class WtProgressionModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=6, commands=0):
        super(WtProgressionModel, self).__init__(properties=properties, commands=commands)

    def getStampsCurrent(self):
        return self._getNumber(0)

    def setStampsCurrent(self, value):
        self._setNumber(0, value)

    def getStampsPrevious(self):
        return self._getNumber(1)

    def setStampsPrevious(self, value):
        self._setNumber(1, value)

    def getStampsNeededPerStage(self):
        return self._getNumber(2)

    def setStampsNeededPerStage(self, value):
        self._setNumber(2, value)

    def getCurrentStage(self):
        return self._getNumber(3)

    def setCurrentStage(self, value):
        self._setNumber(3, value)

    def getPreviousStage(self):
        return self._getNumber(4)

    def setPreviousStage(self, value):
        self._setNumber(4, value)

    def getStages(self):
        return self._getArray(5)

    def setStages(self, value):
        self._setArray(5, value)

    @staticmethod
    def getStagesType():
        return WtProgressionLevelModel

    def _initialize(self):
        super(WtProgressionModel, self)._initialize()
        self._addNumberProperty('stampsCurrent', 0)
        self._addNumberProperty('stampsPrevious', 0)
        self._addNumberProperty('stampsNeededPerStage', 0)
        self._addNumberProperty('currentStage', 0)
        self._addNumberProperty('previousStage', 0)
        self._addArrayProperty('stages', Array())
