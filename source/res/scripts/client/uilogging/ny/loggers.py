# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/uilogging/ny/loggers.py
import typing
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.impl.new_year.navigation import ViewAliases
from helpers import dependency
from items.components.ny_constants import CustomizationObjects
from new_year.ny_constants import NYObjects, NyWidgetTopMenu
from skeletons.gui.impl import IGuiLoader
from uilogging.base.logger import ifUILoggingEnabled, MetricsLogger, FlowLogger
from uilogging.ny.constants import LogActions, FEATURE, LogItems, LogElements, AdditionalInfo, ParentScreens, Views, TransitionMethods, TIME_LIMIT
from wotdecorators import noexcept
if typing.TYPE_CHECKING:
    from uilogging.types import *

class NyLogger(MetricsLogger):
    __slots__ = ()

    def __init__(self):
        super(NyLogger, self).__init__(FEATURE)


class NyMainWidgetLogger(NyLogger):
    __slots__ = ()

    @noexcept
    def logClick(self, isHangar):
        if isHangar:
            parentScreen = ParentScreens.HANGAR
            item = LogElements.NY23_UILOG_WIDG
        else:
            parentScreen = ParentScreens.NY_LOBBY
            item = LogElements.NY23_UILOG_LOGO
        self.log(action=LogActions.CLICK, item=item, info=AdditionalInfo.ENTRY_POINTS_AND_NAVIGATION, parentScreen=parentScreen)


class NyMainWidgetTooltipLogger(NyLogger):
    __slots__ = ()

    @noexcept
    def start(self):
        self.startAction(LogActions.TOOLTIP_WATCHED)

    @noexcept
    def stop(self, isHangar):
        parentScreen = ParentScreens.HANGAR if isHangar else ParentScreens.NY_LOBBY
        self.stopAction(LogActions.TOOLTIP_WATCHED, timeLimit=TIME_LIMIT, item=LogElements.NY23_UILOG_LOGO_INF, info=AdditionalInfo.ENTRY_POINTS_AND_NAVIGATION, parentScreen=parentScreen)


class NyMainViewLogger(NyLogger):
    __slots__ = ()

    @noexcept
    def logExit(self, isEscPressed):
        self.log(action=LogActions.CLICK, item=LogElements.NY23_UILOG_BACK, itemState='isEscPressed' if isEscPressed else None, info=AdditionalInfo.ENTRY_POINTS_AND_NAVIGATION)
        return

    @noexcept
    def start(self):
        self.startAction(LogActions.MAIN_VIEW_WATCHED)

    @noexcept
    def stop(self):
        self.stopAction(LogActions.MAIN_VIEW_WATCHED, timeLimit=TIME_LIMIT, item=LogElements.NY23_UILOG_BACK, info=AdditionalInfo.ENTRY_POINTS_AND_NAVIGATION)


class NyHangarNameViewLogger(NyLogger):
    __slots__ = ()

    @noexcept
    def logClick(self, field):
        self.log(action=LogActions.CLICK, item=LogElements.NY23_UILOG_INPUT, itemState=field, info=AdditionalInfo.PLAYER_HANGAR_AND_FIRST_ENTRY)

    @noexcept
    def start(self):
        self.startAction(LogActions.NAME_VIEW_WATCHED)

    @noexcept
    def stop(self):
        self.stopAction(LogActions.NAME_VIEW_WATCHED, timeLimit=TIME_LIMIT, item=LogElements.NY23_UILOG_NAME, info=AdditionalInfo.PLAYER_HANGAR_AND_FIRST_ENTRY)


class NyResourcesLogger(NyLogger):
    __slots__ = ()

    @noexcept
    def logMenuClick(self, state):
        self.log(action=LogActions.CLICK, item=LogElements.NY23_UILOG_RES_ICON, itemState=state, info=AdditionalInfo.RESOURCES)


class NySelectableObjectLogger(NyLogger):
    __slots__ = ()
    _OBJECT_NAME_TO_ADDITIONAL_INFO = {NYObjects.TREE: AdditionalInfo.TREE,
     NYObjects.CELEBRITY: AdditionalInfo.CELEBRITY}

    @noexcept
    @ifUILoggingEnabled()
    def logClick(self, objectName, currentObject):
        additionalInfo = self._OBJECT_NAME_TO_ADDITIONAL_INFO.get(objectName)
        if not additionalInfo:
            return
        else:
            parentScreen = ParentScreens.HANGAR if currentObject is None else ParentScreens.NY_LOBBY
            self.log(action=LogActions.CLICK, item=LogItems.NY_SELECTABLE_OBJECT, info=additionalInfo.value, parentScreen=parentScreen.value)
            return


