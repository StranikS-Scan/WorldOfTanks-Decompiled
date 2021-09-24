# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/postbattle/progressive_reward_model.py
from frameworks.wulf import ViewModel

class ProgressiveRewardModel(ViewModel):
    __slots__ = ()
    PROB_MIN = 'prob_min'
    PROB_MED = 'prob_med'
    PROB_MAX = 'prob_max'
    RECEIVED = 'received'

    def __init__(self, properties=4, commands=0):
        super(ProgressiveRewardModel, self).__init__(properties=properties, commands=commands)

    def getMaxSteps(self):
        return self._getNumber(0)

    def setMaxSteps(self, value):
        self._setNumber(0, value)

    def getCurrentStep(self):
        return self._getNumber(1)

    def setCurrentStep(self, value):
        self._setNumber(1, value)

    def getCurrentStepState(self):
        return self._getString(2)

    def setCurrentStepState(self, value):
        self._setString(2, value)

    def getIsEnabled(self):
        return self._getBool(3)

    def setIsEnabled(self, value):
        self._setBool(3, value)

    def _initialize(self):
        super(ProgressiveRewardModel, self)._initialize()
        self._addNumberProperty('maxSteps', 0)
        self._addNumberProperty('currentStep', 0)
        self._addStringProperty('currentStepState', '')
        self._addBoolProperty('isEnabled', False)
