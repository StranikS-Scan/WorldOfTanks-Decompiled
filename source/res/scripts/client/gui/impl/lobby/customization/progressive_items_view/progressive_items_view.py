# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/customization/progressive_items_view/progressive_items_view.py
import logging
import BigWorld
from adisp import adisp_process
from CurrentVehicle import g_currentVehicle
from frameworks.wulf import ViewFlags, ViewSettings
from gui import GUI_SETTINGS
from gui.shared.view_helpers.blur_manager import CachedBlur
from gui.game_control.links import URLMacros
from gui.server_events.events_dispatcher import showProgressiveItemsBrowserView
from gui.impl.backport import BackportTooltipWindow, createTooltipData
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.customization.progressive_items_view.item_model import ItemModel
from gui.impl.gen.view_models.views.lobby.customization.progressive_items_view.item_level_info_model import ItemLevelInfoModel
from gui.impl.gen.view_models.views.lobby.customization.progressive_items_view.progressive_items_view_model import ProgressiveItemsViewModel
from gui.impl.pub import ViewImpl
from gui.Scaleform.daapi.view.lobby.customization.shared import getProgressionItemStatusText
from gui.shared.gui_items.customization import CustomizationTooltipContext
from helpers import dependency, int2roman
from helpers.i18n import makeString as _ms
from items import vehicles
from items.components.c11n_constants import ProjectionDecalFormTags
from skeletons.gui.app_loader import IAppLoader
from skeletons.gui.customization import ICustomizationService
from skeletons.gui.impl import IGuiLoader
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
from skeletons.account_helpers.settings_core import ISettingsCore
from web.web_client_api import webApiCollection, ui as ui_web_api, sound as sound_web_api
from gui.shared.utils.graphics import isRendererPipelineDeferred
from items.components.c11n_constants import CustomizationType
_logger = logging.getLogger(__name__)
_PREVIEW_ICON_SIZE = (512, 512)
_PREVIEW_ICON_INNER_SIZE_DEFAULT = (504, 504)
_PREVIEW_ICON_INNER_SIZE = {ProjectionDecalFormTags.SQUARE: (504, 504),
 ProjectionDecalFormTags.RECT1X2: (504, 252),
 ProjectionDecalFormTags.RECT1X3: (504, 168),
 ProjectionDecalFormTags.RECT1X4: (504, 126),
 ProjectionDecalFormTags.RECT1X6: (504, 84)}

