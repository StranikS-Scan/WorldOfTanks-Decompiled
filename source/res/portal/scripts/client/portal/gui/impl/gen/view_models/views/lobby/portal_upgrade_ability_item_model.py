# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: portal/scripts/client/portal/gui/impl/gen/view_models/views/lobby/portal_upgrade_ability_item_model.py
from frameworks.wulf import ViewModel

class PortalUpgradeAbilityItemModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(PortalUpgradeAbilityItemModel, self).__init__(properties=properties, commands=commands)

    def getName(self):
        return self._getString(0)

    def setName(self, value):
        self._setString(0, value)

    def getIsReceived(self):
        return self._getBool(1)

    def setIsReceived(self, value):
        self._setBool(1, value)

    def _initialize(self):
        super(PortalUpgradeAbilityItemModel, self)._initialize()
        self._addStringProperty('name', '')
        self._addBoolProperty('isReceived', False)
