# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/framework/tooltip_mgr.py
import inspect
import itertools
import logging
import Keys
from Event import SafeEvent, EventManager
from gui import InputHandler
from gui.Scaleform.framework.entities.abstract.ToolTipMgrMeta import ToolTipMgrMeta
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.shared import events
from gui.shared.tooltips import builders
from helpers import dependency, uniprof
from helpers.gui_utils import getMousePosition
from skeletons.gui.app_loader import IAppLoader
from skeletons.gui.impl import IGuiLoader
from soft_exception import SoftException
_logger = logging.getLogger(__name__)
UNIPROF_REGION_COLOR = 9611473

class ToolTip(ToolTipMgrMeta):
    appLoader = dependency.descriptor(IAppLoader)
    gui = dependency.descriptor(IGuiLoader)

    def __init__(self, settings, advComplexSettings, *noTooltipSpaceIDs):
        super(ToolTip, self).__init__()
        self._areTooltipsDisabled = False
        self._isAllowedTypedTooltip = True
        self._noTooltipSpaceIDs = noTooltipSpaceIDs
        self._complex = builders.ComplexBuilder(TOOLTIPS_CONSTANTS.DEFAULT, TOOLTIPS_CONSTANTS.COMPLEX_UI, advComplexSettings)
        self._builders = builders.LazyBuildersCollection(settings)
        self._builders.addBuilder(builders.SimpleBuilder(TOOLTIPS_CONSTANTS.DEFAULT, TOOLTIPS_CONSTANTS.COMPLEX_UI))
        self._dynamic = {}
        self.__fastRedraw = False
        self.__isAdvancedKeyPressed = False
        self.__isComplex = False
        self.__tooltipID = None
        self.__args = None
        self.__stateType = None
        self.__tooltipRegion = None
        self.__tooltipWindowId = 0
        self.__em = EventManager()
        self.onShow = SafeEvent(self.__em)
        self.onHide = SafeEvent(self.__em)
        return

    def show(self, data, linkage):
        self.as_showS(data, linkage, self.__fastRedraw)

    def showWulfTooltip(self, toolType, args):
        mouseX, mouseY = getMousePosition()
        self.onCreateWulfTooltip(toolType, args, mouseX, mouseY)

    def hide(self):
        self.__destroyTooltipWindow()
        self.as_hideS()

    def handleKeyEvent(self, event):
        if not self.isReadyToHandleKey(event):
            return
        tooltipType = self.__tooltipID
        args = self.__args
        isSupportAdvanced = self.isSupportAdvanced(tooltipType, *args)
        if isSupportAdvanced:
            self.__fastRedraw = True
            if self.__isComplex:
                self.onCreateComplexTooltip(tooltipType, self.__stateType)
            else:
                self.onCreateTypedTooltip(tooltipType, args, self.__stateType)

    def isReadyToHandleKey(self, event):
        altPressed = event.key == Keys.KEY_LALT or event.key == Keys.KEY_RALT
        self.__isAdvancedKeyPressed = event.isKeyDown() and altPressed
        return self.__tooltipID is not None and altPressed

    def getTypedTooltipDefaultBuildArgs(self, tooltipType):
        builder = self._builders.getBuilder(tooltipType)
        if builder is None:
            raise SoftException('Builder for tooltip: type "%s" is not found', tooltipType)
        provider = builder.provider
        if provider is None:
            raise SoftException('"%s" does not have any provider', builder.__name__)
        spec = inspect.getargspec(provider.context.buildItem)
        return tuple(reversed([ (argName, defaultValue) for argName, defaultValue in itertools.izip_longest(reversed(spec.args), reversed(spec.defaults or [])) if argName != 'self' ]))

    def onCreateTypedTooltip(self, tooltipType, args, stateType):
        if self._areTooltipsDisabled:
            return
        elif not self._isAllowedTypedTooltip:
            return
        else:
            if self.__tooltipRegion is None:
                self.__tooltipRegion = 'Typed tooltip "{}"'.format(tooltipType)
                uniprof.enterToRegion(self.__tooltipRegion, UNIPROF_REGION_COLOR)
            builder = self._builders.getBuilder(tooltipType)
            if builder is not None:
                data = builder.build(self, stateType, self.__isAdvancedKeyPressed, *args)
            else:
                _logger.warning('Tooltip can not be displayed: type "%s" is not found', tooltipType)
                return
            self.__cacheTooltipData(False, tooltipType, args, stateType)
            self.onShow(tooltipType, args, self.__isAdvancedKeyPressed)
            if data is not None and data.isDynamic():
                data.changeVisibility(True)
                if tooltipType not in self._dynamic:
                    self._dynamic[tooltipType] = data
            return

    def onCreateWulfTooltip(self, tooltipType, args, x, y):
        if not self._isAllowedTypedTooltip:
            return
        else:
            builder = self._builders.getBuilder(tooltipType)
            if builder is not None:
                data = builder.build(self, None, self.__isAdvancedKeyPressed, *args)
            else:
                _logger.warning('Tooltip can not be displayed: type "%s" is not found', tooltipType)
                return
            window = data.getDisplayableData(*args)
            window.load()
            window.move(x, y)
            self.__tooltipWindowId = window.uniqueID
            self.onShow(tooltipType, args, self.__isAdvancedKeyPressed)
            return

    def onCreateComplexTooltip(self, tooltipID, stateType):
        if self._areTooltipsDisabled:
            return
        else:
            if self.__tooltipRegion is None:
                self.__tooltipRegion = 'Complex tooltip "{}"'.format(tooltipID)
                uniprof.enterToRegion(self.__tooltipRegion, UNIPROF_REGION_COLOR)
            self._complex.build(self, stateType, self.__isAdvancedKeyPressed, tooltipID)
            self.__cacheTooltipData(True, tooltipID, tuple(), stateType)
            self.onShow(tooltipID, None, self.__isAdvancedKeyPressed)
            return

    def onHideTooltip(self, tooltipId):
        if not self._areTooltipsDisabled and tooltipId in self._dynamic:
            self._dynamic[tooltipId].changeVisibility(False)
        hideTooltipId = tooltipId or self.__tooltipID or ''
        self.__tooltipID = None
        self.__fastRedraw = False
        self.__destroyTooltipWindow()
        if self.__tooltipRegion is not None:
            uniprof.exitFromRegion(self.__tooltipRegion)
            self.__tooltipRegion = None
        self.onHide(hideTooltipId)
        return

    def _populate(self):
        super(ToolTip, self)._populate()
        self.appLoader.onGUISpaceEntered += self.__onGUISpaceEntered
        self.addListener(events.AppLifeCycleEvent.CREATING, self.__onAppCreating)
        InputHandler.g_instance.onKeyDown += self.handleKeyEvent
        InputHandler.g_instance.onKeyUp += self.handleKeyEvent

    def _dispose(self):
        self._builders.clear()
        self.appLoader.onGUISpaceEntered -= self.__onGUISpaceEntered
        self.removeListener(events.AppLifeCycleEvent.CREATING, self.__onAppCreating)
        while self._dynamic:
            _, data = self._dynamic.popitem()
            data.stopUpdates()

        InputHandler.g_instance.onKeyDown -= self.handleKeyEvent
        InputHandler.g_instance.onKeyUp -= self.handleKeyEvent
        self.__destroyTooltipWindow()
        self.__em.clear()
        super(ToolTip, self)._dispose()

    def __onGUISpaceEntered(self, spaceID):
        self._isAllowedTypedTooltip = spaceID not in self._noTooltipSpaceIDs

    def __onAppCreating(self, appNS):
        if self.app.appNS != appNS:
            self._areTooltipsDisabled = True

    def isSupportAdvanced(self, tooltipType, *args):
        builder = self._complex if self.__isComplex else self._builders.getBuilder(tooltipType)
        return False if builder is None else builder.supportAdvanced(tooltipType, *args)

    def __cacheTooltipData(self, isComplex, tooltipID, args, stateType):
        self.__isComplex = isComplex
        self.__tooltipID = tooltipID
        self.__args = args
        self.__stateType = stateType

    def __destroyTooltipWindow(self):
        if self.__tooltipWindowId:
            window = self.gui.windowsManager.getWindow(self.__tooltipWindowId)
            if window is not None:
                window.destroy()
            self.__tooltipWindowId = 0
        return
