# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/post_progression/dialogs/research_steps_main_content.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.common.bonuses_model import BonusesModel
from gui.impl.gen.view_models.views.lobby.post_progression.dialogs.short_modification_model import ShortModificationModel
from gui.impl.gen.view_models.views.lobby.post_progression.dialogs.short_step_model import ShortStepModel

class ResearchStepsMainContent(ViewModel):
    __slots__ = ()

    def __init__(self, properties=4, commands=0):
        super(ResearchStepsMainContent, self).__init__(properties=properties, commands=commands)

    @property
    def modificationsBonuses(self):
        return self._getViewModel(0)

    @staticmethod
    def getModificationsBonusesType():
        return BonusesModel

    def getStepsResearch(self):
        return self._getArray(1)

    def setStepsResearch(self, value):
        self._setArray(1, value)

    @staticmethod
    def getStepsResearchType():
        return ShortStepModel

    def getUnlockModifications(self):
        return self._getArray(2)

    def setUnlockModifications(self, value):
        self._setArray(2, value)

    @staticmethod
    def getUnlockModificationsType():
        return ShortModificationModel

    def getUnlockFeatures(self):
        return self._getArray(3)

    def setUnlockFeatures(self, value):
        self._setArray(3, value)

    @staticmethod
    def getUnlockFeaturesType():
        return ShortModificationModel

    def _initialize(self):
        super(ResearchStepsMainContent, self)._initialize()
        self._addViewModelProperty('modificationsBonuses', BonusesModel())
        self._addArrayProperty('stepsResearch', Array())
        self._addArrayProperty('unlockModifications', Array())
        self._addArrayProperty('unlockFeatures', Array())
