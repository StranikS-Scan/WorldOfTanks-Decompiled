# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/tooltips/ny_customization_object_tooltip_model.py
from enum import Enum
from frameworks.wulf import ViewModel
from gui.impl.wrappers.user_list_model import UserListModel
from gui.impl.gen.view_models.views.lobby.new_year.views.glade.levelup_price_model import LevelupPriceModel

class ResourceCollectState(Enum):
    AVAILABLE = 'available'
    FINISHED = 'finished'
    COLLECTED = 'collected'


class NyCustomizationObjectTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=7, commands=0):
        super(NyCustomizationObjectTooltipModel, self).__init__(properties=properties, commands=commands)

    @property
    def price(self):
        return self._getViewModel(0)

    @staticmethod
    def getPriceType():
        return LevelupPriceModel

    def getObjectName(self):
        return self._getString(1)

    def setObjectName(self, value):
        self._setString(1, value)

    def getCurrentLevel(self):
        return self._getNumber(2)

    def setCurrentLevel(self, value):
        self._setNumber(2, value)

    def getMaxLevel(self):
        return self._getNumber(3)

    def setMaxLevel(self, value):
        self._setNumber(3, value)

    def getResourceBaseCollectAmount(self):
        return self._getNumber(4)

    def setResourceBaseCollectAmount(self, value):
        self._setNumber(4, value)

    def getResourceExtraCollectAmount(self):
        return self._getNumber(5)

    def setResourceExtraCollectAmount(self, value):
        self._setNumber(5, value)

    def getResourceCollectState(self):
        return ResourceCollectState(self._getString(6))

    def setResourceCollectState(self, value):
        self._setString(6, value.value)

    def _initialize(self):
        super(NyCustomizationObjectTooltipModel, self)._initialize()
        self._addViewModelProperty('price', UserListModel())
        self._addStringProperty('objectName', '')
        self._addNumberProperty('currentLevel', 0)
        self._addNumberProperty('maxLevel', 0)
        self._addNumberProperty('resourceBaseCollectAmount', 0)
        self._addNumberProperty('resourceExtraCollectAmount', 0)
        self._addStringProperty('resourceCollectState')