class NyWidgetTopMenuLogger(NyLogger):
    __slots__ = ()

    @noexcept
    @ifUILoggingEnabled()
    def logClick(self, viewName):
        self.log(action=LogActions.CLICK, item=LogItems.WIDGET_TOP_MENU_TAB, itemState=viewName, info=LogElements.NY23_UILOG_MENU, parentScreen=ParentScreens.NY_LOBBY)


class NyCelebrityButtonLogger(NyLogger):
    __slots__ = ()

    @noexcept
    @ifUILoggingEnabled()
    def logClickInMissions(self):
        self.log(action=LogActions.CLICK, item=LogItems.CELEBRITY_BUTTON, parentScreen=ParentScreens.BATTLE_QUESTS_PAGE)


class NyInfoViewLogger(NyLogger):
    __slots__ = ()

    @noexcept
    def onViewClosed(self):
        self.log(action=LogActions.CLOSE, item=LogItems.NY_INFO_PAGE, parentScreen=ParentScreens.NY_INFO_PAGE)


class NyInfoVideoLogger(NyLogger):
    __slots__ = ()

    @noexcept
    def onViewOpened(self):
        self.startAction(LogActions.CLOSE)

    @noexcept
    def onViewClosed(self):
        self.stopAction(LogActions.CLOSE, item=LogItems.INFO_VIDEO, parentScreen=ParentScreens.NY_INFO_PAGE)


class NyStatisticsPopoverLogger(NyLogger):
    __slots__ = ()
    __guiLoader = dependency.descriptor(IGuiLoader)

    @noexcept
    def logClickInBoxes(self):
        self.__logClick(parentScreen=ParentScreens.NY_BOXES_PAGE)

    @noexcept
    def logClickInSingleOpen(self):
        self.__logClick(parentScreen=ParentScreens.REWARDS_PAGE, additionalInfo=AdditionalInfo.SINGLE_OPEN)

    @noexcept
    def logClickInMultipleOpen(self):
        self.__logClick(parentScreen=ParentScreens.REWARDS_PAGE, additionalInfo=AdditionalInfo.MULTI_OPEN)

    @noexcept
    def __logClick(self, parentScreen, additionalInfo=None):
        self.log(action=LogActions.CLICK, item=LogItems.STATISTICS_BUTTON, parentScreen=parentScreen, info=additionalInfo)


class NyDogSysMsgLogger(NyLogger):
    __slots__ = ()

    @noexcept
    def logClick(self):
        self.log(action=LogActions.CLICK, item=LogElements.NY23_UILOG_DOG_CASTOM_BTN, info=AdditionalInfo.DOG_AND_CUSTOMIZATION)


class NyToGiftMachineSysMsgLogger(NyLogger):
    __slots__ = ()

    @noexcept
    def logClick(self):
        self.log(action=LogActions.CLICK, item=LogElements.NY23_UILOG_MSQ_AUTO, info=AdditionalInfo.NOTIFICATIONS)


class NyFlowLogger(FlowLogger):
    __slots__ = ()
    _OBJECT_TO_VIEW = {CustomizationObjects.FIR: Views.TREE,
     CustomizationObjects.FAIR: Views.KITCHEN,
     CustomizationObjects.INSTALLATION: Views.INSTALLATION,
     NYObjects.RESOURCES: Views.RESOURCES,
     NYObjects.CELEBRITY: Views.CELEBRITY,
     NYObjects.TOWN: ViewAliases.GLADE_VIEW}

    def __init__(self):
        super(NyFlowLogger, self).__init__(FEATURE)

    @noexcept
    @ifUILoggingEnabled()
    def logMove(self, sourceView, destinationView, transitionMethod, partnerID=None):
        self.log(action=LogActions.MOVE, sourceItem=sourceView, destinationItem=destinationView, transitionMethod=transitionMethod, partnerID=partnerID)


