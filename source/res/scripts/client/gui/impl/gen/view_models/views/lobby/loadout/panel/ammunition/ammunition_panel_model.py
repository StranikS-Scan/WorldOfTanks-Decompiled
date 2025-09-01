# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/loadout/panel/ammunition/ammunition_panel_model.py
from frameworks.wulf import Array, ViewModel
from gui.impl.gen.view_models.views.lobby.tank_setup.common.ammunition_items_group import AmmunitionItemsGroup

class AmmunitionPanelModel(ViewModel):
    __slots__ = ('onChangeSetupIndex', 'onOpenSlotSpecDialog')
    NO_SLOT_SELECTED = -1

    def __init__(self, properties=5, commands=2):
        super(AmmunitionPanelModel, self).__init__(properties=properties, commands=commands)

    def getGroups(self):
        return self._getArray(0)

    def setGroups(self, value):
        self._setArray(0, value)

    @staticmethod
    def getGroupsType():
        return AmmunitionItemsGroup

    def getIsDisabled(self):
        return self._getBool(1)

    def setIsDisabled(self, value):
        self._setBool(1, value)

    def getSelectedSlot(self):
        return self._getNumber(2)

    def setSelectedSlot(self, value):
        self._setNumber(2, value)

    def getSelectedSection(self):
        return self._getString(3)

    def setSelectedSection(self, value):
        self._setString(3, value)

    def getVehicleId(self):
        return self._getString(4)

    def setVehicleId(self, value):
        self._setString(4, value)

    def _initialize(self):
        super(AmmunitionPanelModel, self)._initialize()
        self._addArrayProperty('groups', Array())
        self._addBoolProperty('isDisabled', False)
        self._addNumberProperty('selectedSlot', -1)
        self._addStringProperty('selectedSection', '')
        self._addStringProperty('vehicleId', '')
        self.onChangeSetupIndex = self._addCommand('onChangeSetupIndex')
        self.onOpenSlotSpecDialog = self._addCommand('onOpenSlotSpecDialog')
