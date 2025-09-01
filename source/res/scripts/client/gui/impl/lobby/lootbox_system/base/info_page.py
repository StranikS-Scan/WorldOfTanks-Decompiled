# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/lootbox_system/base/info_page.py
from enum import Enum
from PlayerEvents import g_playerEvents
from frameworks.wulf import ViewSettings, WindowFlags, WindowLayer
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.Waiting import Waiting
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.lootbox_system.box_model import BoxModel
from gui.impl.gen.view_models.views.lobby.lootbox_system.info_page_model import InfoPageModel
from gui.impl.gen.view_models.views.lobby.lootbox_system.slot_model import SlotModel
from gui.impl.lobby.common.view_wrappers import createBackportTooltipDecorator
from gui.impl.pub import ViewImpl, WindowImpl
from gui.impl.wrappers.function_helpers import replaceNoneKwargsModel
from gui.lootbox_system.base.bonuses_packers import packBonusModelAndTooltipData
from gui.lootbox_system.base.common import ViewID, Views
from gui.lootbox_system.base.decorators import createTooltipContentDecorator
from gui.lootbox_system.base.sound import playInfopageEnterSound, playInfopageExitSound
from gui.lootbox_system.base.utils import getInfoPageSettings, isCountryForShowingExternalLootList, isShopVisible, openExternalLootList
from gui.lootbox_system.base.views_loaders import hideItemPreview, showItemPreview
from gui.shared import events
from gui.shared.event_dispatcher import showShop
from helpers import dependency
from shared_utils import first
from skeletons.gui.game_control import ILootBoxSystemController
from web.web_client_api.loot_boxes_system import ViewsIDs

class _InfoPageSetting(str, Enum):
    VIDEO = 'isVideoVisible'


