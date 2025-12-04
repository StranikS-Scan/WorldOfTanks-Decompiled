# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: gui_lootboxes/scripts/client/gui_lootboxes/gui/impl/lobby/gui_lootboxes/bonus_probabilities_view.py
from functools import partial
from account_helpers.settings_core.settings_constants import OnceOnlyHints
from CurrentVehicle import g_currentVehicle
from frameworks.wulf import ViewSettings, WindowFlags, WindowLayer, Array
from frameworks.wulf.view.array import fillFloatsArray, fillIntsArray
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.impl.gen import R
from gui.impl.lobby.collection.tooltips.collection_item_tooltip_view import CollectionItemTooltipView
from gui.impl.lobby.common.view_helpers import packBonusModelAndTooltipData
from gui.impl.lobby.common.view_wrappers import createBackportTooltipDecorator
from gui.impl.lobby.loot_box.loot_box_helper import aggregateSimilarBonuses
from gui.impl.pub import ViewImpl, WindowImpl
from gui.impl.wrappers.function_helpers import replaceNoneKwargsModel
from gui.shared.event_dispatcher import showVehiclePreview, showHangar
from helpers import dependency
from new_year.skeletons.new_year import INewYearController
from skeletons.gui.impl import IGuiLoader
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.game_control import IGuiLootBoxesController
from gui_lootboxes.gui.impl.lobby.gui_lootboxes import RegisteredTooltips
from gui_lootboxes.gui.bonuses.bonuses_packers import getLootboxesWithPossibleCompensationBonusPacker
from gui_lootboxes.gui.bonuses.bonuses_sorter import sortBonuses
from gui_lootboxes.gui.shared.event_dispatcher import showBonusProbabilitiesWindow, showStorageView
from gui_lootboxes.gui.impl.gen.view_models.views.lobby.gui_lootboxes.bonus_probabilities_view_model import BonusProbabilitiesViewModel
from gui_lootboxes.gui.impl.gen.view_models.views.lobby.gui_lootboxes.slot_view_model import SlotViewModel
from gui_lootboxes.gui.impl.lobby.gui_lootboxes.sound import LOOT_BOXES_OVERLAY_SOUND_SPACE
from gui_lootboxes.gui.impl.lobby.gui_lootboxes.gui_helpers import detectBonusType
from gui_lootboxes.gui.impl.lobby.gui_lootboxes.tooltips.compensation_tooltip import LootBoxesCompensationTooltip
from gui_lootboxes.gui.impl.lobby.gui_lootboxes.tooltips.lootbox_tooltip import LootboxTooltip
from gui_lootboxes.gui.impl.lobby.gui_lootboxes.tooltips.lootbox_key_tooltip import LootboxKeyTooltip
from gui_lootboxes.gui.impl.lobby.gui_lootboxes.tooltips.probability_guaranteed_reward_tooltip import ProbabilityGuaranteedRewardTooltip
from gui_lootboxes.gui.impl.lobby.gui_lootboxes.tooltips.probability_stage_buttons_tooltip import ProbabilityStageButtonsTooltip
from gui_lootboxes.gui.impl.gen.view_models.views.lobby.gui_lootboxes.lb_bonus_type_model import BonusType
from skeletons.gui.shared import IItemsCache
from uilogging.lootboxes import LootboxProbabilityViewLogger
SLOT_BONUSES_PROCESSORS = []

class LootBoxSlot(object):
    __slots__ = ('__id', '__probabilities', '__bonuses', '__bonusType')

    def __init__(self, id, probabilities, bonuses, bonusesSortTags):
        self.__id = id
        self.__probabilities = [ round(probability * 100, 2) for probability in probabilities ]
        self.__bonusType = detectBonusType(bonuses)
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
        bonusesModelArray = slotModel.getBonuses()
        packBonusModelAndTooltipData(self.__bonuses, bonusesModelArray, tooltipData, getLootboxesWithPossibleCompensationBonusPacker())
        bonusesModelArray.invalidate()
        return slotModel

    def __isValidBonus(self, bonus):
        return bonus.isShowInGUI()


