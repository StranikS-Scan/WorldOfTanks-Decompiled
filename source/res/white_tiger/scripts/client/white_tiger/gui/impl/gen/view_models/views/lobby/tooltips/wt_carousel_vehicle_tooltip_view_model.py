# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/impl/gen/view_models/views/lobby/tooltips/wt_carousel_vehicle_tooltip_view_model.py
from gui.impl.gen import R
from frameworks.wulf import ViewModel

class WtCarouselVehicleTooltipViewModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=5, commands=0):
        super(WtCarouselVehicleTooltipViewModel, self).__init__(properties=properties, commands=commands)

    def getTitle(self):
        return self._getString(0)

    def setTitle(self, value):
        self._setString(0, value)

    def getSubtitle(self):
        return self._getString(1)

    def setSubtitle(self, value):
        self._setString(1, value)

    def getDescription(self):
        return self._getString(2)

    def setDescription(self, value):
        self._setString(2, value)

    def getIcon(self):
        return self._getResource(3)

    def setIcon(self, value):
        self._setResource(3, value)

    def getIsSpecialBoss(self):
        return self._getBool(4)

    def setIsSpecialBoss(self, value):
        self._setBool(4, value)

    def _initialize(self):
        super(WtCarouselVehicleTooltipViewModel, self)._initialize()
        self._addStringProperty('title', '')
        self._addStringProperty('subtitle', '')
        self._addStringProperty('description', '')
        self._addResourceProperty('icon', R.invalid())
        self._addBoolProperty('isSpecialBoss', False)
