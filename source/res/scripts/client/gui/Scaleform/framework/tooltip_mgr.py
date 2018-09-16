# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/framework/tooltip_mgr.py
import logging
from gui.Scaleform.framework.entities.abstract.ToolTipMgrMeta import ToolTipMgrMeta
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.shared import events
from gui.shared.tooltips import builders
from gui.app_loader import g_appLoader
_logger = logging.getLogger(__name__)

class ToolTip(ToolTipMgrMeta):

    def __init__(self, settings, *noTooltipSpaceIDs):
        super(ToolTip, self).__init__()
        self._areTooltipsDisabled = False
        self._isAllowedTypedTooltip = True
        self._noTooltipSpaceIDs = noTooltipSpaceIDs
        self._complex = builders.ComplexBuilder(TOOLTIPS_CONSTANTS.DEFAULT, TOOLTIPS_CONSTANTS.COMPLEX_UI)
        self._builders = builders.LazyBuildersCollection(settings)
        self._builders.addBuilder(builders.SimpleBuilder(TOOLTIPS_CONSTANTS.DEFAULT, TOOLTIPS_CONSTANTS.COMPLEX_UI))
        self._dynamic = {}

    def show(self, data, linkage):
        self.as_showS(data, linkage)

    def onCreateTypedTooltip(self, tooltipType, args, stateType):
        if self._areTooltipsDisabled:
            return
        elif not self._isAllowedTypedTooltip:
            return
        else:
            builder = self._builders.getBuilder(tooltipType)
            if builder is not None:
                data = builder.build(self, stateType, *args)
            else:
                _logger.warning('Tooltip can not be displayed: type "%s" is not found', tooltipType)
                return
            if data is not None and data.isDynamic():
                data.changeVisibility(True)
                if tooltipType not in self._dynamic:
                    self._dynamic[tooltipType] = data
            return

    def onCreateComplexTooltip(self, tooltipID, stateType):
        if self._areTooltipsDisabled:
            return
        self._complex.build(self, stateType, tooltipID)

    def onHideTooltip(self, tooltipId):
        if not self._areTooltipsDisabled and tooltipId in self._dynamic:
            self._dynamic[tooltipId].changeVisibility(False)

    def _populate(self):
        super(ToolTip, self)._populate()
        g_appLoader.onGUISpaceEntered += self.__onGUISpaceEntered
        self.addListener(events.AppLifeCycleEvent.CREATING, self.__onAppCreating)

    def _dispose(self):
        self._builders.clear()
        g_appLoader.onGUISpaceEntered -= self.__onGUISpaceEntered
        self.removeListener(events.AppLifeCycleEvent.CREATING, self.__onAppCreating)
        while self._dynamic:
            _, data = self._dynamic.popitem()
            data.stopUpdates()

        super(ToolTip, self)._dispose()

    def __onGUISpaceEntered(self, spaceID):
        self._isAllowedTypedTooltip = spaceID not in self._noTooltipSpaceIDs

    def __onAppCreating(self, appNS):
        if self.app.appNS != appNS:
            self._areTooltipsDisabled = True
