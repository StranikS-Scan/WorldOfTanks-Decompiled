# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/battle/battle_page/ammunition_panel/prebattle_ammunition_panel_view.py
import BigWorld
import typing
import CommandMapping
from Event import Event, EventManager
from account_helpers.settings_core.settings_constants import CONTROLS
from constants import ROLE_TYPE_TO_LABEL
from frameworks.wulf import ViewFlags, ViewSettings, WindowLayer
from gui.impl.backport import createTooltipData, BackportTooltipWindow
from gui.impl.battle.battle_page.ammunition_panel.groups_controller import COMMAND_MAPPING
from gui.impl.battle.battle_page.ammunition_panel.ammunition_panel import PrebattleAmmunitionPanel
from gui.impl.battle.battle_page.skill_select_popover import SkillSelectPopover
from gui.impl.common.ammunition_panel.ammunition_groups_controller import GROUPS_MAP
from gui.impl.gen import R
from gui.impl.gen.view_models.views.battle.battle_page.prebattle_ammunition_panel_view_model import PrebattleAmmunitionPanelViewModel
from gui.impl.pub import PopOverWindow
from gui.impl.pub import ViewImpl
from gui.impl.wrappers.function_helpers import replaceNoneKwargsModel
from gui.shared import g_eventBus, EVENT_BUS_SCOPE
from gui.shared.events import GameEvent
from gui.shared.tooltips.comp7_tooltips import getRoleEquipmentTooltipParts
from gui.shared.utils.functions import makeTooltip
from helpers import dependency
from skeletons.account_helpers.settings_core import ISettingsCore
from items import vehicles
from skeletons.gui.battle_session import IBattleSessionProvider
if typing.TYPE_CHECKING:
    from gui.battle_control.arena_info.interfaces import IPrebattleComp7SkillController
_BACKPORT_TOOLTIP = R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent()

class PrebattleAmmunitionPanelView(ViewImpl):
    __slots__ = ('onSwitchLayout', 'onViewLoaded', '__ammunitionPanel', '_vehicle', '__eventManager')
    __settingsCore = dependency.descriptor(ISettingsCore)

    def __init__(self, vehicle, *args):
        settings = ViewSettings(layoutID=R.views.battle.battle_page.PrebattleAmmunitionPanelView(), flags=ViewFlags.VIEW, model=PrebattleAmmunitionPanelViewModel(), args=args)
        super(PrebattleAmmunitionPanelView, self).__init__(settings)
        self.__ammunitionPanel = None
        self._vehicle = vehicle
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
        self._vehicle = vehicle
        self.__ammunitionPanel.update(self._vehicle, fullUpdate=fullUpdate)
        self.__ammunitionPanel.viewModel.setAmmoNotFull(not self._vehicle.isAmmoFull)

    def updateState(self, state):
        self.viewModel.setState(state)

    def setTimer(self, timeLeft):
        self.viewModel.setTimeTillBattleStart(timeLeft)

    def _initialize(self, *args, **kwargs):
        super(PrebattleAmmunitionPanelView, self)._initialize()
        self._addListeners()
        self.__ammunitionPanel.initialize()

    def _finalize(self):
        self._removeListeners()
        self.__ammunitionPanel.finalize()
        super(PrebattleAmmunitionPanelView, self)._finalize()

    def _onLoading(self, currShellCD, nextShellCD, state, *args, **kwargs):
        super(PrebattleAmmunitionPanelView, self)._onLoading(*args, **kwargs)
        self.__ammunitionPanel = PrebattleAmmunitionPanel(self.viewModel.ammunitionPanel, self._vehicle, ctx={'state': state})
        self.__ammunitionPanel.onLoading()
        self.updateViewVehicle(self._vehicle, fullUpdate=False)
        self.viewModel.setState(state)
        self.setCurrentShellCD(currShellCD)
        self.setNextShellCD(nextShellCD)
        self.__updateAbilitySlot()

    def _onLoaded(self, *args, **kwargs):
        super(PrebattleAmmunitionPanelView, self)._onLoaded(*args, **kwargs)
        self.viewModel.setIsReady(True)
        self.onViewLoaded()

    def _addListeners(self):
        g_eventBus.addListener(GameEvent.CHANGE_AMMUNITION_SETUP, self.__onChangeSetupByKey, scope=EVENT_BUS_SCOPE.BATTLE)
        self.viewModel.ammunitionPanel.onChangeSetupIndex += self.__onChangeSetupByButton
        self.__settingsCore.onSettingsApplied += self.__onSettingsApplied

    def _removeListeners(self):
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
            return

    def __changeSetup(self, hudGroupID, newLayoutIdx=None):
        groupID = GROUPS_MAP[hudGroupID]
        newLayoutIdx = newLayoutIdx or self._vehicle.setupLayouts.getNextLayoutIndex(groupID)
        if self.__ammunitionPanel.isNewSetupLayoutIndexValid(hudGroupID, newLayoutIdx):
            self.onSwitchLayout(groupID, newLayoutIdx)

    def __onSettingsApplied(self, diff):
        if CONTROLS.KEYBOARD in diff:
            self.__ammunitionPanel.updateSectionsWithKeySettings()

    def __updateAbilitySlot(self):
        ability = self.__getCurrentVehicleAbilityData()
        with self.viewModel.transaction() as model:
            model.abilitySlot.setAbility(ability.name if ability is not None else '')
        return

    def __getCurrentVehicleAbilityData(self):
        abilityID = self._vehicle.typeDescr.ability
        return None if abilityID is None else vehicles.g_cache.equipments()[abilityID]