class NySelectableObjectFlowLogger(NyFlowLogger):
    __slots__ = ()

    @noexcept
    def logClick(self, targetObject, currentObject):
        sourceView = self._OBJECT_TO_VIEW.get(currentObject, Views.HANGAR)
        destinationView = self._OBJECT_TO_VIEW.get(targetObject)
        if destinationView is not None:
            self.logMove(sourceView=sourceView, destinationView=destinationView, transitionMethod=TransitionMethods.SELECTABLE_OBJECT)
        return


class NySideBarFlowLogger(NyFlowLogger):
    __slots__ = ()
    _TOP_MENU_TAB_TO_VIEW = {NyWidgetTopMenu.REWARDS: Views.REWARDS}

    @noexcept
    def logTabSelect(self, view, currentTab, targetTab):
        sourceView, destinationView = ('', '')
        if view == NyWidgetTopMenu.GLADE:
            sourceView = self._OBJECT_TO_VIEW.get(currentTab, Views.TREE)
            destinationView = self._OBJECT_TO_VIEW[targetTab]
        if destinationView and sourceView:
            self.logMove(sourceView=sourceView, destinationView=destinationView, transitionMethod=TransitionMethods.SIDE_BAR_TAB)


class NyTopMenuFlowLogger(NyFlowLogger):
    __slots__ = ()
    _TOP_MENU_TAB_TO_VIEW = {NyWidgetTopMenu.CHALLENGE: Views.CELEBRITY,
     NyWidgetTopMenu.MARKETPLACE: Views.MARKETPLACE,
     NyWidgetTopMenu.FRIENDS: Views.FRIENDS,
     NyWidgetTopMenu.INFO: Views.INFO,
     NyWidgetTopMenu.REWARDS: Views.REWARDS_FOR_LEVELS,
     NyWidgetTopMenu.GIFT_MACHINE: Views.SHARDS}
    _OBJECT_TO_VIEW = {CustomizationObjects.FIR: Views.TREE,
     CustomizationObjects.FAIR: Views.KITCHEN,
     CustomizationObjects.INSTALLATION: Views.INSTALLATION}

    @noexcept
    def logTabSelect(self, source, view, selectedObject, previousObject):
        sourceView = self._getViewFromTab(source, selectedObject, previousObject)
        destinationView = self._getViewFromTab(view, selectedObject, previousObject)
        if sourceView and destinationView:
            self.logMove(sourceView=sourceView, destinationView=destinationView, transitionMethod=TransitionMethods.WIDGET_TOP_MENU_TAB)

    @noexcept
    def _getViewFromTab(self, topTab, selectedObject, previousObject=''):
        if topTab == NyWidgetTopMenu.GLADE:
            if selectedObject not in self._OBJECT_TO_VIEW:
                selectedObject = previousObject
            return self._OBJECT_TO_VIEW.get(selectedObject, Views.TREE)
        return self._TOP_MENU_TAB_TO_VIEW[topTab] if topTab in self._TOP_MENU_TAB_TO_VIEW else ''


class NyInfoFlowLogger(NyTopMenuFlowLogger):
    __slots__ = ()

    @noexcept
    def logBackClick(self, view, selectedObject):
        destinationView = self._getViewFromTab(view, selectedObject)
        if destinationView:
            self.logMove(sourceView=Views.INFO, destinationView=destinationView, transitionMethod=TransitionMethods.INFO_BACK_BUTTON)


class NyMainViewFlowLogger(NyTopMenuFlowLogger):
    __slots__ = ('__wasLogged',)
    __guiLoader = dependency.descriptor(IGuiLoader)

    def __init__(self):
        super(NyMainViewFlowLogger, self).__init__()
        self.__wasLogged = False

    @noexcept
    def logCloseClick(self, view, tab, isEscPressed):
        if self.__wasLogged:
            return
        transitionMethod = TransitionMethods.CLOSE_BUTTON if not isEscPressed else TransitionMethods.ESC_BUTTON
        self.__logClose(view=view, tab=tab, transitionMethod=transitionMethod, partnerID=LogElements.NY23_UILOG_BACK)

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
        self.__logClose(view=view, tab=tab, transitionMethod=transitionMethod)

    @noexcept
    def __logClose(self, view, tab, transitionMethod, partnerID=None):
        sourceView = self._getViewFromTab(view, tab, tab)
        if sourceView:
            self.__wasLogged = True
            self.logMove(sourceView=sourceView, destinationView=Views.HANGAR, transitionMethod=transitionMethod, partnerID=partnerID)


