# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/popovers/ny_resources_convert_popover_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.new_year.components.ny_resource_model import NyResourceModel
from gui.impl.gen.view_models.views.lobby.new_year.popovers.ny_resources_convert_rate import NyResourcesConvertRate

class NyResourcesConvertPopoverModel(ViewModel):
    __slots__ = ('onConvertClick', 'onGoToRewardKits', 'onGoToQuests', 'onChangeResourcesType')

    def __init__(self, properties=8, commands=4):
        super(NyResourcesConvertPopoverModel, self).__init__(properties=properties, commands=commands)

    @property
    def convertRate(self):
        return self._getViewModel(0)

    @staticmethod
    def getConvertRateType():
        return NyResourcesConvertRate

    def getIsWalletAvailable(self):
        return self._getBool(1)

    def setIsWalletAvailable(self, value):
        self._setBool(1, value)

    def getResourceTypeFrom(self):
        return self._getString(2)

    def setResourceTypeFrom(self, value):
        self._setString(2, value)

    def getResourceTypeTo(self):
        return self._getString(3)

    def setResourceTypeTo(self, value):
        self._setString(3, value)

    def getIsBoxesAvailable(self):
        return self._getBool(4)

    def setIsBoxesAvailable(self, value):
        self._setBool(4, value)

    def getIsExternal(self):
        return self._getBool(5)

    def setIsExternal(self, value):
        self._setBool(5, value)

    def getIsFriendHangar(self):
        return self._getBool(6)

    def setIsFriendHangar(self, value):
        self._setBool(6, value)

    def getAvailableResources(self):
        return self._getArray(7)

    def setAvailableResources(self, value):
        self._setArray(7, value)

    @staticmethod
    def getAvailableResourcesType():
        return NyResourceModel

    def _initialize(self):
        super(NyResourcesConvertPopoverModel, self)._initialize()
        self._addViewModelProperty('convertRate', NyResourcesConvertRate())
        self._addBoolProperty('isWalletAvailable', False)
        self._addStringProperty('resourceTypeFrom', '')
        self._addStringProperty('resourceTypeTo', '')
        self._addBoolProperty('isBoxesAvailable', False)
        self._addBoolProperty('isExternal', False)
        self._addBoolProperty('isFriendHangar', False)
        self._addArrayProperty('availableResources', Array())
        self.onConvertClick = self._addCommand('onConvertClick')
        self.onGoToRewardKits = self._addCommand('onGoToRewardKits')
        self.onGoToQuests = self._addCommand('onGoToQuests')
        self.onChangeResourcesType = self._addCommand('onChangeResourcesType')
