# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: gui_lootboxes/scripts/client/gui_lootboxes/gui/impl/lobby/gui_lootboxes/lootboxes_full_stats_view.py
import json
from functools import partial
import typing
from frameworks.wulf import ViewSettings, WindowFlags, WindowLayer
from gui.Scaleform.daapi.view.lobby.storage.storage_helpers import getVehicleCDForStyle
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.gen.view_models.constants.loot_box_bonus_group import LootBoxBonusGroup as BonusGroup
from gui.impl.gui_decorators import args2params
from gui.impl.lobby.common.view_wrappers import createBackportTooltipDecorator
from gui.impl.pub import ViewImpl
from gui.impl.pub.lobby_window import LobbyWindow
from gui.impl.wrappers.function_helpers import replaceNoneKwargsModel
from gui.server_events.bonuses import getNonQuestBonuses
from gui.shared.event_dispatcher import showVehiclePreview, showStyleProgressionPreview, showStylePreview, selectVehicleInHangar
from gui.shared.gui_items.loot_box import LootBox
from gui_lootboxes.gui.impl.gen.view_models.views.lobby.gui_lootboxes.lootboxes_full_stats_view_model import LootboxesFullStatsViewModel
from gui_lootboxes.gui.impl.lobby.gui_lootboxes import RegisteredTooltips
from gui_lootboxes.gui.impl.lobby.gui_lootboxes.sound import LOOT_BOXES_OVERLAY_SOUND_SPACE
from gui_lootboxes.gui.impl.lobby.gui_lootboxes.tooltips.deadline_tooltip import DeadlineTooltip
from gui_lootboxes.gui.shared.event_dispatcher import backToFullStatisticView
from gui_lootboxes.gui.shared.gui_helpers import getLootBoxViewModel, fillStatisticModel
from gui_lootboxes.skeletons.statistic_lootbox_controller import IStatisticLootBoxController
from helpers import dependency
from skeletons.gui.game_control import IGuiLootBoxesController
from skeletons.gui.impl import IGuiLoader
from skeletons.gui.shared import IItemsCache
from uilogging.lootboxes import LootboxStorageLogger
if typing.TYPE_CHECKING:
    import Event
    from typing import Dict, List

