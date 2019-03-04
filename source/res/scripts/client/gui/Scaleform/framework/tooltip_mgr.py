# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/framework/tooltip_mgr.py
import logging
import Keys
from gui.Scaleform.framework.entities.abstract.ToolTipMgrMeta import ToolTipMgrMeta
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.shared import events
from gui.shared.tooltips import builders
from gui.app_loader import g_appLoader
from gui import InputHandler
_logger = logging.getLogger(__name__)

class ToolTip(ToolTipMgrMeta):

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
        return

    def show(self, data, linkage):
        self.as_showS(data, linkage, self.__fastRedraw)

    def hide(self):
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

    def onCreateTypedTooltip(self, tooltipType, args, stateType):
        if self._areTooltipsDisabled:
            return
        elif not self._isAllowedTypedTooltip:
            return
        else:
            builder = self._builders.getBuilder(tooltipType)
            if builder is not None:
                data = builder.build(self, stateType, self.__isAdvancedKeyPressed, *args)
            else:
                _logger.warning('Tooltip can not be displayed: type "%s" is not found', tooltipType)
                return
            self.__cacheTooltipData(False, tooltipType, args, stateType)
            if data is not None and data.isDynamic():
                data.changeVisibility(True)
                if tooltipType not in self._dynamic:
                    self._dynamic[tooltipType] = data
            return

    def onCreateComplexTooltip(self, tooltipID, stateType):
        if self._areTooltipsDisabled:
            return
        self._complex.build(self, stateType, self.__isAdvancedKeyPressed, tooltipID)
        self.__cacheTooltipData(True, tooltipID, tuple(), stateType)

    def onHideTooltip(self, tooltipId):
        if not self._areTooltipsDisabled and tooltipId in self._dynamic:
            self._dynamic[tooltipId].changeVisibility(False)
        self.__tooltipID = None
        self.__fastRedraw = False
        return

    def _populate(self):
        super(ToolTip, self)._populate()
        g_appLoader.onGUISpaceEntered += self.__onGUISpaceEntered
        self.addListener(events.AppLifeCycleEvent.CREATING, self.__onAppCreating)
        InputHandler.g_instance.onKeyDown += self.handleKeyEvent
        InputHandler.g_instance.onKeyUp += self.handleKeyEvent

    def _dispose(self):
        self._builders.clear()
        g_appLoader.onGUISpaceEntered -= self.__onGUISpaceEntered
        self.removeListener(events.AppLifeCycleEvent.CREATING, self.__onAppCreating)
        while self._dynamic:
            _, data = self._dynamic.popitem()
            data.stopUpdates()

        InputHandler.g_instance.onKeyDown -= self.handleKeyEvent
        InputHandler.g_instance.onKeyUp -= self.handleKeyEvent
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
