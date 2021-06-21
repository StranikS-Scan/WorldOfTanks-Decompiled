# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/battle/battle_page/ammunition_panel/prebattle_ammunition_panel_view.py
import CommandMapping
from frameworks.wulf import ViewFlags, ViewSettings
from gui.impl.battle.battle_page.ammunition_panel.groups_controller import COMMAND_MAPPING
from gui.impl.battle.battle_page.ammunition_panel.prebattle_ammunition_panel import PrebattleAmmunitionPanel
from gui.impl.battle.battle_page.ammunition_panel.prebattle_ammunition_vehicle_mock import PrbAmmunitionVehicleMock
from gui.impl.common.ammunition_panel.ammunition_groups_controller import GROUPS_MAP
from gui.impl.gen import R
from gui.shared import g_eventBus, EVENT_BUS_SCOPE
from gui.impl.gen.view_models.views.battle.battle_page.prebattle_ammunition_panel_view_model import PrebattleAmmunitionPanelViewModel
from gui.impl.pub import ViewImpl
from gui.shared.events import GameEvent
from gui.veh_post_porgression.sounds import playSound, Sounds
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
from uilogging.veh_post_progression.loggers import VehPostProgressionPrebattleSwitchPanelLogger
_SERVER_GROUP_MAP = {serverGroupID:hudGroupID for hudGroupID, serverGroupID in GROUPS_MAP.iteritems()}

