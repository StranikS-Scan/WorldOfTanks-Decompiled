# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/uilogging/newbie_hints/loggers.py
import BigWorld
import typing
import logging
from helpers import dependency
from wotdecorators import noexcept
from uilogging.constants import DEFAULT_LOGGER_NAME
from uilogging.base.logger import MetricsLogger, ifUILoggingEnabled
from uilogging.newbie_hints.constants import NewbieHintsLogActions, CheckBoxState, SettingsNewbieTooltips, NewbieHintsLogItems, NewbieHintsLogViews, FEATURE_NEWBIE_HINTS, FEATURE_NEWBIE_HINTS_SETTINGS, TOOLTIP_ID_MAPPING, SETTINGS_CHECKBOX_KEYS_MAPPING, TOOLTIP_MIN_VIEW_TIME, NEWBIE_SETTINGS_RETICLE_PARAMS, NEWBIE_HINTS_RETICLE_MAPPING
from skeletons.gui.app_loader import IAppLoader
from skeletons.account_helpers.settings_core import ISettingsCore
from account_helpers.settings_core.settings_constants import GAME, AIM
from PlayerEvents import g_playerEvents
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from hints.battle.schemas.newbie import NewbieClientHintModel
if typing.TYPE_CHECKING:
    from gui.battle_control.controllers.battle_hints.queues import BattleHint
    from gui.Scaleform.framework.tooltip_mgr import ToolTip
_logger = logging.getLogger('{0}.{1}'.format(DEFAULT_LOGGER_NAME, FEATURE_NEWBIE_HINTS.upper()))

class NewbieHintsSettingsUILogger(MetricsLogger):
    __slots__ = ()
    settingsCore = dependency.descriptor(ISettingsCore)

    def __init__(self):
        super(NewbieHintsSettingsUILogger, self).__init__(FEATURE_NEWBIE_HINTS_SETTINGS)

    def resetButtonClicked(self):
        self.log(action=NewbieHintsLogActions.CLICK, item=NewbieHintsLogItems.BTN_RESET_VIEWED_HINTS, parentScreen=NewbieHintsLogViews.SETTINGS)
        _logger.debug('resetButtonClicked')

    @noexcept
    @ifUILoggingEnabled()
    def onSettingsChanged(self, diff):
        for key in set(diff).intersection(SETTINGS_CHECKBOX_KEYS_MAPPING):
            item = SETTINGS_CHECKBOX_KEYS_MAPPING[key]
            state = CheckBoxState.ENABLE if self.settingsCore.getSetting(key) else CheckBoxState.DISABLE
            self.log(NewbieHintsLogActions.APPLY, item, NewbieHintsLogViews.SETTINGS, itemState=state)
            _logger.debug('handle item [%s]', item.value)

        if self.settingsCore.getSetting(GAME.NEWBIE_BATTLE_HINTS):
            for reticleType in set(diff).intersection([AIM.ARCADE, AIM.SNIPER]):
                for paramName in set(diff[reticleType]).intersection(NEWBIE_SETTINGS_RETICLE_PARAMS):
                    parentScreen = NEWBIE_HINTS_RETICLE_MAPPING.get(reticleType)
                    self.log(NewbieHintsLogActions.APPLY, paramName, parentScreen, info=str(diff[reticleType][paramName]))
                    _logger.debug('handle item [%s], screen [%s]', paramName, parentScreen.value)


class NewbieHintsSettingsTooltipsUILogger(MetricsLogger):
    __slots__ = ('_tooltipIdMapping', '_currentTooltip')
    appLoader = dependency.descriptor(IAppLoader)

    def __init__(self):
        super(NewbieHintsSettingsTooltipsUILogger, self).__init__(FEATURE_NEWBIE_HINTS_SETTINGS)
        self._currentTooltip = None
        return

    @property
    def tooltipMgr(self):
        app = self.appLoader.getApp()
        return app.getToolTipMgr() if app is not None else None

    def initialize(self):
        if self.tooltipMgr is not None:
            self.tooltipMgr.onHide += self._onHideTooltip
            self.tooltipMgr.onShow += self._onShowTooltip
        return

    def finalize(self):
        if self.tooltipMgr is not None:
            self.tooltipMgr.onHide -= self._onHideTooltip
            self.tooltipMgr.onShow -= self._onShowTooltip
        self._currentTooltip = None
        return

    @noexcept
    @ifUILoggingEnabled()
    def _onShowTooltip(self, tooltipID, args, _):
        if tooltipID in (SettingsNewbieTooltips.PREBATTLE_HINTS, SettingsNewbieTooltips.INBATTLE_HINTS):
            self._currentTooltip = tooltipID
        elif tooltipID == TOOLTIPS_CONSTANTS.SETTINGS_CONTROL and args and args[0] == SettingsNewbieTooltips.INBATTLE_HINTS_RESET:
            self._currentTooltip = args[0]
        else:
            self._currentTooltip = None
            return
        self.startAction(NewbieHintsLogActions.WATCHED)
        item = TOOLTIP_ID_MAPPING.get(self._currentTooltip)
        _logger.debug('_onShowTooltip [%s], item [%s]', self._currentTooltip, item.value if item else None)
        return

    @noexcept
    def _onHideTooltip(self, _):
        if not self._currentTooltip:
            return
        else:
            item = TOOLTIP_ID_MAPPING.get(self._currentTooltip)
            if item:
                self.stopAction(NewbieHintsLogActions.WATCHED, item, NewbieHintsLogViews.SETTINGS, timeLimit=TOOLTIP_MIN_VIEW_TIME)
                _logger.debug('_onHideTooltip [%s], item [%s]', self._currentTooltip, item.value)
            else:
                _logger.error('_onHideTooltip unknown logging item for tooltip [%s]', self._currentTooltip)
            self._currentTooltip = None
            return


class NewbieHintsShownUILogger(MetricsLogger):
    __slots__ = ('_hint',)

    def __init__(self):
        super(NewbieHintsShownUILogger, self).__init__(FEATURE_NEWBIE_HINTS)
        self._hint = None
        return

    def initialize(self):
        g_playerEvents.onShowBattleHint += self._onHintShown
        g_playerEvents.onHideBattleHint += self._onHintHide

    def finalize(self):
        g_playerEvents.onShowBattleHint -= self._onHintShown
        g_playerEvents.onHideBattleHint -= self._onHintHide

    @noexcept
    @ifUILoggingEnabled()
    def _onHintShown(self, battleHint):
        if not isinstance(battleHint.model, NewbieClientHintModel):
            return
        self._hint = battleHint
        self.startAction(NewbieHintsLogActions.WATCHED)
        _logger.debug('onHintShown [%s]', self._hint.model.props.name)

    @noexcept
    def _onHintHide(self, battleHint):
        if self._hint is not battleHint:
            return
        else:
            hintName = battleHint.model.props.name
            self.stopAction(NewbieHintsLogActions.WATCHED, hintName, NewbieHintsLogViews.BATTLE, info=str(BigWorld.player().arenaUniqueID))
            _logger.debug('_onHintHide [%s]', hintName)
            self._hint = None
            return