class BonusProbabilitiesView(ViewImpl):
    __slots__ = ('__lootBox', '__tooltipData', '__uiLogger')
    __guiLoader = dependency.descriptor(IGuiLoader)
    __guiLootBoxes = dependency.descriptor(IGuiLootBoxesController)
    __itemsCache = dependency.descriptor(IItemsCache)
    __settingsCore = dependency.descriptor(ISettingsCore)
    __nyCtl = dependency.descriptor(INewYearController)
    _COMMON_SOUND_SPACE = LOOT_BOXES_OVERLAY_SOUND_SPACE

    def __init__(self, layoutID, lootBox):
        settings = ViewSettings(layoutID)
        settings.model = BonusProbabilitiesViewModel()
        super(BonusProbabilitiesView, self).__init__(settings)
        self.__lootBox = lootBox
        self.__tooltipData = {}
        self.__uiLogger = LootboxProbabilityViewLogger()

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
        else:
            if contentID == R.views.gui_lootboxes.lobby.gui_lootboxes.tooltips.ProbabilityStageButtonsTooltip():
                return ProbabilityStageButtonsTooltip()
            if contentID == R.views.gui_lootboxes.lobby.gui_lootboxes.tooltips.ProbabilityGuaranteedRewardTooltip():
                return ProbabilityGuaranteedRewardTooltip(self.__lootBox)
        if contentID == R.views.gui_lootboxes.lobby.gui_lootboxes.tooltips.LootboxTooltip():
            tooltipData = self.getTooltipData(event)
            lootBoxID = tooltipData.get('lootBoxID')
            lootBox = self.__itemsCache.items.tokens.getLootBoxByID(int(lootBoxID))
            return LootboxTooltip(lootBox)
        if contentID == R.views.gui_lootboxes.lobby.gui_lootboxes.tooltips.LootboxKeyTooltip():
            tooltipData = self.getTooltipData(event)
            lootBoxKeyID = tooltipData.get('lootBoxKeyID')
            lootBoxKey = self.__guiLootBoxes.getKeyByID(lootBoxKeyID)
            return LootboxKeyTooltip(lootBoxKey)
        if contentID in RegisteredTooltips.REGISTERED_SIMPLE_TOOLTIPS:
            view = RegisteredTooltips.REGISTERED_SIMPLE_TOOLTIPS.get(contentID)
            return view()
        if contentID in RegisteredTooltips.REGISTERED_TOOLTIPS:
            view = RegisteredTooltips.REGISTERED_TOOLTIPS.get(contentID)
            return view(event)
        return super(BonusProbabilitiesView, self).createToolTipContent(event, contentID)

    def getTooltipData(self, event):
        tooltipID = event.getArgument('tooltipId')
        return self.__tooltipData.get(tooltipID, None)

    def _onLoading(self, *args, **kwargs):
        super(BonusProbabilitiesView, self)._onLoading(*args, **kwargs)
        with self.viewModel.transaction() as model:
            self.__update(model=model)
        self.__uiLogger.startViewAction()

    def _finalize(self):
        serverSettings = self.__settingsCore.serverSettings
        if not serverSettings.getOnceOnlyHintsSetting(OnceOnlyHints.LOOT_PROBABILITY_HINT):
            serverSettings.setOnceOnlyHintsSettings({OnceOnlyHints.LOOT_PROBABILITY_HINT: True})
        super(BonusProbabilitiesView, self)._finalize()

    def _getEvents(self):
        return ((self.__guiLootBoxes.onBoxInfoUpdated, self.__update), (self.viewModel.onClose, self._onClose), (self.viewModel.onPreview, self._onPreview))

    def _onClose(self, args):
        self.__uiLogger.stopViewAction(args.get('closeMethod', None))
        self.destroyWindow()
        return

    def _onPreview(self, args):
        vehIntCD = int(args.get('vehIntCD'))
        veh = self.__itemsCache.items.getItemByCD(vehIntCD)
        self.__closeStorageView()
        self.destroyWindow()
        if veh.invID >= 0:
            g_currentVehicle.selectVehicle(veh.invID)
            showHangar()
        else:
            showVehiclePreview(veh.compactDescr, previewAlias=VIEW_ALIAS.STAT_TRACK_VEHICLE_PREVIEW, previewBackCb=partial(BonusProbabilitiesView._backToBonusPropabilitiesView, self.__lootBox))

    @staticmethod
    def _backToBonusPropabilitiesView(lootbox):
        showHangar()
        showStorageView()
        showBonusProbabilitiesWindow(lootbox)

    def __closeStorageView(self):
        view = self.__guiLoader.windowsManager.getViewByLayoutID(R.views.gui_lootboxes.lobby.gui_lootboxes.StorageView())
        if view:
            view.destroy()

    @replaceNoneKwargsModel
    def __update(self, model=None):
        model.setLootboxName(self.__lootBox.getUserNameKey())
        model.setLootboxID(self.__lootBox.getID())
        model.setLootboxTier(self.__lootBox.getTier())
        model.setHasLootLists(self.__lootBox.hasLootLists())
        fillIntsArray(self.__lootBox.getGuaranteedFrequency(multiple=True), model.getGuaranteedFrequencies())
        slots = self.__lootBox.getBonusSlots()
        self.__updateLootLists()
        self.__updateSlots(self.viewModel.getSlots(), slots)

    @replaceNoneKwargsModel
    def __updateLootLists(self, model=None):
        if not self.__lootBox.hasLootLists():
            return
        rotationStage = self.__lootBox.getCurrentRotationStage()
        lootLists = self.__lootBox.getLootLists()
        model.setRotationStage(rotationStage - 1)
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
            lbSlot = LootBoxSlot(id=idx, probabilities=slot.get('probability', [0]), bonuses=slot.get('bonuses', []), bonusesSortTags=bonusesSortTags)
            lbSlots.append(lbSlot)

        if not self.__nyCtl.isLootboxTankType(self.__lootBox.getType()):
            lbSlots = sorted(lbSlots, key=lambda x: (x.getBonusType().value, -x.getProbabilities()[0]))
        for slot in lbSlots:
            slotViewModel = slot.getViewData(self.__tooltipData)
            slotsArrayModel.addViewModel(slotViewModel)

        for idx, data in self.__tooltipData.items():
            self.__tooltipData.update({idx: data})

        slotsArrayModel.invalidate()


class BonusProbabilitiesWindow(WindowImpl):
    __slots__ = ()

    def __init__(self, lootBox, parent=None):
        super(BonusProbabilitiesWindow, self).__init__(WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, content=BonusProbabilitiesView(R.views.gui_lootboxes.lobby.gui_lootboxes.BonusProbabilitiesView(), lootBox), layer=WindowLayer.OVERLAY, parent=parent)
