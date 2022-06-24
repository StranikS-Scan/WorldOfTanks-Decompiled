# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/post_progression/single_step_model.py
from frameworks.wulf import Array
from gui.impl.gen.view_models.views.lobby.post_progression.modification_model import ModificationModel
from gui.impl.gen.view_models.views.lobby.post_progression.step_model import StepModel

class SingleStepModel(StepModel):
    __slots__ = ()

    def __init__(self, properties=10, commands=0):
        super(SingleStepModel, self).__init__(properties=properties, commands=commands)

    @property
    def modification(self):
        return self._getViewModel(6)

    @staticmethod
    def getModificationType():
        return ModificationModel

    def getChildrenIds(self):
        return self._getArray(7)

    def setChildrenIds(self, value):
        self._setArray(7, value)

    @staticmethod
    def getChildrenIdsType():
        return int

    def getIsPrebattleSwitchEnabled(self):
        return self._getBool(8)

    def setIsPrebattleSwitchEnabled(self, value):
        self._setBool(8, value)

    def getIsPrebattleSwitchLocked(self):
        return self._getBool(9)

    def setIsPrebattleSwitchLocked(self, value):
        self._setBool(9, value)

    def _initialize(self):
        super(SingleStepModel, self)._initialize()
        self._addViewModelProperty('modification', ModificationModel())
        self._addArrayProperty('childrenIds', Array())
        self._addBoolProperty('isPrebattleSwitchEnabled', True)
        self._addBoolProperty('isPrebattleSwitchLocked', False)
