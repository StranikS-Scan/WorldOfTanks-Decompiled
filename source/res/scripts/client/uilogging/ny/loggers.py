# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/uilogging/ny/loggers.py
import typing
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.impl.gen.view_models.views.lobby.new_year.views.new_year_info_view_model import Tabs, NewYearInfoViewModel
from gui.impl.new_year.navigation import ViewAliases
from gui.shared import g_eventBus, events, EVENT_BUS_SCOPE
from helpers import dependency
from items.components.ny_constants import CustomizationObjects, YEARS
from new_year.ny_constants import AnchorNames, NyWidgetTopMenu, AdditionalCameraObject, ANCHOR_TO_OBJECT, NyTabBarRewardsView, NyTabBarAlbumsView
from skeletons.gui.impl import IGuiLoader
from uilogging.base.logger import BaseLogger, ifUILoggingEnabled
from uilogging.base.mixins import TimedActionMixin
from uilogging.ny.constants import LogActions, FEATURE, LogGroups, AdditionalInfo, ParentScreens, Views, TransitionMethods
from wotdecorators import noexcept

class NyLogger(BaseLogger):

    def __init__(self, group):
        super(NyLogger, self).__init__(FEATURE, group)

    @noexcept
    @ifUILoggingEnabled()
    def log(self, action, additionalInfo=None, parentScreen=None, **params):
        data = {'additional_info': additionalInfo,
         'parent_screen': parentScreen}
        data = {k:v for k, v in data.iteritems() if v is not None}
        data.update(params)
        super(NyLogger, self).log(action=action.value, **data)


class NyGiftSystemContextMenuLogger(NyLogger):

    def __init__(self):
        super(NyGiftSystemContextMenuLogger, self).__init__(LogGroups.CONTEXT_MENU.value)

    @noexcept
    @ifUILoggingEnabled()
    def logClick(self):
        self.log(action=LogActions.CLICK, parentScreen=ParentScreens.HANGAR.value, additionalInfo=AdditionalInfo.GIFT_SYSTEM_ENTRY_POINT.value)


class NyGiftSystemViewLogger(NyLogger):

    @noexcept
    @ifUILoggingEnabled()
    def log(self, action, additionalInfo=None, **params):
        super(NyGiftSystemViewLogger, self).log(action=action, additionalInfo=additionalInfo, parentScreen=ParentScreens.GIFT_SYSTEM_PAGE.value, **params)


class NyGiftSystemViewTooltipLogger(TimedActionMixin, NyGiftSystemViewLogger):

    @noexcept
    def onTooltipOpened(self):
        self.startAction(LogActions.TOOLTIP_WATCHED)

    @noexcept
    def onTooltipClosed(self):
        self.stopAction(LogActions.TOOLTIP_WATCHED)


class NyGiftSystemSendButtonLogger(NyGiftSystemViewLogger):

    def __init__(self):
        super(NyGiftSystemSendButtonLogger, self).__init__(LogGroups.SEND_BUTTON.value)
        self.__isMessageChanged = False

    @noexcept
    @ifUILoggingEnabled()
    def logClick(self):
        additionalInfo = AdditionalInfo.MESSAGE_CHANGED.value if self.__isMessageChanged else None
        self.log(action=LogActions.CLICK, additionalInfo=additionalInfo)
        return

    def onMessageChanged(self):
        self.__isMessageChanged = True

    def resetMessageChanged(self):
        self.__isMessageChanged = False


class NyGiftSystemIntroLogger(TimedActionMixin, NyGiftSystemViewLogger):

    def __init__(self):
        super(NyGiftSystemIntroLogger, self).__init__(LogGroups.INTRO_PAGE.value)

    @noexcept
    @ifUILoggingEnabled()
    def onViewOpened(self):
        self.startAction(LogActions.CLOSE)

    @noexcept
    @ifUILoggingEnabled()
    def onViewClosed(self):
        self.stopAction(LogActions.CLOSE)


class NyMainWidgetLogger(NyLogger):

    def __init__(self):
        super(NyMainWidgetLogger, self).__init__(LogGroups.NY_MAIN_WIDGET.value)

    @noexcept
    @ifUILoggingEnabled()
    def logClick(self, isHangar):
        parentScreen = ParentScreens.HANGAR if isHangar else ParentScreens.NY_LOBBY
        self.log(action=LogActions.CLICK, parentScreen=parentScreen.value)


