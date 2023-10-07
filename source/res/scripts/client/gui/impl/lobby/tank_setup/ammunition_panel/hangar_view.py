# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/tank_setup/ammunition_panel/hangar_view.py
import logging
from CurrentVehicle import g_currentVehicle
from account_helpers.settings_core.settings_constants import OnceOnlyHints
from gui.limited_ui.lui_rules_storage import LuiRules
from skeletons.gui.game_control import ILimitedUIController
from wg_async import wg_async
from frameworks.wulf import ViewStatus
from gui.impl.lobby.tank_setup.ammunition_panel.base_view import BaseAmmunitionPanelView
from gui.impl.lobby.tank_setup.intro_ammunition_setup_view import showIntro
from gui.shared import g_eventBus, EVENT_BUS_SCOPE
from gui.shared.events import AmmunitionPanelViewEvent
from gui.shared.gui_items.Vehicle import Vehicle
from helpers import dependency
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.game_control import IHalloweenController
_logger = logging.getLogger(__name__)
_AMMUNITION_PANEL_HINTS = (OnceOnlyHints.AMMUNITION_PANEL_HINT, OnceOnlyHints.AMUNNITION_PANEL_EPIC_BATTLE_ABILITIES_HINT)
_HINT_TO_RULE_ID = {OnceOnlyHints.AMMUNITION_PANEL_HINT: LuiRules.AP_ZONE_HINT,
 OnceOnlyHints.AMUNNITION_PANEL_EPIC_BATTLE_ABILITIES_HINT: LuiRules.AP_BATTLE_ABILITIES_HINT}

class HangarAmmunitionPanelView(BaseAmmunitionPanelView):
    _settingsCore = dependency.descriptor(ISettingsCore)
    _limitedUIController = dependency.descriptor(ILimitedUIController)
    _hwController = dependency.descriptor(IHalloweenController)

    def update(self, fullUpdate=True):
        with self.viewModel.transaction():
            super(HangarAmmunitionPanelView, self).update(fullUpdate)
            self._updateViewModel()

    def _updateViewModel(self):
        if g_currentVehicle.isPresent():
            state, _ = g_currentVehicle.item.getState()
            self._ammunitionPanel.viewModel.setAmmoNotFull(state == Vehicle.VEHICLE_STATE.AMMO_NOT_FULL)

    def _addListeners(self):
        super(HangarAmmunitionPanelView, self)._addListeners()
        self.viewModel.ammunitionPanel.onChangeSetupIndex += self._onChangeSetupIndex
        self.viewModel.onEscKeyDown += self.__onEscKeyDown

    def _removeListeners(self):
        super(HangarAmmunitionPanelView, self)._removeListeners()
        self.viewModel.ammunitionPanel.onChangeSetupIndex -= self._onChangeSetupIndex
        self.viewModel.onEscKeyDown -= self.__onEscKeyDown

    def _onLoading(self, *args, **kwargs):
        super(HangarAmmunitionPanelView, self)._onLoading(*args, **kwargs)
        serverSettings = self._settingsCore.serverSettings
        for hintName in _AMMUNITION_PANEL_HINTS:
            showHint = not serverSettings.getOnceOnlyHintsSetting(hintName, default=False)
            ruleID = _HINT_TO_RULE_ID.get(hintName)
            if showHint and (ruleID is None or self._limitedUIController.isRuleCompleted(ruleID)):
                serverSettings.setOnceOnlyHintsSettings({hintName: True})

        return

    @wg_async
    def _onPanelSectionSelected(self, args):
        selectedSection = args['selectedSection']
        isEventHangar = self._hwController.isEventHangar()
        yield showIntro(selectedSection, self.getParentWindow())
        if isEventHangar and not self._hwController.isEnabled():
            return
        if self.viewStatus != ViewStatus.LOADED:
            return
        super(HangarAmmunitionPanelView, self)._onPanelSectionSelected(args)

    def _onChangeSetupIndex(self, args):
        groupID = int(args.get('groupId', None))
        newLayoutIdx = int(args.get('currentIndex', None))
        if groupID is None or newLayoutIdx is None:
            return
        else:
            self._ammunitionPanel.onChangeSetupLayoutIndex(groupID, newLayoutIdx)
            return

    def __onEscKeyDown(self):
        g_eventBus.handleEvent(AmmunitionPanelViewEvent(AmmunitionPanelViewEvent.CLOSE_VIEW), EVENT_BUS_SCOPE.LOBBY)

    def _updateView(self):
        isFullUpdate = not self._wasVehicleOnLoading and self.vehItem is not None
        self.update(fullUpdate=isFullUpdate)
        return
