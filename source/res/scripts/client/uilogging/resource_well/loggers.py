# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/uilogging/resource_well/loggers.py
import typing
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.vehicle_preview.top_panel.top_panel_tabs_model import TabID
from gui.resource_well.resource_well_constants import ProgressionState
from gui.shared import g_eventBus, EVENT_BUS_SCOPE
from gui.shared.events import ViewEventType
from helpers import dependency
from skeletons.gui.impl import IGuiLoader
from uilogging.base.logger import BaseLogger
from uilogging.base.mixins import TimedActionMixin
from uilogging.resource_well.constants import FEATURE, AdditionalInfo, LogActions, LogGroups, ParentScreens
from wotdecorators import noexcept

class ResourceWellLogger(BaseLogger):

    def __init__(self, group):
        super(ResourceWellLogger, self).__init__(FEATURE, group.value)

    @noexcept
    def log(self, action, additionalInfo=None, parentScreen=None, **params):
        data = {'additional_info': additionalInfo,
         'parent_screen': parentScreen}
        data = {k:v.value for k, v in data.iteritems() if v is not None}
        data.update(params)
        super(ResourceWellLogger, self).log(action=action.value, **data)


class ResourceWellMainScreenLogger(ResourceWellLogger):
    __PROGRESSION_STATE_TO_ADDITIONAL_INFO = {ProgressionState.FORBIDDEN: AdditionalInfo.PARTICIPATION_FORBIDDEN,
     ProgressionState.ACTIVE: AdditionalInfo.REFUND_AVAILABLE,
     ProgressionState.NO_PROGRESS: AdditionalInfo.REFUND_UNAVAILABLE,
     ProgressionState.NO_VEHICLES: AdditionalInfo.REFUND_UNAVAILABLE}

    def __init__(self):
        super(ResourceWellMainScreenLogger, self).__init__(LogGroups.MAIN_SCREEN)

    @noexcept
    def onViewOpened(self, progressionState):
        self.log(LogActions.OPEN, additionalInfo=self.__PROGRESSION_STATE_TO_ADDITIONAL_INFO.get(progressionState))


class ResourceWellScreenTimeMixin(TimedActionMixin):

    @noexcept
    def onViewOpened(self):
        self.startAction(LogActions.OPEN)

    @noexcept
    def onViewClosed(self):
        self.stopAction(LogActions.OPEN)


class ResourceWellCompletedScreenLogger(ResourceWellScreenTimeMixin, ResourceWellLogger):
    __guiLoader = dependency.descriptor(IGuiLoader)

    def __init__(self):
        super(ResourceWellCompletedScreenLogger, self).__init__(LogGroups.COMPLETED_SCREEN)

    @noexcept
    def onViewOpened(self):
        super(ResourceWellCompletedScreenLogger, self).onViewOpened()
        self.__guiLoader.windowsManager.onWindowStatusChanged += self.__onWindowsStatusChanged
        g_eventBus.addListener(ViewEventType.LOAD_VIEW, self.__onViewLoaded, scope=EVENT_BUS_SCOPE.LOBBY)

    @noexcept
    def onViewClosed(self):
        self.__guiLoader.windowsManager.onWindowStatusChanged -= self.__onWindowsStatusChanged
        g_eventBus.removeListener(ViewEventType.LOAD_VIEW, self.__onViewLoaded, scope=EVENT_BUS_SCOPE.LOBBY)
        super(ResourceWellCompletedScreenLogger, self).onViewClosed()

    def __onWindowsStatusChanged(self, _, newStatus):

        def predicate(window):
            return window.content is not None and getattr(window.content, 'alias', None) == VIEW_ALIAS.RESOURCE_WELL_BROWSER_VIEW

        if not self.__guiLoader.windowsManager.findWindows(predicate):
            self.resume(LogActions.OPEN)

    def __onViewLoaded(self, event):
        if event.alias == VIEW_ALIAS.RESOURCE_WELL_BROWSER_VIEW:
            self.suspend(LogActions.OPEN)


class ResourceWellIntroScreenLogger(ResourceWellScreenTimeMixin, ResourceWellLogger):

    def __init__(self):
        super(ResourceWellIntroScreenLogger, self).__init__(LogGroups.INTRO_SCREEN)


class ResourceWellIntroVideoLogger(ResourceWellScreenTimeMixin, ResourceWellLogger):

    def __init__(self):
        super(ResourceWellIntroVideoLogger, self).__init__(LogGroups.INTRO_VIDEO)

    @noexcept
    def onViewClosed(self):
        self.stopAction(LogActions.OPEN, parentScreen=ParentScreens.INTRO_SCREEN)


