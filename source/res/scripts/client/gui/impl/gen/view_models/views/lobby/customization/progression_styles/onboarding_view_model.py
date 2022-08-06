# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/customization/progression_styles/onboarding_view_model.py
from frameworks.wulf import ViewModel

class OnboardingViewModel(ViewModel):
    __slots__ = ('onClose', 'onGotoStyle')

    def __init__(self, properties=1, commands=2):
        super(OnboardingViewModel, self).__init__(properties=properties, commands=commands)

    def getIsFirstShow(self):
        return self._getBool(0)

    def setIsFirstShow(self, value):
        self._setBool(0, value)

    def _initialize(self):
        super(OnboardingViewModel, self)._initialize()
        self._addBoolProperty('isFirstShow', False)
        self.onClose = self._addCommand('onClose')
        self.onGotoStyle = self._addCommand('onGotoStyle')
