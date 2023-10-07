# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/crew/common/buttons_bar_model.py
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.crew.common.crew_books_button_model import CrewBooksButtonModel
from gui.impl.gen.view_models.views.lobby.crew.common.crew_operations_button_model import CrewOperationsButtonModel
from gui.impl.gen.view_models.views.lobby.crew.common.toggle_button_model import ToggleButtonModel

class ButtonsBarModel(ViewModel):
    __slots__ = ('onCrewBooksClick', 'onWotPlusClick')

    def __init__(self, properties=4, commands=2):
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
    def wotPlus(self):
        return self._getViewModel(2)

    @staticmethod
    def getWotPlusType():
        return ToggleButtonModel

    def getIsVisible(self):
        return self._getBool(3)

    def setIsVisible(self, value):
        self._setBool(3, value)

    def _initialize(self):
        super(ButtonsBarModel, self)._initialize()
        self._addViewModelProperty('crewOperations', CrewOperationsButtonModel())
        self._addViewModelProperty('crewBooks', CrewBooksButtonModel())
        self._addViewModelProperty('wotPlus', ToggleButtonModel())
        self._addBoolProperty('isVisible', True)
        self.onCrewBooksClick = self._addCommand('onCrewBooksClick')
        self.onWotPlusClick = self._addCommand('onWotPlusClick')
