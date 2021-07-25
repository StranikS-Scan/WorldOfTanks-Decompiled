# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/post_progression/modification_model.py
from enum import Enum
from gui.impl.gen.view_models.common.price_model import PriceModel
from gui.impl.gen.view_models.views.lobby.post_progression.base_modification_model import BaseModificationModel

class RoleCategory(Enum):
    FIREPOWER = 'firepower'
    SURVIVABILITY = 'survivability'
    MOBILITY = 'mobility'
    STEALTH = 'stealth'
    NONE = 'none'


class ModificationModel(BaseModificationModel):
    __slots__ = ()

    def __init__(self, properties=6, commands=0):
        super(ModificationModel, self).__init__(properties=properties, commands=commands)

    @property
    def price(self):
        return self._getViewModel(4)

    def getRoleCategory(self):
        return RoleCategory(self._getString(5))

    def setRoleCategory(self, value):
        self._setString(5, value.value)

    def _initialize(self):
        super(ModificationModel, self)._initialize()
        self._addViewModelProperty('price', PriceModel())
        self._addStringProperty('roleCategory')
