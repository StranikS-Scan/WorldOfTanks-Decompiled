# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: gui_lootboxes/scripts/client/gui_lootboxes/gui/impl/lobby/gui_lootboxes/bonus_probabilities_view.py
from frameworks.wulf import ViewSettings, WindowFlags, WindowLayer, Array
from frameworks.wulf.view.array import fillStringsArray, fillFloatsArray
from gui.impl.gen import R
from gui.impl.lobby.collection.tooltips.collection_item_tooltip_view import CollectionItemTooltipView
from gui.impl.lobby.common.view_helpers import packBonusModelAndTooltipData
from gui.impl.lobby.common.view_wrappers import createBackportTooltipDecorator
from gui.impl.lobby.loot_box.loot_box_helper import aggregateSimilarBonuses, isAllVehiclesObtainedInSlot
from gui.impl.pub import ViewImpl, WindowImpl
from gui.impl.wrappers.function_helpers import replaceNoneKwargsModel
from helpers import dependency
from shared_utils import findFirst
from skeletons.gui.game_control import IGuiLootBoxesController
from gui_lootboxes.gui.bonuses.bonuses_packers import getLootboxesWithPossibleCompensationBonusPacker
from gui_lootboxes.gui.bonuses.bonuses_sorter import sortBonuses
from gui_lootboxes.gui.impl.gen.view_models.views.lobby.gui_lootboxes.bonus_probabilities_view_model import BonusProbabilitiesViewModel
from gui_lootboxes.gui.impl.gen.view_models.views.lobby.gui_lootboxes.slot_view_model import SlotViewModel
from gui_lootboxes.gui.impl.lobby.gui_lootboxes.sound import LOOT_BOXES_OVERLAY_SOUND_SPACE
from gui_lootboxes.gui.impl.lobby.gui_lootboxes.gui_helpers import detectBonusType
from gui_lootboxes.gui.impl.lobby.gui_lootboxes.tooltips.compensation_tooltip import LootBoxesCompensationTooltip
from gui_lootboxes.gui.impl.gen.view_models.views.lobby.gui_lootboxes.lb_bonus_type_model import BonusType
_VEHICLES_BONUS_NAME = 'vehicles'
_SHOW_VEHICLE_ICONS = 'showVehicleIcons'
SLOT_BONUSES_PROCESSORS = []

class LootBoxSlot(object):
    __slots__ = ('__id', '__probabilities', '__bonuses', '__bonusType', '__slotSettings')

    def __init__(self, id, probabilities, bonuses, bonusesSortTags, slotSettings):
        self.__id = id
        self.__probabilities = [ round(probability * 100, 2) for probability in probabilities ]
        self.__bonusType = detectBonusType(bonuses)
        self.__slotSettings = slotSettings
        self.__bonuses = [ b for b in bonuses if self.__isValidBonus(b) ]
        self.__bonuses = sortBonuses(self.__bonuses, bonusesSortTags)
        self.__bonuses = aggregateSimilarBonuses(self.__bonuses)
        for processor in SLOT_BONUSES_PROCESSORS:
            self.__bonuses = processor(self.__bonuses)

    def getProbabilities(self):
        return self.__probabilities

    def getBonusType(self):
        return self.__bonusType

    def getViewData(self, tooltipData):
        slotModel = SlotViewModel()
        slotModel.setId(self.__id)
        fillFloatsArray(self.__probabilities, slotModel.getProbabilities())
        slotModel.setBonusType(BonusType(self.__bonusType))
        fillStringsArray(self.__slotSettings, slotModel.getExtraSlotSettings())
        bonusesModelArray = slotModel.getBonuses()
        packBonusModelAndTooltipData(self.__bonuses, bonusesModelArray, tooltipData, getLootboxesWithPossibleCompensationBonusPacker())
        bonusesModelArray.invalidate()
        return slotModel

    def __isValidBonus(self, bonus):
        return bonus.isShowInGUI() and (self.__bonusType in (BonusType.VEHICLE, BonusType.RENTEDVEHICLE) and bonus.getName() == _VEHICLES_BONUS_NAME or self.__bonusType == BonusType.DEFAULT or _SHOW_VEHICLE_ICONS in self.__slotSettings)


