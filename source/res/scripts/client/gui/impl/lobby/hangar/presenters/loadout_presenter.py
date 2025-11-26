# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/hangar/presenters/loadout_presenter.py
from __future__ import absolute_import
import json
import logging
import typing
import Event
import adisp
from PlayerEvents import g_playerEvents
from CurrentVehicle import g_currentVehicle
from constants import LoadoutParams
from frameworks.state_machine import BaseStateObserver, visitor
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.Scaleform.lobby_entry import getLobbyStateMachine
from gui.game_control.loadout_controller import updateInteractor
from gui.impl.backport import BackportTooltipWindow
from gui.impl.common.ammunition_panel.ammunition_groups_controller import GROUPS_MAP
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.loadout.panel.ammunition.ammunition_panel_model import AmmunitionPanelModel
from gui.impl.gen.view_models.views.lobby.tank_setup.tank_setup_constants import TankSetupConstants
from gui.impl.lobby.hangar.presenters.consumables_presenter import ConsumablesPresenter
from gui.impl.lobby.hangar.presenters.equipments_presenter import EquipmentsPresenter
from gui.impl.lobby.hangar.presenters.instructions_presenter import InstructionsPresenter
from gui.impl.lobby.hangar.presenters.shells_presenter import ShellsPresenter
from gui.impl.lobby.tank_setup.ammunition_panel.groups_controller import HangarAmmunitionGroupsController
from gui.impl.lobby.tank_setup.backports.tooltips import getSlotSpecTooltipData, getSlotTooltipData
from gui.impl.lobby.tank_setup.interactors.base import InteractingItem
from gui.impl.pub.view_component import ViewComponent
from gui.prb_control import prbDispatcherProperty
from gui.shared import events, EVENT_BUS_SCOPE
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.gui_items.items_actions import factory as ActionsFactory
from gui.shared.items_cache import CACHE_SYNC_REASON
from helpers import dependency
from post_progression_common import TankSetupGroupsId
from skeletons.gui.game_control import ILoadoutController, IPlatoonController
from skeletons.gui.shared import IItemsCache
from soft_exception import SoftException
from wg_async import wg_async
if typing.TYPE_CHECKING:
    from gui.impl.common.ammunition_panel.ammunition_groups_controller import AmmunitionGroupsController
    from gui.lobby_state_machine.lobby_state_machine import LobbyStateMachine
    from frameworks.state_machine import StateEvent, State
    from gui.shared.events import NavigationEvent
_logger = logging.getLogger(__name__)

def _getSectionNameByIndices(groupIndex, sectionIndex):
    sectionNameMap = {0: {0: TankSetupConstants.OPT_DEVICES,
         1: TankSetupConstants.BATTLE_BOOSTERS},
     1: {0: TankSetupConstants.SHELLS,
         1: TankSetupConstants.CONSUMABLES}}
    return sectionNameMap.get(groupIndex, {}).get(sectionIndex, '')


class _LoadoutStatesObserver(BaseStateObserver):
    __loadoutController = dependency.descriptor(ILoadoutController)
    _GROUP_SECTIONS_NAMES = [[TankSetupConstants.OPT_DEVICES, TankSetupConstants.BATTLE_BOOSTERS], [TankSetupConstants.SHELLS, TankSetupConstants.CONSUMABLES]]

    def __init__(self):
        super(_LoadoutStatesObserver, self).__init__()
        self.__manager = Event.EventManager()
        self.onPanelSlotSelect = Event.Event(self.__manager)

    def clear(self):
        super(_LoadoutStatesObserver, self).clear()
        self.__manager.clear()

    def isObservingState(self, state):
        lsm = state.getMachine()
        return visitor.isDescendantOf(state, lsm.getStateByID(self._stateID)) or state.getStateID() == self._stateID

    def onStateChanged(self, state, stateEntered, event=None):
        if state.getStateID() == self._stateID:
            if not stateEntered:
                self.onPanelSlotSelect('', None, AmmunitionPanelModel.NO_SLOT_SELECTED)
                self.__loadoutController.clearInteractor()
            return
        else:
            super(_LoadoutStatesObserver, self).onStateChanged(state, stateEntered, event)
            return

    def onEnterState(self, state, event):
        groupIndex = event.params.get(LoadoutParams.groupIndex)
        sectionIndex = event.params.get(LoadoutParams.sectionIndex)
        slotIndex = event.params.get(LoadoutParams.slotIndex)
        sectionName = self._GROUP_SECTIONS_NAMES[groupIndex][sectionIndex]
        self.onPanelSlotSelect(sectionName, groupIndex, slotIndex)

    @property
    def _stateID(self):
        from gui.impl.lobby.hangar.states import LoadoutState
        return LoadoutState.STATE_ID


