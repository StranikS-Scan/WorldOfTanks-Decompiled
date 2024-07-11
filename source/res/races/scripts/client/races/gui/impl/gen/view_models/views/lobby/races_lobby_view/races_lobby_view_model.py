# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: races/scripts/client/races/gui/impl/gen/view_models/views/lobby/races_lobby_view/races_lobby_view_model.py
from frameworks.wulf import ViewModel
from races.gui.impl.gen.view_models.views.lobby.races_lobby_view.lootbox_entry_view_model import LootboxEntryViewModel
from races.gui.impl.gen.view_models.views.lobby.races_lobby_view.progression_widget_model import ProgressionWidgetModel
from races.gui.impl.gen.view_models.views.lobby.vehicles_carousel.vehicles_carousel_model import VehiclesCarouselModel

class RacesLobbyViewModel(ViewModel):
    __slots__ = ('onMoveSpace', 'onAboutEvent', 'onEscapePressed')

    def __init__(self, properties=3, commands=3):
        super(RacesLobbyViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def vehiclesCarouselModel(self):
        return self._getViewModel(0)

    @staticmethod
    def getVehiclesCarouselModelType():
        return VehiclesCarouselModel

    @property
    def lootboxEntryModel(self):
        return self._getViewModel(1)

    @staticmethod
    def getLootboxEntryModelType():
        return LootboxEntryViewModel

    @property
    def progressionWidgetModel(self):
        return self._getViewModel(2)

    @staticmethod
    def getProgressionWidgetModelType():
        return ProgressionWidgetModel

    def _initialize(self):
        super(RacesLobbyViewModel, self)._initialize()
        self._addViewModelProperty('vehiclesCarouselModel', VehiclesCarouselModel())
        self._addViewModelProperty('lootboxEntryModel', LootboxEntryViewModel())
        self._addViewModelProperty('progressionWidgetModel', ProgressionWidgetModel())
        self.onMoveSpace = self._addCommand('onMoveSpace')
        self.onAboutEvent = self._addCommand('onAboutEvent')
        self.onEscapePressed = self._addCommand('onEscapePressed')
