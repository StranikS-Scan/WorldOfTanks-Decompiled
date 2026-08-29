# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/lootbox_system/base/info_page.py
from __future__ import absolute_import
import typing
from enum import Enum
from account_helpers.AccountSettings import LOOT_BOXES_SELECTED_BOX
from frameworks.wulf import WindowFlags
from frameworks.wulf.view.array import fillIntsArray
from gui.Scaleform.Waiting import Waiting
from gui.impl.gen import R
from gui.impl.pub.view_component import ViewComponent
from gui.impl.gen.view_models.views.lobby.lootbox_system.box_model import BoxModel
from gui.impl.gen.view_models.views.lobby.lootbox_system.info_page_model import InfoPageModel
from gui.impl.gen.view_models.views.lobby.lootbox_system.slot_model import SlotModel
from gui.impl.pub import WindowImpl
from gui.impl.wrappers.function_helpers import replaceNoneKwargsModel
from gui.lootbox_system.base.bonuses_packers import packBonusModelAndTooltipData
from gui.lootbox_system.base.common import ViewID, Views
from gui.lootbox_system.base.decorators import createBackportTooltipDecorator, createTooltipContentDecorator
from gui.lootbox_system.base.sound import playInfopageEnterSound, playInfopageExitSound
from gui.lootbox_system.base.utils import getInfoPageSettings, isCountryForShowingExternalLootList, isShopVisible, openExternalLootList
from gui.lootbox_system.base.views_loaders import showItemPreview
from helpers import dependency
from helpers.time_utils import getServerUTCTime
from shared_utils import first
from skeletons.gui.game_control import ILootBoxSystemController
if typing.TYPE_CHECKING:
    from gui.shared.gui_items.loot_box import LootBox

class _InfoPageSetting(str, Enum):
    VIDEO = 'isVideoVisible'