class NyDecorationsSlotPopoverFlowLogger(NyFlowLogger):
    __slots__ = ()

    @noexcept
    def logBigDecorationSlotClick(self, currentObject):
        self.__logSlotClick(currentObject=currentObject, transitionMethod=TransitionMethods.BIG_DECORATIONS_SLOT_POPOVER)

    @noexcept
    def logSmallDecorationSlotClick(self, currentObject):
        self.__logSlotClick(currentObject=currentObject, transitionMethod=TransitionMethods.SMALL_DECORATIONS_SLOT_POPOVER)

    def __logSlotClick(self, currentObject, transitionMethod):
        sourceView = self._OBJECT_TO_VIEW.get(currentObject, Views.HANGAR)
        self.logMove(sourceView=sourceView, destinationView=Views.LOOTBOXES, transitionMethod=transitionMethod)


class NyLootBoxesPopoverFlowLogger(NyFlowLogger):
    __slots__ = ()

    @noexcept
    @ifUILoggingEnabled()
    def logOpen(self, currentObject):
        sourceView = self._OBJECT_TO_VIEW.get(currentObject, Views.HANGAR)
        self.logMove(sourceView=sourceView, destinationView=Views.LOOTBOXES, transitionMethod=TransitionMethods.LOOTBOXES_POPOVER_OPEN)

    @noexcept
    @ifUILoggingEnabled()
    def logBuy(self, currentObject):
        sourceView = self._OBJECT_TO_VIEW.get(currentObject, Views.HANGAR)
        self.logMove(sourceView=sourceView, destinationView=Views.HANGAR, transitionMethod=TransitionMethods.LOOTBOXES_POPOVER_BUY)


class NyLootBoxesFlowLogger(NyFlowLogger):
    __slots__ = ()

    @noexcept
    def logPageButtonsClick(self):
        self.__logClick(destinationView=Views.HANGAR, transitionMethod=TransitionMethods.LOOTBOXES_PAGE_BUTTONS)

    @noexcept
    def logCelebrityClick(self):
        self.__logClick(destinationView=Views.CELEBRITY, transitionMethod=TransitionMethods.LOOTBOXES_CELEBRITY_BUTTON)

    @noexcept
    def logCloseClick(self, currentObject, currentView):
        if currentView == ViewAliases.INFO_VIEW:
            destinationView = Views.INFO
        else:
            destinationView = self._OBJECT_TO_VIEW.get(currentObject, Views.HANGAR)
        self.__logClick(destinationView=destinationView, transitionMethod=TransitionMethods.LOOTBOXES_CLOSE_BUTTON)

    @noexcept
    @ifUILoggingEnabled()
    def __logClick(self, destinationView, transitionMethod):
        self.logMove(sourceView=Views.LOOTBOXES, destinationView=destinationView, transitionMethod=transitionMethod)


class NyLootBoxesRewardsFlowLogger(NyFlowLogger):
    __slots__ = ()

    @noexcept
    def logVehicleShow(self):
        self.logMove(sourceView=Views.LOOTBOXES, destinationView=Views.HANGAR, transitionMethod=TransitionMethods.SHOW_LOOTBOX_VEHICLE)

    @noexcept
    def logStylePreview(self):
        self.logMove(sourceView=Views.LOOTBOXES, destinationView=Views.LOOTBOX_STYLE_PREVIEW, transitionMethod=TransitionMethods.SHOW_LOOTBOX_STYLE_PREVIEW)


class NyLootBoxesRewardPreviewFlowLogger(NyFlowLogger):
    __slots__ = ()

    @noexcept
    def logStylePreviewExit(self):
        self.logMove(sourceView=Views.LOOTBOX_STYLE_PREVIEW, destinationView=Views.HANGAR, transitionMethod=TransitionMethods.LOBBY_HEADER)

    @noexcept
    def logStylePreviewBack(self):
        self.logMove(sourceView=Views.LOOTBOX_STYLE_PREVIEW, destinationView=Views.LOOTBOXES, transitionMethod=TransitionMethods.PREVIEW_BACK_BUTTON)