class BonusProbabilitiesView(ViewImpl):
    __slots__ = ('__lootBox', '__tooltipData')
    __guiLootBoxes = dependency.descriptor(IGuiLootBoxesController)
    _COMMON_SOUND_SPACE = LOOT_BOXES_OVERLAY_SOUND_SPACE

    def __init__(self, layoutID, lootBox):
        settings = ViewSettings(layoutID)
        settings.model = BonusProbabilitiesViewModel()
        super(BonusProbabilitiesView, self).__init__(settings)
        self.__lootBox = lootBox
        self.__tooltipData = {}

    @property
    def viewModel(self):
        return super(BonusProbabilitiesView, self).getViewModel()

    @createBackportTooltipDecorator()
    def createToolTip(self, event):
        return super(BonusProbabilitiesView, self).createToolTip(event)

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.lobby.collection.tooltips.CollectionItemTooltipView():
            tooltipData = self.getTooltipData(event)
            if tooltipData:
                return CollectionItemTooltipView(*tooltipData.specialArgs)
        elif contentID == R.views.gui_lootboxes.lobby.gui_lootboxes.tooltips.CompensationTooltip():
            tooltipData = self.getTooltipData(event)
            if tooltipData:
                return LootBoxesCompensationTooltip(*tooltipData.specialArgs)
        return super(BonusProbabilitiesView, self).createToolTipContent(event, contentID)

    def getTooltipData(self, event):
        tooltipID = event.getArgument('tooltipId')
        return self.__tooltipData.get(tooltipID, None)

    def _onLoading(self, *args, **kwargs):
        super(BonusProbabilitiesView, self)._onLoading(*args, **kwargs)
        with self.viewModel.transaction() as model:
            self.__update(model=model)

    def _getEvents(self):
        return ((self.__guiLootBoxes.onBoxInfoUpdated, self.__update),)

    @replaceNoneKwargsModel
    def __update(self, model=None):
        model.setLootboxName(self.__lootBox.getUserNameKey())
        model.setLootboxTier(self.__lootBox.getTier())
        model.setHasLootLists(self.__lootBox.hasLootLists())
        slots = self.__lootBox.getBonusSlots()
        self.__updateLootLists()
        self.__updateSlots(self.viewModel.getSlots(), slots)

    @replaceNoneKwargsModel
    def __updateLootLists(self, model=None):
        if not self.__lootBox.hasLootLists():
            return
        rotationStage = self.__getRotationStage()
        lootLists = self.__lootBox.getLootLists()
        model.setRotationStage(rotationStage)
        lootListsModel = model.getLootLists()
        lootListsModel.clear()
        for lootList in lootLists:
            slotsInLootListModel = Array()
            self.__updateSlots(slotsInLootListModel, lootList)
            lootListsModel.addArray(slotsInLootListModel)

        lootListsModel.invalidate()

    def __updateSlots(self, slotsArrayModel, slots):
        slotsArrayModel.clear()
        lbSlots = []
        for idx, slot in slots.iteritems():
            bonusesSortTags = self.__guiLootBoxes.getBonusesOrder(self.__lootBox.getCategory())
            lbSlot = LootBoxSlot(id=idx, probabilities=slot.get('probability', [[0]])[0], bonuses=slot.get('bonuses', []), bonusesSortTags=bonusesSortTags, slotSettings=slot.get('slotSettings', []))
            lbSlots.append(lbSlot)

        lbSlots = sorted(lbSlots, key=lambda x: (x.getBonusType().value, -x.getProbabilities()[0]))
        for slot in lbSlots:
            slotViewModel = slot.getViewData(self.__tooltipData)
            slotsArrayModel.addViewModel(slotViewModel)

        for idx, data in self.__tooltipData.items():
            self.__tooltipData.update({idx: data})

        slotsArrayModel.invalidate()

    def __getRotationStage(self):
        if not self.__lootBox.hasLootLists():
            return 0
        else:
            rotationStage = self.__lootBox.getRotationStage()
            lootLists = self.__lootBox.getLootLists()
            firstSlot = findFirst(lambda x: x is not None, lootLists[rotationStage])
            if firstSlot is not None:
                rotationStage += isAllVehiclesObtainedInSlot(lootLists[rotationStage][firstSlot])
            return rotationStage


class BonusProbabilitiesWindow(WindowImpl):
    __slots__ = ()

    def __init__(self, lootBox, parent=None):
        super(BonusProbabilitiesWindow, self).__init__(WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, content=BonusProbabilitiesView(R.views.gui_lootboxes.lobby.gui_lootboxes.BonusProbabilitiesView(), lootBox), layer=WindowLayer.OVERLAY, parent=parent)
