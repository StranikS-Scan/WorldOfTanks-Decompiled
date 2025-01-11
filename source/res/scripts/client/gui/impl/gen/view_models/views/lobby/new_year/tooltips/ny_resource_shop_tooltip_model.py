# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/tooltips/ny_resource_shop_tooltip_model.py
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.new_year.components.ny_resource_model import NyResourceModel

class NyResourceShopTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=1, commands=0):
        super(NyResourceShopTooltipModel, self).__init__(properties=properties, commands=commands)

    @property
    def resource(self):
        return self._getViewModel(0)

    @staticmethod
    def getResourceType():
        return NyResourceModel

    def _initialize(self):
        super(NyResourceShopTooltipModel, self)._initialize()
        self._addViewModelProperty('resource', NyResourceModel())
