# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/detachment/profile_view_model.py
from frameworks.wulf import Array
from gui.impl.gen.view_models.views.lobby.detachment.common.commander_card_model import CommanderCardModel
from gui.impl.gen.view_models.views.lobby.detachment.common.filters_model import FiltersModel
from gui.impl.gen.view_models.views.lobby.detachment.common.navigation_view_model import NavigationViewModel
from gui.impl.gen.view_models.views.lobby.detachment.common.popover_tracker_impl_model import PopoverTrackerImplModel

class ProfileViewModel(NavigationViewModel):
    __slots__ = ('onFiltersReset', 'onCommanderClick', 'onHoverNewCommander')

    def __init__(self, properties=6, commands=6):
        super(ProfileViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def filtersModel(self):
        return self._getViewModel(2)

    @property
    def popover(self):
        return self._getViewModel(3)

    def getVehicleNation(self):
        return self._getString(4)

    def setVehicleNation(self, value):
        self._setString(4, value)

    def getCommandersList(self):
        return self._getArray(5)

    def setCommandersList(self, value):
        self._setArray(5, value)

    def _initialize(self):
        super(ProfileViewModel, self)._initialize()
        self._addViewModelProperty('filtersModel', FiltersModel())
        self._addViewModelProperty('popover', PopoverTrackerImplModel())
        self._addStringProperty('vehicleNation', '')
        self._addArrayProperty('commandersList', Array())
        self.onFiltersReset = self._addCommand('onFiltersReset')
        self.onCommanderClick = self._addCommand('onCommanderClick')
        self.onHoverNewCommander = self._addCommand('onHoverNewCommander')
