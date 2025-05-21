# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/gui/impl/gen/view_models/views/lobby/hangar_view_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from last_stand.gui.impl.gen.view_models.views.lobby.artefact_types_view_model import ArtefactTypesViewModel
from last_stand.gui.impl.gen.view_models.views.lobby.progress_view_model import ProgressViewModel
from last_stand.gui.impl.gen.view_models.views.lobby.vehicle_title_view_model import VehicleTitleViewModel

class HangarViewModel(ViewModel):
    __slots__ = ('onEscPressed', 'onAboutClick', 'onMetaClick', 'onExitClick', 'onViewLoaded', 'onSlide')

    def __init__(self, properties=10, commands=6):
        super(HangarViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def vehicleTitle(self):
        return self._getViewModel(0)

    @staticmethod
    def getVehicleTitleType():
        return VehicleTitleViewModel

    @property
    def progress(self):
        return self._getViewModel(1)

    @staticmethod
    def getProgressType():
        return ProgressViewModel

    def getIsLoadedSetup(self):
        return self._getBool(2)

    def setIsLoadedSetup(self, value):
        self._setBool(2, value)

    def getSelectedSlide(self):
        return self._getNumber(3)

    def setSelectedSlide(self, value):
        self._setNumber(3, value)

    def getSelectedDifficulty(self):
        return self._getNumber(4)

    def setSelectedDifficulty(self, value):
        self._setNumber(4, value)

    def getSlidesCount(self):
        return self._getNumber(5)

    def setSlidesCount(self, value):
        self._setNumber(5, value)

    def getShowRandomLable(self):
        return self._getBool(6)

    def setShowRandomLable(self, value):
        self._setBool(6, value)

    def getShowDailyAnim(self):
        return self._getBool(7)

    def setShowDailyAnim(self, value):
        self._setBool(7, value)

    def getIsLockedNextSlide(self):
        return self._getBool(8)

    def setIsLockedNextSlide(self, value):
        self._setBool(8, value)

    def getArtefacts(self):
        return self._getArray(9)

    def setArtefacts(self, value):
        self._setArray(9, value)

    @staticmethod
    def getArtefactsType():
        return ArtefactTypesViewModel

    def _initialize(self):
        super(HangarViewModel, self)._initialize()
        self._addViewModelProperty('vehicleTitle', VehicleTitleViewModel())
        self._addViewModelProperty('progress', ProgressViewModel())
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
        self.onMetaClick = self._addCommand('onMetaClick')
        self.onExitClick = self._addCommand('onExitClick')
        self.onViewLoaded = self._addCommand('onViewLoaded')
        self.onSlide = self._addCommand('onSlide')
