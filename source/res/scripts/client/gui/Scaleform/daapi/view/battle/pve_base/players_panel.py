# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/pve_base/players_panel.py
from constants import ARENA_PERIOD
from gui.Scaleform.daapi.view.meta.PvePlayersPanelMeta import PvePlayersPanelMeta
from gui.battle_control.controllers.vse_hud_settings_ctrl.settings.respawn_hud import RespawnHUDClientModel
from pve_battle_hud import WidgetType
_RIGHT_PANEL_VISIBLE_PERIODS = (ARENA_PERIOD.BATTLE, ARENA_PERIOD.AFTERBATTLE)

class PvePlayersPanel(PvePlayersPanelMeta):

    def setPeriod(self, period):
        super(PvePlayersPanel, self).setPeriod(period)
        self.as_setRightPanelVisibilityS(period in _RIGHT_PANEL_VISIBLE_PERIODS)

    def _populate(self):
        super(PvePlayersPanel, self)._populate()
        settingsCtrl = self.sessionProvider.dynamic.vseHUDSettings
        if settingsCtrl:
            settingsCtrl.onSettingsChanged += self._settingsChangeHandler
        self._settingsChangeHandler(WidgetType.RESPAWN_HUD)

    def _dispose(self):
        settingsCtrl = self.sessionProvider.dynamic.vseHUDSettings
        if settingsCtrl:
            settingsCtrl.onSettingsChanged -= self._settingsChangeHandler
        super(PvePlayersPanel, self)._dispose()

    def _settingsChangeHandler(self, settingsID):
        settingsCtrl = self.sessionProvider.dynamic.vseHUDSettings
        if settingsCtrl is None:
            return
        else:
            if settingsID == WidgetType.RESPAWN_HUD:
                respawnHUDSettings = settingsCtrl.getSettings(WidgetType.RESPAWN_HUD)
                if not respawnHUDSettings:
                    return
                self.as_setCountLivesVisibilityS(respawnHUDSettings.showLivesInAlliesList)
            return
