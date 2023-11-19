# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/uilogging/crew/loggers.py
from typing import TYPE_CHECKING
from frameworks.wulf import View, Window, WindowStatus, WindowLayer, WindowFlags
from gui.impl.gen.view_models.views.lobby.crew.common.tooltip_constants import TooltipConstants
from helpers import dependency
from skeletons.gui.app_loader import IAppLoader
from skeletons.gui.impl import IGuiLoader
from uilogging.base.logger import MetricsLogger, ifUILoggingEnabled
from uilogging.core.common import convertEnum
from uilogging.crew.logging_constants import FEATURE, MIN_VIEW_TIME, CrewLogActions, TooltipAdditionalInfo, CrewViewKeys, LAYOUT_ID_TO_ITEM, CrewPersonalFileKeys, CrewWidgetKeys, CrewNavigationButtons, CrewMemberChangeKeys
from wotdecorators import noexcept
if TYPE_CHECKING:
    from typing import Optional, Dict
    from uilogging.types import ParentScreenType, ItemType
_CHECK_LAYERS = (WindowLayer.OVERLAY,
 WindowLayer.TOP_WINDOW,
 WindowLayer.FULLSCREEN_WINDOW,
 WindowLayer.TOP_SUB_VIEW)
_NAV_BUTTON = '{parentScreen}_{item}_button'

class CrewMetricsLogger(MetricsLogger):
    __slots__ = ()

    def __init__(self):
        super(CrewMetricsLogger, self).__init__(FEATURE)

    @ifUILoggingEnabled()
    def logClick(self, item, parentScreen=None, info=None):
        self.log(action=CrewLogActions.CLICK, item=item, parentScreen=parentScreen, info=info)

    @noexcept
    @ifUILoggingEnabled()
    def logNavigationButtonClick(self, item, parentScreen=None, info=None):
        self.logClick(_NAV_BUTTON.format(item=convertEnum(item), parentScreen=convertEnum(parentScreen)), parentScreen, info)

    def initialize(self):
        pass

    def finalize(self):
        pass


class CrewMetricsLoggerWithParent(CrewMetricsLogger):
    __slots__ = ('_parentViewKey',)

    def __init__(self):
        self._parentViewKey = None
        super(CrewMetricsLoggerWithParent, self).__init__()
        return

    @property
    def disabled(self):
        return not self._parentViewKey or super(CrewMetricsLoggerWithParent, self).disabled

    def setParentViewKey(self, parentViewKey):
        self._parentViewKey = parentViewKey

    @ifUILoggingEnabled()
    def logNavigationButtonClick(self, item, parentScreen=None, info=None):
        return super(CrewMetricsLoggerWithParent, self).logNavigationButtonClick(item, parentScreen if parentScreen else self._parentViewKey, info)

    @ifUILoggingEnabled()
    def logClick(self, item, parentScreen=None, info=None):
        super(CrewMetricsLoggerWithParent, self).logClick(item, parentScreen if parentScreen else self._parentViewKey, info)