class NySelectableObjectLogger(NyLogger):
    _ANCHOR_NAME_TO_ADDITIONAL_INFO = {AnchorNames.TREE: AdditionalInfo.TREE,
     AnchorNames.CELEBRITY: AdditionalInfo.CELEBRITY}

    def __init__(self):
        super(NySelectableObjectLogger, self).__init__(LogGroups.NY_SELECTABLE_OBJECT.value)

    @noexcept
    def logClick(self, anchorName, currentObject):
        additionalInfo = self._ANCHOR_NAME_TO_ADDITIONAL_INFO.get(anchorName)
        if not additionalInfo:
            return
        else:
            parentScreen = ParentScreens.HANGAR if currentObject is None else ParentScreens.NY_LOBBY
            self.log(action=LogActions.CLICK, additionalInfo=additionalInfo.value, parentScreen=parentScreen.value)
            return


class NyWidgetTopMenuLogger(NyLogger):
    _TAB_VIEW_NAME_TO_ADDITIONAL_INFO = {NyWidgetTopMenu.CHALLENGE: AdditionalInfo.CELEBRITY,
     NyWidgetTopMenu.GLADE: AdditionalInfo.TREE,
     NyWidgetTopMenu.VEHICLES: AdditionalInfo.VEHICLES}

    def __init__(self):
        super(NyWidgetTopMenuLogger, self).__init__(LogGroups.WIDGET_TOP_MENU_TAB.value)

    @noexcept
    def logClick(self, viewName):
        additionalInfo = self._TAB_VIEW_NAME_TO_ADDITIONAL_INFO.get(viewName)
        if not additionalInfo:
            return
        self.log(action=LogActions.CLICK, additionalInfo=additionalInfo.value, parentScreen=ParentScreens.NY_LOBBY.value)


class NyCelebrityButtonLogger(NyLogger):

    def __init__(self):
        super(NyCelebrityButtonLogger, self).__init__(LogGroups.CELEBRITY_BUTTON.value)

    @noexcept
    @ifUILoggingEnabled()
    def logClickInGiftSystem(self):
        self.log(action=LogActions.CLICK, parentScreen=ParentScreens.GIFT_SYSTEM_PAGE.value)

    @noexcept
    @ifUILoggingEnabled()
    def logClickInMissions(self):
        self.log(action=LogActions.CLICK, parentScreen=ParentScreens.BATTLE_QUESTS_PAGE.value)


class NyInfoViewLogger(NyLogger):

    def __init__(self):
        super(NyInfoViewLogger, self).__init__(LogGroups.NY_INFO_PAGE.value)

    @noexcept
    def onViewClosed(self):
        self.log(LogActions.CLOSE, parentScreen=ParentScreens.NY_INFO_PAGE.value)


class NyInfoViewSlideLogger(TimedActionMixin, NyLogger):
    _SLIDE_POSTFIX = '_slide'
    _INTRO_SLIDE_NAME = 'Intro'
    _VEHICLES_NAME = 'NyVehicles'
    _TAB_TO_SLIDE_NAME = {Tabs.DEFAULT: _INTRO_SLIDE_NAME,
     Tabs.VEHICLES: _VEHICLES_NAME}

    def __init__(self, slideName=None, startTab=None):
        if startTab is not None:
            self.__switchType = AdditionalInfo.INFO_ENTRY_POINT.value
            slideName = self._TAB_TO_SLIDE_NAME.get(startTab, self._INTRO_SLIDE_NAME)
        else:
            self.__switchType = None
        group = self.__getGroupFromSlide(slideName)
        super(NyInfoViewSlideLogger, self).__init__(group)
        return

    @noexcept
    def onSlideOpened(self, switchType=None):
        g_eventBus.addListener(events.LootboxesEvent.ON_MAIN_VIEW_CLOSED, self.__onViewClosed, scope=EVENT_BUS_SCOPE.LOBBY)
        if switchType:
            self.__switchType = switchType
        self.startAction(LogActions.CLOSE)

    @noexcept
    def onSlideClosed(self):
        g_eventBus.removeListener(events.LootboxesEvent.ON_MAIN_VIEW_CLOSED, self.__onViewClosed, scope=EVENT_BUS_SCOPE.LOBBY)
        self.stopAction(LogActions.CLOSE, additionalInfo=self.__switchType, parentScreen=ParentScreens.NY_INFO_PAGE.value)

    @noexcept
    def onViewOpened(self):
        self.suspend(LogActions.CLOSE)

    @noexcept
    def __onViewClosed(self):
        self.resume(LogActions.CLOSE)

    @noexcept
    def __getGroupFromSlide(self, slideName):
        if slideName:
            name = ''.join([ ('_' + char.lower() if char.isupper() else char) for char in slideName ]).lstrip('_')
        else:
            name = self._INTRO_SLIDE_NAME
        return name + self._SLIDE_POSTFIX


