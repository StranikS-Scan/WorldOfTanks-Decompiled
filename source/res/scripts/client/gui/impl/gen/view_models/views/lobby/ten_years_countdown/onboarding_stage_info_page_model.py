# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/ten_years_countdown/onboarding_stage_info_page_model.py
from frameworks.wulf import Array
from gui.impl.gen import R
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.ten_years_countdown.onboarding_stage_info_block_model import OnboardingStageInfoBlockModel

class OnboardingStageInfoPageModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(OnboardingStageInfoPageModel, self).__init__(properties=properties, commands=commands)

    def getTitle(self):
        return self._getResource(0)

    def setTitle(self, value):
        self._setResource(0, value)

    def getSubTitle(self):
        return self._getResource(1)

    def setSubTitle(self, value):
        self._setResource(1, value)

    def getBlocks(self):
        return self._getArray(2)

    def setBlocks(self, value):
        self._setArray(2, value)

    def _initialize(self):
        super(OnboardingStageInfoPageModel, self)._initialize()
        self._addResourceProperty('title', R.invalid())
        self._addResourceProperty('subTitle', R.invalid())
        self._addArrayProperty('blocks', Array())
