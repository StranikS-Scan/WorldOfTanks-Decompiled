# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/uilogging/epic_battle/loggers.py
from typing import TYPE_CHECKING
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from helpers import dependency
from skeletons.gui.app_loader import IAppLoader
from uilogging.base.logger import MetricsLogger
from uilogging.epic_battle.constants import FEATURE, EpicBattleLogActions, EpicBattleLogItemStates
from wotdecorators import noexcept
if TYPE_CHECKING:
    from typing import Dict, Tuple, Optional

class EpicBattleLogger(MetricsLogger):
    __slots__ = ()
    TIME_LIMIT = 2.0

    def __init__(self):
        super(EpicBattleLogger, self).__init__(FEATURE)


class EpicBattleTooltipLogger(EpicBattleLogger):
    __slots__ = ('_openedTooltip', '_parentScreen', '_additionalInfo', '_allowedTooltips', '_isAdvancedTooltip', '_skipAdditionalInfoTooltips', '_overrideTooltipsId')
    _appLoader = dependency.descriptor(IAppLoader)

    def __init__(self):
        super(EpicBattleTooltipLogger, self).__init__()
        self._openedTooltip = None
        self._parentScreen = None
        self._additionalInfo = None
        self._isAdvancedTooltip = False
        self._allowedTooltips = None
        self._skipAdditionalInfoTooltips = None
        self._overrideTooltipsId = {}
        return

    def initialize(self, parentScreen, allowedTooltips=None, skipAdditionalInfoTooltips=None, overrideTooltipsId=None):
        self._parentScreen = parentScreen
        self._allowedTooltips = allowedTooltips
        self._skipAdditionalInfoTooltips = skipAdditionalInfoTooltips
        self._overrideTooltipsId = overrideTooltipsId if overrideTooltipsId else {}
        app = self._appLoader.getApp()
        if app is not None:
            tooltipMgr = app.getToolTipMgr()
            if tooltipMgr is not None:
                tooltipMgr.onHide += self.__onHideTooltip
                tooltipMgr.onShow += self.__onShowTooltip
        return

    def reset(self):
        super(EpicBattleTooltipLogger, self).reset()
        self._parentScreen = None
        self._openedTooltip = None
        self._additionalInfo = None
        self._isAdvancedTooltip = False
        self._allowedTooltips = None
        self._skipAdditionalInfoTooltips = None
        self._overrideTooltipsId = {}
        app = self._appLoader.getApp()
        if app is not None:
            tooltipMgr = app.getToolTipMgr()
            if tooltipMgr is not None:
                tooltipMgr.onHide -= self.__onHideTooltip
                tooltipMgr.onShow -= self.__onShowTooltip
        return

    @noexcept
    def __onHideTooltip(self, tooltip, *_):
        if self._openedTooltip and self._openedTooltip == tooltip:
            self._openedTooltip = None
            itemName = self._overrideTooltipsId.get(tooltip, tooltip)
            self.stopAction(EpicBattleLogActions.TOOLTIP_WATCHED.value, itemName, self._parentScreen, info=self._additionalInfo, timeLimit=self.TIME_LIMIT, itemState=EpicBattleLogItemStates.ADVANCED if self._isAdvancedTooltip else None)
            self._isAdvancedTooltip = False
        return

    @noexcept
    def __onShowTooltip(self, tooltip, args, isAdvancedKeyPressed, *_):
        if self._allowedTooltips and tooltip not in self._allowedTooltips:
            return
        else:
            self._isAdvancedTooltip = isAdvancedKeyPressed or self._isAdvancedTooltip
            self._openedTooltip = tooltip
            isSkipped = self._skipAdditionalInfoTooltips is not None and tooltip in self._skipAdditionalInfoTooltips
            self._additionalInfo = str(args[1 if tooltip == TOOLTIPS_CONSTANTS.NOT_ENOUGH_MONEY else 0]) if args and not isSkipped else None
            self.startAction(EpicBattleLogActions.TOOLTIP_WATCHED.value)
            return
