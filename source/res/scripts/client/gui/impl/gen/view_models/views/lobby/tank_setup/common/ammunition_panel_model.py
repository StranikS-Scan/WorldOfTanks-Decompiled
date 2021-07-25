# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/tank_setup/common/ammunition_panel_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.tank_setup.common.ammunition_items_group import AmmunitionItemsGroup

class AmmunitionPanelModel(ViewModel):
    __slots__ = ('onSectionSelect', 'onDragDropSwap', 'onSlotClear', 'onSectionResized', 'onChangeSetupIndex', 'onSpecializationSelect')

    def __init__(self, properties=6, commands=6):
        super(AmmunitionPanelModel, self).__init__(properties=properties, commands=commands)

    def getAmmoNotFull(self):
        return self._getBool(0)

    def setAmmoNotFull(self, value):
        self._setBool(0, value)

    def getSelectedSection(self):
        return self._getString(1)

    def setSelectedSection(self, value):
        self._setString(1, value)

    def getSelectedSlot(self):
        return self._getNumber(2)

    def setSelectedSlot(self, value):
        self._setNumber(2, value)

    def getIsSetupSwitchInProgress(self):
        return self._getBool(3)

    def setIsSetupSwitchInProgress(self, value):
        self._setBool(3, value)

    def getSectionGroups(self):
        return self._getArray(4)

    def setSectionGroups(self, value):
        self._setArray(4, value)

    def getSyncInitiator(self):
        return self._getNumber(5)

    def setSyncInitiator(self, value):
        self._setNumber(5, value)

    def _initialize(self):
        super(AmmunitionPanelModel, self)._initialize()
        self._addBoolProperty('ammoNotFull', False)
        self._addStringProperty('selectedSection', '')
        self._addNumberProperty('selectedSlot', -1)
        self._addBoolProperty('isSetupSwitchInProgress', False)
        self._addArrayProperty('sectionGroups', Array())
        self._addNumberProperty('syncInitiator', 0)
        self.onSectionSelect = self._addCommand('onSectionSelect')
        self.onDragDropSwap = self._addCommand('onDragDropSwap')
        self.onSlotClear = self._addCommand('onSlotClear')
        self.onSectionResized = self._addCommand('onSectionResized')
        self.onChangeSetupIndex = self._addCommand('onChangeSetupIndex')
        self.onSpecializationSelect = self._addCommand('onSpecializationSelect')
