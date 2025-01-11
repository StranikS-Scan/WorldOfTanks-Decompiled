# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/dialogs/resources_converter/resources_convert_dialog_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.new_year.components.ny_resource_model import NyResourceModel

class ResourcesConvertDialogModel(ViewModel):
    __slots__ = ('onAccept', 'onCancel')

    def __init__(self, properties=4, commands=2):
        super(ResourcesConvertDialogModel, self).__init__(properties=properties, commands=commands)

    @property
    def resourceFrom(self):
        return self._getViewModel(0)

    @staticmethod
    def getResourceFromType():
        return NyResourceModel

    @property
    def resourceTo(self):
        return self._getViewModel(1)

    @staticmethod
    def getResourceToType():
        return NyResourceModel

    def getResources(self):
        return self._getArray(2)

    def setResources(self, value):
        self._setArray(2, value)

    @staticmethod
    def getResourcesType():
        return NyResourceModel

    def getIsWalletAvailable(self):
        return self._getBool(3)

    def setIsWalletAvailable(self, value):
        self._setBool(3, value)

    def _initialize(self):
        super(ResourcesConvertDialogModel, self)._initialize()
        self._addViewModelProperty('resourceFrom', NyResourceModel())
        self._addViewModelProperty('resourceTo', NyResourceModel())
        self._addArrayProperty('resources', Array())
        self._addBoolProperty('isWalletAvailable', True)
        self.onAccept = self._addCommand('onAccept')
        self.onCancel = self._addCommand('onCancel')
