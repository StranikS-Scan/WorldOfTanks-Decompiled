# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/uilogging/epic_battle/loggers.py
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from helpers import dependency
from skeletons.gui.app_loader import IAppLoader
from uilogging.base.logger import BaseLogger
from uilogging.base.mixins import TimedActionMixin
from uilogging.core.core_constants import LogLevels
from uilogging.epic_battle.constants import FEATURE, METRICS, EpicBattleLogActions
from wotdecorators import noexcept

class EpicBattleLogger(TimedActionMixin, BaseLogger):

    def __init__(self):
        super(EpicBattleLogger, self).__init__(FEATURE, METRICS)

    @noexcept
    def log(self, action, item, parentScreen, additionalInfo=None, timeSpent=0, loglevel=LogLevels.INFO):
        params = {'parent_screen': parentScreen,
         'additional_info': additionalInfo,
         'partner_id': None,
         'item_state': None}
        return super(EpicBattleLogger, self).log(action=action, item=item, timeSpent=timeSpent, loglevel=loglevel, **params)


class EpicBattleTooltipLogger(EpicBattleLogger):
    _appLoader = dependency.descriptor(IAppLoader)
    TIME_LIMIT = 2.0

    def __init__(self):
        super(EpicBattleTooltipLogger, self).__init__()
        self._openedTooltip = None
        self._parentScreen = None
        self._additionalInfo = None
        return

    def initialize(self, parentScreen):
        self._parentScreen = parentScreen
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
            self.stopAction(EpicBattleLogActions.TOOLTIP_WATCHED.value, timeLimit=self.TIME_LIMIT, item=tooltip, parentScreen=self._parentScreen, additionalInfo=self._additionalInfo)
        return

    @noexcept
    def __onShowTooltip(self, tooltip, args, *_):
        self._openedTooltip = tooltip
        self._additionalInfo = str(args[1 if tooltip == TOOLTIPS_CONSTANTS.NOT_ENOUGH_MONEY else 0]) if args else None
        self.startAction(EpicBattleLogActions.TOOLTIP_WATCHED.value)
        return
