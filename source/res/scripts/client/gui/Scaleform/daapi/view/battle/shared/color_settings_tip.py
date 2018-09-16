# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/shared/color_settings_tip.py
from account_helpers.AccountSettings import AccountSettings, COLOR_SETTINGS_SHOWS_COUNT
from constants import ARENA_PERIOD
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.meta.ColorSettingsTipPanelMeta import ColorSettingsTipPanelMeta
from gui.Scaleform.locale.INGAME_GUI import INGAME_GUI
from gui.battle_control.controllers.period_ctrl import IAbstractPeriodView
from gui.shared import EVENT_BUS_SCOPE
from gui.shared.events import LoadViewEvent, GameEvent
from gui.shared.formatters import text_styles
from gui.shared.utils.graphics import isRendererPipelineDeferred
from helpers import dependency
from helpers import i18n
from skeletons.gui.battle_session import IBattleSessionProvider

class ColorSettingsTipPanel(ColorSettingsTipPanelMeta, IAbstractPeriodView):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)
    MAX_BATTLES_COUNT = 5

    def __init__(self, ctx=None):
        super(ColorSettingsTipPanel, self).__init__()
        battlesCount = AccountSettings.getSettings(COLOR_SETTINGS_SHOWS_COUNT)
        self.__isActive = battlesCount <= self.MAX_BATTLES_COUNT and isRendererPipelineDeferred()
        if self.__isActive:
            AccountSettings.setSettings(COLOR_SETTINGS_SHOWS_COUNT, battlesCount + 1)

    def openColorSettings(self):
        if self.app:
            self.app.enterGuiControlMode(VIEW_ALIAS.COLOR_SETTING, cursorVisible=True, enableAiming=True)
        self.fireEvent(LoadViewEvent(alias=VIEW_ALIAS.COLOR_SETTING), EVENT_BUS_SCOPE.DEFAULT)

    def setPeriod(self, period):
        if self.__isActive and not self.sessionProvider.getCtx().isPlayerObserver():
            if period in (ARENA_PERIOD.PREBATTLE,):
                self.fireEvent(GameEvent(GameEvent.SHOW_COLOR_SETTINGS_TIP, ctx={'isPrebattle': True}), scope=EVENT_BUS_SCOPE.GLOBAL)
            else:
                self.fireEvent(GameEvent(GameEvent.HIDE_COLOR_SETTINGS_TIP), scope=EVENT_BUS_SCOPE.GLOBAL)

    def _populate(self):
        super(ColorSettingsTipPanel, self)._populate()
        self.as_setInitDataS({'header': text_styles.highTitle(INGAME_GUI.COLORSETTINGSTIPPANEL_HEADER),
         'desc': text_styles.main(INGAME_GUI.COLORSETTINGSTIPPANEL_DESC),
         'btnLabel': i18n.makeString(INGAME_GUI.COLORSETTINGSTIPPANEL_BTNLABEL)})
        ctrl = self.sessionProvider.shared.vehicleState
        if ctrl is not None and self.__isActive:
            ctrl.onVehicleStateUpdated += self.__onVehicleStateUpdated
            ctrl.onVehicleControlling += self.__onVehicleControlling
            ctrl.onPostMortemSwitched += self.__onPostMortemSwitched
            ctrl.onRespawnBaseMoving += self.__onRespawnBaseMoving
        return

    def _dispose(self):
        ctrl = self.sessionProvider.shared.vehicleState
        if ctrl is not None and self.__isActive:
            ctrl.onVehicleStateUpdated -= self.__onVehicleStateUpdated
            ctrl.onVehicleControlling -= self.__onVehicleControlling
            ctrl.onPostMortemSwitched -= self.__onPostMortemSwitched
            ctrl.onRespawnBaseMoving -= self.__onRespawnBaseMoving
        return

    def __onVehicleStateUpdated(self, state, value):
        self.__checkColorTip()

    def __onVehicleControlling(self, vehicle):
        self.__checkColorTip()

    def __onPostMortemSwitched(self, noRespawnPossible, respawnAvailable):
        self.__checkColorTip()

    def __onRespawnBaseMoving(self):
        self.__checkColorTip()

    def __checkColorTip(self):
        ctrl = self.sessionProvider.shared.vehicleState
        if ctrl.isInPostmortem and not self.sessionProvider.getCtx().isPlayerObserver():
            vehicle = ctrl.getControllingVehicle()
            if vehicle and vehicle.isPlayerVehicle:
                self.fireEvent(GameEvent(GameEvent.SHOW_COLOR_SETTINGS_TIP, ctx={'isPrebattle': False}), scope=EVENT_BUS_SCOPE.GLOBAL)
            else:
                self.fireEvent(GameEvent(GameEvent.HIDE_COLOR_SETTINGS_TIP), scope=EVENT_BUS_SCOPE.GLOBAL)