class CrewViewLogger(CrewMetricsLogger):
    __slots__ = ('_currentView', '_parentViewKey', '_currentViewKey', '_overlappingWindowsCount', '_isPaused')
    gui = dependency.descriptor(IGuiLoader)

    def __init__(self, currentView, currentViewKey=None, parentViewKey=None):
        super(CrewViewLogger, self).__init__()
        self._currentView = currentView
        self._currentViewKey = currentViewKey
        self._parentViewKey = CrewViewKeys.HANGAR if parentViewKey is None else parentViewKey
        self._overlappingWindowsCount = 0
        self._isPaused = False
        return

    @property
    def disabled(self):
        return not self._currentView or not self._currentViewKey or super(CrewViewLogger, self).disabled

    @ifUILoggingEnabled()
    def logClick(self, item, parentScreen=None, info=None):
        super(CrewViewLogger, self).logClick(item, parentScreen if parentScreen else self._currentViewKey, info)

    @ifUILoggingEnabled()
    def logNavigationButtonClick(self, item, parentScreen=None, info=None):
        return super(CrewViewLogger, self).logNavigationButtonClick(item, parentScreen if parentScreen else self._currentViewKey, info)

    @ifUILoggingEnabled()
    def initialize(self):
        self.gui.windowsManager.onWindowStatusChanged += self._onWindowStatusChanged
        self._viewOpened()

    def finalize(self):
        self.gui.windowsManager.onWindowStatusChanged -= self._onWindowStatusChanged
        self._viewClosed()
        self._clear()

    def _viewOpened(self, info=None):
        self.startAction(CrewLogActions.VIEWED)
        self.log(action=CrewLogActions.OPEN, item=self._currentViewKey, parentScreen=self._parentViewKey, info=info)

    @ifUILoggingEnabled()
    def _viewClosed(self, info=None):
        self.stopAction(action=CrewLogActions.VIEWED, item=self._currentViewKey, parentScreen=self._parentViewKey, timeLimit=MIN_VIEW_TIME, info=info)
        self.log(action=CrewLogActions.CLOSE, item=self._currentViewKey, parentScreen=self._parentViewKey, info=info)

    def _pause(self):
        self._isPaused = True
        self.suspendAction(CrewLogActions.VIEWED)

    def _resume(self):
        self._isPaused = False
        self.resumeAction(CrewLogActions.VIEWED)

    def _onWindowStatusChanged(self, uniqueID, newStatus):
        otherWindow = self.gui.windowsManager.getWindow(uniqueID)
        window = self._currentView.getParentWindow()
        if not window or not otherWindow or window.uniqueID == uniqueID or otherWindow.layer < window.layer or otherWindow.windowFlags in (WindowFlags.CONTEXT_MENU, WindowFlags.POP_OVER) or otherWindow.layer not in _CHECK_LAYERS or newStatus not in (WindowStatus.DESTROYING, WindowStatus.LOADED):
            return
        if newStatus == WindowStatus.LOADED:
            self._updateOverlappingWindowsCount(1)
        elif newStatus == WindowStatus.DESTROYING:
            self._updateOverlappingWindowsCount(-1)
        self._onOverlap(window, otherWindow, newStatus)

    def _onOverlap(self, currentWindow, otherWindow, newStatus):
        pass

    def _updateOverlappingWindowsCount(self, delta):
        self._overlappingWindowsCount += delta
        if self._overlappingWindowsCount > 0:
            self._pause()
        else:
            self._resume()

    def _clear(self):
        self._currentView = None
        self._currentViewKey = None
        self._parentViewKey = None
        self._overlappingWindowsCount = 0
        self._isPaused = False
        return


class CrewBringToFrontViewLogger(CrewViewLogger):
    __slots__ = ('_sameLayerOverlappingWindows',)

    def __init__(self, currentView, layoutID, parentViewKey=None):
        self._sameLayerOverlappingWindows = []
        super(CrewBringToFrontViewLogger, self).__init__(currentView, LAYOUT_ID_TO_ITEM.get(layoutID), parentViewKey)

    @ifUILoggingEnabled()
    def onBringToFront(self, otherWindow):
        window = self._currentView.getParentWindow()
        if window.layer != otherWindow.layer:
            return
        if otherWindow == window:
            self._clearSameLayerOverlappingWindows()
        else:
            self._addSameLayerOverlappingWindow(otherWindow)

    def _onOverlap(self, currentWindow, otherWindow, newStatus):
        if currentWindow.layer != otherWindow.layer:
            return
        if newStatus == WindowStatus.LOADED:
            self._sameLayerOverlappingWindows.append(otherWindow.uniqueID)
        elif newStatus == WindowStatus.DESTROYING and otherWindow.uniqueID in self._sameLayerOverlappingWindows:
            self._sameLayerOverlappingWindows.remove(otherWindow.uniqueID)

    def _clearSameLayerOverlappingWindows(self):
        overlappingWindowsAmount = len(self._sameLayerOverlappingWindows)
        self._sameLayerOverlappingWindows = []
        self._updateOverlappingWindowsCount(-overlappingWindowsAmount)

    def _addSameLayerOverlappingWindow(self, window):
        if window.uniqueID not in self._sameLayerOverlappingWindows:
            self._sameLayerOverlappingWindows.append(window.uniqueID)
            self._updateOverlappingWindowsCount(1)