class PrebattleAmmunitionPanelView(ViewImpl):
    __slots__ = ('_ammunitionPanel', '_vehicle', '_firstUpdate', '_isActive')
    sessionProvider = dependency.descriptor(IBattleSessionProvider)
    uiLogger = VehPostProgressionPrebattleSwitchPanelLogger()

    def __init__(self):
        settings = ViewSettings(R.views.battle.battle_page.PrebattleAmmunitionPanelView())
        settings.flags = ViewFlags.COMPONENT
        settings.model = PrebattleAmmunitionPanelViewModel()
        self._ammunitionPanel = None
        self._vehicle = None
        self._isActive = True
        self._firstUpdate = True
        super(PrebattleAmmunitionPanelView, self).__init__(settings)
        return

    @property
    def viewModel(self):
        return super(PrebattleAmmunitionPanelView, self).getViewModel()

    @property
    def vehItem(self):
        return self._vehicle

    def update(self, fullUpdate=True):
        with self.viewModel.transaction():
            self._ammunitionPanel.update(self.vehItem, fullUpdate=fullUpdate)

    def updateViewActive(self, isActive):
        if self._isActive != isActive:
            self._isActive = isActive
            with self.viewModel.transaction():
                self.viewModel.setIsDisabled(not isActive)

    def createToolTip(self, event):
        pass

    def createContextMenu(self, event):
        pass

    def _initialize(self, *args, **kwargs):
        super(PrebattleAmmunitionPanelView, self)._initialize()
        self._addListeners()
        self._vehicle.initialize()
        self._ammunitionPanel.initialize()
        self._onSetupUpdated()

    def _finalize(self):
        self._removeListeners()
        self._vehicle.finalize()
        self._ammunitionPanel.finalize()
        super(PrebattleAmmunitionPanelView, self)._finalize()

    def destroy(self):
        self.vehItem.destroy()
        super(PrebattleAmmunitionPanelView, self).destroy()

    def _onLoading(self, *args, **kwargs):
        super(PrebattleAmmunitionPanelView, self)._onLoading(*args, **kwargs)
        self._vehicle = PrbAmmunitionVehicleMock()
        self._ammunitionPanel = self._createAmmunitionPanel()

    def _onLoaded(self, *args, **kwargs):
        super(PrebattleAmmunitionPanelView, self)._onLoaded(*args, **kwargs)
        with self.viewModel.transaction():
            self.viewModel.setIsReady(True)

    def _createAmmunitionPanel(self):
        return PrebattleAmmunitionPanel(self.viewModel.ammunitionPanel, self.vehItem)

    def _addListeners(self):
        ctrl = self.sessionProvider.shared.vehiclePostProgression
        if ctrl is not None:
            ctrl.onSetupUpdated += self._onSetupUpdated
        ammoCtrl = self.sessionProvider.shared.ammo
        if ammoCtrl is not None:
            self.__fillShells(ammoCtrl)
            ammoCtrl.onNextShellChanged += self._onNextShellChanged
            ammoCtrl.onCurrentShellChanged += self._onCurrentShellChanged
        vppCtrl = self.sessionProvider.shared.vehiclePostProgression
        if vppCtrl is not None and vppCtrl.postProgression.isPostProgressionEnabled:
            self.viewModel.ammunitionPanel.onChangeSetupIndex += self._onChangeSetupIndex
            g_eventBus.addListener(GameEvent.CHANGE_AMMUNITION_SETUP, self.__handleAmmunitionCmd, scope=EVENT_BUS_SCOPE.BATTLE)
        return

    def _removeListeners(self):
        ctrl = self.sessionProvider.shared.vehiclePostProgression
        if ctrl is not None:
            ctrl.onSetupUpdated -= self._onSetupUpdated
        ammoCtrl = self.sessionProvider.shared.ammo
        if ammoCtrl is not None:
            ammoCtrl.onNextShellChanged -= self._onNextShellChanged
            ammoCtrl.onCurrentShellChanged -= self._onCurrentShellChanged
        vppCtrl = self.sessionProvider.shared.vehiclePostProgression
        if vppCtrl is not None and vppCtrl.postProgression.isPostProgressionEnabled:
            self.viewModel.ammunitionPanel.onChangeSetupIndex -= self._onChangeSetupIndex
        g_eventBus.removeListener(GameEvent.CHANGE_AMMUNITION_SETUP, self.__handleAmmunitionCmd, scope=EVENT_BUS_SCOPE.BATTLE)
        return

    def __fillShells(self, ctrl):
        shellCD = ctrl.getNextShellCD()
        if shellCD is not None:
            self._onNextShellChanged(shellCD)
        shellCD = ctrl.getCurrentShellCD()
        if shellCD is not None:
            self._onCurrentShellChanged(shellCD)
        return

    def _onNextShellChanged(self, intCD):
        self._ammunitionPanel.onNextShellChanged(intCD)

    def _onCurrentShellChanged(self, intCD):
        self._ammunitionPanel.onCurrentShellChanged(intCD)

    def _onSetupUpdated(self):
        ctrl = self.sessionProvider.shared.vehiclePostProgression
        equipments = ctrl.setupEquipments
        playerVehicle = ctrl.playerVehicle
        postProgression = ctrl.postProgression
        if equipments is not None and playerVehicle is not None and postProgression is not None:
            self.vehItem.vehicleUpdate(playerVehicle.typeDescriptor, equipments, postProgression)
            if self._firstUpdate:
                self._firstUpdate = False
                self._ammunitionPanel.onLoading()
                self.update(fullUpdate=False)
            else:
                self.update()
        return

    def _onChangeSetupIndex(self, args):
        if not self.viewModel.getIsDisabled():
            self.__changeSetup(args)
            self.uiLogger.logClick()

    def __changeSetup(self, args):
        hudGroupID = int(args.get('groupId', None))
        newLayoutIdx = int(args.get('currentIndex', None))
        if hudGroupID is None or newLayoutIdx is None:
            return
        else:
            groupID = GROUPS_MAP.get(hudGroupID, None)
            vppCtrl = self.sessionProvider.shared.vehiclePostProgression
            if vppCtrl is not None and groupID is not None and vppCtrl.postProgression.isSetupSwitchAvailable(groupID) and self._ammunitionPanel.isNewSetupLayoutIndexValid(hudGroupID, newLayoutIdx):
                if vppCtrl.switchLayout(groupID, newLayoutIdx):
                    playSound(Sounds.GAMEPLAY_SETUP_SWITCH)
            return

    def __handleAmmunitionCmd(self, event):
        self.__handleKey(event.ctx['key'])

    def __handleKey(self, key):
        if self.vehItem is None or self.viewModel.getIsDisabled():
            return
        else:
            cmdMap = CommandMapping.g_instance
            hudGroupID = None
            if cmdMap.isFired(CommandMapping.CMD_AMMUNITION_SHORTCUT_SWITCH_SETUP_1, key):
                hudGroupID = COMMAND_MAPPING.get(CommandMapping.CMD_AMMUNITION_SHORTCUT_SWITCH_SETUP_1, None)
            elif cmdMap.isFired(CommandMapping.CMD_AMMUNITION_SHORTCUT_SWITCH_SETUP_2, key):
                hudGroupID = COMMAND_MAPPING.get(CommandMapping.CMD_AMMUNITION_SHORTCUT_SWITCH_SETUP_2, None)
            if hudGroupID is not None:
                groupID = _SERVER_GROUP_MAP.get(hudGroupID, None)
                index = self.vehItem.setupLayouts.getNextLayoutIndex(groupID)
                ctx = {'groupId': hudGroupID,
                 'currentIndex': index}
                self.__changeSetup(ctx)
                self.uiLogger.logHotkey()
            return
