# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/crew/common/buttons_bar_model.py
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.crew.common.crew_books_button_model import CrewBooksButtonModel
from gui.impl.gen.view_models.views.lobby.crew.common.crew_operations_button_model import CrewOperationsButtonModel
from gui.impl.gen.view_models.views.lobby.crew.common.toggle_button_model import ToggleButtonModel

class ButtonsBarModel(ViewModel):
    __slots__ = ('onCrewBooksClick', 'onAcceleratedTrainingClick', 'onWotPlusClick')

    def __init__(self, properties=5, commands=3):
        super(ButtonsBarModel, self).__init__(properties=properties, commands=commands)

    @property
    def crewOperations(self):
        return self._getViewModel(0)

    @staticmethod
    def getCrewOperationsType():
        return CrewOperationsButtonModel

    @property
    def crewBooks(self):
        return self._getViewModel(1)

    @staticmethod
    def getCrewBooksType():
        return CrewBooksButtonModel

    @property
    def acceleratedTraining(self):
        return self._getViewModel(2)

    @staticmethod
    def getAcceleratedTrainingType():
        return ToggleButtonModel

    @property
    def wotPlus(self):
        return self._getViewModel(3)

    @staticmethod
    def getWotPlusType():
        return ToggleButtonModel

    def getIsVisible(self):
        return self._getBool(4)

    def setIsVisible(self, value):
        self._setBool(4, value)

    def _initialize(self):
        super(ButtonsBarModel, self)._initialize()
        self._addViewModelProperty('crewOperations', CrewOperationsButtonModel())
        self._addViewModelProperty('crewBooks', CrewBooksButtonModel())
        self._addViewModelProperty('acceleratedTraining', ToggleButtonModel())
        self._addViewModelProperty('wotPlus', ToggleButtonModel())
        self._addBoolProperty('isVisible', True)
        self.onCrewBooksClick = self._addCommand('onCrewBooksClick')
        self.onAcceleratedTrainingClick = self._addCommand('onAcceleratedTrainingClick')
        self.onWotPlusClick = self._addCommand('onWotPlusClick')
