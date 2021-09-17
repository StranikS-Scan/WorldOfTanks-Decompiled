# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/battle/battle_page/ammunition_panel/prebattle_ammunition_panel_view.py
import CommandMapping
from Event import Event, EventManager
from account_helpers.settings_core.settings_constants import CONTROLS
from frameworks.wulf import ViewFlags, ViewSettings
from gui.impl.battle.battle_page.ammunition_panel.groups_controller import COMMAND_MAPPING
from gui.impl.battle.battle_page.ammunition_panel.ammunition_panel import PrebattleAmmunitionPanel
from gui.impl.common.ammunition_panel.ammunition_groups_controller import GROUPS_MAP
from gui.impl.gen import R
from gui.impl.gen.view_models.views.battle.battle_page.prebattle_ammunition_panel_view_model import PrebattleAmmunitionPanelViewModel
from gui.impl.pub import ViewImpl
from gui.shared import g_eventBus, EVENT_BUS_SCOPE
from gui.shared.events import GameEvent
from helpers import dependency
from skeletons.account_helpers.settings_core import ISettingsCore
from uilogging.veh_post_progression.loggers import VehPostProgressionPrebattleSwitchPanelLogger

class PrebattleAmmunitionPanelView(ViewImpl):
    __slots__ = ('onSwitchLayout', 'onViewLoaded', '__ammunitionPanel', '__vehicle', '__eventManager')
    __uiLogger = VehPostProgressionPrebattleSwitchPanelLogger()
    __settingsCore = dependency.descriptor(ISettingsCore)

    def __init__(self, vehicle, *args):
        settings = ViewSettings(layoutID=R.views.battle.battle_page.PrebattleAmmunitionPanelView(), flags=ViewFlags.COMPONENT, model=PrebattleAmmunitionPanelViewModel(), args=args)
        super(PrebattleAmmunitionPanelView, self).__init__(settings)
        self.__ammunitionPanel = None
        self.__vehicle = vehicle
        self.__eventManager = EventManager()
        self.onSwitchLayout = Event(self.__eventManager)
        self.onViewLoaded = Event(self.__eventManager)
        return

    @property
    def viewModel(self):
        return super(PrebattleAmmunitionPanelView, self).getViewModel()

    def createToolTip(self, event):
        pass

    def createContextMenu(self, event):
        pass

    def setNextShellCD(self, shellCD):
        if shellCD is None:
            return
        else:
            self.__ammunitionPanel.onNextShellChanged(shellCD)
            return

    def setCurrentShellCD(self, shellCD):
        if shellCD is None:
            return
        else:
            self.__ammunitionPanel.onCurrentShellChanged(shellCD)
            return

    def updateViewActive(self, isActive):
        self.viewModel.setIsDisabled(not isActive)

    def updateViewVehicle(self, vehicle, fullUpdate=True):
        self.__vehicle = vehicle
        self.__ammunitionPanel.update(self.__vehicle, fullUpdate=fullUpdate)
        self.__ammunitionPanel.viewModel.setAmmoNotFull(not self.__vehicle.isAmmoFull)

    def updateState(self, state):
        self.viewModel.setState(state)

    def setTimer(self, timeLeft):
        self.viewModel.setTimeTillBattleStart(timeLeft)

    def _initialize(self, *args, **kwargs):
        super(PrebattleAmmunitionPanelView, self)._initialize()
        self.__addListeners()
        self.__ammunitionPanel.initialize()

    def _finalize(self):
        self.__removeListeners()
        self.__ammunitionPanel.finalize()
        super(PrebattleAmmunitionPanelView, self)._finalize()

    def _onLoading(self, currShellCD, nextShellCD, state, *args, **kwargs):
        super(PrebattleAmmunitionPanelView, self)._onLoading(*args, **kwargs)
        self.__ammunitionPanel = PrebattleAmmunitionPanel(self.viewModel.ammunitionPanel, self.__vehicle, ctx={'state': state})
        self.__ammunitionPanel.onLoading()
        self.updateViewVehicle(self.__vehicle, fullUpdate=False)
        self.viewModel.setState(state)
        self.setCurrentShellCD(currShellCD)
        self.setNextShellCD(nextShellCD)

    def _onLoaded(self, *args, **kwargs):
        super(PrebattleAmmunitionPanelView, self)._onLoaded(*args, **kwargs)
        self.viewModel.setIsReady(True)
        self.onViewLoaded()

    def __addListeners(self):
        g_eventBus.addListener(GameEvent.CHANGE_AMMUNITION_SETUP, self.__onChangeSetupByKey, scope=EVENT_BUS_SCOPE.BATTLE)
        self.viewModel.ammunitionPanel.onChangeSetupIndex += self.__onChangeSetupByButton
        self.__settingsCore.onSettingsApplied += self.__onSettingsApplied

    def __removeListeners(self):
        g_eventBus.removeListener(GameEvent.CHANGE_AMMUNITION_SETUP, self.__onChangeSetupByKey, scope=EVENT_BUS_SCOPE.BATTLE)
        self.viewModel.ammunitionPanel.onChangeSetupIndex -= self.__onChangeSetupByButton
        self.__settingsCore.onSettingsApplied -= self.__onSettingsApplied
        self.__eventManager.clear()

    def __onChangeSetupByButton(self, args):
        hudGroupID, newLayoutIdx = args.get('groupId', None), args.get('currentIndex', None)
        if self.viewModel.getIsDisabled() or hudGroupID is None or newLayoutIdx is None:
            return
        else:
            self.__changeSetup(int(hudGroupID), int(newLayoutIdx))
            self.__uiLogger.logClick()
            return

    def __onChangeSetupByKey(self, event):
        key = event.ctx['key']
        cmdMap = CommandMapping.g_instance
        hudGroupID = None
        if cmdMap.isFired(CommandMapping.CMD_AMMUNITION_SHORTCUT_SWITCH_SETUP_1, key):
            hudGroupID = COMMAND_MAPPING[CommandMapping.CMD_AMMUNITION_SHORTCUT_SWITCH_SETUP_1]
        elif cmdMap.isFired(CommandMapping.CMD_AMMUNITION_SHORTCUT_SWITCH_SETUP_2, key):
            hudGroupID = COMMAND_MAPPING[CommandMapping.CMD_AMMUNITION_SHORTCUT_SWITCH_SETUP_2]
        if self.viewModel.getIsDisabled() or hudGroupID is None:
            return
        else:
            self.__changeSetup(hudGroupID)
            self.__uiLogger.logHotkey()
            return

    def __changeSetup(self, hudGroupID, newLayoutIdx=None):
        groupID = GROUPS_MAP[hudGroupID]
        newLayoutIdx = newLayoutIdx or self.__vehicle.setupLayouts.getNextLayoutIndex(groupID)
        if self.__ammunitionPanel.isNewSetupLayoutIndexValid(hudGroupID, newLayoutIdx):
            self.onSwitchLayout(groupID, newLayoutIdx)

    def __onSettingsApplied(self, diff):
        if CONTROLS.KEYBOARD in diff:
            self.__ammunitionPanel.updateSectionsWithKeySettings()