class NyInfoVideoLogger(TimedActionMixin, NyLogger):

    def __init__(self):
        super(NyInfoVideoLogger, self).__init__(LogGroups.INFO_VIDEO.value)

    @noexcept
    def onViewOpened(self):
        self.startAction(LogActions.CLOSE)

    @noexcept
    def onViewClosed(self):
        self.stopAction(LogActions.CLOSE, parentScreen=ParentScreens.NY_INFO_PAGE.value)


class NyStatisticsPopoverLogger(NyLogger):
    __guiLoader = dependency.descriptor(IGuiLoader)

    def __init__(self):
        super(NyStatisticsPopoverLogger, self).__init__(LogGroups.STATISTICS_BUTTON.value)

    @noexcept
    def logClickInBoxes(self):
        self.__logClick(parentScreen=ParentScreens.NY_BOXES_PAGE.value)

    @noexcept
    def logClickInSingleOpen(self):
        self.__logClick(parentScreen=ParentScreens.REWARDS_PAGE.value, additionalInfo=AdditionalInfo.SINGLE_OPEN.value)

    @noexcept
    def logClickInMultipleOpen(self):
        self.__logClick(parentScreen=ParentScreens.REWARDS_PAGE.value, additionalInfo=AdditionalInfo.MULTI_OPEN.value)

    @noexcept
    def __logClick(self, parentScreen, additionalInfo=None):
        self.log(action=LogActions.CLICK, parentScreen=parentScreen, additionalInfo=additionalInfo)


class NyFlowLogger(BaseLogger):
    _OBJECT_TO_VIEW = {CustomizationObjects.FIR: Views.TREE,
     CustomizationObjects.FAIR: Views.KITCHEN,
     CustomizationObjects.INSTALLATION: Views.INSTALLATION,
     CustomizationObjects.MEGAZONE: Views.BIG_DECORATIONS,
     AdditionalCameraObject.CELEBRITY: Views.CELEBRITY}

    def __init__(self):
        super(NyFlowLogger, self).__init__(FEATURE, LogGroups.FLOW.value)

    @noexcept
    @ifUILoggingEnabled()
    def log(self, sourceView, destinationView, transitionMethod, **params):
        data = {'source_view': sourceView,
         'destination_view': destinationView,
         'transition_method': transitionMethod}
        data.update(params)
        super(NyFlowLogger, self).log(action=LogActions.MOVE.value, **data)


class NySelectableObjectFlowLogger(NyFlowLogger):

    @noexcept
    def logClick(self, anchorName, currentObject):
        targetObject = ANCHOR_TO_OBJECT.get(anchorName, '')
        sourceView = self._OBJECT_TO_VIEW.get(currentObject, Views.HANGAR)
        destinationView = self._OBJECT_TO_VIEW.get(targetObject)
        if destinationView is not None:
            self.log(sourceView=sourceView.value, destinationView=destinationView.value, transitionMethod=TransitionMethods.SELECTABLE_OBJECT.value)
        return


class NySideBarFlowLogger(NyFlowLogger):
    _TOP_MENU_TAB_TO_VIEW = {NyWidgetTopMenu.COLLECTIONS: Views.ALBUMS,
     NyWidgetTopMenu.REWARDS: Views.REWARDS}

    @noexcept
    def logTabSelect(self, view, currentTab, targetTab):
        sourceView, destinationView = ('', '')
        if view in (NyWidgetTopMenu.COLLECTIONS, NyWidgetTopMenu.REWARDS):
            sourceView = self.__getViewFromYearTab(view, currentTab)
            destinationView = self.__getViewFromYearTab(view, targetTab)
        elif view == NyWidgetTopMenu.GLADE:
            sourceView = self._OBJECT_TO_VIEW.get(currentTab, Views.TREE).value
            destinationView = self._OBJECT_TO_VIEW[targetTab].value
        if destinationView and sourceView:
            self.log(sourceView=sourceView, destinationView=destinationView, transitionMethod=TransitionMethods.SIDE_BAR_TAB.value)

    def __getViewFromYearTab(self, view, tab):
        if tab in NyTabBarRewardsView.COLLECTIONS + NyTabBarAlbumsView.ALL:
            parentView = self._TOP_MENU_TAB_TO_VIEW[view].value
            return parentView + str(YEARS.getYearNumFromYearStr(tab))
        return Views.REWARDS_FOR_LEVELS.value if tab == NyTabBarRewardsView.FOR_LEVELS else ''


