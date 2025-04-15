# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fall_tanks/scripts/client/fall_tanks/gui/Scaleform/daapi/view/battle/hint_panel/plugins.py
import CommandMapping
from account_helpers import AccountSettings
from account_helpers.AccountSettings import HINTS_LEFT
from constants import ARENA_PERIOD
from gui.Scaleform.daapi.view.battle.shared.hint_panel.hint_panel_plugin import HintPriority
from gui.Scaleform.daapi.view.battle.shared.hint_panel.plugins import ButtonPlugin
from gui.impl import backport
from gui.impl.gen import R
from fun_random.gui.Scaleform.daapi.view.battle.hint_panel.plugins import FunRandomHelpPlugin
from fall_tanks.gui.fall_tanks_account_settings import AccountSettingsKeys
from fall_tanks.gui.Scaleform.daapi.view.battle.hint_panel.hint_panel_plugin import VehicleEvacuationHintContext

def createPlugins():
    plugins = {}
    if FunRandomHelpPlugin.isSuitable():
        plugins['fallTanksHelpHint'] = FunRandomHelpPlugin
    if FallTanksEvacuationPlugin.isSuitable():
        plugins['fallTanksEvacuationHint'] = FallTanksEvacuationPlugin
    return plugins


class FallTanksEvacuationPlugin(ButtonPlugin):
    _PERIODS = (ARENA_PERIOD.BATTLE,)
    __LOCALE_RES = R.strings.fall_tanks.buttonHint.evacuation

    def __init__(self, parentObj):
        super(FallTanksEvacuationPlugin, self).__init__(CommandMapping.CMD_REQUEST_RECOVERY, AccountSettingsKeys.FALL_TANKS_HINTS, AccountSettingsKeys.VEHICLE_EVACUATION, self.__LOCALE_RES, HintPriority.HELP, VehicleEvacuationHintContext.FALL_TANKS_EVACUATION, parentObj)

    def updateMapping(self):
        if self._isActive:
            self._hide()

    def setPeriod(self, period):
        if not self._isActive:
            return
        self.__isInDisplayPeriod = period in self._PERIODS
        if self._isVisible and not self.__isInDisplayPeriod:
            self._hide()
        elif not self._isVisible and self.__isInDisplayPeriod:
            self._showHint()

    @classmethod
    def isSuitable(cls):
        fallTanksSettings = AccountSettings.getSettings(AccountSettingsKeys.FALL_TANKS_HINTS)
        settingsKey = AccountSettingsKeys.VEHICLE_EVACUATION
        return settingsKey not in fallTanksSettings or fallTanksSettings[settingsKey][HINTS_LEFT] > 0

    def _getDefaultKeyMessage(self):
        return backport.text(self.__LOCALE_RES.noBindingKey())
