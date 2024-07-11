# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: races/scripts/client/races/gui/impl/battle/races_hud/races_hud_view.py
import logging
import weakref
from collections import deque
import BigWorld
import GUI
import typing
from races.gui.impl.battle.battle_helpers import getRemainingTime
from races.gui.impl.battle.races_hud.announcements import AnnouncementGoal, getAnnouncementType
from races.gui.impl.battle.races_hud.player_list_component import PlayerListComponent
from races.gui.impl.battle.races_hud.races_minimap_component import RacesMinimapComponent, _UPDATE_POSITIONS_SEC
from races.gui.impl.battle.races_hud.tooltips.ability_tooltip import AbilityTooltip
from races.gui.impl.battle.races_hud.vehicle_markers_manager import VehicleMarkersManager
from races.gui.impl.gen.view_models.views.battle.races_hud.ability_model import AbilityModel, Ability
from races.gui.impl.gen.view_models.views.battle.races_hud.races_hud_view_model import RacesHudViewModel, AnnouncementTypeEnum, ArenaPhaseEnum
from races.gui.impl.gen.view_models.views.lobby.races_lobby_view.scoring_model import ScoringTypeEnum
from races.gui.shared.event import RacesEvent
from races.settings import HINTS
from races_common.races_constants import BATTLE_EVENT_TYPE, RACES_ROCKET_BOOSTER, RACES_RAPIDSHELLING, RACES_SHIELD, RACES_POWER_IMPULSE
import CommandMapping
from account_helpers.AccountSettings import RACES_F1_HELPER_SHOWN
from constants import SERVER_TICK_LENGTH, ARENA_PERIOD, EQUIPMENT_STAGES
from frameworks.wulf import ViewFlags, ViewSettings
from frameworks.wulf.view.array import fillViewModelsArray
from gui.battle_control import avatar_getter
from gui.battle_control.battle_constants import FEEDBACK_EVENT_ID
from gui.battle_control.battle_constants import VEHICLE_VIEW_STATE
from gui.impl.gen import R
from gui.impl.pub import ViewImpl
from gui.shared import EVENT_BUS_SCOPE
from gui.shared.utils.key_mapping import getReadableKey
from helpers import dependency, time_utils
from helpers.CallbackDelayer import CallbackDelayer
from skeletons.gui.battle_session import IBattleSessionProvider, IArenaDataProvider
from skeletons.gui.game_control import IRacesBattleController
UPDATE_TICK_LENGTH = SERVER_TICK_LENGTH
_logger = logging.getLogger(__name__)
if typing.TYPE_CHECKING:
    from typing import Sequence, Tuple, TypeVar, Callable, Optional, Any, List
    from Event import Event
    from gui.battle_control.controllers.consumables.equipment_ctrl import _VisualScriptItem
    from races.gui.battle_control.controllers.consumables.equipment_ctrl import RacesEquipmentsController
    from gui.battle_control.controllers.consumables.ammo_ctrl import ReloadingTimeSnapshot, AmmoController
    from gui.battle_control.arena_info.arena_vos import VehicleArenaInfoVO
    from gui.battle_control.controllers.interfaces import IBattleController
    from gui.battle_control.controllers.vehicle_state_ctrl import VehicleStateController
    from gui.battle_control.controllers.feedback_adaptor import BattleFeedbackAdaptor
    from gui.battle_control.controllers.feedback_events import PlayerFeedbackEvent
    from races.settings import Goal
    BattleControllerType = TypeVar('BattleControllerType', bound=IBattleController)
SCORE_EVENT_IDS = {BATTLE_EVENT_TYPE.RACES_SHOT: ScoringTypeEnum.SHOT,
 BATTLE_EVENT_TYPE.RACES_RAMMING: ScoringTypeEnum.RAM,
 BATTLE_EVENT_TYPE.RACES_ELECTRICAL_SHOCK: ScoringTypeEnum.SHOCK,
 BATTLE_EVENT_TYPE.RACES_BOOST: ScoringTypeEnum.BOOST,
 BATTLE_EVENT_TYPE.RACES_SHIELD: ScoringTypeEnum.SHIELD,
 BATTLE_EVENT_TYPE.RACES_POWER_IMPULSE: ScoringTypeEnum.IMPULSE}
