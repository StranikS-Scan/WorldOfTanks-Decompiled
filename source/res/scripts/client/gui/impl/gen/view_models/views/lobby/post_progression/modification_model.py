# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/post_progression/modification_model.py
from enum import Enum
from gui.impl.gen import R
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.common.price_model import PriceModel

class RoleCategory(Enum):
    FIREPOWER = 'firepower'
    SURVIVABILITY = 'survivability'
    MOBILITY = 'mobility'
    STEALTH = 'stealth'
    NONE = 'none'


class ModificationModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=6, commands=0):
        super(ModificationModel, self).__init__(properties=properties, commands=commands)

    @property
    def price(self):
        return self._getViewModel(0)

    def getId(self):
        return self._getNumber(1)

    def setId(self, value):
        self._setNumber(1, value)

    def getImageResName(self):
        return self._getString(2)

    def setImageResName(self, value):
        self._setString(2, value)

    def getTitleRes(self):
        return self._getResource(3)

    def setTitleRes(self, value):
        self._setResource(3, value)

    def getRoleCategory(self):
        return RoleCategory(self._getString(4))

    def setRoleCategory(self, value):
        self._setString(4, value.value)

    def getTooltipContentId(self):
        return self._getNumber(5)

    def setTooltipContentId(self, value):
        self._setNumber(5, value)

    def _initialize(self):
        super(ModificationModel, self)._initialize()
        self._addViewModelProperty('price', PriceModel())
        self._addNumberProperty('id', 0)
        self._addStringProperty('imageResName', '')
        self._addResourceProperty('titleRes', R.invalid())
        self._addStringProperty('roleCategory')
        self._addNumberProperty('tooltipContentId', 0)
