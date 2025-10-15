# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: portal/scripts/client/portal/gui/impl/gen/view_models/views/lobby/portal_upgrade_vehicle_item_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from portal.gui.impl.gen.view_models.views.lobby.portal_upgrade_ability_item_model import PortalUpgradeAbilityItemModel

class PortalUpgradeVehicleItemModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=4, commands=0):
        super(PortalUpgradeVehicleItemModel, self).__init__(properties=properties, commands=commands)

    def getName(self):
        return self._getString(0)

    def setName(self, value):
        self._setString(0, value)

    def getLvl(self):
        return self._getNumber(1)

    def setLvl(self, value):
        self._setNumber(1, value)

    def getPoints(self):
        return self._getNumber(2)

    def setPoints(self, value):
        self._setNumber(2, value)

    def getAbilities(self):
        return self._getArray(3)

    def setAbilities(self, value):
        self._setArray(3, value)

    @staticmethod
    def getAbilitiesType():
        return PortalUpgradeAbilityItemModel

    def _initialize(self):
        super(PortalUpgradeVehicleItemModel, self)._initialize()
        self._addStringProperty('name', '')
        self._addNumberProperty('lvl', 0)
        self._addNumberProperty('points', 0)
        self._addArrayProperty('abilities', Array())
