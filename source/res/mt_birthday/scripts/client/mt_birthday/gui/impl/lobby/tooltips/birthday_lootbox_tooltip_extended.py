# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: mt_birthday/scripts/client/mt_birthday/gui/impl/lobby/tooltips/birthday_lootbox_tooltip_extended.py
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.lobby.common.view_helpers import packBonusModelAndTooltipData
from gui_lootboxes.gui.bonuses.bonuses_packers import getLootBoxesBonusPacker
from gui.impl.pub import ViewImpl
from helpers import dependency
from shared_utils import first
from skeletons.gui.game_control import IGuiLootBoxesController
from gui_lootboxes.gui.impl.lobby.gui_lootboxes.tooltips.lootbox_tooltip import _getSortedBonuses
from mt_birthday.gui.impl.gen.view_models.views.lobby.tooltips.birthday_lootbox_tooltip_extended_model import BirthdayLootboxTooltipExtendedModel
from mt_birthday.gui.impl.gen.view_models.views.lobby.tooltips.birthday_lootbox_slot_model import BirthdayLootboxSlotModel

class BirthdayLootboxTooltipExtended(ViewImpl):
    __slots__ = ('__lootBox',)
    __guiLootBoxes = dependency.descriptor(IGuiLootBoxesController)

    def __init__(self, lootbox):
        settings = ViewSettings(R.views.mt_birthday.lobby.tooltips.BirthdayLootboxTooltipExtended())
        settings.model = BirthdayLootboxTooltipExtendedModel()
        super(BirthdayLootboxTooltipExtended, self).__init__(settings)
        self.__lootBox = lootbox

    def _finalize(self):
        self.__lootBox = None
        super(BirthdayLootboxTooltipExtended, self)._finalize()
        return

    def _onLoading(self, *args, **kwargs):
        super(BirthdayLootboxTooltipExtended, self)._onLoading()
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
                if bonus.getName() == 'vehicles':
                    vehicleBonuses.append(bonus)
                otherBonuses.append(bonus)

            lbSlot = BirthdayLootboxSlotModel()
            lbSlot.setProbability(slotProbability)
            self.__fillVehiclesData(vehicleBonuses, lbSlot)
            self.__packBonusesToModel(lbSlot, otherBonuses)
            lbSlots.append(lbSlot)

        for slot in lbSlots:
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
        packBonusModelAndTooltipData(_getSortedBonuses(bonuses, bonusesSortTags), slotModel.getBonuses(), packer=getLootBoxesBonusPacker())
