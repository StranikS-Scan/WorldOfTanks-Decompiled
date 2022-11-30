# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/popovers/ny_resources_convert_popover_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.new_year.components.ny_resource_model import NyResourceModel
from gui.impl.gen.view_models.views.lobby.new_year.popovers.ny_resources_convert_rate import NyResourcesConvertRate

class NyResourcesConvertPopoverModel(ViewModel):
    __slots__ = ('onConvertClick', 'onGoToRewardKits', 'onGoToQuests')

    def __init__(self, properties=2, commands=3):
        super(NyResourcesConvertPopoverModel, self).__init__(properties=properties, commands=commands)

    @property
    def convertRate(self):
        return self._getViewModel(0)

    @staticmethod
    def getConvertRateType():
        return NyResourcesConvertRate

    def getAvailableResources(self):
        return self._getArray(1)

    def setAvailableResources(self, value):
        self._setArray(1, value)

    @staticmethod
    def getAvailableResourcesType():
        return NyResourceModel

    def _initialize(self):
        super(NyResourcesConvertPopoverModel, self)._initialize()
        self._addViewModelProperty('convertRate', NyResourcesConvertRate())
        self._addArrayProperty('availableResources', Array())
        self.onConvertClick = self._addCommand('onConvertClick')
        self.onGoToRewardKits = self._addCommand('onGoToRewardKits')
        self.onGoToQuests = self._addCommand('onGoToQuests')