class InfoPage(ViewImpl):
    __slots__ = ('__previousWindowID', '__category', '__tooltipData', '__eventName', '__backCallback')
    __lootBoxes = dependency.descriptor(ILootBoxSystemController)
    __baseWindowID = None

    def __init__(self, layoutID, previousWindow, category, eventName, backCallback=None):
        settings = ViewSettings(layoutID)
        settings.model = InfoPageModel()
        self.__previousWindowID = previousWindow
        self.__category = category
        self.__eventName = eventName
        self.__tooltipData = {}
        self.__backCallback = backCallback
        InfoPage.__baseWindowID = self.__getBaseWindow(previousWindow)
        super(InfoPage, self).__init__(settings)

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

    @classmethod
    def cleanBaseWindow(cls):
        cls.__baseWindowID = None
        return

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
         (self.__lootBoxes.onBoxesAvailabilityChanged, self.__onStatusChange),
         (g_playerEvents.onDisconnected, self.__onDisconnected))

    def _getListeners(self):
        return ((events.BrowserEvent.BROWSER_CREATED, self.__handleBrowserCreated),)

    def __onDisconnected(self):
        self.destroyWindow()

    def __handleBrowserCreated(self, event):
        if event.ctx['browserID'] == VIEW_ALIAS.OVERLAY_WEB_STORE:
            self.destroyWindow()

    def __sortedSlotsIDs(self, slotsInfo):
        return sorted(slotsInfo.keys()) or []

    def __onStatusChange(self):
        if not (self.__lootBoxes.isAvailable(self.__eventName) and self.__lootBoxes.getActiveBoxes(self.__eventName)):
            self.destroyWindow()
        else:
            self.__updateState()

    def __fillChosenCategory(self, category='', box=None):
        if category and self.__lootBoxes.getActiveBoxes(self.__eventName, lambda b: b.getCategory() == category):
            self.__category = category
        elif box is not None:
            self.__category = box.getCategory()
        self.viewModel.setChosenCategory(self.__category)
        return

    def __updateCategory(self, ctx=None, model=None):
        if ctx is not None:
            self.__fillChosenCategory(category=ctx.get('chosenCategory', ''))
        else:
            self.__fillChosenCategory(category=self.__category, box=first(self.__lootBoxes.getActiveBoxes(self.__eventName)))
        return

    @replaceNoneKwargsModel
    def __updateState(self, model=None):
        starTime, endTime = self.__lootBoxes.getActiveTime(self.__eventName)
        model.setStartDate(starTime)
        model.setEndDate(endTime)
        model.setEventName(self.__eventName)
        self.__updateCategory()
        self.__updateBoxes(model=model)

    @replaceNoneKwargsModel
    def __updateBoxes(self, model=None):
        boxes = model.getBoxes()
        boxes.clear()
        for box in self.__lootBoxes.getActiveBoxes(self.__eventName):
            boxInfo = self.__lootBoxes.getBoxInfo(box.getID())
            filledBoxModel = self.__setLootBox(box.getCategory(), boxInfo.get('limit', 0), boxInfo.get('slots', {}))
            boxes.addViewModel(filledBoxModel)

        boxes.invalidate()

    def __setLootBox(self, category, guaranteed, slotsInfo):
        boxModel = BoxModel()
        boxModel.setCategory(category)
        boxModel.setGuaranteedLimit(guaranteed)
        slotsModel = boxModel.getSlots()
        slotsModel.clear()
        for slotID in self.__sortedSlotsIDs(slotsInfo):
            slot = slotsInfo.get(slotID, {})
            lbSlot = self.__setLootBoxSlot(slot.get('probability', [0])[0], slot.get('bonuses', []))
            slotsModel.addViewModel(lbSlot)

        slotsModel.invalidate()
        return boxModel

    def __setLootBoxSlot(self, probability, bonuses):
        slotModel = SlotModel()
        slotModel.setProbability(int(probability * 10000 + 1e-06) / 100.0)
        slotModel.bonuses.clearItems()
        packBonusModelAndTooltipData(bonuses, slotModel.bonuses, tooltipData=self.__tooltipData, merge=True, eventName=self.__eventName)
        return slotModel

    def __getBaseWindow(self, windowID):
        if windowID in (ViewID.MAIN, ViewID.SHOP):
            return windowID
        else:
            return ViewID.MAIN if self.__baseWindowID is None else self.__baseWindowID

    def __showPreview(self, ctx):
        showItemPreview(str(ctx.get('bonusType')), int(ctx.get('bonusId')), int(ctx.get('styleID')), self.__eventName, self.__reopen)
        self.destroyWindow()

    def __showShop(self):
        Views.load(ViewID.SHOP, executePreconditions=True, eventName=self.__eventName)

    def __showIntroPage(self):
        Views.load(ViewID.INTRO, eventName=self.__eventName)

    def __showExternalLootList(self):
        openExternalLootList()

    def __onClose(self):
        if self.__previousWindowID == ViewsIDs.OVERLAY and self.__baseWindowID != ViewID.SHOP:
            Views.load(ViewID.SHOP, executePreconditions=True, eventName=self.__eventName)
        else:
            self.destroyWindow()

    def __reopen(self):
        hideItemPreview()
        Waiting.show('loading')
        if self.__baseWindowID == ViewID.SHOP:
            showShop()
        elif self.__baseWindowID == ViewID.MAIN:
            Views.load(self.__baseWindowID, eventName=self.__eventName, backCallback=self.__backCallback)
        Views.load(ViewID.INFO, previousWindow=self.__previousWindowID, category=self.__category, eventName=self.__eventName, backCallback=self.__backCallback)


class InfoPageWindow(WindowImpl):
    __slots__ = ()

    def __init__(self, eventName, previousWindow=None, category='', parent=None, backCallback=None):
        super(InfoPageWindow, self).__init__(WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, content=InfoPage(R.views.mono.lootbox.info_page(), previousWindow=previousWindow, category=category, eventName=eventName, backCallback=backCallback), parent=parent, layer=WindowLayer.TOP_WINDOW)