class CrewPersonalCaseTabLogger(CrewBringToFrontViewLogger):
    __slots__ = ('_parentView', '_layoutID', '_isTabActive')

    def __init__(self, currentView, parentView, layoutID, parentViewKey=None):
        self._parentView = parentView
        self._layoutID = layoutID
        self._isTabActive = False
        super(CrewPersonalCaseTabLogger, self).__init__(currentView, layoutID, parentViewKey)

    @ifUILoggingEnabled()
    def initialize(self):
        self.gui.windowsManager.onWindowStatusChanged += self._onWindowStatusChanged
        self._parentView.onTabChanged += self._onTabChanged

    def finalize(self):
        self._stopTabLogging()
        self._parentView.onTabChanged -= self._onTabChanged
        self.gui.windowsManager.onWindowStatusChanged -= self._onWindowStatusChanged
        self._clear()

    def _pause(self):
        if self._isTabActive:
            super(CrewPersonalCaseTabLogger, self)._pause()

    def _resume(self):
        if self._isTabActive:
            super(CrewPersonalCaseTabLogger, self)._resume()

    def _clear(self):
        super(CrewPersonalCaseTabLogger, self)._clear()
        self._isTabActive = False

    def _startTabLogging(self):
        if not self._isTabActive:
            self._isTabActive = True
            self._viewOpened()

    def _stopTabLogging(self):
        if self._isTabActive:
            self._isTabActive = False
            self._viewClosed()

    def _onTabChanged(self, tabID, prevTabKey=None):
        if self._layoutID == tabID:
            if prevTabKey is not None:
                self._parentViewKey = prevTabKey
            self._startTabLogging()
        else:
            self._stopTabLogging()
        return


class CrewDialogLogger(CrewViewLogger):
    __slots__ = ('_additionalInfo',)
    _CLOSE_REASON_ESCAPE = 'escape'

    def __init__(self, currentView, currentViewKey=None, parentViewKey=None, additionalInfo=None):
        self._additionalInfo = additionalInfo
        super(CrewDialogLogger, self).__init__(currentView, currentViewKey, parentViewKey)

    @ifUILoggingEnabled()
    def logClick(self, item, parentScreen=None, info=None):
        return super(CrewDialogLogger, self).logClick(item, parentScreen, info or self._additionalInfo)

    @ifUILoggingEnabled()
    def logClose(self, reason):
        self.logNavigationButtonClick(CrewNavigationButtons.ESC if reason == self._CLOSE_REASON_ESCAPE else CrewNavigationButtons.CLOSE)

    def _viewOpened(self, info=None):
        super(CrewDialogLogger, self)._viewOpened(info or self._additionalInfo)

    def _viewClosed(self, info=None):
        super(CrewDialogLogger, self)._viewClosed(info or self._additionalInfo)