class InfoPage(ViewComponent):
    __lootBoxes = dependency.descriptor(ILootBoxSystemController)
    __baseWindowID = None

    def __init__(self, ctx=None):
        self.__category = ctx.get('category')
        self.__eventName = ctx.get('eventName')
        self.__savedCategory = self.__lootBoxes.getSetting(self.__eventName, LOOT_BOXES_SELECTED_BOX)
        self.__tooltipData = {}
        super(InfoPage, self).__init__(R.views.mono.lootbox.info_page(), InfoPageModel)

    @property
    def viewModel(self):
        return super(InfoPage, self).getViewModel()

    @createBackportTooltipDecorator()
    def createToolTip(self, event):
        return super(InfoPage, self).createToolTip(event)

    @createTooltipContentDecorator()
    def createToolTipContent(self, event, contentID):
        return super(InfoPage, self).createToolTipContent(event, contentID)

    def getTooltipData(self, event):
        return self.__tooltipData.get(event.getArgument('tooltipId', 0))

    def _getBonusPacker(self):
        return None

    def _onLoading(self, *args, **kwargs):
        super(InfoPage, self)._onLoading(*args, **kwargs)
        playInfopageEnterSound(self.__eventName)
        with self.viewModel.transaction() as model:
            model.setHasLootListLink(isCountryForShowingExternalLootList())
            model.setHasVideoButton(getInfoPageSettings(self.__eventName, _InfoPageSetting.VIDEO))
            model.setHasShopButton(isShopVisible(self.__eventName))
            self.__updateState(model=model)

    def _onLoaded(self, *args, **kwargs):
        super(InfoPage, self)._onLoaded(*args, **kwargs)
        Waiting.hide('loading')

    def _finalize(self):
        playInfopageExitSound(self.__eventName)
        super(InfoPage, self)._finalize()

    def _getEvents(self):
        return ((self.viewModel.onClose, self.__onClose),
         (self.viewModel.onShowVideo, self.__showIntroPage),
         (self.viewModel.onShowShop, self.__showShop),
         (self.viewModel.onShowLootList, self.__showExternalLootList),
         (self.viewModel.onPreview, self.__showPreview),
         (self.viewModel.onChosenCategory, self.__updateCategory),
         (self.__lootBoxes.onStatusChanged, self.__onStatusChange),
         (self.__lootBoxes.onBoxesAvailabilityChanged, self.__onStatusChange))

    def __sortedSlotsIDs(self, slotsInfo):
        return sorted(slotsInfo.keys()) or []

    def __onStatusChange(self):
        if self.__lootBoxes.isAvailable(self.__eventName) and self.__lootBoxes.getActiveBoxes(self.__eventName):
            self.__updateState()

    def __fillChosenCategory(self, category='', box=None):
        if category and self.__lootBoxes.getActiveBoxes(self.__eventName, lambda b: b.getCategory() == category):
            self.__category = category
        elif box is not None:
            self.__category = box.getCategory()
        self.viewModel.setChosenCategory(self.__category)
        self.__lootBoxes.setSetting(self.__eventName, LOOT_BOXES_SELECTED_BOX, self.__category)
        return

    def __updateCategory(self, ctx=None, model=None):
        if ctx is not None:
            self.__fillChosenCategory(category=ctx.get('chosenCategory', ''))
        elif self.__savedCategory is not None:
            self.__fillChosenCategory(category=self.__savedCategory)
        else:
            self.__fillChosenCategory(category=self.__category, box=first(self.__lootBoxes.getActiveBoxes(self.__eventName)))
        return

    @replaceNoneKwargsModel
    def __updateState(self, model=None):
        _, endTime = self.__lootBoxes.getActiveTime(self.__eventName)
        timeLeft = max(0, endTime - getServerUTCTime())
        model.setEventExpireTime(timeLeft)
        model.setEventName(self.__eventName)
        self.__updateCategory()
        self.__updateBoxes(model=model)

    @replaceNoneKwargsModel
    def __updateBoxes(self, model=None):
        boxes = model.getBoxes()
        boxes.clear()
        for box in self.__lootBoxes.getActiveBoxes(self.__eventName):
            boxes.addViewModel(self._setLootBox(box))

        boxes.invalidate()

    def _setLootBox(self, box):
        boxInfo = self.__lootBoxes.getBoxInfo(box.getID())
        boxModel = BoxModel()
        boxModel.setCategory(box.getCategory())
        boxModel.setGuaranteedLimit(boxInfo.get('limit', 0))
        boxModel.setCount(box.getInventoryCount())
        boxModel.setCountToGuaranteed(boxInfo.get('boxCountToGuaranteedBonus', 0))
        if box.isRerollable():
            boxModel.setRerollCurrency(box.getRerollCurrency())
            fillIntsArray(box.getRerollPrices(), boxModel.getRerollPrices())
        slotsModel = boxModel.getSlots()
        slotsModel.clear()
        slotsInfo = boxInfo.get('slots', {})
        for slotID in self.__sortedSlotsIDs(slotsInfo):
            slot = slotsInfo.get(slotID, {})
            lbSlot = self._setLootBoxSlot(slot.get('probability', [0])[0], slot.get('bonuses', []))
            slotsModel.addViewModel(lbSlot)

        slotsModel.invalidate()
        return boxModel

    def _setLootBoxSlot(self, probability, bonuses):
        slotModel = SlotModel()
        slotModel.setProbability(int(probability * 10000 + 1e-06) / 100.0)
        slotModel.bonuses.clearItems()
        packBonusModelAndTooltipData(bonuses, slotModel.bonuses, tooltipData=self.__tooltipData, merge=True, eventName=self.__eventName, packer=self._getBonusPacker())
        return slotModel

    def __showPreview(self, ctx):
        showItemPreview(str(ctx.get('bonusType')), int(ctx.get('bonusId')), int(ctx.get('styleID')))

    def __showShop(self):
        Views.load(ViewID.SHOP, eventName=self.__eventName)

    def __showIntroPage(self):
        Views.load(ViewID.INTRO, eventName=self.__eventName)

    def __showExternalLootList(self):
        openExternalLootList()

    def __onClose(self):
        from gui.Scaleform.lobby_entry import getLobbyStateMachine
        lsm = getLobbyStateMachine()
        lsm.getStateFromView(self).goBack()


class InfoPageWindow(WindowImpl):

    def __init__(self, layer, ctx, **kwargs):
        super(InfoPageWindow, self).__init__(WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, content=InfoPage(ctx=ctx), layer=layer)