class ProgressiveItemsView(ViewImpl):
    __slots__ = ('__c11nView', '_itemsProgressData', '_possibleItems', '_vehicle', '__blur', '__layoutID', '__urlMacros', '__guiSettings')
    __lobbyContext = dependency.descriptor(ILobbyContext)
    __itemsCache = dependency.descriptor(IItemsCache)
    __customizationService = dependency.descriptor(ICustomizationService)
    __appLoader = dependency.descriptor(IAppLoader)
    __settingsCore = dependency.descriptor(ISettingsCore)
    __guiLoader = dependency.descriptor(IGuiLoader)

    def __init__(self, layoutID, c11nView, *args, **kwargs):
        settings = ViewSettings(layoutID)
        settings.args = args
        settings.kwargs = kwargs
        settings.flags = ViewFlags.LOBBY_TOP_SUB_VIEW
        settings.model = ProgressiveItemsViewModel()
        super(ProgressiveItemsView, self).__init__(settings)
        self._itemsProgressData = None
        self._possibleItems = None
        self._vehicle = None
        self.__blur = CachedBlur()
        self.__layoutID = layoutID
        self.__c11nView = c11nView
        self.__urlMacros = URLMacros()
        self.__guiSettings = GUI_SETTINGS.progressiveItems.get('tutorialVideo', {})
        return

    def createToolTip(self, event):
        if event.contentID == R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent():
            intCD = int(event.getArgument('id'))
            level = int(event.getArgument('level'))
            window = BackportTooltipWindow(self.__getTooltipData(intCD, event.getArgument('tooltip'), level), self.getParentWindow())
            window.load()
            return window
        return super(ProgressiveItemsView, self).createToolTip(event)

    def update(self, *args, **kwargs):
        itemIntCD = kwargs.get('itemIntCD')
        self._vehicle = g_currentVehicle.item
        self._possibleItems = self._getPossibleItemsForVehicle()
        self._itemsProgressData = self.__itemsCache.items.inventory.getC11nProgressionDataForVehicle(self._vehicle.intCD)
        with self.getViewModel().transaction() as model:
            model.setTankName(self._vehicle.userName)
            model.setTankLevel(int2roman(self._vehicle.level))
            model.setTankType(self._vehicle.typeBigIconResource())
            self.__setItems(model)
            model.setIsRendererPipelineDeferred(isRendererPipelineDeferred())
            model.setItemToScroll(0 if itemIntCD is None else itemIntCD)
        return

    @property
    def viewModel(self):
        return super(ProgressiveItemsView, self).getViewModel()

    def _initialize(self, *args, **kwargs):
        super(ProgressiveItemsView, self)._initialize(*args, **kwargs)
        layoutID = R.views.lobby.customization.CustomizationCart()
        customizationCartView = self.__guiLoader.windowsManager.getViewByLayoutID(layoutID)
        if customizationCartView is not None:
            customizationCartView.destroyWindow()
        if self.__c11nView is not None:
            self.__c11nView.changeVisible(False)
        self.viewModel.onSelectItem += self._onSelectItem
        self.viewModel.tutorial.showVideo += self._showVideoPage
        return

    def _finalize(self):
        super(ProgressiveItemsView, self)._finalize()
        if self.__c11nView is not None:
            self.__c11nView.changeVisible(True)
            self.__c11nView = None
        self.__blur.fini()
        self.viewModel.onSelectItem -= self._onSelectItem
        self.viewModel.tutorial.showVideo -= self._showVideoPage
        return

    def _onLoading(self, *args, **kwargs):
        self.update(*args, **kwargs)

    def _onLoaded(self, *args, **kwargs):
        self.__blur.enable()

    def _onSelectItem(self, args=None):
        if args is not None:
            intCD = int(args['intCD'])
            level = int(args['level'])
            item = self.__customizationService.getItemByCD(intCD)
            ctx = self.__customizationService.getCtx()

            def changeTabAndGetItemToHand():
                ctx.changeModeWithProgressionDecal(intCD)
                ctx.events.onGetItemBackToHand(item, level, scrollToItem=True)
                noveltyCount = self._vehicle.getC11nItemNoveltyCounter(proxy=self.__itemsCache.items, item=item)
                if noveltyCount:
                    BigWorld.callback(0.0, lambda : ctx.resetItemsNovelty([item.intCD]))

            BigWorld.callback(0.0, changeTabAndGetItemToHand)
        self.destroyWindow()
        return

    def _showVideoPage(self, args=None):
        self.__showVideo()

    @adisp_process
    def __showVideo(self):
        url = yield self.__urlMacros.parse(self.__guiSettings.get('url'))
        webHandlers = webApiCollection(ui_web_api.CloseViewWebApi, sound_web_api.SoundWebApi, sound_web_api.HangarSoundWebApi)
        ctx = {'url': url,
         'webHandlers': webHandlers,
         'allowRightClick': False}
        showProgressiveItemsBrowserView(ctx)

    def _getPossibleItemsForVehicle(self):
        customizationCache = vehicles.g_cache.customization20()
        vehicleType = self._vehicle.descriptor.type
        sortedItems = sorted(customizationCache.customizationWithProgression.itervalues(), key=lambda i: i.id)
        return [ item.compactDescr for item in sortedItems if (item.filter is None or item.filter.matchVehicleType(vehicleType)) and item.itemType == CustomizationType.PROJECTION_DECAL ]

    def __setItems(self, model):
        model.progressiveItems.clearItems()
        for intCD in self._possibleItems:
            itemModel = ItemModel()
            item = self.__customizationService.getItemByCD(intCD)
            itemModel.setItemId(intCD)
            itemModel.setItemUserString(item.userName)
            itemModel.setMaxLevel(item.getMaxProgressionLevel())
            itemModel.setScaleFactor(item.formfactor)
            latestOpenedLevel = item.getLatestOpenedProgressionLevel(self._vehicle)
            itemModel.setCurrentLevel(1 if latestOpenedLevel == -1 else latestOpenedLevel + 1)
            self.__setEachLevelInfo(itemModel, item)
            model.progressiveItems.addViewModel(itemModel)

    def __setEachLevelInfo(self, model, item):
        for level in xrange(1, model.getMaxLevel() + 1):
            levelInfo = ItemLevelInfoModel()
            levelInfo.setLevel(level)
            levelInfo.setLevelText(getProgressionItemStatusText(level))
            levelInfo.setUnlocked(level < model.getCurrentLevel())
            icon = item.iconUrlByProgressionLevel(level, _PREVIEW_ICON_SIZE, _PREVIEW_ICON_INNER_SIZE.get(item.formfactor))
            levelInfo.setIcon(icon)
            levelConditions = item.progressionConditions.get(level, {}).get('conditions')
            if level == model.getCurrentLevel() and levelConditions:
                levelInfo.setInProgress(True)
                levelInfo.progressBlock.setUnlockCondition(_ms(levelConditions[0].get('description', '')))
                currProgress = int(item.getCurrentProgressOnCurrentLevel(self._vehicle))
                currProgress = currProgress if currProgress > 0 else 0
                maxProgress = int(levelConditions[0].get('value', '1'))
                if maxProgress > 1:
                    levelInfo.progressBlock.setProgressionVal(currProgress)
                    levelInfo.progressBlock.setMaxProgressionVal(maxProgress)
                else:
                    levelInfo.progressBlock.setHideProgressBarAndString(True)
            model.eachLevelInfo.addViewModel(levelInfo)

    @staticmethod
    def __getTooltipData(intCD, tooltip, level):
        return createTooltipData(isSpecial=True, specialAlias=tooltip, specialArgs=CustomizationTooltipContext(itemCD=intCD, level=level, showOnlyProgressBlock=True))