class LoadoutPresenter(ViewComponent[AmmunitionPanelModel]):
    _VIEW_MODEL = AmmunitionPanelModel
    _STATES_OBSERVER = _LoadoutStatesObserver
    __itemsCache = dependency.descriptor(IItemsCache)
    __loadoutController = dependency.descriptor(ILoadoutController)
    __platoonCtrl = dependency.descriptor(IPlatoonController)

    def __init__(self):
        super(LoadoutPresenter, self).__init__(model=self._VIEW_MODEL)
        self._vehInteractingItem = self.__createVehicleItem()
        self.__ammunitionGroupsController = None
        self.__currentSectionName = ''
        self.__currentGroupIndex = None
        self.__currentSlotIndex = AmmunitionPanelModel.NO_SLOT_SELECTED
        self.__slotSelectionObserver = self._STATES_OBSERVER()
        return

    def getSlotSelectionObserver(self):
        return self.__slotSelectionObserver

    def createToolTip(self, event):
        backportTooltipContentID = R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent()
        isBackportContentId = event.contentID == R.aliases.common.tooltip.Backport() or event.contentID == backportTooltipContentID
        if isBackportContentId and g_currentVehicle.isPresent():
            tooltipData = self.__getBackportTooltipData(event)
            if tooltipData is not None:
                window = BackportTooltipWindow(tooltipData, self.getParentWindow())
                window.load()
                return window
        return super(LoadoutPresenter, self).createToolTip(event)

    @prbDispatcherProperty
    def prbDispatcher(self):
        return None

    def _getChildComponents(self):
        hangar = R.aliases.hangar.shared
        return {hangar.Equipments(): lambda : EquipmentsPresenter(self._vehInteractingItem),
         hangar.Instructions(): lambda : InstructionsPresenter(self._vehInteractingItem),
         hangar.Shells(): lambda : ShellsPresenter(self._vehInteractingItem),
         hangar.Consumables(): lambda : ConsumablesPresenter(self._vehInteractingItem)}

    def _getEvents(self):
        model = self.getViewModel()
        return super(LoadoutPresenter, self)._getEvents() + ((g_currentVehicle.onChanged, self.__onVehicleChanged),
         (self.__platoonCtrl.onMembersUpdate, self.__onMembersUpdate),
         (self.__slotSelectionObserver.onPanelSlotSelect, self.__onPanelSlotSelect),
         (self.__itemsCache.onSyncCompleted, self.__onCacheResync),
         (model.onChangeSetupIndex, self.__onChangeSetupIndex),
         (model.onOpenSlotSpecDialog, self.__onSpecializationSelect),
         (self._vehInteractingItem.onItemUpdated, self.__onItemUpdated),
         (self._vehInteractingItem.onAcceptComplete, self.__onAcceptComplete),
         (self._vehInteractingItem.onRevert, self.__onRevert),
         (g_playerEvents.onKickedFromPrebattle, self.__onKickedFromPrebattle),
         (g_playerEvents.onPrebattleLeft, self.__onPrebattleLeft))

    def _getListeners(self):
        return ((events.PrbActionEvent.LEAVE, self.__onDoLeaveAction, EVENT_BUS_SCOPE.LOBBY),)

    def _onLoading(self, *args, **kwargs):
        lsm = getLobbyStateMachine()
        lsm.connect(self.__slotSelectionObserver)
        self.__updateAmmunitionGroupsController(True)
        super(LoadoutPresenter, self)._onLoading(*args, **kwargs)

    def _finalize(self):
        super(LoadoutPresenter, self)._finalize()
        self._vehInteractingItem = None
        lsm = getLobbyStateMachine()
        lsm.disconnect(self.__slotSelectionObserver)
        self.__slotSelectionObserver = None
        return

    def __createVehicleCopy(self):
        if not g_currentVehicle.isPresent():
            return None
        else:
            currentVehicle = g_currentVehicle.item
            copyVehicle = self.__itemsCache.items.getVehicleCopy(currentVehicle)
            copyVehicle.battleAbilities.setInstalled(*currentVehicle.battleAbilities.installed)
            copyVehicle.battleAbilities.setLayout(*currentVehicle.battleAbilities.layout)
            return copyVehicle

    def __createVehicleItem(self):
        return InteractingItem(self.__createVehicleCopy())

    def __getBackportTooltipData(self, event):
        tooltipId = event.getArgument('tooltip')
        return getSlotSpecTooltipData(event, tooltipId) if tooltipId == TOOLTIPS_CONSTANTS.HANGAR_SLOT_SPEC else getSlotTooltipData(event, self._vehInteractingItem.getItem(), self.getViewModel().getSelectedSlot(), self.__currentSectionName)

    def __updateModel(self, recreate=False, sectionName=None):
        with self.getViewModel().transaction() as panelModel:
            if recreate:
                self.__ammunitionGroupsController.createGroupsModels(panelModel.getGroups())
            elif sectionName is not None:
                self.__ammunitionGroupsController.updateGroupSectionModel(sectionName, panelModel.getGroups())
            else:
                self.__ammunitionGroupsController.updateGroupsModels(panelModel.getGroups())
            panelModel.setVehicleId(str(g_currentVehicle.intCD) if g_currentVehicle.isPresent() else '')
            panelModel.setIsDisabled(not self.__canChangeVehicle() or self.__isAmmunitionPanelDisabled())
            if self.__currentSlotIndex is not None:
                panelModel.setSelectedSlot(self.__currentSlotIndex)
            panelModel.setSelectedSection(self.__currentSectionName)
        return

    def __canChangeVehicle(self):
        if self.prbDispatcher is not None:
            permission = self.prbDispatcher.getGUIPermissions()
            if permission is not None:
                return permission.canChangeVehicle()
        return True

    def __onAcceptComplete(self):
        self.__updateAmmunitionGroupsController(True)

    def __onRevert(self, *args):
        self.__updateAmmunitionGroupsController()

    def __onCacheResync(self, reason, diff):
        if reason != CACHE_SYNC_REASON.CLIENT_UPDATE:
            return
        else:
            if diff is not None and GUI_ITEM_TYPE.VEHICLE in diff and g_currentVehicle.isPresent() and g_currentVehicle.item.intCD in diff[GUI_ITEM_TYPE.VEHICLE]:
                if GUI_ITEM_TYPE.TANKMAN in diff:
                    self._vehInteractingItem.getItem().copyCrew(g_currentVehicle.item)
                self.__updateModel()
            return

    def __onItemUpdated(self, sectionName):
        self.__updateAmmunitionGroupsController(False, sectionName)

    def __getVehicle(self):
        return self._vehInteractingItem.getItem()

    def __onVehicleChanged(self):
        if not g_currentVehicle.isPresent():
            return
        else:
            needToRecreate = self._vehInteractingItem.getItem() is None or g_currentVehicle.item.intCD != self._vehInteractingItem.getItem().intCD or not self._vehInteractingItem.getItem().isAlive
            if needToRecreate:
                self._vehInteractingItem.setItem(self.__createVehicleCopy())
                self.__loadoutController.onResetItem()
            else:
                self._recreateVehicleSetups()
                self._vehInteractingItem.getItem().settings = g_currentVehicle.item.settings
                self.__loadoutController.onUpdateFromItem(g_currentVehicle.item)
            self.__updateAmmunitionGroupsController(needToRecreate)
            return

    def __onDoLeaveAction(self, _):
        self.getViewModel().setIsDisabled(self.__isAmmunitionPanelDisabled())

    def __onKickedFromPrebattle(self, _):
        self.getViewModel().setIsDisabled(self.__isAmmunitionPanelDisabled())

    def __onPrebattleLeft(self):
        self.getViewModel().setIsDisabled(self.__isAmmunitionPanelDisabled())

    def __onMembersUpdate(self):
        self.getViewModel().setIsDisabled(not self.__canChangeVehicle() or self.__isAmmunitionPanelDisabled())

    def _recreateVehicleSetups(self):
        vehicle = self._vehInteractingItem.getItem()
        currentVehicle = g_currentVehicle.item
        for groupID, newIdx in currentVehicle.setupLayouts.groups.items():
            if newIdx != vehicle.setupLayouts.getLayoutIndex(groupID):
                for vehEquip, curVehEquip in self._getEquipmentsPairs(groupID):
                    vehEquip.setInstalled(*curVehEquip.installed)
                    vehEquip.setLayout(*curVehEquip.layout)
                    vehEquip.setupLayouts.setLayoutIndex(newIdx)

        vehicle.setupLayouts.setGroups(currentVehicle.setupLayouts.groups.copy())

    def _getEquipmentsPairs(self, groupID):
        currentVehicle = g_currentVehicle.item
        vehicle = self._vehInteractingItem.getItem()
        eqPairs = set()
        if groupID == TankSetupGroupsId.EQUIPMENT_AND_SHELLS:
            eqPairs.add((vehicle.consumables, currentVehicle.consumables))
            eqPairs.add((vehicle.shells, currentVehicle.shells))
        elif groupID == TankSetupGroupsId.OPTIONAL_DEVICES_AND_BOOSTERS:
            eqPairs.add((vehicle.optDevices, currentVehicle.optDevices))
            eqPairs.add((vehicle.battleBoosters, currentVehicle.battleBoosters))
        else:
            raise SoftException('Vehicle setup group id must match for any type of equipments. groupID {}'.format(groupID))
        return eqPairs

    def __updateAmmunitionGroupsController(self, recreate=False, sectionName=None):
        if not g_currentVehicle.isPresent():
            return
        if self.__ammunitionGroupsController:
            self.__ammunitionGroupsController.updateVehicle(self.__getVehicle())
        else:
            self.__ammunitionGroupsController = HangarAmmunitionGroupsController(self.__getVehicle())
        self.__updateModel(recreate, sectionName)

    @staticmethod
    def __isAmmunitionPanelDisabled():
        return not g_currentVehicle.isInHangar() or g_currentVehicle.isLocked() or g_currentVehicle.isBroken()

    def __setCurrentSection(self, selectedSection):
        self.__ammunitionGroupsController.updateCurrentSection(selectedSection)

    def __isNewSetupLayoutIndexValid(self, hudGroupID, newLayoutIdx):
        groupID = GROUPS_MAP.get(hudGroupID, None)
        layoutIdx = self.__getVehicle().setupLayouts.getLayoutIndex(groupID)
        capacity = self.__getVehicle().setupLayouts.getGroupCapacity(groupID)
        return newLayoutIdx != layoutIdx and 0 <= layoutIdx < capacity

    @wg_async
    def __onChangeSetupIndex(self, args):
        jsonArgs = json.loads(args.get('args'))
        hudGroupID = jsonArgs['groupId']
        currentIndex = jsonArgs['currentIndex']
        if self.__isNewSetupLayoutIndexValid(hudGroupID, currentIndex):
            if self.__loadoutController.interactor and self.__loadoutController.interactor.hasChanged() and self.__ammunitionGroupsController.getGroupIdBySection(self.__currentSectionName) == hudGroupID:
                result = yield self.__loadoutController.interactor.showExitConfirmDialog()
                confirmed, data = result.result
                rollback = data.get('rollBack', False)
                proceed = confirmed or rollback
                yield updateInteractor(self.__loadoutController.interactor, confirmed, rollback)
                if not proceed:
                    return
            groupId = GROUPS_MAP[hudGroupID]
            self.__doChangeSetupIndex(groupId, currentIndex)

    @adisp.adisp_process
    def __doChangeSetupIndex(self, groupId, currentIndex):
        action = ActionsFactory.getAction(ActionsFactory.CHANGE_SETUP_EQUIPMENTS_INDEX, self.__getVehicle(), groupId, currentIndex)
        if action is not None:
            yield action.doAction()
            self.__slotSelectionObserver.onPanelSlotSelect(self.__currentSectionName, self.__currentGroupIndex, self.__currentSlotIndex)
            self.__updateAmmunitionGroupsController(True)
        return

    @adisp.adisp_process
    def __onSpecializationSelect(self, args=None):
        action = ActionsFactory.getAction(ActionsFactory.SET_EQUIPMENT_SLOT_TYPE, self.__getVehicle())
        if action is not None:
            yield action.doAction()
            self._vehInteractingItem.getItem().optDevices.dynSlotType = g_currentVehicle.item.optDevices.dynSlotType
            self.__updateModel()
            self.__loadoutController.onSpecializationSelect()
        return

    def __onPanelSlotSelect(self, sectionName, groupIndex, slotIndex):
        self.__ammunitionGroupsController.updateCurrentSection(sectionName)
        if self.__currentGroupIndex != groupIndex:
            self.__updateAmmunitionGroupsController()
        self.__currentGroupIndex = groupIndex
        self.__currentSlotIndex = slotIndex
        sectionSwitched = sectionName != self.__currentSectionName
        self.__currentSectionName = sectionName
        with self.getViewModel().transaction() as panelModel:
            panelModel.setSelectedSlot(self.__currentSlotIndex)
            panelModel.setSelectedSection(self.__currentSectionName)
        self.__loadoutController.onSlotSelected(slotIndex=slotIndex if self.__currentSlotIndex != AmmunitionPanelModel.NO_SLOT_SELECTED else 0, sectionName=sectionName, sectionSwitched=sectionSwitched)
