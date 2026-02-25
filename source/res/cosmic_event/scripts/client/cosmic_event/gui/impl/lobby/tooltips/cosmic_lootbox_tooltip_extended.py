# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: cosmic_event/scripts/client/cosmic_event/gui/impl/lobby/tooltips/cosmic_lootbox_tooltip_extended.py
from frameworks.wulf import ViewSettings
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.lobby.common.view_helpers import packBonusModelAndTooltipData
from gui.impl.pub import ViewImpl
from helpers import dependency
from shared_utils import first
from skeletons.gui.game_control import IGuiLootBoxesController
from skeletons.gui.shared import IItemsCache
from gui_lootboxes.gui.impl.lobby.gui_lootboxes.tooltips.lootbox_tooltip import _getSortedBonuses
from cosmic_event.gui.impl.gen.view_models.views.lobby.tooltips.cosmic_lootbox_tooltip_extended_model import CosmicLootboxTooltipExtendedModel
from cosmic_event.gui.impl.gen.view_models.views.lobby.tooltips.cosmic_lootbox_slot_model import CosmicLootboxSlotModel, SlotType

class CosmicExtendedLootboxTooltip(ViewImpl):
    __slots__ = ('__lootBox',)
    __guiLootBoxes = dependency.descriptor(IGuiLootBoxesController)
    __itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, lootbox):
        settings = ViewSettings(R.views.cosmic_event.lobby.tooltips.CosmicLootboxTooltipExtended())
        settings.model = CosmicLootboxTooltipExtendedModel()
        super(CosmicExtendedLootboxTooltip, self).__init__(settings)
        self.__lootBox = lootbox

    def _finalize(self):
        self.__lootBox = None
        super(CosmicExtendedLootboxTooltip, self)._finalize()
        return

    def _onLoading(self, *args, **kwargs):
        super(CosmicExtendedLootboxTooltip, self)._onLoading()
        with self.getViewModel().transaction() as vm:
            slotsArrayModel = vm.getSlots()
            lootBoxSlots = self.__lootBox.getBonusSlots()
            self.__fillSlots(slotsArrayModel, lootBoxSlots)
            vm.setLootboxName(self.__lootBox.getUserNameKey())

    def __fillSlots(self, slotsArrayModel, lootBoxSlots):
        slotsArrayModel.clear()
        lbSlots = []
        for slot in lootBoxSlots.itervalues():
            bonuses = slot.get('bonuses', [])
            slotProbability = first(slot.get('probability', [0])) * 100
            vehicleBonuses = []
            otherBonuses = []
            for bonus in bonuses:
                if hasattr(bonus, 'getVehicles'):
                    vehicleBonuses.append(bonus)
                otherBonuses.append(bonus)

            lbSlot = CosmicLootboxSlotModel()
            lbSlot.setProbability(slotProbability)
            self.__fillVehiclesData(vehicleBonuses, lbSlot)
            if self.__isLootBoxBonuses(otherBonuses):
                lbSlot.setSlotType(SlotType.LOOTBOX)
            self.__packBonusesToModel(lbSlot, otherBonuses)
            lbSlots.append(lbSlot)

        lbSlots = sorted(lbSlots, key=lambda x: -x.getProbability())
        for idx, slot in enumerate(lbSlots, 1):
            resource = R.strings.cosmicEvent.cosmicLootboxTooltipExtended.slot.description()
            slot.setDescription(backport.text(resource, idx=idx))
            slotsArrayModel.addViewModel(slot)

        slotsArrayModel.invalidate()

    def __fillVehiclesData(self, vehicleBonuses, slotModel):
        vehNames = slotModel.getVehicleNames()
        vehNames.clear()
        for bonus in vehicleBonuses:
            for item, _ in bonus.getVehicles():
                vehNames.addString(item.shortUserName)

        vehNames.invalidate()

    def __packBonusesToModel(self, slotModel, bonuses):
        bonusesSortTags = self.__guiLootBoxes.getBonusesOrder(self.__lootBox.getCategory())
        packBonusModelAndTooltipData(_getSortedBonuses(bonuses, bonusesSortTags), slotModel.getBonuses())

    def __isLootBoxBonuses(self, bonuses):
        return all((bonus.getName() == 'lootBoxToken' for bonus in bonuses))