class Comp7PrebattleAmmunitionPanelView(PrebattleAmmunitionPanelView):
    __slots__ = ('__skillPopover', '__isReplay')
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self, vehicle, *args):
        super(Comp7PrebattleAmmunitionPanelView, self).__init__(vehicle, *args)
        self.__skillPopover = None
        self.__isReplay = self.__sessionProvider.isReplayPlaying
        return

    def createToolTip(self, event):
        if event.contentID == _BACKPORT_TOOLTIP:
            intCD = event.getArgument('intCD')
            roleSkill = vehicles.g_cache.equipments()[intCD]
            header, body = getRoleEquipmentTooltipParts(roleSkill)
            tooltipData = createTooltipData(makeTooltip(header=header, body=body))
            window = BackportTooltipWindow(tooltipData, self.getParentWindow())
            window.load()
            return window
        return super(Comp7PrebattleAmmunitionPanelView, self).createToolTip(event)

    def updateViewVehicle(self, vehicle, fullUpdate=True):
        super(Comp7PrebattleAmmunitionPanelView, self).updateViewVehicle(vehicle, fullUpdate)
        self.__updateComp7SkillSlot()

    def createPopOver(self, event):
        if event.contentID == R.views.battle.battle_page.SkillSelectPopover():
            content = SkillSelectPopover(self._vehicle, self)
            self.__skillPopover = content
            window = PopOverWindow(event, content, self.getParentWindow(), WindowLayer.TOP_WINDOW)
            window.load()
            return window
        super(Comp7PrebattleAmmunitionPanelView, self).createPopOver(event)

    @replaceNoneKwargsModel
    def setPopoverState(self, hasPopover, model=None):
        model.roleSkillSlot.setIsPopoverOpen(hasPopover)
        if not hasPopover:
            self.__skillPopover = None
        return

    def _finalize(self):
        if self.__skillPopover:
            self.__skillPopover.destroyWindow()
            self.__skillPopover = None
        super(Comp7PrebattleAmmunitionPanelView, self)._finalize()
        return

    def _addListeners(self):
        super(Comp7PrebattleAmmunitionPanelView, self)._addListeners()
        self.__skillCtrl.onVehicleSkillUpdated += self.__updateComp7SkillSlot
        self.__skillCtrl.onSwitchStopped += self.__onSwitchStopped

    def _removeListeners(self):
        if self.__skillCtrl is not None:
            self.__skillCtrl.onVehicleSkillUpdated -= self.__updateComp7SkillSlot
            self.__skillCtrl.onSwitchStopped -= self.__onSwitchStopped
        super(Comp7PrebattleAmmunitionPanelView, self)._removeListeners()
        return

    @property
    def __skillCtrl(self):
        return self.__sessionProvider.dynamic.comp7PrebattleSkillController

    def __updateComp7SkillSlot(self, *_):
        playerVehicle = BigWorld.entities.get(BigWorld.player().playerVehicleID)
        intCD = playerVehicle.selectedComp7Skill if playerVehicle is not None else self._vehicle.selectedComp7Skill
        self._vehicle.selectedComp7Skill = intCD
        roleSkill, roleName = self.__getVehicleRoleInfo(self._vehicle)
        if roleSkill is None or roleName is None:
            return
        else:
            with self.viewModel.transaction() as tx:
                tx.roleSkillSlot.setRoleSkill(roleSkill.name)
                tx.roleSkillSlot.setRoleName(roleName)
                tx.roleSkillSlot.setIntCD(roleSkill.id.itemID)
                tx.roleSkillSlot.setCanSwitch(self.__skillCtrl.canSwitch() and not self.__isReplay)
            return

    def __onSwitchStopped(self):
        with self.viewModel.transaction() as tx:
            tx.roleSkillSlot.setCanSwitch(self.__skillCtrl.canSwitch())
        if self.__skillPopover:
            self.__skillPopover.destroyWindow()
            self.__skillPopover = None
        return

    @staticmethod
    def __getVehicleRoleInfo(vehicle):
        roleName = ROLE_TYPE_TO_LABEL.get(vehicle.descriptor.role)
        equipmentID = vehicle.selectedComp7Skill
        roleSkill = vehicles.g_cache.equipments()[equipmentID]
        return (roleSkill, roleName)
