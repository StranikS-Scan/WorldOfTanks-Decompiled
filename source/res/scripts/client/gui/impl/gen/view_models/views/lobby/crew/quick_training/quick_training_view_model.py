# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/crew/quick_training/quick_training_view_model.py
from gui.impl.gen.view_models.views.lobby.crew.common.base_crew_view_model import BaseCrewViewModel
from gui.impl.gen.view_models.views.lobby.crew.quick_training.books_list_component_model import BooksListComponentModel
from gui.impl.gen.view_models.views.lobby.crew.quick_training.freeXp_book_component_model import FreeXpBookComponentModel
from gui.impl.gen.view_models.views.lobby.crew.quick_training.learning_results_component_model import LearningResultsComponentModel
from gui.impl.gen.view_models.views.lobby.crew.quick_training.mentoring_license_component_model import MentoringLicenseComponentModel
from gui.impl.gen.view_models.views.lobby.crew.quick_training.tips_list_component_model import TipsListComponentModel

class QuickTrainingViewModel(BaseCrewViewModel):
    __slots__ = ('mouseLeave',)

    def __init__(self, properties=14, commands=5):
        super(QuickTrainingViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def freeXp(self):
        return self._getViewModel(2)

    @staticmethod
    def getFreeXpType():
        return FreeXpBookComponentModel

    @property
    def books(self):
        return self._getViewModel(3)

    @staticmethod
    def getBooksType():
        return BooksListComponentModel

    @property
    def learningResults(self):
        return self._getViewModel(4)

    @staticmethod
    def getLearningResultsType():
        return LearningResultsComponentModel

    @property
    def tips(self):
        return self._getViewModel(5)

    @staticmethod
    def getTipsType():
        return TipsListComponentModel

    @property
    def mentoringLicense(self):
        return self._getViewModel(6)

    @staticmethod
    def getMentoringLicenseType():
        return MentoringLicenseComponentModel

    def getNationName(self):
        return self._getString(7)

    def setNationName(self, value):
        self._setString(7, value)

    def getVehicleName(self):
        return self._getString(8)

    def setVehicleName(self, value):
        self._setString(8, value)

    def getTankmanName(self):
        return self._getString(9)

    def setTankmanName(self, value):
        self._setString(9, value)

    def getIsWholeCrewHasPerkLimit(self):
        return self._getBool(10)

    def setIsWholeCrewHasPerkLimit(self, value):
        self._setBool(10, value)

    def getIsAnyTankmanHasPerkLimit(self):
        return self._getBool(11)

    def setIsAnyTankmanHasPerkLimit(self, value):
        self._setBool(11, value)

    def getIsCurrentTankmanHasPerkLimit(self):
        return self._getBool(12)

    def setIsCurrentTankmanHasPerkLimit(self, value):
        self._setBool(12, value)

    def getIsCurrentTankmanHasLowEfficiency(self):
        return self._getBool(13)

    def setIsCurrentTankmanHasLowEfficiency(self, value):
        self._setBool(13, value)

    def _initialize(self):
        super(QuickTrainingViewModel, self)._initialize()
        self._addViewModelProperty('freeXp', FreeXpBookComponentModel())
        self._addViewModelProperty('books', BooksListComponentModel())
        self._addViewModelProperty('learningResults', LearningResultsComponentModel())
        self._addViewModelProperty('tips', TipsListComponentModel())
        self._addViewModelProperty('mentoringLicense', MentoringLicenseComponentModel())
        self._addStringProperty('nationName', '')
        self._addStringProperty('vehicleName', '')
        self._addStringProperty('tankmanName', '')
        self._addBoolProperty('isWholeCrewHasPerkLimit', False)
        self._addBoolProperty('isAnyTankmanHasPerkLimit', False)
        self._addBoolProperty('isCurrentTankmanHasPerkLimit', False)
        self._addBoolProperty('isCurrentTankmanHasLowEfficiency', False)
        self.mouseLeave = self._addCommand('mouseLeave')
