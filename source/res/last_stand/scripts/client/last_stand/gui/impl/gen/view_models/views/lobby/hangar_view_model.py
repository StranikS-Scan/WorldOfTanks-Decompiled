# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/gui/impl/gen/view_models/views/lobby/hangar_view_model.py
from frameworks.wulf import Array, ViewModel
from last_stand.gui.impl.gen.view_models.views.lobby.artefact_types_view_model import ArtefactTypesViewModel
from last_stand.gui.impl.gen.view_models.views.lobby.vehicle_title_view_model import VehicleTitleViewModel

class HangarViewModel(ViewModel):
    __slots__ = ('onEscPressed', 'onAboutClick', 'onExitClick', 'onViewLoaded', 'onSlide')

    def __init__(self, properties=9, commands=5):
        super(HangarViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def vehicleTitle(self):
        return self._getViewModel(0)

    @staticmethod
    def getVehicleTitleType():
        return VehicleTitleViewModel

    def getIsLoadedSetup(self):
        return self._getBool(1)

    def setIsLoadedSetup(self, value):
        self._setBool(1, value)

    def getSelectedSlide(self):
        return self._getNumber(2)

    def setSelectedSlide(self, value):
        self._setNumber(2, value)

    def getSelectedDifficulty(self):
        return self._getNumber(3)

    def setSelectedDifficulty(self, value):
        self._setNumber(3, value)

    def getSlidesCount(self):
        return self._getNumber(4)

    def setSlidesCount(self, value):
        self._setNumber(4, value)

    def getShowRandomLable(self):
        return self._getBool(5)

    def setShowRandomLable(self, value):
        self._setBool(5, value)

    def getShowDailyAnim(self):
        return self._getBool(6)

    def setShowDailyAnim(self, value):
        self._setBool(6, value)

    def getIsLockedNextSlide(self):
        return self._getBool(7)

    def setIsLockedNextSlide(self, value):
        self._setBool(7, value)

    def getArtefacts(self):
        return self._getArray(8)

    def setArtefacts(self, value):
        self._setArray(8, value)

    @staticmethod
    def getArtefactsType():
        return ArtefactTypesViewModel

    def _initialize(self):
        super(HangarViewModel, self)._initialize()
        self._addViewModelProperty('vehicleTitle', VehicleTitleViewModel())
        self._addBoolProperty('isLoadedSetup', False)
        self._addNumberProperty('selectedSlide', 0)
        self._addNumberProperty('selectedDifficulty', 0)
        self._addNumberProperty('slidesCount', 0)
        self._addBoolProperty('showRandomLable', False)
        self._addBoolProperty('showDailyAnim', False)
        self._addBoolProperty('isLockedNextSlide', False)
        self._addArrayProperty('artefacts', Array())
        self.onEscPressed = self._addCommand('onEscPressed')
        self.onAboutClick = self._addCommand('onAboutClick')
        self.onExitClick = self._addCommand('onExitClick')
        self.onViewLoaded = self._addCommand('onViewLoaded')
        self.onSlide = self._addCommand('onSlide')