class CrewTooltipLogger(CrewMetricsLogger):
    __slots__ = ('_parentViewKey', '_currentTooltip', '_previousTooltipId', '_tooltipIdMapping', '_openedTooltipId', '_openedTooltipArgs')
    appLoader = dependency.descriptor(IAppLoader)

    def __init__(self, parentViewKey, tooltipIdMapping):
        super(CrewTooltipLogger, self).__init__()
        self._parentViewKey = CrewViewKeys.HANGAR if parentViewKey is None else parentViewKey
        self._tooltipIdMapping = tooltipIdMapping
        self._currentTooltip = None
        self._previousTooltipId = None
        self._openedTooltipId = None
        self._openedTooltipArgs = None
        return

    @ifUILoggingEnabled()
    def onBeforeTooltipOpened(self, tooltipId):
        if tooltipId in self._tooltipIdMapping:
            self._openedTooltipId = tooltipId
            self._openedTooltipArgs = None
        return

    @property
    def tooltipMgr(self):
        app = self.appLoader.getApp()
        return app.getToolTipMgr() if app is not None else None

    @ifUILoggingEnabled()
    def initialize(self):
        if self.tooltipMgr is not None:
            self.tooltipMgr.onHide += self.__onHideTooltip
            self.tooltipMgr.onShow += self.__onShowTooltip
        return

    def finalize(self):
        if self.tooltipMgr is not None:
            self.tooltipMgr.onHide -= self.__onHideTooltip
            self.tooltipMgr.onShow -= self.__onShowTooltip
        self._clear()
        return

    @ifUILoggingEnabled()
    def logClick(self, item):
        self.log(action=CrewLogActions.CLICK, item=item, parentScreen=self._parentViewKey)

    def _clear(self):
        self._parentViewKey = None
        self._tooltipIdMapping = None
        self._currentTooltip = None
        self._previousTooltipId = None
        self._openedTooltipId = None
        self._openedTooltipArgs = None
        return

    def _stop(self, item, info=None):
        self.stopAction(action=CrewLogActions.VIEWED, item=item, parentScreen=self._parentViewKey, timeLimit=MIN_VIEW_TIME, info=info)

    def __onShowTooltip(self, tooltipID, args, isAlt):
        hasSameArgs = self._openedTooltipArgs is None or id(args) == id(self._openedTooltipArgs)
        if self._openedTooltipId == tooltipID and hasSameArgs:
            self._openedTooltipArgs = args
            self.startAction(CrewLogActions.VIEWED)
            self._currentTooltip = (tooltipID, isAlt)
        else:
            self._openedTooltipArgs = None
            self._openedTooltipId = None
        return

    def __onHideTooltip(self, _):
        if not self._currentTooltip:
            return
        else:
            tooltipId, isAlt = self._currentTooltip
            item = self._tooltipIdMapping.get(tooltipId)
            if item:
                self._stop(item, TooltipAdditionalInfo.ALT if isAlt else TooltipAdditionalInfo.MAIN)
            self._currentTooltip = None
            return


class CrewTankmanInfoLogger(CrewTooltipLogger):
    __slots__ = ('__isDisabled',)

    def __init__(self, isDisabled):
        self.__isDisabled = isDisabled
        super(CrewTankmanInfoLogger, self).__init__(CrewViewKeys.PERSONAL_FILE, {TooltipConstants.TANKMAN: CrewPersonalFileKeys.TANKMAN_TOOLTIP})

    @property
    def disabled(self):
        return self.__isDisabled or super(CrewTankmanInfoLogger, self).disabled


class CrewWidgetLogger(CrewTooltipLogger):
    __slots__ = ()

    def __init__(self, currentViewID):
        super(CrewWidgetLogger, self).__init__(LAYOUT_ID_TO_ITEM.get(currentViewID), {TooltipConstants.TANKMAN: CrewWidgetKeys.TANKMAN_TOOLTIP})

    @ifUILoggingEnabled()
    def updateParentViewKey(self, currentViewID):
        self._parentViewKey = LAYOUT_ID_TO_ITEM.get(currentViewID)


class CrewMemberChangeLogger(CrewTooltipLogger):
    __slots__ = ()

    def __init__(self):
        super(CrewMemberChangeLogger, self).__init__(CrewViewKeys.MEMBER_CHANGE, {TooltipConstants.TANKMAN: CrewMemberChangeKeys.TANKMAN_CARD_TOOLTIP,
         TooltipConstants.TANKMAN_NOT_RECRUITED: CrewMemberChangeKeys.TANKMAN_CARD_TOOLTIP})

    def logDismissedTooltip(self, window):
        self.startAction(CrewLogActions.VIEWED)
        window.onStatusChanged += self._onDismissedStatusChange

    def _onDismissedStatusChange(self, status):
        if status == WindowStatus.DESTROYED:
            self._stop(CrewMemberChangeKeys.DISMISSED_TOGGLE_TOOLTIP)