class LootBoxesFullStatsView(ViewImpl):
    __slots__ = ('__tooltipData', '__statistic', '__lootbox', '__selectedLootBoxes', '__category', '__uiLogger')
    __guiLoader = dependency.descriptor(IGuiLoader)
    __guiLootBoxes = dependency.descriptor(IGuiLootBoxesController)
    __itemsCache = dependency.descriptor(IItemsCache)
    __statisticCtrl = dependency.descriptor(IStatisticLootBoxController)
    _COMMON_SOUND_SPACE = LOOT_BOXES_OVERLAY_SOUND_SPACE

    def __init__(self, statistic, category, lootbox, layoutID, selectedLootBoxes):
        settings = ViewSettings(layoutID)
        settings.model = LootboxesFullStatsViewModel()
        self.__tooltipData = {}
        self.__statistic = statistic
        self.__lootbox = lootbox
        self.__category = category
        self.__selectedLootBoxes = selectedLootBoxes
        self.__uiLogger = LootboxStorageLogger()
        super(LootBoxesFullStatsView, self).__init__(settings)

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.gui_lootboxes.lobby.gui_lootboxes.tooltips.DeadlineTooltip():
            return DeadlineTooltip()
        if contentID in RegisteredTooltips.REGISTERED_SIMPLE_TOOLTIPS:
            view = RegisteredTooltips.REGISTERED_SIMPLE_TOOLTIPS.get(contentID)
            return view()
        if contentID in RegisteredTooltips.REGISTERED_TOOLTIPS:
            view = RegisteredTooltips.REGISTERED_TOOLTIPS.get(contentID)
            return view(event)
        return super(LootBoxesFullStatsView, self).createToolTipContent(event, contentID)

    @createBackportTooltipDecorator()
    def createToolTip(self, event):
        return super(LootBoxesFullStatsView, self).createToolTip(event)

    def getTooltipData(self, event):
        index = event.getArgument('tooltipId')
        return self.__tooltipData.get(index, None)

    @property
    def viewModel(self):
        return super(LootBoxesFullStatsView, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        with self.viewModel.transaction() as model:
            self.__fillLootBoxesModel(model=model)
            self.__fillRewardsModels(model=model)
            self.__fillSelectedLootBoxesModel(model=model)
            if self.__category:
                model.setCategory(self.__category)
        super(LootBoxesFullStatsView, self)._onLoading(*args, **kwargs)

    def _onLoaded(self, *args, **kwargs):
        if not self.__category:
            self.__uiLogger.logFullStatisticClick(self.__lootbox, self.__isHasPreviewItems())
        super(LootBoxesFullStatsView, self)._onLoaded(*args, **kwargs)

    @replaceNoneKwargsModel
    def __fillLootBoxesModel(self, model=None):
        lbArray = model.getLootboxes()
        lbArray.clear()
        lootBoxes = sorted(self.__guiLootBoxes.getGuiLootBoxes())
        lootBoxesInfo = self.__statisticCtrl.getLootboxesExpireInfo()
        for lootBox in lootBoxes:
            if lootBox.getID() in lootBoxesInfo:
                attemptsAfterGuaranteed = self.__itemsCache.items.tokens.getAttemptsAfterGuaranteedRewards(lootBox)
                lbArray.addViewModel(getLootBoxViewModel(lootBox, attemptsAfterGuaranteed))

        lbArray.invalidate()

    def __fillSelectedLootBoxesModel(self, model=None):
        selectedLootBoxes = model.getSelectedLootBoxes()
        selectedLootBoxes.clear()
        if self.__statistic:
            for lootBoxID in self.__selectedLootBoxes:
                selectedLootBoxes.addNumber(lootBoxID)

        selectedLootBoxes.invalidate()

    @replaceNoneKwargsModel
    def __fillRewardsModels(self, model=None):
        rewardsList = model.getAllRewards()
        rewardsList.clear()
        rewards = []
        for statType, statValue in self.__statistic.items():
            rewards.extend(getNonQuestBonuses(statType, statValue))

        fillStatisticModel(rewards, rewardsList, self.__lootbox, self.__tooltipData)

    def _getEvents(self):
        return ((self.viewModel.onClose, self.__onClose),
         (self.viewModel.onVehiclePreview, self.__onVehiclePreview),
         (self.viewModel.onStylePreview, self.__onStylePreview),
         (self.viewModel.onSelectedLootBoxes, self.__onSelectedLootBoxes))

    def __onClose(self):
        self.destroyWindow()

    def __onSelectedLootBoxes(self, args):
        with self.viewModel.transaction() as model:
            self.__selectedLootBoxes = json.loads(args.get(self.viewModel.SELECT_LOOTBOXES_ARG_NAME))
            self.__statistic = self.__statisticCtrl.getMergeStatByLootboxIDs(self.__selectedLootBoxes)
            self.__fillSelectedLootBoxesModel(model=model)
            self.__fillRewardsModels(model=model)

    @args2params(int)
    def __onStylePreview(self, styleCD):
        if styleCD == 0:
            return
        style = self.__itemsCache.items.getItemByCD(styleCD)
        vehicleCD = getVehicleCDForStyle(style, itemsCache=self.__itemsCache)
        self.destroyWindow()
        self.__closeStorageView()
        if style.isProgressive:
            showStyleProgressionPreview(vehicleCD, style, style.getDescription(), backCallback=partial(backToFullStatisticView, self.__statistic, BonusGroup.VEHICLECUSTOMIZATIONS, self.__lootbox, self.__selectedLootBoxes), backBtnDescrLabel=backport.text(R.strings.gui_lootboxes.window.lootBoxes.preview()))
        else:
            showStylePreview(vehicleCD, style, style.getDescription(), backCallback=partial(backToFullStatisticView, self.__statistic, BonusGroup.VEHICLECUSTOMIZATIONS, self.__lootbox, self.__selectedLootBoxes), backBtnDescrLabel=backport.text(R.strings.gui_lootboxes.window.lootBoxes.preview()))

    @args2params(int)
    def __onVehiclePreview(self, vehicleCD):
        vehicle = self.__itemsCache.items.getItemByCD(vehicleCD)
        self.destroyWindow()
        self.__closeStorageView()
        if vehicle.isInInventory:
            selectVehicleInHangar(vehicle.intCD)
        else:
            showVehiclePreview(vehicle.compactDescr, backBtnLabel=backport.text(R.strings.gui_lootboxes.window.lootBoxes.preview()), previewBackCb=partial(backToFullStatisticView, self.__statistic, BonusGroup.VEHICLE, self.__lootbox, self.__selectedLootBoxes))

    def __closeStorageView(self):
        view = self.__guiLoader.windowsManager.getViewByLayoutID(R.views.gui_lootboxes.lobby.gui_lootboxes.StorageView())
        if view:
            view.destroyWindow()

    def __isHasPreviewItems(self):
        if 'vehicles' in self.__statistic:
            return True
        return any((item['custType'] == 'style' for item in self.__statistic['customizations'])) if 'customizations' in self.__statistic else False


class LootboxFullStatsWindow(LobbyWindow):

    def __init__(self, statistic, category, lootbox, selectedLootBoxes, parent=None):
        super(LootboxFullStatsWindow, self).__init__(WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, content=LootBoxesFullStatsView(statistic=statistic, category=category, lootbox=lootbox, layoutID=R.views.gui_lootboxes.lobby.gui_lootboxes.LootboxesFullStatsView(), selectedLootBoxes=selectedLootBoxes), layer=WindowLayer.OVERLAY, parent=parent)
