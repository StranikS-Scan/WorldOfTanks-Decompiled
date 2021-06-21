# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/tank_setup/ammunition_panel/hangar_view.py
import logging
from CurrentVehicle import g_currentVehicle
from account_helpers.settings_core.settings_constants import OnceOnlyHints
from async import async
from frameworks.wulf import ViewStatus, ViewFlags
from gui.impl.gen.view_models.views.lobby.tank_setup.tank_setup_constants import TankSetupConstants
from gui.impl.lobby.tank_setup.ammunition_panel.base_view import BaseAmmunitionPanelView
from gui.impl.lobby.tank_setup.intro_ammunition_setup_view import getIntroAmmunitionSetupWindowProc
from gui.shared.gui_items.Vehicle import Vehicle
from helpers import dependency
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.game_control import IUISpamController
from uilogging.veh_post_progression.loggers import VehPostProgressionSpecSlotLogger
_logger = logging.getLogger(__name__)

class HangarAmmunitionPanelView(BaseAmmunitionPanelView):
    _settingsCore = dependency.descriptor(ISettingsCore)
    _uiSpamController = dependency.descriptor(IUISpamController)
    _uiLogger = VehPostProgressionSpecSlotLogger()
    __slots__ = ('__introProc',)

    def __init__(self, flags=ViewFlags.VIEW):
        super(HangarAmmunitionPanelView, self).__init__(flags)
        self.__introProc = getIntroAmmunitionSetupWindowProc()

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
        showAmmunitionHint = not serverSettings.getOnceOnlyHintsSetting(OnceOnlyHints.AMMUNITION_PANEL_HINT, default=False)
        if showAmmunitionHint and self._uiSpamController.shouldBeHidden(OnceOnlyHints.AMMUNITION_PANEL_HINT):
            serverSettings.setOnceOnlyHintsSettings({OnceOnlyHints.AMMUNITION_PANEL_HINT: True})
            self.__introProc.setShown()

    def _initialize(self, *args, **kwargs):
        super(HangarAmmunitionPanelView, self)._initialize(*args, **kwargs)
        self._uiLogger.initialize()

    def _finalize(self):
        super(HangarAmmunitionPanelView, self)._finalize()
        self._uiLogger.reset()

    @async
    def _onPanelSectionSelected(self, args):
        selectedSection = args['selectedSection']
        if selectedSection == TankSetupConstants.OPT_DEVICES:
            if self.__introProc.showAllowed():
                if self._uiSpamController.shouldBeHidden(OnceOnlyHints.AMMUNITION_PANEL_HINT):
                    self.__introProc.setShown()
                else:
                    yield self.__introProc.show(self.getParentWindow())
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