class NyTopMenuFlowLogger(NyFlowLogger):
    _TOP_MENU_TAB_TO_VIEW = {NyWidgetTopMenu.CHALLENGE: Views.CELEBRITY,
     NyWidgetTopMenu.DECORATIONS: Views.COLLIDER,
     NyWidgetTopMenu.GIFT_SYSTEM: Views.GIFT_SYSTEM,
     NyWidgetTopMenu.INFO: Views.INFO,
     NyWidgetTopMenu.REWARDS: Views.REWARDS_FOR_LEVELS,
     NyWidgetTopMenu.SHARDS: Views.SHARDS,
     NyWidgetTopMenu.VEHICLES: Views.VEHICLES}
    _OBJECT_TO_VIEW = {CustomizationObjects.FIR: Views.TREE,
     CustomizationObjects.FAIR: Views.KITCHEN,
     CustomizationObjects.INSTALLATION: Views.INSTALLATION,
     CustomizationObjects.MEGAZONE: Views.BIG_DECORATIONS}

    @noexcept
    def logTabSelect(self, source, view, rewardTab, albumTab, selectedObject, previousObject):
        sourceView = self._getViewFromTab(source, rewardTab, albumTab, selectedObject)
        destinationView = self._getViewFromTab(view, rewardTab, albumTab, selectedObject, previousObject)
        if sourceView and destinationView:
            self.log(sourceView=sourceView, destinationView=destinationView, transitionMethod=TransitionMethods.WIDGET_TOP_MENU_TAB.value)

    @noexcept
    def logInfoClick(self, source, rewardTab, albumTab, selectedObject):
        sourceView = self._getViewFromTab(source, rewardTab, albumTab, selectedObject)
        if sourceView:
            self.log(sourceView=sourceView, destinationView=Views.INFO.value, transitionMethod=TransitionMethods.INFO_ENTRY_POINT.value)

    @noexcept
    def _getViewFromTab(self, topTab, rewardTab, albumTab, selectedObject, previousObject=''):
        if topTab == NyWidgetTopMenu.GLADE:
            if selectedObject not in self._OBJECT_TO_VIEW:
                selectedObject = previousObject
            return self._OBJECT_TO_VIEW.get(selectedObject, Views.TREE).value
        if topTab == NyWidgetTopMenu.REWARDS and rewardTab in NyTabBarRewardsView.COLLECTIONS:
            return Views.REWARDS.value + str(YEARS.getYearNumFromYearStr(rewardTab))
        if topTab == NyWidgetTopMenu.COLLECTIONS:
            return Views.ALBUMS.value + str(YEARS.getYearNumFromYearStr(albumTab))
        return self._TOP_MENU_TAB_TO_VIEW[topTab].value if topTab in self._TOP_MENU_TAB_TO_VIEW else ''


class NyInfoFlowLogger(NyTopMenuFlowLogger):
    _ACTION_TO_VIEW = {NewYearInfoViewModel.BIGBOXES: Views.HANGAR,
     NewYearInfoViewModel.CELEBRITY: Views.CELEBRITY,
     NewYearInfoViewModel.GIFT: Views.GIFT_SYSTEM,
     NewYearInfoViewModel.LEVELS: Views.REWARDS_FOR_LEVELS,
     NewYearInfoViewModel.SMALLBOXES: Views.LOOTBOXES}

    @noexcept
    def logBackClick(self, view, rewardTab, albumTab, selectedObject):
        destinationView = self._getViewFromTab(view, rewardTab, albumTab, selectedObject)
        if destinationView:
            self.log(sourceView=Views.INFO.value, destinationView=destinationView, transitionMethod=TransitionMethods.INFO_BACK_BUTTON.value)

    @noexcept
    def logButtonClick(self, action):
        destinationView = ''
        if action in self._ACTION_TO_VIEW:
            destinationView = self._ACTION_TO_VIEW[action].value
        elif action == NewYearInfoViewModel.STYLES:
            destinationView = Views.ALBUMS.value + str(YEARS.YEAR22)
        if destinationView:
            self.log(sourceView=Views.INFO.value, destinationView=destinationView, transitionMethod=TransitionMethods.INFO_PAGE_BUTTON.value)


