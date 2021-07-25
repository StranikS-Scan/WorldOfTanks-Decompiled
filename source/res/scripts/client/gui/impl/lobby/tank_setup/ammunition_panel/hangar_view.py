# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/tank_setup/ammunition_panel/hangar_view.py
import logging
from CurrentVehicle import g_currentVehicle
from account_helpers.settings_core.ServerSettingsManager import UI_STORAGE_KEYS
from account_helpers.settings_core.settings_constants import OnceOnlyHints
from async import async
from frameworks.wulf import ViewStatus
from gui.impl.gen.view_models.views.lobby.tank_setup.tank_setup_constants import TankSetupConstants
from gui.impl.lobby.tank_setup.ammunition_panel.base_view import BaseAmmunitionPanelView
from gui.impl.lobby.tank_setup.intro_ammunition_setup_view import showIntroAmmunitionSetupWindow
from gui.shared.gui_items.Vehicle import Vehicle
from helpers import dependency
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.game_control import IUISpamController
from uilogging.veh_post_progression.loggers import VehPostProgressionSpecSlotLogger
_logger = logging.getLogger(__name__)
_AMMUNITION_PANEL_HINTS = {OnceOnlyHints.AMMUNITION_PANEL_HINT: UI_STORAGE_KEYS.OPTIONAL_DEVICE_SETUP_INTRO_SHOWN,
 OnceOnlyHints.AMUNNITION_PANEL_EPIC_BATTLE_ABILITIES_HINT: UI_STORAGE_KEYS.EPIC_BATTLE_ABILITIES_INTRO_SHOWN}
_TANK_SETUP_TO_HINT_SETTINGS = {TankSetupConstants.OPT_DEVICES: OnceOnlyHints.AMMUNITION_PANEL_HINT,
 TankSetupConstants.BATTLE_ABILITIES: OnceOnlyHints.AMUNNITION_PANEL_EPIC_BATTLE_ABILITIES_HINT}

class HangarAmmunitionPanelView(BaseAmmunitionPanelView):
    _settingsCore = dependency.descriptor(ISettingsCore)
    _uiSpamController = dependency.descriptor(IUISpamController)
    _uiLogger = VehPostProgressionSpecSlotLogger()

    def update(self, fullUpdate=True):
        with self.viewModel.transaction():
            super(HangarAmmunitionPanelView, self).update(fullUpdate)
            if g_currentVehicle.isPresent():
                state, _ = g_currentVehicle.item.getState()
                self._ammunitionPanel.viewModel.setAmmoNotFull(state == Vehicle.VEHICLE_STATE.AMMO_NOT_FULL)

    def _addListeners(self):
        super(HangarAmmunitionPanelView, self)._addListeners()
        self.viewModel.ammunitionPanel.onChangeSetupIndex += self._onChangeSetupIndex

    def _removeListeners(self):
        super(HangarAmmunitionPanelView, self)._removeListeners()
        self.viewModel.ammunitionPanel.onChangeSetupIndex -= self._onChangeSetupIndex

    def _onLoading(self, *args, **kwargs):
        super(HangarAmmunitionPanelView, self)._onLoading(*args, **kwargs)
        serverSettings = self._settingsCore.serverSettings
        for hintName, uiStorage in _AMMUNITION_PANEL_HINTS.iteritems():
            showHint = not serverSettings.getOnceOnlyHintsSetting(hintName, default=False)
            if showHint and not self._uiSpamController.shouldBeHidden(hintName):
                serverSettings.setOnceOnlyHintsSettings({hintName: True})
                serverSettings.saveInUIStorage({uiStorage: True})

    def _initialize(self, *args, **kwargs):
        super(HangarAmmunitionPanelView, self)._initialize(*args, **kwargs)
        self._uiLogger.initialize()

    def _finalize(self):
        super(HangarAmmunitionPanelView, self)._finalize()
        self._uiLogger.reset()

    @async
    def _onPanelSectionSelected(self, args):
        selectedSection = args['selectedSection']
        showIntro = selectedSection in _TANK_SETUP_TO_HINT_SETTINGS.keys()
        if showIntro and not self._uiSpamController.shouldBeHidden(_TANK_SETUP_TO_HINT_SETTINGS[selectedSection]):
            self._settingsCore.serverSettings.saveInUIStorage({_AMMUNITION_PANEL_HINTS[_TANK_SETUP_TO_HINT_SETTINGS[selectedSection]]: True})
            showIntro = False
        if showIntro:
            yield showIntroAmmunitionSetupWindow(selectedSection)
            self._uiSpamController.setVisited(_TANK_SETUP_TO_HINT_SETTINGS[selectedSection])
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
