# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/bootcamp/bootcamp_nation_view_model.py
from frameworks.wulf import Array
from gui.impl.gen import R
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.bootcamp.bootcamp_nation_model import BootcampNationModel
from gui.impl.gen.view_models.views.bootcamp.preview_model import PreviewModel

class BootcampNationViewModel(ViewModel):
    __slots__ = ('onNationSelected', 'onNationShow', 'onMoveSpace', 'onEscPressed')

    def __init__(self, properties=8, commands=4):
        super(BootcampNationViewModel, self).__init__(properties=properties, commands=commands)

    def getSelectedNation(self):
        return self._getNumber(0)

    def setSelectedNation(self, value):
        self._setNumber(0, value)

    def getNationsList(self):
        return self._getArray(1)

    def setNationsList(self, value):
        self._setArray(1, value)

    @staticmethod
    def getNationsListType():
        return BootcampNationModel

    def getPromoteNationsList(self):
        return self._getArray(2)

    def setPromoteNationsList(self, value):
        self._setArray(2, value)

    @staticmethod
    def getPromoteNationsListType():
        return BootcampNationModel

    def getSelectedTitle(self):
        return self._getString(3)

    def setSelectedTitle(self, value):
        self._setString(3, value)

    def getSelectedDescription(self):
        return self._getResource(4)

    def setSelectedDescription(self, value):
        self._setResource(4, value)

    def getIsPromote(self):
        return self._getBool(5)

    def setIsPromote(self, value):
        self._setBool(5, value)

    def getPreviewVehiclesList(self):
        return self._getArray(6)

    def setPreviewVehiclesList(self, value):
        self._setArray(6, value)

    @staticmethod
    def getPreviewVehiclesListType():
        return PreviewModel

    def getIsPreviewLoading(self):
        return self._getBool(7)

    def setIsPreviewLoading(self, value):
        self._setBool(7, value)

    def _initialize(self):
        super(BootcampNationViewModel, self)._initialize()
        self._addNumberProperty('selectedNation', 0)
        self._addArrayProperty('nationsList', Array())
        self._addArrayProperty('promoteNationsList', Array())
        self._addStringProperty('selectedTitle', '')
        self._addResourceProperty('selectedDescription', R.invalid())
        self._addBoolProperty('isPromote', False)
        self._addArrayProperty('previewVehiclesList', Array())
        self._addBoolProperty('isPreviewLoading', False)
        self.onNationSelected = self._addCommand('onNationSelected')
        self.onNationShow = self._addCommand('onNationShow')
        self.onMoveSpace = self._addCommand('onMoveSpace')
        self.onEscPressed = self._addCommand('onEscPressed')