class NyMainViewFlowLogger(NyTopMenuFlowLogger):
    __guiLoader = dependency.descriptor(IGuiLoader)

    def __init__(self):
        super(NyMainViewFlowLogger, self).__init__()
        self.__wasLogged = False

    @noexcept
    def logCloseClick(self, view, tab, isEscPressed):
        if self.__wasLogged:
            return
        transitionMethod = TransitionMethods.CLOSE_BUTTON if not isEscPressed else TransitionMethods.ESC_BUTTON
        self.__logClose(view=view, tab=tab, transitionMethod=transitionMethod.value)

    @noexcept
    def logFinalize(self, view, tab):
        if self.__wasLogged:
            return

        def __battleQueuePredicate(window):
            return window.content is not None and getattr(window.content, 'alias', None) == VIEW_ALIAS.BATTLE_QUEUE

        if self.__guiLoader.windowsManager.findWindows(__battleQueuePredicate):
            transitionMethod = TransitionMethods.FIGHT_BUTTON
        else:
            transitionMethod = TransitionMethods.LOBBY_HEADER
        self.__logClose(view=view, tab=tab, transitionMethod=transitionMethod.value)

    @noexcept
    def __logClose(self, view, tab, transitionMethod):
        sourceView = self._getViewFromTab(view, tab, tab, tab)
        if sourceView:
            self.__wasLogged = True
            self.log(sourceView=sourceView, destinationView=Views.HANGAR.value, transitionMethod=transitionMethod)


class NyVehiclesInfoLogger(NyFlowLogger):

    @noexcept
    def logInfoClick(self):
        self.log(sourceView=Views.VEHICLES.value, destinationView=Views.INFO.value, transitionMethod=TransitionMethods.VEHICLES_INFO_BUTTON.value)


class NyGiftSystemFlowLogger(NyFlowLogger):

    @noexcept
    def logCelebrityClick(self):
        self.log(sourceView=Views.GIFT_SYSTEM.value, destinationView=Views.CELEBRITY.value, transitionMethod=TransitionMethods.GIFT_SYSTEM_CELEBRITY_BUTTON.value)


class NyDecorationsSlotPopoverFlowLogger(NyFlowLogger):

    @noexcept
    def logBigDecorationSlotClick(self, currentObject):
        self.__logSlotClick(currentObject=currentObject, transitionMethod=TransitionMethods.BIG_DECORATIONS_SLOT_POPOVER.value)

    @noexcept
    def logSmallDecorationSlotClick(self, currentObject):
        self.__logSlotClick(currentObject=currentObject, transitionMethod=TransitionMethods.SMALL_DECORATIONS_SLOT_POPOVER.value)

    def __logSlotClick(self, currentObject, transitionMethod):
        sourceView = self._OBJECT_TO_VIEW.get(currentObject)
        if sourceView:
            self.log(sourceView=sourceView.value, destinationView=Views.COLLIDER.value, transitionMethod=transitionMethod)


class NyAlbumsFlowLogger(NyFlowLogger):

    @noexcept
    def logToySlotClick(self, albumTab):
        sourceView = self.__getAlbumNameFromYear(albumTab)
        self.log(sourceView=sourceView, destinationView=Views.COLLIDER.value, transitionMethod=TransitionMethods.ALBUM_DECORATIONS_SLOT.value)

    @noexcept
    def logRewardsClick(self, albumTab):
        sourceView = self.__getAlbumNameFromYear(albumTab)
        destinationView = self.__getRewardsNameFromYear(albumTab)
        self.log(sourceView=sourceView, destinationView=destinationView, transitionMethod=TransitionMethods.ALBUM_REWARDS_BUTTON.value)

    def __getAlbumNameFromYear(self, albumTab):
        return Views.ALBUMS.value + str(YEARS.getYearNumFromYearStr(albumTab))

    def __getRewardsNameFromYear(self, albumTab):
        return Views.REWARDS.value + str(YEARS.getYearNumFromYearStr(albumTab))


