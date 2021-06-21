# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/post_progression/tooltip/role_slot_tooltip_view_model.py
from frameworks.wulf import Array
from gui.impl.gen.view_models.common.price_model import PriceModel
from gui.impl.gen.view_models.views.lobby.post_progression.tooltip.feature_tooltip_view_model import FeatureTooltipViewModel
from gui.impl.gen.view_models.views.lobby.post_progression.tooltip.role_model import RoleModel

class RoleSlotTooltipViewModel(FeatureTooltipViewModel):
    __slots__ = ()

    def __init__(self, properties=7, commands=0):
        super(RoleSlotTooltipViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def price(self):
        return self._getViewModel(3)

    @property
    def chosenRole(self):
        return self._getViewModel(4)

    def getAvailableRoles(self):
        return self._getArray(5)

    def setAvailableRoles(self, value):
        self._setArray(5, value)

    def getSlots(self):
        return self._getArray(6)

    def setSlots(self, value):
        self._setArray(6, value)

    def _initialize(self):
        super(RoleSlotTooltipViewModel, self)._initialize()
        self._addViewModelProperty('price', PriceModel())
        self._addViewModelProperty('chosenRole', RoleModel())
        self._addArrayProperty('availableRoles', Array())
        self._addArrayProperty('slots', Array())