class ResourceWellInfoScreenLogger(ResourceWellScreenTimeMixin, ResourceWellLogger):

    def __init__(self):
        super(ResourceWellInfoScreenLogger, self).__init__(LogGroups.INFO_SCREEN)


class ResourceWellVehiclePreviewLogger(ResourceWellScreenTimeMixin, ResourceWellLogger):
    __TAB_TO_ADDITIONAL_INFO = {TabID.PERSONAL_NUMBER_VEHICLE: AdditionalInfo.STYLE_TAB,
     TabID.BASE_VEHICLE: AdditionalInfo.BASIC_TAB}

    def __init__(self):
        super(ResourceWellVehiclePreviewLogger, self).__init__(LogGroups.VEHICLE_PREVIEW)
        self.__firstTab = None
        return

    @noexcept
    def onViewOpened(self, tab):
        super(ResourceWellVehiclePreviewLogger, self).onViewOpened()
        self.__firstTab = tab

    @noexcept
    def onViewClosed(self):
        self.stopAction(LogActions.OPEN, additionalInfo=self.__TAB_TO_ADDITIONAL_INFO.get(self.__firstTab))


class ResourceWellLoadingScreenLogger(TimedActionMixin, ResourceWellLogger):

    def __init__(self):
        super(ResourceWellLoadingScreenLogger, self).__init__(LogGroups.CHOOSE_SCREEN)

    @noexcept
    def onViewOpened(self, parentScreen):
        self.log(LogActions.OPEN, parentScreen=parentScreen)
        self.startAction(LogActions.CLOSE)

    @noexcept
    def onViewClosed(self):
        self.stopAction(LogActions.CLOSE)


class ResourceWellEntryPointLogger(ResourceWellLogger):

    def __init__(self):
        super(ResourceWellEntryPointLogger, self).__init__(LogGroups.ENTRY_SCREEN)

    @noexcept
    def logEntryPointClick(self):
        self.__logClick(AdditionalInfo.HANGAR_ENTRY_POINT)

    @noexcept
    def logWebClick(self, backToShop=False):
        additionalInfo = AdditionalInfo.SHOP_BANNER if backToShop else AdditionalInfo.COMBAT_INTELLIGENCE
        self.__logClick(additionalInfo)

    @noexcept
    def logStartNotificationButtonClick(self):
        self.__logClick(AdditionalInfo.START_NOTIFICATION_BUTTON)

    @noexcept
    def logNoVehiclesNotificationButtonClick(self):
        self.__logClick(AdditionalInfo.NO_VEHICLES_NOTIFICATION_BUTTON)

    def __logClick(self, additionalInfo):
        self.log(LogActions.CLICK, additionalInfo=additionalInfo)


class ResourceWellReturnTooltipLogger(TimedActionMixin, ResourceWellLogger):

    def __init__(self):
        super(ResourceWellReturnTooltipLogger, self).__init__(LogGroups.REFUND_TOOLTIP)

    @noexcept
    def onTooltipOpened(self):
        self.startAction(LogActions.TOOLTIP_WATCHED)

    @noexcept
    def onTooltipClosed(self):
        self.stopAction(LogActions.TOOLTIP_WATCHED, parentScreen=ParentScreens.MAIN_SCREEN)


class ResourceWellSerialNumberTooltipLogger(TimedActionMixin, ResourceWellLogger):
    __LAYOUT_TO_PARENT_SCREEN = {R.views.lobby.resource_well.AwardView(): ParentScreens.AWARD_SCREEN,
     R.views.lobby.resource_well.IntroView(): ParentScreens.INTRO_SCREEN,
     R.views.lobby.resource_well.ProgressionView(): ParentScreens.MAIN_SCREEN}

    def __init__(self):
        super(ResourceWellSerialNumberTooltipLogger, self).__init__(LogGroups.SERIAL_NUMBER_TOOLTIP)
        self.__parentScreen = None
        return

    @noexcept
    def onTooltipOpened(self, layoutID):
        self.startAction(LogActions.TOOLTIP_WATCHED)
        self.__parentScreen = self.__LAYOUT_TO_PARENT_SCREEN.get(layoutID)

    @noexcept
    def onTooltipClosed(self):
        self.stopAction(LogActions.TOOLTIP_WATCHED, parentScreen=self.__parentScreen)