class NyCurrentYearAlbumFlowLogger(NyFlowLogger):

    @noexcept
    def logClick(self, currentAlbumTab, targetAlbumTab):
        sourceView = self.__getViewNameFromYear(currentAlbumTab)
        destinationView = self.__getViewNameFromYear(targetAlbumTab)
        self.log(sourceView=sourceView, destinationView=destinationView, transitionMethod=TransitionMethods.CURRENT_YEAR_ALBUM_BUTTON.value)

    @noexcept
    def __getViewNameFromYear(self, albumTab):
        return Views.ALBUMS.value + str(YEARS.getYearNumFromYearStr(albumTab))


class NyRewardsFlowLogger(NyFlowLogger):

    @noexcept
    def logCollectionsClick(self, rewardsTab):
        sourceView = Views.REWARDS.value + str(YEARS.getYearNumFromYearStr(rewardsTab))
        destinationView = Views.ALBUMS.value + str(YEARS.getYearNumFromYearStr(rewardsTab))
        self.log(sourceView=sourceView, destinationView=destinationView, transitionMethod=TransitionMethods.REWARDS_ALBUM_BUTTON.value)


class NyLootBoxesPopoverFlowLogger(NyFlowLogger):

    @noexcept
    @ifUILoggingEnabled()
    def logOpen(self, currentObject):
        sourceView = self._OBJECT_TO_VIEW.get(currentObject, Views.HANGAR).value
        self.log(sourceView=sourceView, destinationView=Views.LOOTBOXES.value, transitionMethod=TransitionMethods.LOOTBOXES_POPOVER_OPEN.value)

    @noexcept
    @ifUILoggingEnabled()
    def logBuy(self, currentObject):
        sourceView = self._OBJECT_TO_VIEW.get(currentObject, Views.HANGAR).value
        self.log(sourceView=sourceView, destinationView=Views.HANGAR.value, transitionMethod=TransitionMethods.LOOTBOXES_POPOVER_BUY.value)


class NyLootBoxesFlowLogger(NyFlowLogger):

    @noexcept
    def logPageButtonsClick(self):
        self.__logClick(destinationView=Views.HANGAR.value, transitionMethod=TransitionMethods.LOOTBOXES_PAGE_BUTTONS.value)

    @noexcept
    def logCelebrityClick(self):
        self.__logClick(destinationView=Views.CELEBRITY.value, transitionMethod=TransitionMethods.LOOTBOXES_CELEBRITY_BUTTON.value)

    @noexcept
    def logCloseClick(self, currentObject, currentView):
        if currentView == ViewAliases.INFO_VIEW:
            destinationView = Views.INFO.value
        else:
            destinationView = self._OBJECT_TO_VIEW.get(currentObject, Views.HANGAR).value
        self.__logClick(destinationView=destinationView, transitionMethod=TransitionMethods.LOOTBOXES_CLOSE_BUTTON.value)

    @noexcept
    @ifUILoggingEnabled()
    def __logClick(self, destinationView, transitionMethod):
        self.log(sourceView=Views.LOOTBOXES.value, destinationView=destinationView, transitionMethod=transitionMethod)


class NyLootBoxesRewardsFlowLogger(NyFlowLogger):

    @noexcept
    def logVehicleShow(self):
        self.log(sourceView=Views.LOOTBOXES.value, destinationView=Views.HANGAR.value, transitionMethod=TransitionMethods.SHOW_LOOTBOX_VEHICLE.value)

    @noexcept
    def logStylePreview(self):
        self.log(sourceView=Views.LOOTBOXES.value, destinationView=Views.LOOTBOX_STYLE_PREVIEW.value, transitionMethod=TransitionMethods.SHOW_LOOTBOX_STYLE_PREVIEW.value)


class NyLootBoxesRewardPreviewFlowLogger(NyFlowLogger):

    @noexcept
    def logStylePreviewExit(self):
        self.log(sourceView=Views.LOOTBOX_STYLE_PREVIEW.value, destinationView=Views.HANGAR.value, transitionMethod=TransitionMethods.LOBBY_HEADER.value)

    @noexcept
    def logStylePreviewBack(self):
        self.log(sourceView=Views.LOOTBOX_STYLE_PREVIEW.value, destinationView=Views.LOOTBOXES.value, transitionMethod=TransitionMethods.PREVIEW_BACK_BUTTON.value)
