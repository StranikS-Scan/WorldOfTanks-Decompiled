# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/ten_years_countdown/onboarding_stage_info_block_model.py
from gui.impl.gen import R
from frameworks.wulf import ViewModel

class OnboardingStageInfoBlockModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(OnboardingStageInfoBlockModel, self).__init__(properties=properties, commands=commands)

    def getTitle(self):
        return self._getResource(0)

    def setTitle(self, value):
        self._setResource(0, value)

    def getDescription(self):
        return self._getResource(1)

    def setDescription(self, value):
        self._setResource(1, value)

    def getImage(self):
        return self._getResource(2)

    def setImage(self, value):
        self._setResource(2, value)

    def _initialize(self):
        super(OnboardingStageInfoBlockModel, self)._initialize()
        self._addResourceProperty('title', R.invalid())
        self._addResourceProperty('description', R.invalid())
        self._addResourceProperty('image', R.invalid())
