# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: gui_lootboxes/scripts/client/gui_lootboxes/gui/impl/lobby/gui_lootboxes/tooltips/lootbox_tooltip.py
import sys
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl import backport
from gui.impl.pub import ViewImpl
from gui_lootboxes.gui.impl.gen.view_models.views.lobby.gui_lootboxes.tooltips.lootbox_tooltip_model import LootboxTooltipModel
from gui_lootboxes.gui.bonuses.bonuses_sorter import sortBonuses
from gui_lootboxes.gui.bonuses.bonuses_packers import getLootboxesWithPossibleCompensationBonusPacker
from gui.impl.lobby.loot_box.loot_box_helper import aggregateSimilarBonuses
from gui.server_events.bonuses import VehiclesBonus
from gui.impl.lobby.common.view_helpers import packBonusModelAndTooltipData
from gui_lootboxes.gui.impl.gen.view_models.views.lobby.gui_lootboxes.tooltips.lootbox_tooltip_extended_model import LootboxTooltipExtendedModel
from gui_lootboxes.gui.impl.gen.view_models.views.lobby.gui_lootboxes.tooltips.complex_lootbox_slot_model import ComplexLootboxSlotModel
from skeletons.gui.game_control import IGuiLootBoxesController
from skeletons.gui.shared import IItemsCache
from helpers import dependency
from shared_utils import first

def _getSortedBonuses(bonuses, bonusesSortTags):
    result = [ b for b in bonuses if b.isShowInGUI() and not b.isCompensation() ]
    result = sortBonuses(result, bonusesSortTags)
    result = aggregateSimilarBonuses(result)
    return result


class LootboxTooltip(ViewImpl):
    __slots__ = ('__lootBox', '__showCount')

    def __init__(self, lootBox, showCount=False):
        settings = ViewSettings(R.views.gui_lootboxes.lobby.gui_lootboxes.tooltips.LootboxTooltip())
        settings.model = LootboxTooltipModel()
        super(LootboxTooltip, self).__init__(settings)
        self.__lootBox = lootBox
        self.__showCount = showCount

    @property
    def viewModel(self):
        return super(LootboxTooltip, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(LootboxTooltip, self)._onLoading()
        with self.viewModel.transaction() as vm:
            vm.setUserNameKey(self.__lootBox.getUserNameKey())
            vm.setDescriptionKey(self.__lootBox.getDesrciption())
            vm.setTier(self.__lootBox.getTier())
            if self.__showCount:
                vm.setCount(self.__lootBox.getInventoryCount())


class _ExtendedLootboxSlot(object):
    __slots__ = ('__id', '__bonuses', '__probability')

    def __init__(self, idx, probability, bonuses, bonusesSortTags):
        self.__id = idx
        self.__bonuses = _getSortedBonuses(bonuses, bonusesSortTags)
        self.__probability = probability

    def getFilledSlotModel(self):
        slotModel = ComplexLootboxSlotModel()
        slotModel.setProbability(self.__probability)
        bonusesModelArray = slotModel.getBonuses()
        packBonusModelAndTooltipData(self.__bonuses, bonusesModelArray, {}, getLootboxesWithPossibleCompensationBonusPacker())
        bonusesModelArray.invalidate()
        return slotModel

    def getProbability(self):
        return self.__probability

    def getId(self):
        return self.__id


class ExtendedLootboxTooltip(ViewImpl):
    __slots__ = ('__lootBox',)
    __guiLootBoxes = dependency.descriptor(IGuiLootBoxesController)
    __itemsCache = dependency.descriptor(IItemsCache)
    _START_INDEX_FOR_DEFAULT_BONUSES = 2

    def __init__(self, lootbox):
        settings = ViewSettings(R.views.gui_lootboxes.lobby.gui_lootboxes.tooltips.LootboxTooltipExtended())
        settings.model = LootboxTooltipExtendedModel()
        super(ExtendedLootboxTooltip, self).__init__(settings)
        self.__lootBox = lootbox

    @property
    def viewModel(self):
        return super(ExtendedLootboxTooltip, self).getViewModel()

    def _finalize(self):
        self.__lootBox = None
        super(ExtendedLootboxTooltip, self)._finalize()
        return

    def _onLoading(self, *args, **kwargs):
        super(ExtendedLootboxTooltip, self)._onLoading()
        with self.viewModel.transaction() as vm:
            slotsArrayModel = self.viewModel.getSlots()
            lootBoxSlots = self.__lootBox.getBonusSlots()
            self.__fillSlots(slotsArrayModel, lootBoxSlots)
            tokensRequester = self.__itemsCache.items.tokens
            openings = tokensRequester.getAttemptsAfterGuaranteedRewards(self.__lootBox)
            garant = self.__lootBox.getGuaranteedFrequency()
            rotationsToGarant = garant - openings if openings <= garant else garant
            vm.setRotationsToGuaranteedVehicle(rotationsToGarant)
            vm.setLootboxName(self.__lootBox.getUserNameKey())

    def __fillSlots(self, slotsArrayModel, lootBoxSlots):
        slotsArrayModel.clear()
        bonusesSortTags = self.__guiLootBoxes.getBonusesOrder(self.__lootBox.getCategory())
        lbSlots = []
        for idx, slot in lootBoxSlots.iteritems():
            bonuses = slot.get('bonuses', [])
            slotProbability = first(slot.get('probability', [0])) * 100
            if self.__isVehicleBonuses(bonuses):
                self.__fillSpecialVehicleSlot(bonuses, bonusesSortTags, slotProbability)
                continue
            lbSlot = _ExtendedLootboxSlot(idx=idx, probability=slotProbability, bonuses=bonuses, bonusesSortTags=bonusesSortTags)
            lbSlots.append(lbSlot)

        lbSlots = sorted(lbSlots, key=lambda x: x.getId())
        for idx, slot in enumerate(lbSlots, self._START_INDEX_FOR_DEFAULT_BONUSES):
            slotViewModel = slot.getFilledSlotModel()
            resource = R.strings.gui_lootboxes.lootBox.slot.description()
            slotViewModel.setDescription(backport.text(resource, idx=idx))
            slotsArrayModel.addViewModel(slotViewModel)

        slotsArrayModel.invalidate()

    def __fillSpecialVehicleSlot(self, bonuses, bonusesSortTags, probability):
        with self.viewModel.transaction() as vm:
            model = vm.vehicleSpecialSlot
            model.setProbability(probability)
            model.setGarant(self.__lootBox.getGuaranteedFrequency())
            vehNames = model.getVehicleNames()
            vehNames.clear()
            sortedBonuses = _getSortedBonuses(bonuses, bonusesSortTags)
            minLevel = sys.maxint
            maxLevel = -1
            for bonus in sortedBonuses:
                for item, _ in bonus.getVehicles():
                    minLevel = item.level if item.level <= minLevel else minLevel
                    maxLevel = item.level if item.level >= maxLevel else maxLevel
                    vehNames.addString(item.shortUserName)

            vehNames.invalidate()
            model.setMinLevel(minLevel)
            model.setMaxLevel(maxLevel)

    def __isVehicleBonuses(self, bonuses):
        return any((bonus.getName() == VehiclesBonus.VEHICLES_BONUS for bonus in bonuses))
