# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/vehicle_compare/panel_blocks.py
from frameworks.wulf import Array
from gui.Scaleform.daapi.view.lobby.vehicle_compare import cmp_helpers
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.tank_setup.common.compare_toggle_ammunition_slot import CompareToggleAmmunitionSlot
from gui.impl.gen.view_models.views.lobby.tank_setup.tank_setup_constants import TankSetupConstants
from gui.impl.common.ammunition_panel.ammunition_panel_blocks import OptDeviceBlock, BaseBlock, ConsumablesBlock, BattleBoostersBlock
from helpers import dependency
from skeletons.gui.shared import IItemsCache

class CompareOptDeviceBlock(OptDeviceBlock):

    def _updateSlotWithItem(self, model, idx, slotItem):
        super(CompareOptDeviceBlock, self)._updateSlotWithItem(model, idx, slotItem)
        model.setIsInstalled(False)


class CompareShellsBlock(BaseBlock):
    _itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, vehicle, currentSection):
        super(CompareShellsBlock, self).__init__(vehicle, currentSection)
        self.__selectedIndex = None
        return

    def createBlock(self, viewModel):
        super(CompareShellsBlock, self).createBlock(viewModel)
        viewModel.setType(self._getSectionName())

    def updateBlock(self, viewModel):
        self.__selectedIndex = cmp_helpers.getCmpConfiguratorMainView().getCurrentShellIndex()
        super(CompareShellsBlock, self).updateBlock(viewModel)

    def _getSectionName(self):
        return TankSetupConstants.TOGGLE_SHELLS

    def _getAmmunitionSlotModel(self):
        return CompareToggleAmmunitionSlot()

    def _getInstalled(self):
        getter = self._itemsCache.items.getItemByCD
        return [ getter(shot.shell.compactDescr) for shot in self._vehicle.descriptor.gun.shots ]

    def _getSetupLayout(self):
        return None

    def _getLayout(self):
        return self._getInstalled()

    def _updateSlotWithItem(self, model, idx, slotItem):
        model.setImageSource(R.images.gui.maps.icons.shell.small.dyn(slotItem.descriptor.iconName)())
        model.setIsSelected(self.__selectedIndex == idx)


class CompareConsumablesBlock(ConsumablesBlock):

    def _getKeySettings(self):
        pass

    def _updateSlotWithItem(self, model, idx, slotItem):
        super(CompareConsumablesBlock, self)._updateSlotWithItem(model, idx, slotItem)
        model.setIsInstalled(slotItem.isBuiltIn)
        model.setWithAttention(slotItem.name in cmp_helpers.NOT_AFFECTED_EQUIPMENTS)


class CompareBattleBoostersBlock(BattleBoostersBlock):

    def _updateSlotWithItem(self, model, idx, slotItem):
        super(CompareBattleBoostersBlock, self)._updateSlotWithItem(model, idx, slotItem)
        model.setIsInstalled(False)


class CompareCamouflageBlock(BaseBlock):

    def createBlock(self, viewModel):
        super(CompareCamouflageBlock, self).createBlock(viewModel)
        viewModel.setType(self._getSectionName())

    def updateBlock(self, viewModel):
        if not viewModel.getSlots():
            viewModel.setSlots(self._createSlots())
        else:
            isSet = cmp_helpers.getCmpConfiguratorMainView().isCamouflageSet()
            viewModel.getSlots()[0].setIsSelected(isSet)

    def _getSectionName(self):
        return TankSetupConstants.TOGGLE_CAMOUFLAGE

    def _getAmmunitionSlotModel(self):
        return CompareToggleAmmunitionSlot()

    def _getLayout(self):
        return None

    def _getInstalled(self):
        return None

    def _getSetupLayout(self):
        return None

    def _createSlots(self):
        array = Array()
        slot = self._createAmmunitionSlot(0)
        slot.setIsSelected(cmp_helpers.getCmpConfiguratorMainView().isCamouflageSet())
        slot.setIsLocked(self._vehicle.isOutfitLocked)
        array.addViewModel(slot)
        return array
