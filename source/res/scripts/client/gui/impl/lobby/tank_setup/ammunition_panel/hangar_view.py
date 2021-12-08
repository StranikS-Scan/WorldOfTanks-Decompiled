# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/tank_setup/ammunition_panel/hangar_view.py
import logging
from CurrentVehicle import g_currentVehicle
from account_helpers.settings_core.ServerSettingsManager import UI_STORAGE_KEYS
from account_helpers.settings_core.settings_constants import OnceOnlyHints
from async import async
from frameworks.wulf import ViewStatus
from gui.impl.lobby.tank_setup.ammunition_panel.base_view import BaseAmmunitionPanelView
from gui.impl.lobby.tank_setup.intro_ammunition_setup_view import showIntro
from gui.shared.gui_items.Vehicle import Vehicle
from helpers import dependency
from new_year.ny_constants import SyncDataKeys
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.game_control import IUISpamController
from skeletons.new_year import INewYearController
from uilogging.veh_post_progression.loggers import VehPostProgressionSpecSlotLogger
_logger = logging.getLogger(__name__)
_AMMUNITION_PANEL_HINTS = {OnceOnlyHints.AMMUNITION_PANEL_HINT: UI_STORAGE_KEYS.OPTIONAL_DEVICE_SETUP_INTRO_SHOWN,
 OnceOnlyHints.AMUNNITION_PANEL_EPIC_BATTLE_ABILITIES_HINT: UI_STORAGE_KEYS.EPIC_BATTLE_ABILITIES_INTRO_SHOWN}

class HangarAmmunitionPanelView(BaseAmmunitionPanelView):
    _settingsCore = dependency.descriptor(ISettingsCore)
    _uiSpamController = dependency.descriptor(IUISpamController)
    _nyController = dependency.descriptor(INewYearController)
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
        self.viewModel.onEscKeyDown += self.__onEscKeyDown
        self._nyController.onDataUpdated += self.__onDataUpdated
        self._nyController.onStateChanged += self.__onStateChanged

    def _removeListeners(self):
        super(HangarAmmunitionPanelView, self)._removeListeners()
        self.viewModel.ammunitionPanel.onChangeSetupIndex -= self._onChangeSetupIndex
        self.viewModel.onEscKeyDown -= self.__onEscKeyDown
        self._nyController.onDataUpdated -= self.__onDataUpdated
        self._nyController.onStateChanged -= self.__onStateChanged

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
        yield showIntro(selectedSection, self.getParentWindow())
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
        self.onEscKeyDown()

    def __onDataUpdated(self, keys):
        vehicleBranchChanged = SyncDataKeys.VEHICLE_BRANCH in keys
        if vehicleBranchChanged:
            self.update(fullUpdate=True)

    def __onStateChanged(self):
        self.update(fullUpdate=True)
