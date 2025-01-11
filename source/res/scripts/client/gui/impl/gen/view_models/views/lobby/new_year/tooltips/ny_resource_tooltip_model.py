# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/tooltips/ny_resource_tooltip_model.py
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.new_year.components.ny_resource_model import NyResourceModel

class NyResourceTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(NyResourceTooltipModel, self).__init__(properties=properties, commands=commands)

    @property
    def resource(self):
        return self._getViewModel(0)

    @staticmethod
    def getResourceType():
        return NyResourceModel

    def getFirstCollectAmount(self):
        return self._getNumber(1)

    def setFirstCollectAmount(self, value):
        self._setNumber(1, value)

    def getSecondCollectAmount(self):
        return self._getNumber(2)

    def setSecondCollectAmount(self, value):
        self._setNumber(2, value)

    def _initialize(self):
        super(NyResourceTooltipModel, self)._initialize()
        self._addViewModelProperty('resource', NyResourceModel())
        self._addNumberProperty('firstCollectAmount', 0)
        self._addNumberProperty('secondCollectAmount', 0)