_ABILITY_TYPE_BY_EQUIP_NAME = {RACES_ROCKET_BOOSTER: Ability.ACCELERATION,
 RACES_SHIELD: Ability.SHIELD,
 RACES_RAPIDSHELLING: Ability.RAPID_SHELLING,
 RACES_POWER_IMPULSE: Ability.POWER_IMPULSE}
_AMMO_START_IDX = 0
_AMMO_COUNT = 1
_EQUIPMENT_START_IDX = _AMMO_START_IDX + _AMMO_COUNT
_EQUIPMENT_COUNT = 2
_PICKUP_COUNT = 1
_TOTAL_ABILITIES = _AMMO_COUNT + _EQUIPMENT_COUNT + _PICKUP_COUNT
_NO_BINDING = ''

def _getArenaScoreComponent():
    player = BigWorld.player()
    if player and player.arena is not None:
        arenaInfo = player.arena.arenaInfo
        if arenaInfo:
            return arenaInfo.dynamicComponents.get('ArenaInfoRacesScoreSystemComponent', None)
    return


class RacesHudView(ViewImpl):
    __slots__ = ('__callbackDelayer', '_vehMarkersMan', '_currentGoal', '_shootingAbilityCD', '_markersCtrl', '_period', '_minimapComponent', '_messages', '_playerListComponent', '_inShooting', '__baseReloadTime')
    __racesCtrl = dependency.descriptor(IRacesBattleController)
    MAX_MESSAGES_TO_SHOW = 8
    sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        settings = ViewSettings(R.views.races.battle.races_hud.RacesReactHudView(), ViewFlags.VIEW, RacesHudViewModel())
        super(RacesHudView, self).__init__(settings)
        self.__callbackDelayer = CallbackDelayer()
        self._markersCtrl = GUI.WGMarkerPositionController()
        self._vehMarkersMan = VehicleMarkersManager(self.viewModel.getVehicleMarkers(), weakref.proxy(self._markersCtrl))
        self._currentGoal = None
        self._period = ARENA_PERIOD.IDLE
        self._minimapComponent = RacesMinimapComponent(self.viewModel, self.sessionProvider)
        self._playerListComponent = PlayerListComponent()
        self._messages = deque(maxlen=self.MAX_MESSAGES_TO_SHOW)
        self._inShooting = False
        self.__baseReloadTime = 0
        return

    @property
    def viewModel(self):
        return super(RacesHudView, self).getViewModel()

    @property
    def currentGoal(self):
        return self._currentGoal

    @property
    def vehicleID(self):
        player = BigWorld.player()
        return player.playerVehicleID

    def createToolTipContent(self, event, contentID):
        ability = event.getArgument('ability')
        return AbilityTooltip(ability=ability)

    def _onLoading(self, *args, **kwargs):
        super(RacesHudView, self)._onLoading(*args, **kwargs)
        crosshair = self.sessionProvider.shared.crosshair
        aimPos = crosshair.getPosition()
        self._onCrosshairPositionChanged(aimPos[0], aimPos[1])
        self._vehMarkersMan.start()
        gunMarkersSetInfo = crosshair.getGunMarkersSetInfo()
        self._markersCtrl.add(self.viewModel.crosshair.proxy, gunMarkersSetInfo.clientMarkerDataProvider.positionMatrixProvider)
        arenaDP = self.sessionProvider.getArenaDP()
        playerVehicleInfo = arenaDP.getVehicleInfo()
        playerName = playerVehicleInfo.player.name
        self.viewModel.setPlayerName(playerName if playerName is not None else '')
        self._currentGoal = AnnouncementGoal(HINTS.get(AnnouncementTypeEnum.AWAITINGPLAYERS.value), {})
        self.viewModel.setAnnouncementType(AnnouncementTypeEnum.AWAITINGPLAYERS)
        self.viewModel.setArenaPhase(ArenaPhaseEnum.PREBATTLE)
        self._setIsArenaPrebattlePeriod(True)
        if not self.__racesCtrl.getRacesAccountSettings(RACES_F1_HELPER_SHOWN):
            self.viewModel.setIsVisibleHelpHint(True)
        abilitiesArray = self.viewModel.getAbilities()
        abilitiesArray.reserve(_TOTAL_ABILITIES)
        for i in range(_TOTAL_ABILITIES):
            model = AbilityModel()
            self._clearSlot(model)
            model.setKeyBind(self._getKeyString(i))
            abilitiesArray.addViewModel(model)

        _logger.info('HUD: onLoading')
        self._minimapComponent.setMinimapVehiclePositions()
        self._playerListComponent.updatePlayerList(self.viewModel)
        return

    def _finalize(self):
        self.__stopCallbackDelayer()
        self._markersCtrl.clear()
        self._vehMarkersMan.stop()
        super(RacesHudView, self)._finalize()

    def _getListeners(self):
        listeners = [(RacesEvent.ON_OPEN_F1_HELP, self._onDisableF1HelperHint, EVENT_BUS_SCOPE.BATTLE), (RacesEvent.ON_RACE_FINISHED, self._onRaceFinished, EVENT_BUS_SCOPE.BATTLE)]
        return listeners

    def _onDisableF1HelperHint(self, *args):
        self.viewModel.setIsVisibleHelpHint(False)

    def _onRaceFinished(self, *args):
        self.viewModel.setIsRaceFinished(True)

    def _onRaceArenaFinished(self, *args):
        self.viewModel.setIsArenaFinished(True)

    def _setIsArenaPrebattlePeriod(self, isPrebattle, *args):
        self.viewModel.setIsPrebattlePeriod(isPrebattle)

    def _getEvents(self):
        events = [(CommandMapping.g_instance.onMappingChanged, self._onMappingChanged)]
        eqCtrl = self.sessionProvider.shared.equipments
        if eqCtrl is not None:
            events.extend(((eqCtrl.onEquipmentCooldownTime, self._onEquipmentReloadTimeSet),
             (eqCtrl.onEquipmentAdded, self._onEquipmentAdded),
             (eqCtrl.onEquipmentRemoved, self._onEquipmentRemoved),
             (eqCtrl.onEquipmentUpdated, self._onEquipmentUpdated),
             (eqCtrl.onEquipmentsCleared, self._onClearEquipment)))
        ammoCtrl = self.sessionProvider.shared.ammo
        if ammoCtrl is not None:
            events.extend(((ammoCtrl.onGunReloadTimeSet, self._onGunReloadTimeSet), (ammoCtrl.onShellsAdded, self._onShellsAdded)))
        crosshair = self.sessionProvider.shared.crosshair
        if crosshair is not None:
            events.append((crosshair.onCrosshairPositionChanged, self._onCrosshairPositionChanged))
        vehicleCtrl = self.sessionProvider.shared.vehicleState
        if vehicleCtrl is not None:
            events.append((vehicleCtrl.onVehicleStateUpdated, self._onVehicleStateUpdated))
        feedbackCtrl = self.sessionProvider.shared.feedback
        if feedbackCtrl is not None:
            events.append((feedbackCtrl.onPlayerFeedbackReceived, self._onPlayerFeedbackReceived))
            events.append((feedbackCtrl.onVehicleFeedbackReceived, self.__onVehicleFeedbackReceived))
        return events

    def __onSecond(self):
        with self.viewModel.transaction() as model:
            self._updateArenaTimer(model)
            self._updateAnnouncement(model)
            self._playerListComponent.updatePlayerList(model)
        return time_utils.ONE_SECOND

    def _updateArenaTimer(self, transaction):
        periodCtrl = self.sessionProvider.shared.arenaPeriod
        period = periodCtrl.getPeriod()
        if period == ARENA_PERIOD.BATTLE:
            transaction.setArenaTimeLeft(getRemainingTime())

    def _updateAnnouncement(self, transaction):
        if self.currentGoal is not None:
            self.currentGoal.updateAnnouncement(transaction)
        return

    def _clearCurrentGoal(self, transaction=None):
        if self._currentGoal is None:
            return
        else:
            self._currentGoal.endAnnouncement(transaction)
            self._currentGoal = None
            return

    def setPeriod(self, period):
        if period == ARENA_PERIOD.PREBATTLE:
            self._currentGoal = AnnouncementGoal(HINTS.get(AnnouncementTypeEnum.PREBATTLE.value), {'param2': 'True'})
        elif period == ARENA_PERIOD.BATTLE:
            self._setIsArenaPrebattlePeriod(False)
            self._onDisableF1HelperHint()
            with self.viewModel.transaction() as transaction:
                transaction.setArenaPhase(ArenaPhaseEnum.RACE)
                self._clearCurrentGoal(transaction=transaction)
                self._updateAnnouncement(transaction)
        elif period == ARENA_PERIOD.AFTERBATTLE:
            with self.viewModel.transaction() as transaction:
                self._clearCurrentGoal(transaction=transaction)
                transaction.setAnnouncementType(AnnouncementTypeEnum.MISSIONCOMPLETED)
                self._onRaceArenaFinished()
        self.__stopPeriodTimer(self._period)
        self.__startPeriodTimer(period)
        self._period = period

    def showHint(self, hint, data=None):
        if self._currentGoal is not None and self._currentGoal.type in [AnnouncementTypeEnum.SCANNING, AnnouncementTypeEnum.SCANAVAILABLE, AnnouncementTypeEnum.SCANNING] and not self._currentGoal.ended:
            _logger.warning('Tried to show hint while scanning event is in progress.')
            return
        else:
            self._currentGoal = getAnnouncementType(hint, data)
            return

    def __startPeriodTimer(self, period):
        cd = self.__callbackDelayer
        if period == ARENA_PERIOD.PREBATTLE or period == ARENA_PERIOD.BATTLE:
            if not cd.hasDelayedCallback(self.__onSecond):
                self.__onSecond()
                cd.delayCallback(time_utils.ONE_SECOND, self.__onSecond)
            if not cd.hasDelayedCallback(self._minimapComponent.onPositionsUpdate):
                self._minimapComponent.onPositionsUpdate()
                cd.delayCallback(_UPDATE_POSITIONS_SEC, self._minimapComponent.onPositionsUpdate)

    def __stopPeriodTimer(self, period):
        if period == ARENA_PERIOD.BATTLE:
            self.__callbackDelayer.stopCallback(self.__onSecond)
            self.__callbackDelayer.stopCallback(self._minimapComponent.onPositionsUpdate)

    def __stopCallbackDelayer(self):
        self.__callbackDelayer.clearCallbacks()

    def _onCrosshairPositionChanged(self, posx, posy):
        aimModel = self.viewModel.aim
        with aimModel.transaction() as model:
            model.setPosx(posx)
            model.setPosy(posy)

    def _onShellsAdded(self, intCD, descriptor, *args):
        _logger.debug('Shell added: %s, %s', str(intCD), descriptor)
        idx = self._getAmmoIdx(intCD)
        if idx is None:
            return
        else:

            def addShell(model):
                model.setReloadTime(0)
                model.setAbility(Ability.SHELL)
                model.setReloadTimeLeft(0)
                model.setIsActive(False)
                model.setKeyBind('')

            self._updateAbilityModel(idx, addShell)
            return

    def _onGunReloadTimeSet(self, intCD, state, skipAutoLoader):
        _logger.debug('Reload: %s, %s, %d', str(intCD), str(state), skipAutoLoader)
        timeLeft = state.getTimeLeft()
        if self.__baseReloadTime == 0:
            self.__baseReloadTime = avatar_getter.getPlayerVehicle().typeDescriptor.gun.reloadTime
        idx = self._getAmmoIdx(intCD)
        if idx is None:
            return
        else:
            with self.viewModel.transaction() as model:
                model.setReloadTimeLeft(timeLeft)
                model.setReloadTime(self.__baseReloadTime)
                abilityArray = model.getAbilities()
                abilityModel = abilityArray[idx]
                abilityModel.setReloadTime(self.__baseReloadTime)
                abilityModel.setReloadTimeLeft(timeLeft)
            return

    def _onEquipmentReloadTimeSet(self, intCD, timeLeft, isBaseTime, isFinish):
        _logger.debug('Reload equipment: %s, %s, %d, %d', str(intCD), timeLeft, isBaseTime, isFinish)
        idx = self._getEquipmentIdx(intCD)
        if idx is None:
            return
        else:

            def updateReload(model):
                if isBaseTime:
                    model.setReloadTime(timeLeft)
                    model.setReloadTimeLeft(0)
                else:
                    model.setReloadTimeLeft(timeLeft)

            self._updateAbilityModel(idx, updateReload)
            return

    def _onEquipmentUpdated(self, slotIndex, item):
        timeLeft = item.getTimeRemaining()
        maxTime = item.getTotalTime()
        stage = item.getStage()
        _logger.debug('Equipment updated: slotIndex: %s, name: %s, timeLeft: %s, maxtime: %s, stage: %s, quantity: %s', str(slotIndex), item.getDescriptor().name, timeLeft, maxTime, stage, item.getQuantity())
        idx = self._getEquipmentIdx(slotIndex)
        if idx is None:
            return
        else:

            def updateReload(model):
                equipmentName = item.getDescriptor().name
                isActive = stage == EQUIPMENT_STAGES.ACTIVE
                if stage == EQUIPMENT_STAGES.DEPLOYING and equipmentName == RACES_RAPIDSHELLING:
                    isActive = True
                    if not self._inShooting:
                        model.setIsShooting(True)
                        self._inShooting = True
                else:
                    model.setIsShooting(False)
                model.setIsActive(isActive)
                if stage == EQUIPMENT_STAGES.COOLDOWN:
                    model.setReloadTimeLeft(timeLeft)
                    model.setReloadTime(maxTime)
                if stage == EQUIPMENT_STAGES.READY:
                    model.setReloadTimeLeft(0)
                model.setAbilityDuration(item.getDescriptor().duration)

            self._updateAbilityModel(idx, updateReload)
            return

    def _onEquipmentAdded(self, slotIndex, item):
        equipmentName = item.getDescriptor().name
        _logger.debug('Equipment added: slotIndex %s, name: %s, quantity: %s, totalTime: %s, stage: %s', str(slotIndex), equipmentName, item.getQuantity(), item.getTotalTime(), item.getStage())
        idx = self._getEquipmentIdx(slotIndex)
        if idx is None:
            return
        else:

            def addEquipment(model):
                model.setReloadTime(item.getTotalTime())
                model.setAbility(_ABILITY_TYPE_BY_EQUIP_NAME[equipmentName])
                model.setReloadTimeLeft(item.getTimeRemaining())
                model.setIsActive(False)
                model.setAbilityDuration(item.getDescriptor().duration)
                model.setIsShooting(False)

            self._updateAbilityModel(idx, addEquipment)
            return

    def _onMappingChanged(self, *args):
        _logger.debug('Consumable panel: Updating key bindings.')
        with self.viewModel.transaction() as model:
            abilities = model.getAbilities()
            for i, ability in enumerate(abilities):
                ability.setKeyBind(self._getKeyString(i))

            abilities.invalidate()

    def _getKeyString(self, idx):
        if _AMMO_START_IDX <= idx < _EQUIPMENT_START_IDX:
            _logger.debug('Index is of an ammo slot, ammo slots should not have keybindings.')
            return _NO_BINDING
        relativeEquipmentIndex = idx - _EQUIPMENT_START_IDX
        command = CommandMapping.CMD_AMMO_CHOICE_1 + relativeEquipmentIndex
        if command > CommandMapping.CMD_AMMO_CHOICE_0:
            _logger.warning('No free command slots. Command: %s', command)
            return _NO_BINDING
        return getReadableKey(command)

    def _onEquipmentRemoved(self, slotIndex, item):
        _logger.debug('Equipment removed: %s, %s, %s', str(slotIndex), item.getDescriptor().name, item.getQuantity())
        abilityArray = self.viewModel.getAbilities()
        model = abilityArray[slotIndex + _AMMO_COUNT]
        self._clearSlot(model)
        abilityArray.invalidate()
        self._inShooting = False

    def _clearSlot(self, model):
        model.setAbility(Ability.NONE)
        model.setReloadTimeLeft(0)
        model.setIsShooting(False)
        model.setIsActive(False)
        model.setReloadTime(0)

    def _onClearEquipment(self):
        _logger.debug('clearing equipment from panel.')
        abilityArray = self.viewModel.getAbilities()
        for model in abilityArray:
            self._clearSlot(model)

        abilityArray.invalidate()

    def _getEquipmentIdx(self, slotIndex):
        idx = slotIndex
        if idx is None:
            return
        else:
            idx += _EQUIPMENT_START_IDX
            if idx >= _TOTAL_ABILITIES:
                _logger.warning('Equipment %d at index %d. The index is out of the expected range. Equipment indices start at %d, total equipment slots %d', slotIndex, idx, _EQUIPMENT_START_IDX, _TOTAL_ABILITIES)
                return
            return idx

    def _getAmmoIdx(self, intCD):
        ammoCtrl = self.sessionProvider.shared.ammo
        if intCD not in ammoCtrl.getShellsOrderIter():
            _logger.warning('Shell %d cannot be found in ammo controller. Ammo list %s', intCD, ammoCtrl.getShellsLayout())
            return None
        idx = list(ammoCtrl.getShellsOrderIter()).index(intCD)
        idx += _AMMO_START_IDX
        if idx >= _EQUIPMENT_START_IDX:
            _logger.info('Additional shell %d cannot be displayed in model. Model only displays %d shell(s).', intCD, _AMMO_COUNT)
            return None
        else:
            return idx

    def _updateAbilityModel(self, idx, updateFunc):
        abilityArray = self.viewModel.getAbilities()
        if idx >= len(abilityArray):
            _logger.warning('Index is out of range for the abilities array. Array length: %s, Expected number of abilities %s', len(abilityArray), _TOTAL_ABILITIES)
            return
        abilityModel = abilityArray[idx]
        with abilityModel.transaction() as model:
            updateFunc(model)
        abilityArray.invalidate()

    def _onVehicleStateUpdated(self, state, value):
        if state == VEHICLE_VIEW_STATE.DESTROY_TIMER:
            self.viewModel.setVehicleOverturned(avatar_getter.isVehicleOverturned())
        if state == VEHICLE_VIEW_STATE.SPEED:
            self.viewModel.setVehicleSpeed(value)
        if state == VEHICLE_VIEW_STATE.LOOT:
            pass

    def __onVehicleFeedbackReceived(self, eventID, vehicleID, _):
        if eventID == FEEDBACK_EVENT_ID.ENTITY_IN_FOCUS:
            vehicle = BigWorld.entity(vehicleID)
            if vehicle is not None:
                vehicle.removeEdge()
        return

    def _onPlayerFeedbackReceived(self, events):
        nextID = self._messages[-1].getId() + 1 if self._messages else 0
        playerTotalScore = self.viewModel.getPlayerTotalScore()
        for event in events:
            eventType = event.getBattleEventType()
            if eventType in SCORE_EVENT_IDS:
                messageModel = self.viewModel.getMessagesType()()
                messageModel.setId(nextID)
                messageModel.setType(SCORE_EVENT_IDS.get(eventType))
                racesPoints = event.getExtra()
                messageModel.setRacesPoints(racesPoints)
                playerTotalScore += racesPoints
                self._messages.append(messageModel)
                nextID += 1

        with self.viewModel.transaction() as model:
            fillViewModelsArray(self._messages, model.getMessages())
            model.setPlayerTotalScore(playerTotalScore)
