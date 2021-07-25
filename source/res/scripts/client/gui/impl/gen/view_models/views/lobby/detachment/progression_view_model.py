# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/detachment/progression_view_model.py
from gui.impl.gen.view_models.views.lobby.detachment.common.detachment_top_panel_model import DetachmentTopPanelModel
from gui.impl.gen.view_models.views.lobby.detachment.common.navigation_view_model import NavigationViewModel
from gui.impl.gen.view_models.views.lobby.detachment.progression_crew_books_model import ProgressionCrewBooksModel
from gui.impl.gen.view_models.views.lobby.detachment.progression_experience_exchange_model import ProgressionExperienceExchangeModel

class ProgressionViewModel(NavigationViewModel):
    __slots__ = ('goToPersonalCase', 'onTabActive')
    EXCHANGE = 'Exchange'
    CREW_BOOKS = 'CrewBooks'

    def __init__(self, properties=8, commands=5):
        super(ProgressionViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def crewBooks(self):
        return self._getViewModel(2)

    @property
    def experienceExchange(self):
        return self._getViewModel(3)

    @property
    def topPanelModel(self):
        return self._getViewModel(4)

    def getNewCrewBooksAmount(self):
        return self._getNumber(5)

    def setNewCrewBooksAmount(self, value):
        self._setNumber(5, value)

    def getIsExchangeDiscount(self):
        return self._getBool(6)

    def setIsExchangeDiscount(self, value):
        self._setBool(6, value)

    def getIsBooksAvailable(self):
        return self._getBool(7)

    def setIsBooksAvailable(self, value):
        self._setBool(7, value)

    def _initialize(self):
        super(ProgressionViewModel, self)._initialize()
        self._addViewModelProperty('crewBooks', ProgressionCrewBooksModel())
        self._addViewModelProperty('experienceExchange', ProgressionExperienceExchangeModel())
        self._addViewModelProperty('topPanelModel', DetachmentTopPanelModel())
        self._addNumberProperty('newCrewBooksAmount', -1)
        self._addBoolProperty('isExchangeDiscount', False)
        self._addBoolProperty('isBooksAvailable', True)
        self.goToPersonalCase = self._addCommand('goToPersonalCase')
        self.onTabActive = self._addCommand('onTabActive')
