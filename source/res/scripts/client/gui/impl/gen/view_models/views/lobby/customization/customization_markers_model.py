# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/customization/customization_markers_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.customization.customization_marker_edit_mode_model import CustomizationMarkerEditModeModel
from gui.impl.gen.view_models.views.lobby.customization.customization_marker_model import CustomizationMarkerModel
from gui.impl.gen.view_models.views.lobby.customization.customization_types_model import CustomizationTypesModel

class CustomizationMarkersModel(ViewModel):
    __slots__ = ('onSelectAnchor', 'onHoverAnchor', 'onDragAnchor', 'onRemoveChar', 'onAddChar', 'onDeleteAllChars', 'onEnterInput')

    def __init__(self, properties=3, commands=7):
        super(CustomizationMarkersModel, self).__init__(properties=properties, commands=commands)

    @property
    def editModeData(self):
        return self._getViewModel(0)

    @staticmethod
    def getEditModeDataType():
        return CustomizationMarkerEditModeModel

    @property
    def customizationTypes(self):
        return self._getViewModel(1)

    @staticmethod
    def getCustomizationTypesType():
        return CustomizationTypesModel

    def getMarkersList(self):
        return self._getArray(2)

    def setMarkersList(self, value):
        self._setArray(2, value)

    @staticmethod
    def getMarkersListType():
        return CustomizationMarkerModel

    def _initialize(self):
        super(CustomizationMarkersModel, self)._initialize()
        self._addViewModelProperty('editModeData', CustomizationMarkerEditModeModel())
        self._addViewModelProperty('customizationTypes', CustomizationTypesModel())
        self._addArrayProperty('markersList', Array())
        self.onSelectAnchor = self._addCommand('onSelectAnchor')
        self.onHoverAnchor = self._addCommand('onHoverAnchor')
        self.onDragAnchor = self._addCommand('onDragAnchor')
        self.onRemoveChar = self._addCommand('onRemoveChar')
        self.onAddChar = self._addCommand('onAddChar')
        self.onDeleteAllChars = self._addCommand('onDeleteAllChars')
        self.onEnterInput = self._addCommand('onEnterInput')
