# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: gui_lootboxes/scripts/client/gui_lootboxes/gui/impl/lobby/gui_lootboxes/bonus_probabilities_view.py
from frameworks.wulf import ViewSettings, WindowFlags, WindowLayer
from gui.impl.gen import R
from gui.impl.lobby.collection.tooltips.collection_item_tooltip_view import CollectionItemTooltipView
from gui.impl.lobby.common.view_helpers import packBonusModelAndTooltipData
from gui.impl.lobby.common.view_wrappers import createBackportTooltipDecorator
from gui.impl.lobby.loot_box.loot_box_helper import aggregateSimilarBonuses
from gui.impl.pub import ViewImpl, WindowImpl
from gui.impl.wrappers.function_helpers import replaceNoneKwargsModel
from helpers import dependency
from skeletons.gui.game_control import IGuiLootBoxesController
from gui_lootboxes.gui.bonuses.bonuses_packers import getLootBoxesBonusPacker
from gui_lootboxes.gui.bonuses.bonuses_sorter import sortBonuses
from gui_lootboxes.gui.impl.gen.view_models.views.lobby.gui_lootboxes.bonus_probabilities_view_model import BonusProbabilitiesViewModel
from gui_lootboxes.gui.impl.gen.view_models.views.lobby.gui_lootboxes.slot_view_model import SlotViewModel
from gui_lootboxes.gui.impl.lobby.gui_lootboxes.sound import LOOT_BOXES_OVERLAY_SOUND_SPACE
from gui_lootboxes.gui.impl.lobby.gui_lootboxes.gui_helpers import detectBonusType
from gui_lootboxes.gui.impl.gen.view_models.views.lobby.gui_lootboxes.lb_bonus_type_model import BonusType
_VEHICLES_BONUS_NAME = 'vehicles'

class LootBoxSlot(object):
    __slots__ = ('__probability', '__bonuses', '__bonusType')

    def __init__(self, probability, bonuses, bonusesSortTags):
        self.__probability = round(probability * 100, 2)
        self.__bonusType = detectBonusType(bonuses)
        self.__bonuses = [ b for b in bonuses if self.__isValidBonus(b) ]
        self.__bonuses = sortBonuses(self.__bonuses, bonusesSortTags)
        self.__bonuses = aggregateSimilarBonuses(self.__bonuses)

    def getProbability(self):
        return self.__probability

    def getBonusType(self):
        return self.__bonusType

    def getViewData(self):
        slotModel = SlotViewModel()
        slotModel.setProbability(self.__probability)
        slotModel.setBonusType(BonusType(self.__bonusType))
        bonusesModelArray = slotModel.getBonuses()
        tooltipData = {}
        packBonusModelAndTooltipData(self.__bonuses, bonusesModelArray, tooltipData, getLootBoxesBonusPacker())
        bonusesModelArray.invalidate()
        return (slotModel, tooltipData)

    def __isValidBonus(self, bonus):
        return bonus.isShowInGUI() and (self.__bonusType in (BonusType.VEHICLE, BonusType.RENTEDVEHICLE) and bonus.getName() == _VEHICLES_BONUS_NAME or self.__bonusType == BonusType.DEFAULT)


class BonusProbabilitiesView(ViewImpl):
    __slots__ = ('__lootBox', '__slotsTooltipData')
    __guiLootBoxes = dependency.descriptor(IGuiLootBoxesController)
    _COMMON_SOUND_SPACE = LOOT_BOXES_OVERLAY_SOUND_SPACE

    def __init__(self, layoutID, lootBox):
        settings = ViewSettings(layoutID)
        settings.model = BonusProbabilitiesViewModel()
        super(BonusProbabilitiesView, self).__init__(settings)
        self.__lootBox = lootBox
        self.__slotsTooltipData = {}

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
        return super(BonusProbabilitiesView, self).createToolTipContent(event, contentID)

    def getTooltipData(self, event):
        slotID = event.getArgument('slotId')
        tooltipID = event.getArgument('tooltipId')
        return self.__slotsTooltipData.get(slotID, {}).get(tooltipID, None)

    def _onLoading(self, *args, **kwargs):
        super(BonusProbabilitiesView, self)._onLoading(*args, **kwargs)
        slots = self.__lootBox.getBonusSlots()
        with self.viewModel.transaction() as model:
            model.setLootboxName(self.__lootBox.getUserNameKey())
            model.setLootboxTier(self.__lootBox.getTier())
            self.__updateSlots(slots=slots, model=model)

    def _getEvents(self):
        return ((self.__guiLootBoxes.onBoxInfoUpdated, self.__onBoxInfoUpdated),)

    def __onBoxInfoUpdated(self):
        slots = self.__lootBox.getBonusSlots()
        self.__updateSlots(slots=slots)

    @replaceNoneKwargsModel
    def __updateSlots(self, slots, model=None):
        slotsModel = model.getSlots()
        slotsModel.clear()
        lbSlots = []
        for slot in slots.values():
            bonusesSortTags = self.__guiLootBoxes.getBonusesOrder(self.__lootBox.getCategory())
            lbSlot = LootBoxSlot(slot.get('probability', [[0]])[0][0], slot.get('bonuses', []), bonusesSortTags)
            lbSlots.append(lbSlot)

        lbSlots = sorted(lbSlots, key=lambda x: (x.getBonusType().value, -x.getProbability()))
        for slotIndex, slot in enumerate(lbSlots):
            slotViewModel, tooltipData = slot.getViewData()
            self.__slotsTooltipData.update({slotIndex: tooltipData})
            slotsModel.addViewModel(slotViewModel)

        slotsModel.invalidate()


class BonusProbabilitiesWindow(WindowImpl):
    __slots__ = ()

    def __init__(self, lootBox, parent=None):
        super(BonusProbabilitiesWindow, self).__init__(WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, content=BonusProbabilitiesView(R.views.gui_lootboxes.lobby.gui_lootboxes.BonusProbabilitiesView(), lootBox), layer=WindowLayer.OVERLAY, parent=parent)
